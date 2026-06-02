from langchain_core.tools import tool
from core.logging import logger
import os
import tempfile
import urllib.request


@tool
def read_pdf(source: str, max_pages: int = 10) -> str:
    """
    Read and extract text content from a PDF file.
    Source can be a local file path or a URL to a PDF.

    Args:
        source: File path or URL pointing to a PDF document
        max_pages: Maximum number of pages to read (default 10)

    Returns:
        Extracted text content from the PDF
    """
    try:
        import fitz

        pdf_path = source
        temp_file = None

        if source.startswith("http://") or source.startswith("https://"):
            temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            logger.info(f"Downloading PDF from {source}")
            urllib.request.urlretrieve(source, temp_file.name)
            pdf_path = temp_file.name

        if not os.path.exists(pdf_path):
            return f"PDF not found at path: {pdf_path}"

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_to_read = min(max_pages, total_pages)

        text_parts = [f"PDF: {os.path.basename(source)} ({total_pages} pages, reading {pages_to_read})\n"]

        for page_num in range(pages_to_read):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_parts.append(f"\n--- Page {page_num + 1} ---\n{text[:1500]}")

        doc.close()

        if temp_file:
            os.unlink(temp_file.name)

        result = "\n".join(text_parts)
        logger.info(f"PDF read successfully: {pages_to_read} pages from {source}")
        return result

    except Exception as e:
        logger.error(f"PDF reading failed: {e}")
        return f"PDF reading failed: {str(e)}"
