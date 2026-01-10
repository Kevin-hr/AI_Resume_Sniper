"""
TalentOS Package / 人才操作系统主包

v1.0 Plugin-based architecture.
"""

from .core.engine import TalentOSEngine, create_engine, AnalysisResult
from .core.config import get_config, reload_config, AppConfig
from .core.exceptions import (
    TalentOSError,
    PluginError,
    LLMProviderError,
    DocumentParserError,
    StorageError,
)

__version__ = "1.0.0"

__all__ = [
    'TalentOSEngine',
    'create_engine',
    'AnalysisResult',
    'get_config',
    'reload_config',
    'AppConfig',
    'TalentOSError',
    'PluginError',
    'LLMProviderError',
    'DocumentParserError',
    'StorageError',
]
