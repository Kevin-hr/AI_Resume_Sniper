"""
ILLMProvider Interface / LLM提供商接口

Abstract base class for LLM provider plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM API response wrapper."""
    content: str
    model: str
    tokens_used: int
    latency_ms: float
    raw_response: Optional[Any] = None


class ILLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM plugins must implement these methods:
    - chat(): Send a chat completion request
    - get_model_info(): Get model configuration
    - health_check(): Verify API connectivity
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier for this provider."""
        pass

    @property
    @abstractmethod
    def supported_models(self) -> list:
        """List of supported model names."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (uses default if None)
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum response tokens
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object with content and metadata
        """
        pass

    @abstractmethod
    def chat_stream(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ):
        """
        Send a streaming chat completion request.

        Yields:
            Chunks of the response content.
        """
        pass

    @abstractmethod
    def get_model_info(self, model: str) -> Dict:
        """Get configuration info for a specific model."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify API connectivity and authentication."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is properly configured and ready."""
        pass
