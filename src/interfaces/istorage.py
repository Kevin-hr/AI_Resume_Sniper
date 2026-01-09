"""
IStorage Interface / 存储接口

Abstract base class for storage and caching plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StorageItem:
    """Storage item wrapper."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def is_expired(self) -> bool:
        """Check if item has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class IStorage(ABC):
    """
    Abstract base class for storage and caching.

    All storage plugins must implement these methods:
    - save(): Store a value with a key
    - load(): Retrieve a value by key
    - delete(): Remove a value by key
    - exists(): Check if key exists
    - clear(): Clear all stored data
    """

    @property
    @abstractmethod
    def storage_name(self) -> str:
        """Unique identifier for this storage."""
        pass

    @abstractmethod
    def save(self, key: str, value: Any, ttl: int = None, **kwargs) -> bool:
        """
        Save a value to storage.

        Args:
            key: Unique identifier for the value
            value: Value to store (will be serialized)
            ttl: Time-to-live in seconds (None = no expiry)
            **kwargs: Additional storage-specific parameters

        Returns:
            True if save successful, False otherwise
        """
        pass

    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from storage.

        Args:
            key: Unique identifier for the value

        Returns:
            Stored value or None if not found
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a value from storage.

        Args:
            key: Unique identifier for the value

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in storage."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all stored data."""
        pass

    @abstractmethod
    def get_cache_key(self, *args) -> str:
        """
        Generate a consistent cache key from arguments.

        Useful for creating cache keys based on input content.
        """
        pass
