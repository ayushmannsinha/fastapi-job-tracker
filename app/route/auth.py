from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.models import User
from app.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from datetime import timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def authenticate_user(email: str, password: str, db: Session):
    db_user = db.query(models.User).filter(models.User.email == email).first()

    if db_user is None:
        return None

    if not verify_password(password, db_user.password_hash):
        return None

    return db_user

@router.post("/login", response_model = schemas.AccessToken)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(
        email = user_credentials.email,
        password = user_credentials.password,
        db = db
    )

    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    if not verify_password(user_credentials.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid mail or Password")

    access_token_expire = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    ## creating access token in the below section
    access_token = create_access_token(
        data = {"sub": str(db_user.id)},
        expires_delta = access_token_expire
    )

    return {'access_token': access_token,
            'token_type': 'bearer'
    }

@router.post("/token", response_model = schemas.AccessToken)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = authenticate_user(
        email = form_data.username,
        password = form_data.password,
        db = db
    )

    if db_user is None:
        raise HTTPException(status_code=401, detail = "User not found")

    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    ## creating access token in the below section
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expire
    )

    return {'access_token': access_token,
            'token_type': 'bearer'
    }

## Section used to validate user token using JWT

def get_current_user( token:str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials",
                                           headers={"WWW-Authenticate":"Bearer"},)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id = int(user_id))
    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception

    db_user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if db_user is None:
        raise credentials_exception

    return db_user

@router.get("/me", response_model = schemas.UserResponse)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user