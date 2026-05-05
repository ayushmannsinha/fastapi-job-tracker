import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app import schemas, models
from app.ml.matcher import calculate_matchScore
from app.route.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/match_scores", tags=["match_scores"])

@router.post("/", response_model=schemas.MatchScoreResponse)
def match_scores_preview(match_request: schemas.MatchScoreCreate, db: Session = Depends(get_db),
                         current_user: models.User = Depends(get_current_user)):

    resume = db.query(models.Resume).filter(models.Resume.id == match_request.resume_id).first()

    if resume is None:
        raise HTTPException(status_code = 404, detail = "Resume does not exist.")

    if resume.user_id != current_user.id:
        raise HTTPException(status_code=401, detail = "Enter your own resume ID.")

    ## this will match score to any job in the DB for which the user gives ID
    job = db.query(models.Job).filter(models.Job.id == match_request.job_id).first()

    if job is None:
        raise HTTPException(status_code = 404, detail = "Job does not exist.")

    result = calculate_matchScore(resume_text = resume.resume_text, job_description= job.job_description)

    return result

@router.post("/preview-text", response_model=schemas.MatchScoreResponse)
def preview_match_score_from_raw_text(
    match_request: schemas.MatchScorePreviewRequest,
    current_user: models.User = Depends(get_current_user),
):
    result = calculate_matchScore(
        resume_text=match_request.resume_text,
        job_description=match_request.job_description,
    )

    return result

@router.post("/applications/{application_id}", response_model=schemas.SavedMatchScoreResponse   )
def save_match_score(application_id: int, db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):

    application = db.query(models.Application).filter(models.Application.id == application_id,
                                                      models.Application.user_id == current_user.id).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application does not exist.")

    resume = application.resume
    job = application.job

    if resume is None:
        raise HTTPException(status_code = 404, detail = "Resume does not exist.")

    if job is None:
        raise HTTPException(status_code = 404, detail = "Job does not exist.")


    result = calculate_matchScore(resume_text = resume.resume_text, job_description = job.job_description)

    matched_skills_json = json.dumps(result["matched_skills"])
    missing_skills_json = json.dumps(result["missing_skills"])

    ## Checking if the application_id in the Match_Score table is same as the id of the application which we pulled above
    match_score = (db.query(models.MatchScore).filter(models.MatchScore.application_id == application.id)).first()

    if match_score:
        match_score.score = result["score"]
        match_score.matched_skills = matched_skills_json
        match_score.missing_skills = missing_skills_json
        match_score.updated_at = datetime.utcnow()
    else:
        match_score = models.MatchScore(
            application_id = application.id,
            score = result["score"],
            matched_skills = matched_skills_json,
            missing_skills = missing_skills_json
        )

        db.add(match_score)

    db.commit()
    db.refresh(match_score)

    return {
        "id":match_score.id,
        "application_id":match_score.application_id,
        "score": match_score.score,
        "matched_skills": json.loads(match_score.matched_skills),
        "missing_skills": json.loads(match_score.missing_skills),
        "created_at": match_score.created_at,
        "updated_at": match_score.updated_at
    }

@router.get("/applications/{application_id}", response_model=schemas.SavedMatchScoreResponse)
def get_match_score(application_id: int, db:Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    application = db.query(models.Application).filter(models.Application.id == application_id,
                                                      models.Application.user_id == current_user.id).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found.")

    match_score = db.query(models.MatchScore).filter(models.MatchScore.application_id == application.id).first()

    if match_score is None:
        raise HTTPException(status_code=404, detail="Match score does not Exist.")

    return {
        "id": match_score.id,
        "application_id": match_score.application_id,
        "score": match_score.score,
        "matched_skills": json.loads(match_score.matched_skills),
        "missing_skills": json.loads(match_score.missing_skills),
        "created_at": match_score.created_at,
        "updated_at": match_score.updated_at
    }
