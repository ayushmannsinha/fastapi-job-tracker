from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.security import hash_password
from app import models, schemas

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse)
def create_user(user:schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = hash_password(user.password)

    db_user = models.User(
        name = user.name,
        email = user.email,
        password_hash = hashed_password
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

@router.get("/", response_model=list[schemas.UserResponse])
def get_users(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users