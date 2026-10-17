from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.candidate_profile_repository import (
    get_candidate_profile_by_user_id,
    get_jobs_with_required_skills,
)

def get_recommendations_for_user(
    db: Session,
    user_id,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    # 1. Fetch profile via repository
    profile = get_candidate_profile_by_user_id(db, user_id)
    if not profile or not profile.skills:
        return []

    # 2. Fetch jobs via repository
    jobs = get_jobs_with_required_skills(db)
    if not jobs:
        return []

    # 3. Vectorize text and calculate cosine similarity
    candidate_text = profile.skills.replace(",", " ")
    job_texts = [job.required_skills.replace(",", " ") for job in jobs]

    # Imported here rather than at module scope: scikit-learn takes several
    # seconds to import, so it stays off the API's startup path and is only paid
    # by requests that actually compute a match.
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    corpus = [candidate_text] + job_texts
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # 4. Map, score, and rank descending
    candidate_skill_set = set(
        s.strip().lower() for s in profile.skills.split(",") if s.strip()
    )
    scored_jobs = []
    for job, score in zip(jobs, similarities):
        match_percentage = round(float(score) * 100, 2)
        if match_percentage > 0:
            required_skills = [
                r.strip() for r in (job.required_skills or "").split(",") if r.strip()
            ]
            missing_skills = [
                r
                for r in required_skills
                if r.lower() not in candidate_skill_set
            ]
            scored_jobs.append({
                "id": str(job.id),
                "title": job.title,
                "description": job.description,
                "location": job.location,
                "job_type": job.job_type,
                "required_skills": job.required_skills,
                "recommendation_score": match_percentage,
                "missing_skills": missing_skills,
            })

    scored_jobs.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return scored_jobs[:top_n]