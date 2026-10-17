import io

import pdfplumber


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Safely extracts and returns text from PDF bytes using advanced layout detection.

    Takes the bytes rather than a path: the API is deployed on a host with a
    read-only filesystem, so an upload is never written to disk first.
    """
    try:
        extracted_text = ""
        # pdfplumber automatically handles visual kerning and ghost spaces
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                # extract_text() in pdfplumber is much smarter about word boundaries
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
                    
        return extracted_text.strip()
    except Exception as e:
        print(f"Error parsing PDF upload: {e}")
        return ""