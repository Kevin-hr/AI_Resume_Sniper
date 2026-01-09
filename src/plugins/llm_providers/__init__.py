"""
LLM Providers Package / LLM提供商插件包

Plugin implementations for various LLM services.
"""

from .deepseek import DeepSeekProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider

__all__ = ['DeepSeekProvider', 'OpenAIProvider', 'AnthropicProvider']

# Provider registry for dynamic loading
PROVIDER_REGISTRY = {
    'deepseek': DeepSeekProvider,
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
}


def get_provider(provider_name: str, **kwargs):
    """
    Factory function to get a provider instance.

    Args:
        provider_name: Name of the provider (deepseek, openai, anthropic)
        **kwargs: Configuration parameters

    Returns:
        ILLMProvider instance
    """
    if provider_name not in PROVIDER_REGISTRY:
        from src.core.exceptions import PluginNotFoundError
        raise PluginNotFoundError(f"LLM provider '{provider_name}' not found. "
                                   f"Available: {list(PROVIDER_REGISTRY.keys())}")

    return PROVIDER_REGISTRY[provider_name](**kwargs)
