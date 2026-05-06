from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Sequence, List
from datetime import date, datetime
from enum import Enum

##------------------------ User Classes ------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

##------------------------ Job Classes ------------------------
class JobCreate(BaseModel):
    company_name: str
    job_title: str
    job_description: str
    location: Optional[str] = None
    salary: Optional[int] = None
    date_posted: Optional[date] = None

class JobResponse(JobCreate):
    id: int

    class Config:
        from_attributes = True

##------------------------ Application Classes ------------------------
class ApplicationStatus(str, Enum):
    applied = "Applied"
    oa = "OA"
    interview = "Interview"
    offer = "Offer"
    rejected = "Rejected"

class ApplicationBase(BaseModel):
    job_id: int
    resume_id: int
    status: ApplicationStatus
    applied_date: Optional[date] = None
    followup_date: Optional[date] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ApplicationDetailResponse(ApplicationBase):
    id:int
    status: ApplicationStatus
    applied_date: Optional[date] = None
    followup_date: Optional[date] = None

    job_id: int
    company_name: str
    job_title: str
    location: Optional[str] = None
    salary: Optional[int] = None

    resume_id: int
    resume_version: str

    match_score: Optional[float]
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)

class ApplicationSummaryResponse(BaseModel):
    id: int
    company_name: str
    job_title: str
    status: ApplicationStatus
    resume_version: str
    match_score: Optional[float]

class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
    followup_date: Optional[date] = None

## ------------------------ Resume Classes ------------------------
class ResumeBase(BaseModel):
    resume_text: str
    resume_version: str

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(BaseModel):
    resume_text: Optional[str] = None
    resume_version: Optional[str] = None

class ResumeResponse(ResumeBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

## ------------------------ MatchScore Classes ------------------------
class MatchScoreCreate(BaseModel):
    resume_id: int
    job_id: int

class MatchScorePreviewRequest(BaseModel):
    resume_text: str
    job_description: str

class MatchScoreResponse(BaseModel):
    score: float
    matched_skills: List[str]
    missing_skills: List[str]

class SavedMatchScoreResponse(BaseModel):
    id: int
    score: float
    application_id: int
    matched_skills: List[str]
    missing_skills: List[str]

    class Config:
        from_attributes = True

## ------------------------ Security Classes ------------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AccessToken(BaseModel):
    access_token:str
    token_type: str

class TokenData(BaseModel):
    user_id:int | None = None