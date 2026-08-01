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
    request: CheckoutSessionRequest,
    user: User = Depends(get_current_user)
):
    """Create a Stripe Checkout Session."""
    try:
        # We need the active Price ID for the given Product ID
        prices = stripe.Price.list(product=request.product_id, active=True, limit=1)
        
        if not prices.data:
            raise HTTPException(
                status_code=404,
                detail=f"No active price found for product {request.product_id}"
            )
            
        price_id = prices.data[0].id

        # Create Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            client_reference_id=str(user.id),
            metadata={
                "tier": "Starter" if request.product_id == "prod_UzilBzFZtKK3ms" else "Professional"
            },
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{settings.frontend_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/pricing",
        )

        return {"url": checkout_session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Stripe Webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature header")

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
        
        if user_id:
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.subscription_tier = tier
                user.stripe_customer_id = customer_id
                await db.commit()
                print(f"Checkout completed. Updated user {user_id} to tier {tier}")

    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        # Handle subscription upgrades/downgrades if necessary
        print(f"Subscription updated: {getattr(subscription, 'id', None)}")

    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        customer_id = getattr(subscription, "customer", None)
        if customer_id:
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
            user = result.scalar_one_or_none()
            if user:
                user.subscription_tier = None
                await db.commit()
                print(f"Subscription deleted. Reverted user {user.id} to Free")

    else:
        print(f"Unhandled event type: {event.type}")

    return Response(status_code=200)
