import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    """Safely extracts and returns text from a saved PDF file using advanced layout detection."""
    try:
        extracted_text = ""
        # pdfplumber automatically handles visual kerning and ghost spaces
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # extract_text() in pdfplumber is much smarter about word boundaries
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
                    
        return extracted_text.strip()
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {e}")
        return ""