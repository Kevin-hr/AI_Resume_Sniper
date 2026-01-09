"""
Storage Package / 存储插件包

Plugin implementations for caching and persistence.
"""

from .local_storage import LocalStorage
from .memory_cache import MemoryCache

__all__ = ['LocalStorage', 'MemoryCache']

# Storage registry for dynamic loading
STORAGE_REGISTRY = {
    'local': LocalStorage,
    'memory': MemoryCache,
}


def get_storage(storage_name: str, **kwargs):
    """
    Factory function to get a storage instance.

    Args:
        storage_name: Name of the storage backend (local, memory)
        **kwargs: Configuration parameters

    Returns:
        IStorage instance
    """
    if storage_name not in STORAGE_REGISTRY:
        from src.core.exceptions import PluginNotFoundError
        raise PluginNotFoundError(f"Storage backend '{storage_name}' not found. "
                                   f"Available: {list(STORAGE_REGISTRY.keys())}")

    return STORAGE_REGISTRY[storage_name](**kwargs)
