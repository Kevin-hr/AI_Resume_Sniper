"""
Anthropic Provider / Anthropic提供商

LLM provider implementation for Claude API.
"""

import os
import time
from typing import Dict, Optional, Any

try:
    from anthropic import Anthropic, APIError, RateLimitError, AuthenticationError
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from src.interfaces.illm_provider import ILLMProvider, LLMResponse
from src.core.config import get_config, LLMProviderConfig
from src.core.exceptions import (
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMAPIError,
    ConfigurationError
)


class AnthropicProvider(ILLMProvider):
    """
    Anthropic Claude API provider implementation.

    Supports Claude models (Sonnet, Haiku, etc.).
    """

    PROVIDER_NAME = "anthropic"
    SUPPORTED_MODELS = [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-haiku-3-20250514"
    ]

    # OpenAI-compatible model name mapping
    MODEL_NAME_MAP = {
        "claude-sonnet-4-20250514": "sonnet-4",
        "claude-opus-4-20250514": "opus-4",
        "claude-haiku-3-20250514": "haiku-3"
    }

    def __init__(self, config: LLMProviderConfig = None, api_key: str = None,
                 base_url: str = None, **kwargs):
        """
        Initialize Anthropic provider.

        Args:
            config: LLMProviderConfig object (optional)
            api_key: API key string (overrides config)
            base_url: Base URL (overrides config)
            **kwargs: Additional parameters
        """
        if not HAS_ANTHROPIC:
            raise ConfigurationError(
                "Anthropic package not installed. Run: pip install anthropic"
            )

        self._config = config
        self._api_key = api_key
        self._base_url = base_url
        self._client: Optional[Anthropic] = None
        self._setup_client()

    def _setup_client(self):
        """Initialize the Anthropic client."""
        # Get API key
        if self._api_key:
            api_key = self._api_key
        elif self._config and self._config.api_key:
            api_key = self._config.api_key
        elif self._config and self._config.api_key_env:
            api_key = os.getenv(self._config.api_key_env, "")
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY", "")

        if not api_key:
            self._api_key = None
            return

        # Get base URL
        if self._base_url:
            base_url = self._base_url
        elif self._config and self._config.base_url:
            base_url = self._config.base_url
        else:
            base_url = os.getenv("ANTHROPIC_BASE_URL", None)

        # Initialize client
        self._client = Anthropic(
            api_key=api_key,
            base_url=base_url,
            timeout=self._config.timeout if self._config else 60
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
        Send chat completion request to Anthropic.

        Args:
            messages: List of message dicts (converted to proper format)
            model: Model name
            temperature: Response creativity
            max_tokens: Maximum response tokens
            **kwargs: Additional parameters

        Returns:
            LLMResponse object
        """
        if not self.is_available():
            raise LLMAuthenticationError(
                "Anthropic API key not configured."
            )

        # Use default model if not specified
        if model is None:
            if self._config and self._config.default_model:
                model = self._config.default_model
            else:
                model = "claude-sonnet-4-20250514"

        # Get max tokens from config
        if self._config:
            model_cfg = self.get_model_info(model)
            if model_cfg:
                max_tokens = model_cfg.get("max_tokens", max_tokens)

        start_time = time.time()
        tokens_used = 0

        # Convert messages format (Anthropic uses different format)
        # Anthropic expects: [{"role": "user", "content": "..."}]
        # System messages should be separate
        system_message = None
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content")
            else:
                user_messages.append(msg)

        try:
            # Claude API call
            response = self._client.messages.create(
                model=self.MODEL_NAME_MAP.get(model, model),
                messages=user_messages,
                system=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                raw_response=response
            )

        except AuthenticationError as e:
            raise LLMAuthenticationError(f"Anthropic authentication failed: {e}")
        except RateLimitError as e:
            retry_after = getattr(e, 'retry_after', None)
            raise LLMRateLimitError(
                f"Anthropic rate limit exceeded: {e}",
                retry_after=retry_after
            )
        except APIError as e:
            raise LLMAPIError(f"Anthropic API error: {e}")
        except Exception as e:
            raise LLMAPIError(f"Unexpected error calling Anthropic: {e}")

    def chat_stream(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ):
        """
        Send a streaming chat completion request to Anthropic.
        """
        if not self.is_available():
            raise LLMAuthenticationError("Anthropic API key not configured.")

        # Use default model if not specified
        if model is None:
            if self._config and self._config.default_model:
                model = self._config.default_model
            else:
                model = "claude-sonnet-4-20250514"

        # Convert messages format
        system_message = None
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content")
            else:
                user_messages.append(msg)

        try:
            with self._client.messages.stream(
                model=self.MODEL_NAME_MAP.get(model, model),
                messages=user_messages,
                system=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            raise LLMAPIError(f"Anthropic API error: {e}")

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
            response = self._client.messages.create(
                model=self.MODEL_NAME_MAP.get(self.supported_models[0], self.supported_models[0]),
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return response is not None
        except Exception:
            return False

    def is_available(self) -> bool:
        """Check if provider is properly configured."""
        return self._client is not None
