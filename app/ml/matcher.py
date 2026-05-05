import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TECH_SKILLS = ["python","java","javascript","typescript","sql","postgresql","mysql","fastapi",
    "flask","django","react","node","aws","docker","kubernetes","git","rest api",
    "sqlalchemy","machine learning","deep learning","nlp","pandas","numpy","scikit-learn","tensorflow","pytorch"]

def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    matched_skills = []

    for skill in TECH_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text_lower):
            matched_skills.append(skill)

    return matched_skills

def calculate_matchScore(resume_text: str, job_description: str) -> dict:

    if not resume_text.strip() or not job_description.strip():
        return {
            "score": 0.0,
            "matched skills": [],
            "missing skills": []
        }

    documents = [resume_text, job_description]

    vector = TfidfVectorizer(stop_words="english")

    try:
        tfidf_matrix = vector.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        similarity = 0.0

    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))

    matched_skills = sorted(resume_skills.intersection(job_skills))
    missing_skills = sorted(job_skills.difference(resume_skills))

    score = float(round(similarity * 100, 2))

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }