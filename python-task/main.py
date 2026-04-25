from client import OpenLibraryClient
from filters import filter_books
from formatters import JSONFormatter

def main():
    print("Initializing client...")
    client = OpenLibraryClient()
    
    print("Searching for books about 'python'...")
    try:
        response = client.search_books("python")
        print(f"Success! Found {response.numFound} books on Open Library.")
        
        # Apply our business logic filters
        # Look for "programming" in the title and published in or after 2000
        filtered_results = filter_books(
            books=response.docs,
            title_keyword="programming",
            min_year=2000
        )
        print(f"After filtering by title keyword 'programming' and min_year >= 2000, {len(filtered_results)} books remain.")
        
        if filtered_results:
            output_file = "filtered_books.json"
            print(f"Writing results to {output_file}...")
            
            # Using the Formatter interface
            formatter = JSONFormatter()
            formatter.format_and_save(filtered_results, output_file)
            
            print("Done!")
        else:
            print("No books matched the filter criteria.")
            
    except RuntimeError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
