from typing import List
from models import Book

def filter_by_title_keyword(books: List[Book], keyword: str) -> List[Book]:
    """
    Returns a list of books where the title contains the given keyword (case-insensitive).
    """
    keyword_lower = keyword.lower()
    return [book for book in books if keyword_lower in book.title.lower()]

def filter_by_min_publication_year(books: List[Book], min_year: int) -> List[Book]:
    """
    Returns a list of books published in or after the given year.
    """
    return [
        book for book in books 
        if book.first_publish_year is not None and book.first_publish_year >= min_year
    ]

def filter_books(books: List[Book], title_keyword: str | None = None, min_year: int | None = None) -> List[Book]:
    """
    Applies multiple filters to a list of books.
    
    Args:
        books: The list of Book models to filter.
        title_keyword: Optional keyword to search for in the title.
        min_year: Optional minimum publication year (inclusive).
        
    Returns:
        List[Book]: The filtered list.
    """
    filtered_books = books
    
    if title_keyword is not None:
        filtered_books = filter_by_title_keyword(filtered_books, title_keyword)
        
    if min_year is not None:
        filtered_books = filter_by_min_publication_year(filtered_books, min_year)
        
    return filtered_books
