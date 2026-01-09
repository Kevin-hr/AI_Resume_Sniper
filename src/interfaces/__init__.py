"""
Plugin Interfaces / 插件接口定义

Abstract Base Classes (ABC) for plugin system.
所有插件必须实现相应的抽象接口。
"""

from .illm_provider import ILLMProvider
from .idocument_parser import IDocumentParser
from .istorage import IStorage

__all__ = ['ILLMProvider', 'IDocumentParser', 'IStorage']
