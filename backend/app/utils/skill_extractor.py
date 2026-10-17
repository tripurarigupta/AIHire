import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skillNer.skill_extractor_class import SkillExtractor

# The skill extractor is built on first use rather than at import, and kept for
# the life of the process.
#
# Why it matters: importing skillNer pulls in nltk, which pulls in scipy, and
# that chain costs roughly 15 seconds of module import time on its own. This
# module used to do it at import, so a serverless cold start paid it before the
# API could answer *any* request - including ones that never touch a resume, like
# listing jobs. Deferring it keeps cold starts short and pushes the cost onto the
# request that genuinely needs the model (resume upload, job posting).
_skill_extractor = None
_extractor_lock = threading.Lock()


def _get_skill_extractor() -> "SkillExtractor":
    """Builds the skill extractor once, on first use."""
    global _skill_extractor

    if _skill_extractor is None:
        with _extractor_lock:
            # Re-check under the lock: two requests can reach a cold instance at
            # the same time and both find the extractor missing.
            if _skill_extractor is None:
                # Imported here, not at module scope, so the nltk/scipy chain is
                # only paid by the requests that extract skills.
                import spacy
                from spacy.matcher import PhraseMatcher
                from skillNer.general_params import SKILL_DB
                from skillNer.skill_extractor_class import SkillExtractor

                print("Loading NLP models for Skill Extractor... (This takes a few seconds)")
                nlp = spacy.load("en_core_web_sm")
                _skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
                print("NLP models loaded successfully!")

    return _skill_extractor


def extract_skills_from_text(text: str) -> str:
    """
    Extracts skills from text and returns a comma-separated string 
    (e.g., "python, react, postgresql") to save directly to the database.
    """
    if not text:
        return ""

    try:
        annotations = _get_skill_extractor().annotate(text)
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