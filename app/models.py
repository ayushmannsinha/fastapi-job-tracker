from sqlalchemy import Column, Identity, Integer, String, ForeignKey, Text, Date, Float, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="user")
    applications = relationship("Application", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_description = Column(String, nullable=False)
    location = Column(String)
    salary = Column(Integer)
    date_posted = Column(Date)

    applications = relationship("Application", back_populates="job")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_text = Column(Text, nullable=False)
    resume_version = Column(String, nullable=False)

    user = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    status = Column(Integer, nullable=False)
    applied_date = Column(Date)
    followup_date = Column(Date)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    match_scores = relationship("MatchScore", back_populates="application",
                                uselist=False, cascade="all, delete-orphan")

class MatchScore(Base):
    __tablename__ = "match_scores"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="Cascade"),
        nullable=False,
        unique=True)
    score = Column(Float, nullable=False)
    matched_skills = Column(Text, default="[]")
    missing_skills = Column(Text, default="[]")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    application = relationship("Application", back_populates="match_scores")
