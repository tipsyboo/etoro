import requests
from requests.exceptions import RequestException
from pydantic import ValidationError
from models import BookSearchResponse

class OpenLibraryClient:
    """Client for interacting with the Open Library API."""
    
    BASE_URL = "https://openlibrary.org"
    DEFAULT_TIMEOUT = 10

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout

    def search_books(self, query: str) -> BookSearchResponse:
        """
        Search for books using the Open Library API.
        
        Args:
            query: The search term (e.g., "python").
            
        Returns:
            BookSearchResponse: Validated Pydantic model containing the results.
            
        Raises:
            RuntimeError: If the API request fails, returns invalid data, or violates the schema.
        """
        url = f"{self.BASE_URL}/search.json"
        params = {"q": query}
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            data = response.json()
            return BookSearchResponse(**data)
            
        except RequestException as e:
            # Catch all network related errors
            raise RuntimeError(f"Failed to fetch data from Open Library API: {e}") from e
        except ValueError as e:
            # Catch JSON decoding errors
            raise RuntimeError(f"Failed to parse JSON response from API: {e}") from e
        except ValidationError as e:
            # Catch Pydantic schema validation errors
            raise RuntimeError(f"Data received from API does not match expected schema: {e}") from e
