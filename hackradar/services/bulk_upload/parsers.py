"""
File parsers for bulk project upload.

Uses the Strategy pattern: each parser implements FileParser and extracts
raw text tokens from a specific file format. The factory selects the right
parser based on the file extension.
"""

import csv
import io
from abc import ABC, abstractmethod


class FileParser(ABC):
    """Extract raw text tokens from a file's contents."""

    @abstractmethod
    def parse(self, content: str) -> list[str]:
        """Return a flat list of string tokens to be searched for GitHub URLs."""
        ...


class TxtFileParser(FileParser):
    """Parse plain-text files — each non-empty line is a token."""

    def parse(self, content: str) -> list[str]:
        return [line.strip() for line in content.splitlines() if line.strip()]


class CsvFileParser(FileParser):
    """Parse CSV files — every cell value is a token."""

    def parse(self, content: str) -> list[str]:
        reader = csv.reader(io.StringIO(content))
        return [cell.strip() for row in reader for cell in row if cell.strip()]


class FileParserFactory:
    """Return the appropriate FileParser for a given file extension."""

    _registry: dict[str, type[FileParser]] = {
        ".txt": TxtFileParser,
        ".csv": CsvFileParser,
    }

    @classmethod
    def create(cls, extension: str) -> FileParser:
        parser_cls = cls._registry.get(extension.lower())
        if parser_cls is None:
            supported = ", ".join(cls._registry)
            raise ValueError(f"Unsupported file type '{extension}'. Supported: {supported}")
        return parser_cls()

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return list(cls._registry)
