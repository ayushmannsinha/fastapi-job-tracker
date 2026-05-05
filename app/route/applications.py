import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas
from app.route.auth import get_current_user

router = APIRouter(
    prefix = "/applications",
    tags = ["applications"]
)

@router.post("/", response_model = schemas.ApplicationResponse)
## Gets Application Create Schema, starts a session with the DB and brings info of the current user logged in.
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db),
                       current_user = Depends(get_current_user)):

    ## fetch the job which from db matches the job_id in application
    db_job = db.query(models.Job).filter(models.Job.id == application.job_id).first()

    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    ## fetch the resume which from db matches the job_id in application
    db_resume = db.query(models.Resume).filter(models.Resume.id == application.resume_id).first()

    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    if db_resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot use someone else's resume")

    db_application = models.Application(
        user_id = current_user.id,
        job_id = application.job_id,
        resume_id = application.resume_id,
        status = application.status.value,
        applied_date = application.applied_date,
        followup_date = application.followup_date
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application

@router.get("/", response_model = list[schemas.ApplicationResponse])
def get_applications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    applications = db.query(models.Application).filter(models.Application.user_id == current_user.id).all()
    return applications

@router.get("/summary", response_model=list[schemas.ApplicationSummaryResponse])
def get_application_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    applications = db.query(models.Application).options(joinedload(models.Application.job),
                                                       joinedload(models.Application.resume),
                                                       joinedload(models.Application.match_scores)).filter(models.Application.user_id == current_user.id).all()

    result = []

    for application in applications:
        result.append({
            "id": application.id,
            "status": application.status,
            "company_name": application.job.company_name,
            "job_title": application.job.job_title,
            "resume_version": application.resume.resume_version,
            "match_score": application.match_scores.score if application.match_scores else None
        })
    return result

@router.get("/{application_id}", response_model=schemas.ApplicationResponse)
def get_application_byId(application_id: int, db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    application = db.query(models.Application).filter(models.Application.id == application_id,
                                                      models.Application.user_id == current_user.id).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found.")

    return application

@router.get("/{application_id}/details", response_model=schemas.ApplicationDetailResponse)
def get_application_details(application_id: int, db:Session = Depends(get_db), current_user = Depends(get_current_user)):

    application = db.query(models.Application).filter(models.Application.id == application_id,
                                                      models.Application.user_id == current_user.id).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found.")

    job = db.query(models.Job).filter(models.Job.id == application.job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    resume = db.query(models.Resume).filter(models.Resume.id == application.resume_id).first()

    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")

    match_score = db.query(models.MatchScore).filter(models.MatchScore.application_id == application.id).first()

    if match_score:
        score = match_score.score
        matched_skills = json.loads(match_score.matched_skills)
        missing_skills = json.loads(match_score.missing_skills)
    else:
        score = None
        matched_skills = []
        missing_skills = []

    return {
        "id":application.id,
        "status":application.status,
        "applied_date":application.applied_date,
        "followup_date":application.followup_date,

        "job_id":application.job_id,
        "company_name":job.company_name,
        "job_title":job.job_title,
        "location":job.location,
        "salary":job.salary,

        "resume_id":application.resume_id,
        "resume_version":resume.resume_version,

        "match_score":score,
        "matched_skills":matched_skills,
        "missing_skills":missing_skills
    }

@router.put("/{application_id}", response_model = schemas.ApplicationResponse)
def update_application(application_id: int, application_update: schemas.ApplicationUpdate,
                       db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    db_application = (db.query(models.Application)
                      .filter(models.Application.id == application_id, models.Application.user_id == current_user.id)
                      .first())

    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    db_application.status = application_update.status.value
    db_application.followup_date = application_update.followup_date

    db.commit()
    db.refresh(db_application)

    return db_application