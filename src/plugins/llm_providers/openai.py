"""
OpenAI Provider / OpenAI提供商

LLM provider implementation for OpenAI API.
"""

import os
import time
from typing import Dict, Optional, Any
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

from src.interfaces.illm_provider import ILLMProvider, LLMResponse
from src.core.config import get_config, LLMProviderConfig
from src.core.exceptions import (
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMAPIError
)


class OpenAIProvider(ILLMProvider):
    """
    OpenAI API provider implementation.

    Supports GPT-4o, GPT-4o-mini, and other OpenAI models.
    """

    PROVIDER_NAME = "openai"
    SUPPORTED_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

    def __init__(self, config: LLMProviderConfig = None, api_key: str = None,
                 base_url: str = None, **kwargs):
        """
        Initialize OpenAI provider.

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
        """Initialize the OpenAI client."""
        # Get API key
        if self._api_key:
            api_key = self._api_key
        elif self._config and self._config.api_key:
            api_key = self._config.api_key
        elif self._config and self._config.api_key_env:
            api_key = os.getenv(self._config.api_key_env, "")
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")

        if not api_key:
            self._api_key = None
            return

        # Get base URL (for Azure OpenAI or compatible endpoints)
        if self._base_url:
            base_url = self._base_url
        elif self._config and self._config.base_url:
            base_url = self._config.base_url
        else:
            base_url = "https://api.openai.com/v1"

        # Initialize client
        self._client = OpenAI(
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
        """Send chat completion request to OpenAI."""
        if not self.is_available():
            raise LLMAuthenticationError(
                "OpenAI API key not configured."
            )

        # Use default model if not specified
        if model is None:
            if self._config and self._config.default_model:
                model = self._config.default_model
            else:
                model = "gpt-4o"

        # Get max tokens from config
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
            raise LLMAuthenticationError(f"OpenAI authentication failed: {e}")
        except RateLimitError as e:
            retry_after = getattr(e, 'retry_after', None)
            raise LLMRateLimitError(
                f"OpenAI rate limit exceeded: {e}",
                retry_after=retry_after
            )
        except APIError as e:
            raise LLMAPIError(f"OpenAI API error: {e}")
        except Exception as e:
            raise LLMAPIError(f"Unexpected error calling OpenAI: {e}")

    def chat_stream(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ):
        """
        Send a streaming chat completion request to OpenAI.
        """
        if not self.is_available():
            raise LLMAuthenticationError("OpenAI API key not configured.")

        # Use default model if not specified
        if model is None:
            if self._config and self._config.default_model:
                model = self._config.default_model
            else:
                model = "gpt-4o"

        try:
            stream = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise LLMAPIError(f"OpenAI API error: {e}")

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
