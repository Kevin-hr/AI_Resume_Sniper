"""
Text Parser / 文本解析器

Document parser plugin for plain text and Markdown files.
"""

import os
from typing import Dict, Optional

from src.interfaces.idocument_parser import IDocumentParser, ParsedDocument
from src.core.exceptions import ParseError, UnsupportedFormatError


class TextParser(IDocumentParser):
    """
    Text document parser for plain text and Markdown files.

    Handles various text encodings with automatic fallback.
    """

    PARSER_NAME = "text"
    SUPPORTED_FORMATS = ['.txt', '.md']

    # Common encodings to try in order
    ENCODING_PRIORITY = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'cp1252']

    def __init__(self, **kwargs):
        """
        Initialize text parser.

        Args:
            **kwargs: Additional parameters
        """
        pass

    @property
    def parser_name(self) -> str:
        return self.PARSER_NAME

    @property
    def supported_formats(self) -> list:
        return self.SUPPORTED_FORMATS

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse a text file and extract content.

        Args:
            file_path: Path to the text file

        Returns:
            ParsedDocument object
        """
        if not os.path.exists(file_path):
            raise ParseError(f"File not found: {file_path}")

        # Validate file extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(f"Text parser only supports .txt and .md, got: {ext}")

        content = self._read_file(file_path)

        # Detect file type
        file_type = "markdown" if ext.lower() == '.md' else "text"

        return ParsedDocument(
            content=content,
            file_path=file_path,
            file_type=file_type,
            metadata={
                "encoding": self._detect_encoding(file_path),
                "lines": len(content.splitlines())
            }
        )

    def validate_file(self, file_path: str) -> bool:
        """Check if file is a supported text format."""
        if not os.path.exists(file_path):
            return False

        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.SUPPORTED_FORMATS

    def parse_content(self, content: bytes, file_extension: str) -> str:
        """
        Parse text content from raw bytes.

        Args:
            content: Raw file bytes
            file_extension: File extension (e.g., '.txt', '.md')

        Returns:
            Decoded text content
        """
        for encoding in self.ENCODING_PRIORITY:
            try:
                return content.decode(encoding)
            except (UnicodeDecodeError, UnicodeError):
                continue

        # Last resort: ignore errors
        return content.decode('utf-8', errors='ignore')

    def _read_file(self, file_path: str) -> str:
        """Read file with automatic encoding detection."""
        # First try UTF-8
        for encoding in self.ENCODING_PRIORITY:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue

        raise ParseError(f"Unable to decode file with any supported encoding: {file_path}")

    def _detect_encoding(self, file_path: str) -> str:
        """Detect the encoding of a file."""
        for encoding in self.ENCODING_PRIORITY:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue

        return "unknown"
