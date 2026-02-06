"""Settings router for user account management."""

from fastapi import APIRouter, Depends

from api.dependencies import (
    get_current_user,
    get_email_verification_repository,
    get_event_bus_dependency,
    get_user_repository,
)
from application.schemas import (
    AddEmailRequest,
    AddEmailResponse,
    VerifyAdditionalEmailRequest,
    VerifyAdditionalEmailResponse,
)
from domain.entities import User
from domain.repositories import IUserRepository
from infrastructure.events.event_bus import EventBus

router = APIRouter(prefix="/settings", tags=["settings"])


@router.post("/add-email", response_model=AddEmailResponse)
async def add_email(
    request: AddEmailRequest,
    current_user: User = Depends(get_current_user),
    user_repository: IUserRepository = Depends(get_user_repository),
    verification_repository=Depends(get_email_verification_repository),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Add and verify a new email address for the user."""
    from application.use_cases.settings.add_additional_email import (
        AddAdditionalEmailUseCase,
    )

    use_case = AddAdditionalEmailUseCase(
        user_repository, verification_repository, event_bus
    )
    await use_case.execute(str(current_user.id), request.email)

    return AddEmailResponse()


@router.post(
    "/verify-additional-email", response_model=VerifyAdditionalEmailResponse
)
async def verify_additional_email(
    request: VerifyAdditionalEmailRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    verification_repository=Depends(get_email_verification_repository),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Verify the additional email address."""
    from application.use_cases.settings.verify_additional_email import (
        VerifyAdditionalEmailUseCase,
    )

    use_case = VerifyAdditionalEmailUseCase(
        user_repository, verification_repository, event_bus
    )
    message, email = await use_case.execute(request.token)

    return VerifyAdditionalEmailResponse(message=message, email=email)
