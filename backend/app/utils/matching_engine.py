def calculate_keyword_match(resume_skills_str: str, job_skills_str: str) -> float:
    """
    Calculates a baseline ATS keyword match percentage.
    """
    if not job_skills_str:
        return 0.0
        
    if not resume_skills_str:
        return 0.0

    # Convert comma-separated strings back into sets
    # e.g., "python, react, sql" -> {"python", "react", "sql"}
    resume_skills = {skill.strip().lower() for skill in resume_skills_str.split(",")}
    job_skills = {skill.strip().lower() for skill in job_skills_str.split(",")}

    # Find the overlapping skills
    matched_skills = resume_skills.intersection(job_skills)
    
    # Calculate the percentage
    match_score = (len(matched_skills) / len(job_skills)) * 100
    
    return round(match_score, 2)