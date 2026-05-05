from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)

@router.post("/", response_model=schemas.JobResponse)
def create_job(job:schemas.JobCreate, db: Session = Depends(get_db)):
    db_job = models.Job(**job.model_dump())

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return db_job

@router.get("/", response_model=list[schemas.JobResponse])
def get_Jobs(db:Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return jobs
