import spacy
from spacy.matcher import PhraseMatcher
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.general_params import SKILL_DB

# 1. Initialize globally so it only loads ONCE when FastAPI starts
print("Loading NLP models for Skill Extractor... (This takes a few seconds)")
nlp = spacy.load("en_core_web_sm")
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
print("NLP models loaded successfully!")

def extract_skills_from_text(text: str) -> str:
    """
    Extracts skills from text and returns a comma-separated string 
    (e.g., "python, react, postgresql") to save directly to the database.
    """
    if not text:
        return ""

    try:
        annotations = skill_extractor.annotate(text)
        extracted = set()
        
        # Exact matches
        for match in annotations.get("results", {}).get("full_matches", []):
            if name := match.get("doc_node_value"):
                if len(name) > 1:
                    extracted.add(name.lower())
                    
        # Fuzzy matches
        for match in annotations.get("results", {}).get("ngram_scored", []):
            if name := match.get("doc_node_value"):
                if len(name) > 1:
                    extracted.add(name.lower())
                    
        # Return as a comma-separated string for our Text column
        return ", ".join(sorted(list(extracted)))
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return ""