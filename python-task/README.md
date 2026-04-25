# Small Book Fetcher

A modular Python tool that fetches book data from the Open Library API, filters the results based on business rules, and outputs the data to a JSON file.

## Architecture

This project is built with development best practices, focusing on modularity, error handling, and testability:

- **`models.py`:** Uses Pydantic to validate and parse API responses, creating a strict data boundary.
- **`client.py`:** Encapsulates external HTTP communication with timeouts and explicit error handling.
- **`filters.py`:** Pure business logic functions for filtering data, easily testable in isolation.
- **`formatters.py`:** Defines an output interface (Protocol) ensuring the system is open for extension without modifying core logic.

## Setup

1. Create and activate a virtual environment (Python 3.10+ recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main orchestrator script:

```bash
python main.py
```

This will:

1. Search the Open Library API for books about "python".
2. Filter the results for books with "programming" in the title, published in or after the year 2000.
3. Save the structured data to `filtered_books.json`.

## Testing

The project includes isolated unit tests. Run them using pytest:

```bash
pytest tests/
```
