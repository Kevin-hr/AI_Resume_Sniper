"""
Local Storage / 本地存储

File-based storage for caching and persistence.
"""

import os
import json
import hashlib
import pickle
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from threading import Lock

from src.interfaces.istorage import IStorage, StorageItem
from src.core.exceptions import StorageError


class LocalStorage(IStorage):
    """
    Local file-based storage implementation.

    Stores cached data as JSON files in a specified directory.
    Supports TTL-based expiration.
    """

    STORAGE_NAME = "local"

    def __init__(self, cache_dir: str = "cache", **kwargs):
        """
        Initialize local storage.

        Args:
            cache_dir: Directory for storing cache files
            **kwargs: Additional parameters
        """
        self._cache_dir = Path(cache_dir)
        self._lock = Lock()
        self._ensure_dir()

    def _ensure_dir(self):
        """Create cache directory if it doesn't exist."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def storage_name(self) -> str:
        return self.STORAGE_NAME

    def save(self, key: str, value: Any, ttl: int = None, **kwargs) -> bool:
        """
        Save a value to local storage.

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

                file_path = self._get_file_path(key)
                with open(file_path, 'wb') as f:
                    pickle.dump(item, f)

                return True

        except Exception as e:
            raise StorageError(f"Failed to save to local storage: {e}")

    def load(self, key: str) -> Optional[Any]:
        """
        Load a value from local storage.

        Args:
            key: Unique identifier

        Returns:
            Stored value or None if not found/expired
        """
        try:
            with self._lock:
                file_path = self._get_file_path(key)

                if not file_path.exists():
                    return None

                with open(file_path, 'rb') as f:
                    item = pickle.load(f)

                if item.is_expired():
                    self.delete(key)
                    return None

                return item.value

        except Exception as e:
            raise StorageError(f"Failed to load from local storage: {e}")

    def delete(self, key: str) -> bool:
        """
        Delete a value from local storage.

        Args:
            key: Unique identifier

        Returns:
            True if deleted
        """
        try:
            with self._lock:
                file_path = self._get_file_path(key)

                if file_path.exists():
                    file_path.unlink()
                    return True

                return False

        except Exception as e:
            raise StorageError(f"Failed to delete from local storage: {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        try:
            file_path = self._get_file_path(key)

            if not file_path.exists():
                return False

            with open(file_path, 'rb') as f:
                item = pickle.load(f)

            if item.is_expired():
                self.delete(key)
                return False

            return True

        except Exception:
            return False

    def clear(self) -> bool:
        """Clear all stored data."""
        try:
            with self._lock:
                for file_path in self._cache_dir.glob("*.cache"):
                    file_path.unlink()
                return True

        except Exception as e:
            raise StorageError(f"Failed to clear local storage: {e}")

    def get_cache_key(self, *args) -> str:
        """Generate a consistent cache key from arguments."""
        content = json.dumps(args, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_file_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        safe_key = "".join(c if c.isalnum() or c in "_-." else "_" for c in key)
        return self._cache_dir / f"{safe_key}.cache"

    def cleanup_expired(self):
        """Remove all expired cache entries."""
        try:
            with self._lock:
                for file_path in self._cache_dir.glob("*.cache"):
                    try:
                        with open(file_path, 'rb') as f:
                            item = pickle.load(f)
                        if item.is_expired():
                            file_path.unlink()
                    except Exception:
                        file_path.unlink()

        except Exception as e:
            raise StorageError(f"Failed to cleanup expired items: {e}")
