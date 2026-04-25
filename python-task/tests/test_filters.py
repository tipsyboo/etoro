import pytest
from models import Book
from filters import filter_books

@pytest.fixture
def dummy_books():
    """
    Provides a standard set of dummy books for all tests to share.
    Includes edge cases like missing years, mixed-case titles, and old publications.
    """
    return [
        Book(title="Learn Python", key="1", first_publish_year=2015),
        Book(title="advanced PROGRAMMING", key="2", first_publish_year=2018),
        Book(title="Python Programming Basics", key="3", first_publish_year=2020),
        Book(title="Old programming guide", key="4", first_publish_year=1995),
        Book(title="Unknown Year Book", key="5"), # No year
    ]

def test_filter_books_by_title(dummy_books):
    """
    Tests that title filtering works and proves case-insensitivity.
    """
    results = filter_books(dummy_books, title_keyword="programming")

    assert len(results) == 3
    titles = [b.title for b in results]
    assert "advanced PROGRAMMING" in titles
    assert "Python Programming Basics" in titles
    assert "Old programming guide" in titles

def test_filter_books_by_min_year(dummy_books):
    """
    Tests that year filtering works and gracefully skips books with None as the year.
    """
    results = filter_books(dummy_books, min_year=2000)

    assert len(results) == 3
    titles = [b.title for b in results]
    assert "Learn Python" in titles
    assert "advanced PROGRAMMING" in titles
    assert "Python Programming Basics" in titles
    # Negatives
    assert "Old programming guide" not in titles
    assert "Unknown Year Book" not in titles

def test_filter_books_combined(dummy_books):
    """
    Tests that the pipeline correctly chains multiple filters together.
    """
    results = filter_books(dummy_books, title_keyword="programming", min_year=2000)

    assert len(results) == 2
    titles = [b.title for b in results]
    assert "advanced PROGRAMMING" in titles
    assert "Python Programming Basics" in titles

def test_filter_books_no_matches(dummy_books):
    """
    Tests that overly strict filters safely return an empty list.
    """
    results = filter_books(dummy_books, title_keyword="Ruby", min_year=2025)
    
    assert len(results) == 0
    assert isinstance(results, list)
