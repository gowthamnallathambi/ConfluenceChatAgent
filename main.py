from dotenv import load_dotenv
load_dotenv()

from app.ingest import ingest_all

if __name__ == "__main__":
    """
    Main entry point for the ingestion script.

    - Loads environment variables.
    - Calls the ingest_all() function to fetch, parse, and embed Confluence content.
    - Saves the resulting vector store locally.
    """
    ingest_all()
    print("Ingestion completed and vector store saved.")
