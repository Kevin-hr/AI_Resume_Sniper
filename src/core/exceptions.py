"""
Custom Exceptions / 自定义异常

Exception hierarchy for Resume Sniper plugin system.
"""

from typing import Optional


class ResumeSniperError(Exception):
    """Base exception for all Resume Sniper errors."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.details = details or {}


class PluginError(ResumeSniperError):
    """Base exception for plugin-related errors."""
    pass


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin is not found."""
    pass


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""
    pass


class PluginValidationError(PluginError):
    """Raised when plugin configuration is invalid."""
    pass


class LLMProviderError(PluginError):
    """Base exception for LLM provider errors."""
    pass


class LLMAPIError(LLMProviderError):
    """Raised when LLM API call fails."""
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(message, kwargs)
        self.status_code = status_code


class LLMAuthenticationError(LLMProviderError):
    """Raised when API authentication fails."""
    pass


class LLMRateLimitError(LLMProviderError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class DocumentParserError(PluginError):
    """Base exception for document parser errors."""
    pass


class UnsupportedFormatError(DocumentParserError):
    """Raised when document format is not supported."""
    pass


class ParseError(DocumentParserError):
    """Raised when document parsing fails."""
    pass


class StorageError(PluginError):
    """Base exception for storage errors."""
    pass


class CacheKeyError(StorageError):
    """Raised when cache key generation fails."""
    pass


class ConfigurationError(ResumeSniperError):
    """Raised when configuration is invalid."""
    pass


class AnalysisError(ResumeSniperError):
    """Raised when resume analysis fails."""
    pass
