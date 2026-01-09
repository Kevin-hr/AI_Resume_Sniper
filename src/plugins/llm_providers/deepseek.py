"""
DeepSeek Provider / DeepSeek提供商

LLM provider implementation for DeepSeek API.
"""

import os
import time
from typing import Dict, Optional, Any
from openai import OpenAI, APIError, RateLimitError, AuthenticationError
import httpx

from src.interfaces.illm_provider import ILLMProvider, LLMResponse
from src.core.config import get_config, LLMProviderConfig
from src.core.exceptions import (
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMAPIError,
    ConfigurationError
)


def _get_proxy_client() -> Optional[httpx.Client]:
    """Create an HTTP client with proxy if environment variables are set."""
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

    if not http_proxy and not https_proxy:
        return None

    # Use https proxy if available, otherwise http proxy
    proxy_url = https_proxy or http_proxy
    return httpx.Client(proxy=proxy_url)


class DeepSeekProvider(ILLMProvider):
    """
    DeepSeek API provider implementation.

    Supports deepseek-chat model with OpenAI-compatible API.
    """

    PROVIDER_NAME = "deepseek"
    SUPPORTED_MODELS = ["deepseek-chat", "deepseek-reasoner"]

    def __init__(self, config: LLMProviderConfig = None, api_key: str = None,
                 base_url: str = None, **kwargs):
        """
        Initialize DeepSeek provider.

        Args:
            config: LLMProviderConfig object (optional)
            api_key: API key string (overrides config)
            base_url: Base URL (overrides config)
            **kwargs: Additional parameters
        """
        self._config = config
        self._api_key = api_key
        self._base_url = base_url
        self._client: Optional[OpenAI] = None
        self._setup_client()

    def _setup_client(self):
        """Initialize the OpenAI client for DeepSeek."""
        # Get API key
        if self._api_key:
            api_key = self._api_key
        elif self._config and self._config.api_key:
            api_key = self._config.api_key
        elif self._config and self._config.api_key_env:
            api_key = os.getenv(self._config.api_key_env, "")
        else:
            api_key = os.getenv("DEEPSEEK_API_KEY", "")

        if not api_key:
            self._api_key = None
            return

        # Get base URL
        if self._base_url:
            base_url = self._base_url
        elif self._config and self._config.base_url:
            base_url = self._config.base_url
        else:
            base_url = "https://api.deepseek.com"

        # Initialize client with proxy support
        http_client = _get_proxy_client()
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=self._config.timeout if self._config else 60,
            http_client=http_client
        )
        self._api_key = api_key

    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME

    @property
    def supported_models(self) -> list:
        return self.SUPPORTED_MODELS

    def chat(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """
        Send chat completion request to DeepSeek.

        Args:
            messages: List of message dicts
            model: Model name (defaults to deepseek-chat)
            temperature: Response creativity
            max_tokens: Maximum response tokens
            **kwargs: Additional parameters

        Returns:
            LLMResponse object
        """
        if not self.is_available():
            raise LLMAuthenticationError(
                "DeepSeek API key not configured. "
                "Set DEEPSEEK_API_KEY env var or provide api_key parameter."
            )

        # Use default model if not specified
        if model is None:
            if self._config and self._config.default_model:
                model = self._config.default_model
            else:
                model = "deepseek-chat"

        # Get max tokens from config if available
        if self._config:
            model_cfg = self.get_model_info(model)
            if model_cfg:
                max_tokens = model_cfg.get("max_tokens", max_tokens)

        start_time = time.time()
        tokens_used = 0

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                raw_response=response
            )

        except AuthenticationError as e:
            raise LLMAuthenticationError(f"DeepSeek authentication failed: {e}")
        except RateLimitError as e:
            retry_after = getattr(e, 'retry_after', None)
            raise LLMRateLimitError(
                f"DeepSeek rate limit exceeded: {e}",
                retry_after=retry_after
            )
        except APIError as e:
            raise LLMAPIError(f"DeepSeek API error: {e}")
        except Exception as e:
            raise LLMAPIError(f"Unexpected error calling DeepSeek: {e}")

    def chat_stream(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ):
        """
        Send a streaming chat completion request to DeepSeek.
        """
        if not self.is_available():
            raise LLMAuthenticationError(
                "DeepSeek API key not configured. "
                "Set DEEPSEEK_API_KEY env var or provide api_key parameter."
            )

        # Use default model if not specified
        if model is None:
            if self._config and self._config.default_model:
                model = self._config.default_model
            else:
                model = "deepseek-chat"

        # Get max tokens from config if available
        if self._config:
            model_cfg = self.get_model_info(model)
            if model_cfg:
                max_tokens = model_cfg.get("max_tokens", max_tokens)

        try:
            stream = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            # Track if we are in reasoning mode
            in_reasoning = False
            
            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    
                    # Handle reasoning content (DeepSeek R1/V3)
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                        if not in_reasoning:
                            yield "> **Thinking Process:**\n> "
                            in_reasoning = True
                        
                        # Replace newlines with newline + > for blockquote continuity
                        content = delta.reasoning_content.replace("\n", "\n> ")
                        yield content
                        
                    elif hasattr(delta, 'content') and delta.content:
                        # If we were in reasoning mode and now getting content, close the blockquote
                        if in_reasoning:
                            yield "\n\n---\n\n"
                            in_reasoning = False
                            
                        yield delta.content

        except AuthenticationError as e:
            raise LLMAuthenticationError(f"DeepSeek authentication failed: {e}")
        except RateLimitError as e:
            retry_after = getattr(e, 'retry_after', None)
            raise LLMRateLimitError(
                f"DeepSeek rate limit exceeded: {e}",
                retry_after=retry_after
            )
        except APIError as e:
            raise LLMAPIError(f"DeepSeek API error: {e}")
        except Exception as e:
            raise LLMAPIError(f"Unexpected error calling DeepSeek: {e}")

    def get_model_info(self, model: str) -> Dict:
        """Get configuration info for a specific model."""
        if not self._config:
            return {"name": model, "max_tokens": 16384, "temperature": 0.7}

        for m in self._config.models:
            if m.name == model:
                return {
                    "name": m.name,
                    "max_tokens": m.max_tokens,
                    "temperature": m.temperature,
                    "context_window": m.context_window,
                    "capabilities": m.capabilities
                }

        return {"name": model, "max_tokens": 16384, "temperature": 0.7}

    def health_check(self) -> bool:
        """Verify API connectivity."""
        if not self.is_available():
            return False

        try:
            # Simple test request
            response = self._client.chat.completions.create(
                model=self.supported_models[0],
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return response is not None
        except Exception:
            return False

    def is_available(self) -> bool:
        """Check if provider is properly configured."""
        return self._client is not None
