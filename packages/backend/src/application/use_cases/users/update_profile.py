from domain.repositories import IUserRepository
from application.schemas import UpdateUserRequest
from domain.entities import User
from domain.value_objects import Email, Username
from domain.exceptions import (
    UserEmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    UsernameChangeTooSoonException,
)


class UpdateProfileUseCase:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository

    async def execute(self, update_data: UpdateUserRequest, current_user: User):
        # Check if email is being updated and if it's already taken
        if update_data.email and str(update_data.email) != str(
            current_user.email
        ):
            if await self._user_repository.exists_by_email(
                Email(value=str(update_data.email))
            ):
                raise UserEmailAlreadyExistsException(str(update_data.email))
            email_to_update = Email(value=str(update_data.email))
        else:
            email_to_update = None

        if update_data.username and str(update_data.username) == str(
            current_user.username
        ):
            raise UsernameAlreadyExistsException(str(update_data.username))

        # Check if username is being updated and if it's already taken
        if update_data.username and str(update_data.username) != str(
            current_user.username
        ):
            from datetime import datetime, timezone, timedelta

            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)

            # Check if account is old enough
            if current_user.created_at > thirty_days_ago:
                days_remaining = 30 - (now - current_user.created_at).days
                raise UsernameChangeTooSoonException(days_remaining)

            # Check if username was changed recently
            if (
                current_user.username_last_changed_at
                and current_user.username_last_changed_at > thirty_days_ago
            ):
                days_since_change = (
                    now - current_user.username_last_changed_at
                ).days
                days_remaining = 30 - days_since_change
                raise UsernameChangeTooSoonException(days_remaining)

            if await self._user_repository.exists_by_username(
                Username(value=str(update_data.username))
            ):
                raise UsernameAlreadyExistsException(str(update_data.username))
            username_to_update = Username(value=str(update_data.username))
        else:
            username_to_update = None

        # Update user profile
        current_user.update_profile(
            name=update_data.name,
            email=email_to_update,
            avatar=update_data.avatar,
            username=username_to_update,
        )

        # Save to database
        await self._user_repository.save(current_user)
