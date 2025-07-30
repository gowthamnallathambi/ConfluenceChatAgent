from app.parser import clean_html, extract_text_from_file
from app.vectorstore import build_vectorstore_from_docs, save_vectorstore
from atlassian import Confluence
import os

def ingest_all():
    """
    Ingests all Confluence pages and their attachments across all spaces,
    cleans and parses the content, and builds a vector store for RAG-based querying.

    Steps:
    -------
    1. Authenticate with the Confluence API using credentials from environment variables.
    2. Retrieve all spaces from the Confluence instance.
    3. For each space:
        a. Retrieve all pages and clean the HTML content.
        b. Retrieve and parse all file attachments for each page.
    4. Build and save the vector store using the combined page and attachment content.
    """
    # Initialize Confluence client using environment credentials
    confluence = Confluence(
        url=os.getenv("CONFLUENCE_BASE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        password=os.getenv("CONFLUENCE_API_TOKEN")
    )

    docs = []
    metadata = []

    # 1. Get all spaces
    all_spaces = confluence.get_all_spaces(start=0, limit=500)
    print(f"Found {len(all_spaces['results'])} spaces.")

    for space in all_spaces['results']:
        space_key = space['key']
        space_name = space['name']
        print(f"Processing space: {space_key} ({space_name})")

        # 2. Get all pages in the space
        start = 0
        limit = 1000
        while True:
            pages = confluence.get_all_pages_from_space(space=space_key, start=start, limit=limit, expand='body.storage')
            if not pages:
                break

            for page in pages:
                page_id = page['id']
                page_title = page['title']
                html = page['body']['storage']['value']
                clean_text = clean_html(html)

                docs.append(clean_text)
                metadata.append({
                    "source": page_title,
                    "type": "page",
                    "space": space_key,
                    "page_id": page_id,
                    "link": f"{os.getenv('CONFLUENCE_BASE_URL')}/pages/viewpage.action?pageId={page_id}"
                })

                # 3. Get attachments for each page
                attachments = confluence.get_attachments_from_content(page_id, expand="body")
                for att in attachments.get('results', []):
                    file_name = att['title']
                    download_link = att['_links']['download']
                    file_data = confluence.get(download_link, not_json_response=True)

                    parsed_text = extract_text_from_file(file_name, file_data)
                    docs.append(parsed_text)
                    metadata.append({
                        "source": file_name,
                        "type": "attachment",
                        "space": space_key,
                        "page_id": page_id,
                        "link": f"{os.getenv('CONFLUENCE_BASE_URL')}/pages/viewpage.action?pageId={page_id}"
                    })

            start += limit

    # 4. Build and persist vector store
    print(f"Ingested {len(docs)} documents.")
    vectorstore = build_vectorstore_from_docs(docs, metadata)
    save_vectorstore(vectorstore)
