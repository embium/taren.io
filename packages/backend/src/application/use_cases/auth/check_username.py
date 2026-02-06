"""Check username use case."""

from domain.repositories import IUserRepository
from domain.value_objects import Username


class CheckUsernameUseCase:
    """Use case for checking username availability."""

    def __init__(
        self,
        user_repository: IUserRepository,
    ):
        self._user_repository = user_repository

    async def execute(self, username: str) -> bool:
        """
        Check if username exists.

        Args:
            username: Username to check

        Returns:
            bool: True if username exists, False otherwise
        """
        # Create value object (validates format)
        try:
            username_vo = Username(value=username)
        except ValueError:
            # If invalid format, we can consider it as "not existing" or raise error
            # For checking availability, if it's invalid it's technically not taken,
            # but also not usable.
            # However, typically this endpoint checks if it's TAKEN.
            return False

        return await self._user_repository.exists_by_username(username_vo)
