# FastAPI Job Tracker with Resume Match Scoring

A full-stack job application tracking system built with FastAPI, PostgreSQL, SQLAlchemy, JWT authentication, and a React frontend. The project allows users to manage jobs, resumes, applications, application statuses, and generate resume-to-job match scores using a simple TF-IDF and cosine similarity based ML feature.

## Features

- User registration and login with JWT-based authentication
- Protected backend routes using the currently authenticated user
- Create and manage job postings
- Create and manage resume versions
- Create job applications by linking a job with a resume
- View application dashboard and application details
- Update application status such as Applied, OA, Interview, Offer, or Rejected
- Generate and save resume-job match scores
- View matched and missing skills for each application
- Seed script for creating clean local demo data
## Tech Stack

**Backend:** FastAPI, Python, SQLAlchemy, Pydantic  
**Database:** PostgreSQL  
**Authentication:** JWT, OAuth2 Password Flow, pwdlib  
**ML / Scoring:** scikit-learn, TF-IDF, cosine similarity, regex-based skill extraction  
**Frontend:** React, Vite, JavaScript, CSS  
**Tools:** Git, GitHub, Swagger UI, Postman  

## Project Structure
```text
app/
  database.py          # Database connection and SQLAlchemy session setup
  main.py              # FastAPI application entry point
  models.py            # SQLAlchemy database models
  seed.py              # Local demo data seed script

  route/
    auth.py            # Login, JWT token, and password authentication logic
    users.py           # User registration and user-related routes
    jobs.py            # Job posting routes
    resumes.py         # Resume routes
    applications.py    # Application tracking routes
    match_scores.py    # Resume-job match scoring routes

  ml/
    matcher.py         # TF-IDF, cosine similarity, and skill extraction logic

job-tracker-frontend/
  src/
    App.jsx            # Main React UI and page logic
    api.js             # Frontend API helper and JWT token handling
    styles.css         # Frontend styling 
```

## Backend Setup
Create and activate a Python virtual environment.
```powershell
python -m venv .venv
.venv\Scripts\activate
```
```
powershell
pip install -r requirements.txt
```
```
env
DATABASE_URL=your_postgresql_database_url
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
```
powershell
uvicorn app.main:app --reload
```
```
text
http://127.0.0.1:8000
```
```
text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Go to the frontend folder.

```powershell
cd job-tracker-frontend
```

Install frontend dependencies.

```powershell
npm.cmd install
```

Run the React frontend.

```powershell
npm.cmd run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

## Seed Demo Data

## Seed Demo Data

The project includes a local seed script for creating clean demo data.

To run the seed script:

```powershell
python -m app.seed
```

The seed script creates:

- One demo user
- Sample job postings
- Sample resume versions
- Sample job applications

It does not create match scores by default. Match scores are generated from the frontend by opening an application and clicking **Generate / Save Match Score**.

Demo login:

```text
Email: john@example.com
Password: password123
```

To reset the local database before seeding, temporarily set this in `app/seed.py`:

```python
RESET_DATABASE = True
```

Run the seed script once, then change it back to:

```python
RESET_DATABASE = False
```
## API Overview

The backend exposes REST APIs for authentication, users, jobs, resumes, applications, and match scores.

### Authentication

```text
POST /auth/token
```

Used to log in and receive a JWT access token.

### Users

```text
POST /users/
```

Used to register a new user.

### Jobs

```text
GET  /jobs/
POST /jobs/
```

Used to list and create job postings.

### Resumes

```text
GET  /resumes/
POST /resumes/
```

Used to list and create resume versions for the authenticated user.

### Applications

```text
GET  /applications/
POST /applications/
GET  /applications/summary
GET  /applications/{application_id}/details
PUT  /applications/{application_id}/status
```

Used to create applications, view application summaries/details, and update application status.

### Match Scores

```text
POST /match_scores/preview
POST /match_scores/applications/{application_id}
GET  /match_scores/applications/{application_id}
```

Used to preview, generate, save, and retrieve resume-job match scores.

## Match Scoring Logic

The project includes a simple resume-to-job match scoring feature.

The scoring pipeline uses:

- TF-IDF vectorization to convert resume text and job descriptions into numerical vectors
- Cosine similarity to calculate how closely the resume matches the job description
- Regex-based skill extraction to identify matched and missing skills

The match score is not created automatically when an application is created. Users generate it manually from the application details page by clicking **Generate / Save Match Score**.

This keeps the application flow realistic because match scoring is treated as an optional analysis step, not mandatory application data.

## Live Demo

Frontend: https://job-tracker-production-9b92.up.railway.app  
Backend API Docs: https://fastapi-job-tracker-production.up.railway.app/docs

## Current Status

The project currently supports the full local workflow:

- User registration and login
- Creating jobs and resumes
- Creating applications
- Viewing application dashboard and details
- Updating application status
- Generating and saving match scores
- Seeding clean demo data for testing

## Future Improvements

- Add delete APIs for applications and resumes
- Block resume deletion when it is already linked to applications
- Improve frontend routing with React Router
- Add better form validation and loading states
- Add deployment-ready configuration for backend, frontend, and database
- Improve match scoring with better skill extraction and semantic embeddings

## Author

Ayushmann Sinha
