"""Password service interface for hashing and verification."""

from abc import ABC, abstractmethod

from src.domain.value_objects import HashedPassword, Password


class IPasswordService(ABC):
    """Abstract interface for password hashing operations."""

    @abstractmethod
    def hash_password(self, password: Password) -> HashedPassword:
        """Hash a plaintext password."""
        pass

    @abstractmethod
    def verify_password(
        self, password: Password, hashed_password: HashedPassword
    ) -> bool:
        """Verify a plaintext password against a hashed password."""
        pass
