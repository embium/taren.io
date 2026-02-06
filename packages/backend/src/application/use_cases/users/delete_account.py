"""Delete account use case."""

from application.schemas import DeleteAccountRequest
from application.services.password_service import IPasswordService
from domain.value_objects import Password
from domain.entities import User
from domain.repositories import IUserRepository, ISessionRepository
from domain.exceptions import IncorrectPasswordException


class DeleteAccountUseCase:
    """Use case for deleting user account."""

    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: ISessionRepository,
        password_service: IPasswordService,
    ):
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._password_service = password_service

    async def execute(
        self, delete_data: DeleteAccountRequest, current_user: User
    ) -> None:
        """
        Delete user account.

        Args:
            delete_data: Delete account request
            current_user: Current user
        """
        # Verify password
        is_valid, _ = self._password_service.verify_password(
            Password(value=delete_data.password),
            current_user.password_hash,
        )
        if not is_valid:
            raise IncorrectPasswordException()

        # Deactivate user account (soft delete)
        current_user.deactivate()
        await self._user_repository.save(current_user)

        # Revoke all active sessions
        await self._session_repository.revoke_all_for_user(current_user.id)
