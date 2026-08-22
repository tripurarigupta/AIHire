import docx

def extract_text_from_docx(file_path: str) -> str:
    """Safely extracts and returns text from a saved DOCX file."""
    try:
        doc = docx.Document(file_path)
        extracted_text = ""
        
        # Word documents are split into paragraphs
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                extracted_text += text + "\n"
                
        return extracted_text.strip()
    except Exception as e:
        print(f"Error parsing DOCX {file_path}: {e}")
        return ""