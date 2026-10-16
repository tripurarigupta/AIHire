import re

# Heuristic ATS-style analyzer for resumes. Produces a 0-100 score plus
# actionable improvement suggestions and detected strengths.

_CONTACT_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_CONTACT_PHONE = re.compile(
    r"(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}"
)
_QUANTIFIED = re.compile(
    r"\d+\s?(?:%|percent|million|billion|users|customers|revenue|projects|"
    r"clients|team|employees|requests|files|hours|days|weeks|years|increase|"
    r"improvement|downtime|uptime|bugs|issues|tests|locations|countries|campaigns)"
)
_RAW_NUMBERS = re.compile(r"\d+")
_ACTION_VERBS = re.compile(
    r"\b(?:built|designed|developed|launched|led|managed|delivered|created|"
    r"improved|implemented|spearheaded|automated|optimized|scaled|achieved|"
    r"reduced|increased|migrated|architected|engineered|coordinated|drove)\b",
    re.IGNORECASE,
)

_SECTION_PATTERNS = {
    "skills": re.compile(
        r"^\s*(?:technical\s+)?(?:skills|technologies|tech[\s-]*stack|expertise|"
        r"proficien\w+|tools?|languages)\s*(?:[:]|$)",
        re.MULTILINE | re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^\s*(?:professional\s+|work\s+)?(?:experience|employment\s+histor\w*|"
        r"background|work\s+history|internships?|projects?)\s*(?:[:]|$)",
        re.MULTILINE | re.IGNORECASE,
    ),
    "education": re.compile(
        r"^\s*(?:education|academic\s+background|qualifications?|degree|"
        r"university|college|school)\s*(?:[:]|$)",
        re.MULTILINE | re.IGNORECASE,
    ),
    "summary": re.compile(
        r"^\s*(?:professional\s+)?(?:summary|profile|objective|certifications?|"
        r"achievements?|awards?|additional\s+information)\s*(?:[:]|$)",
        re.MULTILINE | re.IGNORECASE,
    ),
}


def _count_sections(text: str) -> dict[str, bool]:
    found = {key: bool(pattern.search(text)) for key, pattern in _SECTION_PATTERNS.items()}
    return found


def analyze_resume(text: str, skills: str | None = None):
    """Analyze parsed resume text and return ATS score + suggestions + strengths."""
    text = text or ""
    skills = skills or ""
    word_count = len(re.findall(r"\S+", text))
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    sections = _count_sections(text)

    has_email = bool(_CONTACT_EMAIL.search(text))
    has_phone = bool(_CONTACT_PHONE.search(text))
    has_contact = has_email or has_phone
    has_quantified = bool(_QUANTIFIED.search(text))
    raw_number_count = len(_RAW_NUMBERS.findall(text))
    verbs_hit = len(set(_ACTION_VERBS.findall(text.lower())))

    score = 0.0
    score += 12 if has_contact else 0
    score += 12 if sections["skills"] or len(skill_list) >= 3 else 0
    score += 12 if sections["experience"] else 0
    score += 10 if sections["education"] else 0
    score += min(14, len(skill_list) * 2)  # up to 7 skills
    score += 15 if word_count >= 60 else (10 if word_count >= 30 else (5 if word_count >= 10 else 0))
    score += 15 if has_quantified else (8 if raw_number_count >= 3 else 0)
    score += 10 if verbs_hit >= 3 else (5 if verbs_hit >= 1 else 0)

    score = round(min(100, max(0, score)), 2)

    suggestions: list[str] = []
    strengths: list[str] = []

    if not has_contact:
        suggestions.append("Add a professional email and phone number so recruiters can reach you.")
    elif has_email and not has_phone:
        suggestions.append("Add a phone number - many ATS filters look for both email and phone on first pass.")

    if not sections["skills"] and len(skill_list) < 3:
        suggestions.append("Add a dedicated Skills section listing relevant technologies (aim for 5-8 skills).")
    elif len(skill_list) < 5:
        suggestions.append("Add more skills to fill out your Skills section - 5+ strongly improves keyword matches.")

    if not sections["experience"]:
        suggestions.append("Add an Experience or Projects section describing what you have built or shipped.")
    if not sections["education"]:
        suggestions.append("Add an Education section with your degree, certification, or coursework.")

    if not has_quantified and raw_number_count < 3:
        suggestions.append("Quantify achievements with numbers (e.g., % improvement, users served, project scale).")
    elif not has_quantified:
        suggestions.append("Add quantified results to at least 2-3 bullet points (metrics, percentages, scale).")

    if word_count < 30:
        suggestions.append(f"Resume is very short ({word_count} words) - expand it with project and role details.")
    elif word_count < 60:
        suggestions.append("Add more detail to reach 150+ words; concise resumes tend to score lower on ATS parsing.")

    if verbs_hit == 0:
        suggestions.append("Use action verbs (built, led, improved, delivered, automated) to describe achievements.")

    if has_contact:
        strengths.append("Contact information is detectable.")
    if sections["skills"] or len(skill_list) >= 3:
        strengths.append("Skills section detected for keyword matching.")
    if sections["experience"]:
        strengths.append("Professional experience section present.")
    if sections["education"]:
        strengths.append("Education section present.")
    if has_quantified:
        strengths.append("Quantified, measurable achievements detected.")
    if verbs_hit >= 3:
        strengths.append("Strong use of action verbs.")

    if not suggestions:
        suggestions.append("Your resume is well-structured - keep this format for best ATS results.")

    return {
        "ats_score": score,
        "word_count": word_count,
        "skills_detected": skill_list,
        "suggestions": suggestions,
        "strengths": strengths,
    }
