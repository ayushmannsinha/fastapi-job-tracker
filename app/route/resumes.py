from fastapi import APIRouter, Depends, HTTPException, status
from pip._internal.cli import status_codes
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.route.auth import get_current_user
from typing import Optional

router = APIRouter(
    prefix = "/resumes",
    tags = ["resumes"]
)

@router.post("/", response_model = schemas.ResumeResponse)
## what this does is it checks access the DB and gets current user and then creates a new resume for that user
def create_resume(resume: schemas.ResumeCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    db_resume = models.Resume(
        user_id = current_user.id,
        resume_text = resume.resume_text,
        resume_version = resume.resume_version
    )

    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    return db_resume

@router.get("/", response_model = list[schemas.ResumeResponse])
## what this does is it checks access the DB and gets current user and then returns all the resume for that user only
def get_resumes(db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    resumes = db.query(models.Resume).filter(models.Resume.user_id == current_user.id).all()
    return resumes

@router.patch("/{resume_id}", response_model=schemas.ResumeResponse)
def edit_resume(resume_update: schemas.ResumeUpdate, resume_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):

    resume = db.query(models.Resume).filter(models.Resume.id == resume_id,
                                            models.Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")

    application = db.query(models.Application).filter(models.Application.resume_id == resume_id,
                                                      models.Application.user_id == current_user.id).first()
    if application is not None:
        raise HTTPException(status_code=409, detail="Cannot edit a resume attached to an application.")

    update_data = resume_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update.")

    for field, value in update_data.items():
        setattr(resume, field, value)

    db.commit()
    db.refresh(resume)

    return resume

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, db:Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    resume = db.query(models.Resume).filter(models.Resume.id == resume_id,
                                            models.Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")

    application = db.query(models.Application).filter(models.Application.resume_id == resume_id,
                                                      models.Application.user_id == current_user.id).first()
    if application is not None:
        raise HTTPException(status_code=409, detail="Cannot delete a resume attached to an application.")

    db.delete(resume)
    db.commit()

    return None