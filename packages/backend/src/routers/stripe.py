import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from core.dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/stripe", tags=["Stripe"])

# Configure Stripe
stripe.api_key = settings.stripe_secret_key


class CheckoutSessionRequest(BaseModel):
    product_id: str


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest, user: User = Depends(get_current_user)
):
    """Create a Stripe Checkout Session."""
    try:
        # We need the active Price ID for the given Product ID
        prices = stripe.Price.list(
            product=request.product_id, active=True, limit=1
        )

        if not prices.data:
            raise HTTPException(
                status_code=404,
                detail=f"No active price found for product {request.product_id}",
            )

        price_id = prices.data[0].id

        is_starter = request.product_id == settings.stripe_product_id_starter

        # Build subscription_data — include a free trial for the Starter plan
        subscription_data: dict = {}
        if is_starter and settings.stripe_starter_trial_days > 0:
            subscription_data["trial_period_days"] = (
                settings.stripe_starter_trial_days
            )
            subscription_data["trial_settings"] = {
                "end_behavior": {"missing_payment_method": "cancel"}
            }

        # Create Checkout Session — only pass subscription_data when it's non-empty
        session_kwargs: dict = {
            "payment_method_types": ["card"],
            "client_reference_id": str(user.id),
            "metadata": {"tier": "Starter" if is_starter else "Professional"},
            "line_items": [{"price": price_id, "quantity": 1}],
            "mode": "subscription",
            "success_url": f"{settings.frontend_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{settings.frontend_url}/pricing",
        }
        if subscription_data:
            session_kwargs["subscription_data"] = subscription_data

        checkout_session = stripe.checkout.Session.create(**session_kwargs)

        return {"url": checkout_session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Stripe error"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/subscription")
async def get_subscription(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get the current user's subscription details from Stripe."""
    if not user.stripe_subscription_id:
        return None

    try:
        subscription = stripe.Subscription.retrieve(
            str(user.stripe_subscription_id),
            expand=["items.data.price.product"],
        )

        if subscription.status == "canceled":
            # Self-heal if webhook was missed
            user.stripe_subscription_id = None
            user.subscription_tier = None
            await db.commit()
            return None

        item = subscription.items.data[0]
        price = item.price

        # product may be a Product object or a plain string ID depending on expand
        product = price.product if hasattr(price, "product") else None
        product_name = (
            product.name
            if product is not None
            and not isinstance(product, str)
            and hasattr(product, "name")
            else None
        )
        tier = user.subscription_tier or product_name or "Starter"

        # In Stripe API >= 2025-03-31, current_period_end lives on the item
        current_period_end = getattr(
            item, "current_period_end", None
        ) or getattr(subscription, "current_period_end", None)

        # cancel_at_period_end is deprecated; fall back to cancel_at for newer API versions
        cancel_at_period_end = getattr(
            subscription, "cancel_at_period_end", False
        ) or bool(getattr(subscription, "cancel_at", None))

        # recurring can be None on some price types; guard against that
        recurring = getattr(price, "recurring", None)
        interval = (
            getattr(recurring, "interval", "month") if recurring else "month"
        )

        return {
            "status": subscription.status,
            "trial_end": getattr(subscription, "trial_end", None),
            "current_period_end": current_period_end,
            "cancel_at_period_end": cancel_at_period_end,
            "amount": getattr(price, "unit_amount", 0),
            "interval": interval,
            "tier": tier,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Stripe error"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/cancel-subscription")
async def cancel_subscription(user: User = Depends(get_current_user)):
    """Cancel a Stripe Subscription."""
    try:
        # We need the active Price ID for the given Product ID
        if not user.stripe_subscription_id:
            raise HTTPException(
                status_code=404,
                detail="No active subscription found",
            )

        response = stripe.Subscription.modify(
            str(user.stripe_subscription_id), cancel_at_period_end=True
        )

        return {"status": "success", "canceled_at": response.canceled_at}
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Stripe error"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe Webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(
            status_code=400, detail="Missing Stripe signature header"
        )

    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = getattr(session, "client_reference_id", None)

        metadata = getattr(session, "metadata", None)
        tier = getattr(metadata, "tier", "Starter") if metadata else "Starter"

        customer_id = getattr(session, "customer", None)
        subscription_id = getattr(session, "subscription", None)

        if user_id:
            from sqlalchemy import select

            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.subscription_tier = tier
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                await db.commit()
                print(
                    f"Checkout completed. Updated user {user_id} to tier {tier}"
                )

    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        customer_id = getattr(subscription, "customer", None)
        sub_status = getattr(subscription, "status", None)

        if customer_id:
            from sqlalchemy import select

            result = await db.execute(
                select(User).where(User.stripe_customer_id == customer_id)
            )
            user = result.scalar_one_or_none()
            if user:
                # If the subscription is no longer active (canceled, unpaid, etc.),
                # revoke the tier rather than trying to map the product.
                active_statuses = {"active", "trialing", "past_due"}
                if sub_status not in active_statuses:
                    user.subscription_tier = None
                    user.stripe_subscription_id = None
                    await db.commit()
                    print(
                        f"Subscription {getattr(subscription, 'id', None)} moved to "
                        f"status '{sub_status}'. Reverted user {user.id} to Free."
                    )
                else:
                    # Map the Stripe product back to our tier name
                    try:
                        items = getattr(subscription, "items", None)
                        product_id = None
                        if items and items.data:
                            price = getattr(items.data[0], "price", None)
                            if price:
                                product = getattr(price, "product", None)
                                product_id = (
                                    product
                                    if isinstance(product, str)
                                    else getattr(product, "id", None)
                                )

                        if product_id == settings.stripe_product_id_starter:
                            new_tier = "Starter"
                        elif (
                            product_id
                            == settings.stripe_product_id_professional
                        ):
                            new_tier = "Professional"
                        else:
                            new_tier = (
                                user.subscription_tier
                            )  # keep existing if unknown

                        user.subscription_tier = new_tier
                        user.stripe_subscription_id = getattr(
                            subscription, "id", user.stripe_subscription_id
                        )
                        await db.commit()
                        print(
                            f"Subscription updated for user {user.id}: "
                            f"tier={new_tier}, status={sub_status}"
                        )
                    except Exception as e:
                        print(f"Error processing subscription.updated: {e}")

    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        customer_id = getattr(subscription, "customer", None)
        if customer_id:
            from sqlalchemy import select

            result = await db.execute(
                select(User).where(User.stripe_customer_id == customer_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.subscription_tier = None
                user.stripe_subscription_id = None
                await db.commit()
                print(f"Subscription deleted. Reverted user {user.id} to Free.")

    else:
        print(f"Unhandled event type: {event.type}")

    return Response(status_code=200)
