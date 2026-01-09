"""
Document Parsers Package / 文档解析器插件包

Plugin implementations for various document formats.
"""

from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .text_parser import TextParser

__all__ = ['PDFParser', 'DOCXParser', 'TextParser']

# Parser registry for dynamic loading
PARSER_REGISTRY = {
    'pdf': PDFParser,
    'docx': DOCXParser,
    'text': TextParser,
}


def get_parser(parser_name: str, **kwargs):
    """
    Factory function to get a parser instance.

    Args:
        parser_name: Name of the parser (pdf, docx, text)
        **kwargs: Configuration parameters

    Returns:
        IDocumentParser instance
    """
    if parser_name not in PARSER_REGISTRY:
        from src.core.exceptions import PluginNotFoundError
        raise PluginNotFoundError(f"Document parser '{parser_name}' not found. "
                                   f"Available: {list(PARSER_REGISTRY.keys())}")

    return PARSER_REGISTRY[parser_name](**kwargs)


def get_parser_for_file(file_path: str, **kwargs):
    """
    Factory function to get appropriate parser for a file.

    Args:
        file_path: Path to the file
        **kwargs: Configuration parameters

    Returns:
        IDocumentParser instance
    """
    import os
    _, ext = os.path.splitext(file_path)
    ext = ext.lower().lstrip('.')

    # Map extension to parser name
    ext_map = {
        'pdf': 'pdf',
        'docx': 'docx',
        'doc': 'docx',  # Legacy support
        'txt': 'text',
        'md': 'text',
    }

    parser_name = ext_map.get(ext)
    if parser_name is None:
        from src.core.exceptions import UnsupportedFormatError
        raise UnsupportedFormatError(f"Unsupported file format: .{ext}")

    return get_parser(parser_name, **kwargs)
