"""
IDocumentParser Interface / 文档解析器接口

Abstract base class for document parser plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ParsedDocument:
    """Parsed document wrapper."""
    content: str
    file_path: str
    file_type: str
    metadata: Dict = None
    encoding: str = "utf-8"

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IDocumentParser(ABC):
    """
    Abstract base class for document parsers.

    All document parser plugins must implement these methods:
    - parse(): Parse a file and return content
    - get_supported_formats(): List supported file extensions
    - validate_file(): Check if file can be processed
    """

    @property
    @abstractmethod
    def parser_name(self) -> str:
        """Unique identifier for this parser."""
        pass

    @property
    @abstractmethod
    def supported_formats(self) -> list:
        """List of supported file extensions (e.g., ['.pdf', '.docx'])."""
        pass

    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse a document file and extract text content.

        Args:
            file_path: Path to the document file

        Returns:
            ParsedDocument object with extracted content and metadata
        """
        pass

    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the document file

        Returns:
            True if file format is supported, False otherwise
        """
        pass

    @abstractmethod
    def parse_content(self, content: bytes, file_extension: str) -> str:
        """
        Parse content from raw bytes.

        Args:
            content: Raw file bytes
            file_extension: File extension (e.g., '.pdf')

        Returns:
            Extracted text content
        """
        pass
