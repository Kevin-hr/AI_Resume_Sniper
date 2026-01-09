"""
PDF Parser / PDF解析器

Document parser plugin for PDF files using pdfplumber.
"""

import os
from typing import Dict, Optional
import pdfplumber

from src.interfaces.idocument_parser import IDocumentParser, ParsedDocument
from src.core.exceptions import ParseError


class PDFParser(IDocumentParser):
    """
    PDF document parser using pdfplumber.

    Extracts text from PDF files with page-by-page processing.
    """

    PARSER_NAME = "pdf"
    SUPPORTED_FORMATS = ['.pdf']

    def __init__(self, extract_tables: bool = False, **kwargs):
        """
        Initialize PDF parser.

        Args:
            extract_tables: Whether to extract table data
            **kwargs: Additional parameters
        """
        self._extract_tables = extract_tables

    @property
    def parser_name(self) -> str:
        return self.PARSER_NAME

    @property
    def supported_formats(self) -> list:
        return self.SUPPORTED_FORMATS

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse a PDF file and extract text content.

        Args:
            file_path: Path to the PDF file

        Returns:
            ParsedDocument object
        """
        if not os.path.exists(file_path):
            raise ParseError(f"File not found: {file_path}")

        try:
            text = ""
            metadata = {
                "pages": 0,
                "extracted_tables": 0
            }

            with pdfplumber.open(file_path) as pdf:
                metadata["pages"] = len(pdf.pages)

                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                    # Extract tables if enabled
                    if self._extract_tables:
                        tables = page.extract_tables()
                        if tables:
                            metadata["extracted_tables"] += len(tables)
                            for table in tables:
                                text += self._format_table(table) + "\n"

            return ParsedDocument(
                content=text.strip(),
                file_path=file_path,
                file_type="pdf",
                metadata=metadata
            )

        except Exception as e:
            raise ParseError(f"Failed to parse PDF {file_path}: {e}")

    def validate_file(self, file_path: str) -> bool:
        """Check if file is a valid PDF."""
        if not os.path.exists(file_path):
            return False

        _, ext = os.path.splitext(file_path)
        return ext.lower() == '.pdf'

    def parse_content(self, content: bytes, file_extension: str) -> str:
        """
        Parse PDF content from raw bytes.

        Args:
            content: Raw PDF bytes
            file_extension: File extension (should be '.pdf')

        Returns:
            Extracted text content
        """
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            doc = self.parse(tmp_path)
            return doc.content
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _format_table(self, table: list) -> str:
        """Format extracted table data as text."""
        if not table:
            return ""

        lines = []
        for row in table:
            if row:
                formatted_row = " | ".join(str(cell) if cell else "" for cell in row)
                lines.append(formatted_row)

        return "\n".join(lines)
