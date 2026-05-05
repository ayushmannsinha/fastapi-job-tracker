from fastapi import FastAPI
from app.database import Base, engine
from app.route import jobs, users, resumes, applications, auth, match_scores
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Smart Job Application Tracker API")

app.include_router(jobs.router)
app.include_router(users.router)
app.include_router(resumes.router)
app.include_router(applications.router)
app.include_router(auth.router)
app.include_router(match_scores.router)
@app.get("/")
async def root():
    return {"App is running"}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)