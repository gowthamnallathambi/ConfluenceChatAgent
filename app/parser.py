from bs4 import BeautifulSoup
import textract
import tempfile
import os
import textract.exceptions


def clean_html(html):
    """
    Cleans raw HTML content by removing scripts, styles, and non-visible tags.

    Args:
        html (str): The raw HTML string to be cleaned.

    Returns:
        str: Cleaned plain text extracted from the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Remove non-content tags
    for tag in soup(["script", "style", "head", "title"]):
        tag.decompose()
    # Extract visible text, strip empty lines, and preserve spacing
    return '\n'.join(line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip())

def extract_text_from_file(filename, content_bytes):
    """
    Extracts plain text content from binary file data using `textract`.

    Args:
        filename (str): Name of the file, used to determine the extension/type.
        content_bytes (bytes): The raw byte content of the file.

    Returns:
        str: Extracted plain text, or a fallback error message if parsing fails.
    """
    # Determine file suffix/extension; default to ".bin" if unknow
    suffix = os.path.splitext(filename)[-1] or ".bin"

    # Save file temporarily for parsing
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content_bytes)
        tmp.flush()
        try:
            # Attempt to extract text using textract
            text = textract.process(tmp.name).decode("utf-8")
            return text
        except textract.exceptions.MissingFileError:
            # File was not found or accessible during parsing
            return f"[File not found while parsing: {filename}]"
        except Exception as e:
            # General error during parsing
            return f"[Error parsing {filename}: {str(e)}]"
        finally:
            # Ensure the temporary file is removed
            os.unlink(tmp.name)