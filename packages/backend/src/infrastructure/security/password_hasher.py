"""Password hashing service using Argon2id."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.application.services.password_service import IPasswordService
from src.domain.value_objects import HashedPassword, Password


class Argon2PasswordHasher(IPasswordService):
    """Password hashing implementation using Argon2id algorithm."""

    def __init__(self):
        """Initialize Argon2 password hasher with secure defaults."""
        self._hasher = PasswordHasher(
            time_cost=2,  # Number of iterations
            memory_cost=65536,  # Memory usage in KiB (64 MB)
            parallelism=4,  # Number of parallel threads
            hash_len=32,  # Length of the hash in bytes
            salt_len=16,  # Length of the salt in bytes
        )

    def hash_password(self, password: Password) -> HashedPassword:
        """
        Hash a plaintext password using Argon2id.

        Args:
            password: Password value object containing plaintext password

        Returns:
            HashedPassword value object containing the hashed password
        """
        hashed = self._hasher.hash(password.value)
        return HashedPassword(value=hashed)

    def verify_password(
        self, password: Password, hashed_password: HashedPassword
    ) -> bool:
        """
        Verify a plaintext password against a hashed password.

        Args:
            password: Password value object containing plaintext password
            hashed_password: HashedPassword value object to verify against

        Returns:
            True if password matches, False otherwise
        """
        try:
            self._hasher.verify(hashed_password.value, password.value)

            # Check if rehashing is needed (parameters changed)
            if self._hasher.check_needs_rehash(hashed_password.value):
                # Note: In production, you might want to trigger a password rehash here
                pass

            return True
        except VerifyMismatchError:
            return False
