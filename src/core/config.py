"""
Configuration Management / 配置管理

Centralized configuration for Resume Sniper plugin system.
Supports YAML config file and environment variables.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model."""
    name: str
    max_tokens: int = 16384
    temperature: float = 0.7
    context_window: int = 65536
    cost_per_1k_tokens: float = 0.0
    capabilities: List[str] = field(default_factory=list)


@dataclass
class LLMProviderConfig:
    """Configuration for an LLM provider."""
    provider: str
    enabled: bool = True
    api_key_env: str = ""
    api_key: str = ""
    base_url: str = ""
    models: List[ModelConfig] = field(default_factory=list)
    default_model: str = ""
    timeout: int = 60
    max_retries: int = 3


@dataclass
class ParserConfig:
    """Configuration for a document parser."""
    parser: str
    enabled: bool = True
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StorageConfig:
    """Configuration for storage backend."""
    backend: str
    enabled: bool = True
    cache_ttl: int = 3600  # 1 hour default
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppConfig:
    """Main application configuration."""
    app_name: str = "AI Resume Sniper"
    version: str = "1.3.0"
    debug: bool = False
    log_level: str = "INFO"

    # Plugin configurations
    llm_providers: Dict[str, LLMProviderConfig] = field(default_factory=dict)
    document_parsers: Dict[str, ParserConfig] = field(default_factory=dict)
    storage: StorageConfig = None

    # Analysis settings
    analysis: Dict[str, Any] = field(default_factory=dict)

    # Paths
    data_dir: str = "data"
    cache_dir: str = "cache"
    output_dir: str = "output"

    def get_llm_provider_config(self, provider_name: str) -> Optional[LLMProviderConfig]:
        """Get configuration for a specific LLM provider."""
        return self.llm_providers.get(provider_name)

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled LLM providers."""
        return [name for name, cfg in self.llm_providers.items() if cfg.enabled]

    def get_model_config(self, provider_name: str, model_name: str = None) -> Optional[ModelConfig]:
        """Get configuration for a specific model."""
        provider_cfg = self.get_llm_provider_config(provider_name)
        if not provider_cfg:
            return None

        if model_name is None:
            model_name = provider_cfg.default_model

        for model in provider_cfg.models:
            if model.name == model_name:
                return model

        return provider_cfg.models[0] if provider_cfg.models else None


class ConfigManager:
    """
    Centralized configuration manager.

    Loads configuration from YAML file with environment variable override.
    """

    DEFAULT_CONFIG = {
        "app_name": "AI Resume Sniper",
        "version": "1.3.0",
        "debug": False,
        "log_level": "INFO",
        "llm_providers": {
            "deepseek": {
                "provider": "deepseek",
                "enabled": True,
                "api_key_env": "DEEPSEEK_API_KEY",
                "base_url": "https://api.deepseek.com",
                "models": [
                    {"name": "deepseek-chat", "max_tokens": 4096, "temperature": 0.7}
                ],
                "default_model": "deepseek-chat",
                "timeout": 60,
                "max_retries": 3
            },
            "openai": {
                "provider": "openai",
                "enabled": False,
                "api_key_env": "OPENAI_API_KEY",
                "base_url": "https://api.openai.com/v1",
                "models": [
                    {"name": "gpt-4o", "max_tokens": 16384, "temperature": 0.7},
                    {"name": "gpt-4o-mini", "max_tokens": 16384, "temperature": 0.7}
                ],
                "default_model": "gpt-4o",
                "timeout": 60,
                "max_retries": 3
            },
            "anthropic": {
                "provider": "anthropic",
                "enabled": False,
                "api_key_env": "ANTHROPIC_API_KEY",
                "base_url": "https://api.anthropic.com",
                "models": [
                    {"name": "claude-sonnet-4-20250514", "max_tokens": 16384, "temperature": 0.7}
                ],
                "default_model": "claude-sonnet-4-20250514",
                "timeout": 60,
                "max_retries": 3
            }
        },
        "document_parsers": {
            "pdf": {"parser": "pdf", "enabled": True},
            "docx": {"parser": "docx", "enabled": True},
            "text": {"parser": "text", "enabled": True}
        },
        "storage": {
            "backend": "local",
            "enabled": True,
            "cache_ttl": 3600,
            "options": {}
        },
        "analysis": {
            "default_persona": "hrbp",
            "personas": {
                "hrbp": {
                    "name": "Senior HRBP",
                    "description": "Direct, result-oriented, harsh but professional",
                    "system_prompt": "You are a Senior HRBP with 10+ years experience..."
                },
                "coach": {
                    "name": "Career Coach",
                    "description": "Friendly, supportive, encouraging",
                    "system_prompt": "You are a supportive career coach..."
                }
            }
        },
        "paths": {
            "data_dir": "data",
            "cache_dir": "cache",
            "output_dir": "output"
        }
    }

    def __init__(self, config_path: str = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to YAML config file (optional)
        """
        self._config_path = config_path
        self._config: AppConfig = None
        self._load_config()

    def _load_config(self):
        """Load configuration from file or use defaults."""
        raw_config = self.DEFAULT_CONFIG.copy()

        # Load from YAML if available
        if self._config_path and Path(self._config_path).exists():
            if HAS_YAML:
                try:
                    with open(self._config_path, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f)
                        if yaml_config:
                            raw_config = self._deep_merge(raw_config, yaml_config)
                except Exception as e:
                    print(f"Warning: Failed to load config file: {e}")

        # Apply environment variable overrides
        raw_config = self._apply_env_overrides(raw_config)

        # Convert to AppConfig dataclass
        self._config = self._dict_to_app_config(raw_config)

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_env_overrides(self, config: dict) -> dict:
        """Apply environment variable overrides."""
        # Map env vars to config paths
        env_mappings = {
            "DEEPSEEK_API_KEY": ("llm_providers", "deepseek", "api_key"),
            "OPENAI_API_KEY": ("llm_providers", "openai", "api_key"),
            "OPENAI_BASE_URL": ("llm_providers", "openai", "base_url"),
            "OPENAI_DEFAULT_MODEL": ("llm_providers", "openai", "default_model"),
            "OPENAI_ENABLED": ("llm_providers", "openai", "enabled"),
            "ANTHROPIC_API_KEY": ("llm_providers", "anthropic", "api_key"),
            "ANTHROPIC_BASE_URL": ("llm_providers", "anthropic", "base_url"),
            "ANTHROPIC_DEFAULT_MODEL": ("llm_providers", "anthropic", "default_model"),
            "ANTHROPIC_ENABLED": ("llm_providers", "anthropic", "enabled"),
            "RESUME_SNIPER_DEBUG": ("debug",),
        }

        for env_var, path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested(config, path, value)

        return config

    def _set_nested(self, d: dict, path: tuple, value):
        """Set a nested dictionary value."""
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    def _dict_to_app_config(self, d: dict) -> AppConfig:
        """Convert dictionary to AppConfig dataclass."""
        # Extract paths
        paths = d.pop("paths", {})

        # Convert LLM providers
        llm_providers = {}
        for name, cfg in d.get("llm_providers", {}).items():
            models = [ModelConfig(**m) for m in cfg.get("models", [])]
            llm_providers[name] = LLMProviderConfig(
                provider=cfg.get("provider", name),
                enabled=cfg.get("enabled", True),
                api_key_env=cfg.get("api_key_env", ""),
                api_key=cfg.get("api_key", ""),
                base_url=cfg.get("base_url", ""),
                models=models,
                default_model=cfg.get("default_model", ""),
                timeout=cfg.get("timeout", 60),
                max_retries=cfg.get("max_retries", 3)
            )

        # Convert document parsers
        parsers = {}
        for name, cfg in d.get("document_parsers", {}).items():
            parsers[name] = ParserConfig(
                parser=cfg.get("parser", name),
                enabled=cfg.get("enabled", True),
                options=cfg.get("options", {})
            )

        # Convert storage
        storage_cfg = d.get("storage", {})
        storage = StorageConfig(
            backend=storage_cfg.get("backend", "local"),
            enabled=storage_cfg.get("enabled", True),
            cache_ttl=storage_cfg.get("cache_ttl", 3600),
            options=storage_cfg.get("options", {})
        )

        return AppConfig(
            app_name=d.get("app_name", "AI Resume Sniper"),
            version=d.get("version", "1.3.0"),
            debug=d.get("debug", False),
            log_level=d.get("log_level", "INFO"),
            llm_providers=llm_providers,
            document_parsers=parsers,
            storage=storage,
            analysis=d.get("analysis", {}),
            data_dir=paths.get("data_dir", "data"),
            cache_dir=paths.get("cache_dir", "cache"),
            output_dir=paths.get("output_dir", "output")
        )

    @property
    def config(self) -> AppConfig:
        """Get current configuration."""
        return self._config

    def get_llm_provider_config(self, provider_name: str) -> Optional[LLMProviderConfig]:
        """Get configuration for a specific LLM provider."""
        return self._config.llm_providers.get(provider_name)

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled LLM providers."""
        return [name for name, cfg in self._config.llm_providers.items() if cfg.enabled]

    def get_model_config(self, provider_name: str, model_name: str = None) -> Optional[ModelConfig]:
        """Get configuration for a specific model."""
        provider_cfg = self.get_llm_provider_config(provider_name)
        if not provider_cfg:
            return None

        if model_name is None:
            model_name = provider_cfg.default_model

        for model in provider_cfg.models:
            if model.name == model_name:
                return model

        # Return first model if specified not found
        return provider_cfg.models[0] if provider_cfg.models else None

    def reload(self):
        """Reload configuration from file."""
        self._load_config()


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config(config_path: str = None) -> AppConfig:
    """Get or create global configuration instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager.config


def reload_config(config_path: str = None):
    """Reload global configuration."""
    global _config_manager
    _config_manager = ConfigManager(config_path)
