from client import OpenLibraryClient

def main():
    print("Initializing client...")
    client = OpenLibraryClient()
    
    print("Searching for books about 'python'...")
    try:
        response = client.search_books("python")
        print(f"Success! Found {response.numFound} books.")
        
        if response.docs:
            first_book = response.docs[0]
            print("\nFirst book details:")
            print(f"Title: {first_book.title}")
            print(f"Authors: {', '.join(first_book.author_name)}")
            print(f"Year: {first_book.first_publish_year}")
            print(f"Key: {first_book.key}")
        else:
            print("No books found in the response docs.")
            
    except RuntimeError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
