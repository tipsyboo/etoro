import json
from typing import Protocol, List
from pathlib import Path
from models import Book

class DataFormatter(Protocol):
    """
    Interface for output formatters.
    Any class implementing this protocol must provide a format_and_save method.
    """
    def format_and_save(self, data: List[Book], output_path: str | Path) -> None:
        ...

class JSONFormatter:
    """
    Formatter that writes a list of Book models to a JSON file.
    """
    def format_and_save(self, data: List[Book], output_path: str | Path) -> None:
        # Convert Pydantic models to dictionaries
        dict_data = [book.model_dump() for book in data]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dict_data, f, indent=4, ensure_ascii=False)
