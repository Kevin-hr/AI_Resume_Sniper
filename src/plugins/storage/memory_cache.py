"""
Memory Cache / 内存缓存

In-memory storage for fast access caching.
"""

import hashlib
import json
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from threading import Lock

from src.interfaces.istorage import IStorage, StorageItem
from src.core.exceptions import StorageError


class MemoryCache(IStorage):
    """
    In-memory storage implementation.

    Stores cached data in memory with thread-safe access.
    Useful for short-lived caches within a single process.
    """

    STORAGE_NAME = "memory"

    def __init__(self, max_size: int = 1000, **kwargs):
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of items to store
            **kwargs: Additional parameters
        """
        self._cache: Dict[str, StorageItem] = {}
        self._max_size = max_size
        self._lock = Lock()

    @property
    def storage_name(self) -> str:
        return self.STORAGE_NAME

    def save(self, key: str, value: Any, ttl: int = None, **kwargs) -> bool:
        """
        Save a value to memory cache.

        Args:
            key: Unique identifier
            value: Value to store
            ttl: Time-to-live in seconds
            **kwargs: Additional parameters

        Returns:
            True if save successful
        """
        try:
            with self._lock:
                # Calculate expiration
                expires_at = None
                if ttl:
                    expires_at = datetime.now() + timedelta(seconds=ttl)

                item = StorageItem(
                    key=key,
                    value=value,
                    created_at=datetime.now(),
                    expires_at=expires_at,
                    metadata=kwargs
                )

                # Evict oldest if at capacity
                if len(self._cache) >= self._max_size:
                    self._evict_oldest()

                self._cache[key] = item
                return True

        except Exception as e:
            raise StorageError(f"Failed to save to memory cache: {e}")

    def load(self, key: str) -> Optional[Any]:
        """
        Load a value from memory cache.

        Args:
            key: Unique identifier

        Returns:
            Stored value or None if not found/expired
        """
        try:
            with self._lock:
                if key not in self._cache:
                    return None

                item = self._cache[key]

                # Check expiration
                if item.is_expired():
                    self.delete(key)
                    return None

                return item.value

        except Exception as e:
            raise StorageError(f"Failed to load from memory cache: {e}")

    def delete(self, key: str) -> bool:
        """
        Delete a value from memory cache.

        Args:
            key: Unique identifier

        Returns:
            True if deleted
        """
        try:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    return True
                return False

        except Exception as e:
            raise StorageError(f"Failed to delete from memory cache: {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        try:
            with self._lock:
                if key not in self._cache:
                    return False

                item = self._cache[key]

                if item.is_expired():
                    self.delete(key)
                    return False

                return True

        except Exception:
            return False

    def clear(self) -> bool:
        """Clear all cached data."""
        try:
            with self._lock:
                self._cache.clear()
                return True

        except Exception as e:
            raise StorageError(f"Failed to clear memory cache: {e}")

    def get_cache_key(self, *args) -> str:
        """
        Generate a consistent cache key from arguments.

        Creates a hash from string representations of arguments.
        """
        content = json.dumps(args, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _evict_oldest(self):
        """Remove the oldest item from cache."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self._lock:
            expired = sum(1 for item in self._cache.values() if item.is_expired())
            return {
                "total_items": len(self._cache),
                "valid_items": len(self._cache) - expired,
                "expired_items": expired,
                "max_size": self._max_size
            }
