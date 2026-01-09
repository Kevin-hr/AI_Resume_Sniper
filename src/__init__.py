"""
Resume Sniper Package / 简历狙击手主包

v1.3 Plugin-based architecture.
"""

from .core.engine import ResumeSniperEngine, create_engine, AnalysisResult
from .core.config import get_config, reload_config, AppConfig
from .core.exceptions import (
    ResumeSniperError,
    PluginError,
    LLMProviderError,
    DocumentParserError,
    StorageError,
)

__version__ = "1.3.0"

__all__ = [
    'ResumeSniperEngine',
    'create_engine',
    'AnalysisResult',
    'get_config',
    'reload_config',
    'AppConfig',
    'ResumeSniperError',
    'PluginError',
    'LLMProviderError',
    'DocumentParserError',
    'StorageError',
]
