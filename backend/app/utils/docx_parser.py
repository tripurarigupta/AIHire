import io

import docx


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Safely extracts and returns text from DOCX bytes.

    Takes the bytes rather than a path: the API is deployed on a host with a
    read-only filesystem, so an upload is never written to disk first.
    """
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        extracted_text = ""
        
        # Word documents are split into paragraphs
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                extracted_text += text + "\n"
                
        return extracted_text.strip()
    except Exception as e:
        print(f"Error parsing DOCX upload: {e}")
        return ""