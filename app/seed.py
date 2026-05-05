from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Job, Resume, Application, MatchScore
from app.security import hash_password
from app.schemas import ApplicationStatus

RESET_DATABASE = False

DEMO_NAME = "John Doe"
DEMO_EMAIL = "john@example.com"
DEMO_PASSWORD = "password123"

def reset_database(db: Session):
    print("Resetting local database tables...")

    db.execute(
        text(
            """
            TRUNCATE TABLE
                match_scores,
                applications,
                resumes,
                jobs,
                users
            RESTART IDENTITY CASCADE;
            """
        )
    )

    db.commit()
    print("Database reset completed.")


def print_table_counts(db: Session, label: str):
    print(f"\n--- {label} ---")
    print(f"User Count: {db.query(User).count()}")
    print(f"Job Count: {db.query(Job).count()}")
    print(f"Resume Count: {db.query(Resume).count()}")
    print(f"Application Count: {db.query(Application).count()}")
    print(f"MatchScore Count: {db.query(MatchScore).count()}")


def create_demo_user(db: Session):
    print("\nCreating demo user...")

    existing_user = db.query(User).filter(User.email == DEMO_EMAIL).first()

    if existing_user:
        print(f"Demo user already exists with id: {existing_user.id}")
        return existing_user

    demo_user = User(
        name=DEMO_NAME,
        email=DEMO_EMAIL,
        password_hash=hash_password(DEMO_PASSWORD),
    )

    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)

    print(f"Demo user created with id: {demo_user.id}")
    return demo_user


def create_demo_job(
    db: Session,
    company_name: str,
    job_title: str,
    job_description: str,
    location: Optional[str] = None,
    salary: Optional[int] = None,
):
    print(f"\nCreating demo job: {company_name} - {job_title}")

    existing_job = (
        db.query(Job)
        .filter(
            Job.company_name == company_name,
            Job.job_title == job_title,
        )
        .first()
    )

    if existing_job:
        print(f"Demo job already exists with id: {existing_job.id}")
        return existing_job

    demo_job = Job(
        company_name=company_name,
        job_title=job_title,
        job_description=job_description,
        location=location,
        salary=salary,
        date_posted=date.today(),
    )

    db.add(demo_job)
    db.commit()
    db.refresh(demo_job)

    print(f"Demo job created with id: {demo_job.id}")
    return demo_job


def create_demo_resume(
    db: Session,
    demo_user: User,
    resume_version: str,
    resume_text: str,
):
    print(f"\nCreating demo resume: {resume_version}")

    existing_resume = (
        db.query(Resume)
        .filter(
            Resume.user_id == demo_user.id,
            Resume.resume_version == resume_version,
        )
        .first()
    )

    if existing_resume:
        print(f"Demo resume already exists with id: {existing_resume.id}")
        return existing_resume

    demo_resume = Resume(
        user_id=demo_user.id,
        resume_version=resume_version,
        resume_text=resume_text,
    )

    db.add(demo_resume)
    db.commit()
    db.refresh(demo_resume)

    print(f"Demo resume created with id: {demo_resume.id}")
    return demo_resume


def create_demo_application(
    db: Session,
    demo_user: User,
    demo_job: Job,
    demo_resume: Resume,
    status: int,
):
    print(
        f"\nCreating demo application: "
        f"user_id={demo_user.id}, job_id={demo_job.id}, resume_id={demo_resume.id}"
    )

    existing_application = (
        db.query(Application)
        .filter(
            Application.user_id == demo_user.id,
            Application.job_id == demo_job.id,
            Application.resume_id == demo_resume.id,
        )
        .first()
    )

    if existing_application:
        print(f"Demo application already exists with id: {existing_application.id}")
        return existing_application

    demo_application = Application(
        user_id=demo_user.id,
        job_id=demo_job.id,
        resume_id=demo_resume.id,
        status=status,
        applied_date=date.today(),
        followup_date=None,
    )

    db.add(demo_application)
    db.commit()
    db.refresh(demo_application)

    print(f"Demo application created with id: {demo_application.id}")
    return demo_application


def seed_database(db: Session):
    demo_user = create_demo_user(db)

    google_job = create_demo_job(
        db=db,
        company_name="Google",
        job_title="Software Engineering Intern",
        job_description=(
            "We are looking for a Software Engineering Intern with experience in "
            "Python, REST APIs, backend systems, SQL databases, authentication, "
            "machine learning, and scalable software development."
        ),
        location="Mountain View, CA",
        salary=None,
    )

    microsoft_job = create_demo_job(
        db=db,
        company_name="Microsoft",
        job_title="AI/ML Engineering Intern",
        job_description=(
            "Work on machine learning features using Python, scikit-learn, data "
            "preprocessing, model evaluation, APIs, cloud systems, and production "
            "software engineering practices."
        ),
        location="Redmond, WA",
        salary=None,
    )

    backend_resume = create_demo_resume(
        db=db,
        demo_user=demo_user,
        resume_version="Backend + ML Resume v1",
        resume_text=(
            "Graduate student in Computer Science with experience in Python, "
            "FastAPI, PostgreSQL, SQLAlchemy, REST API development, JWT authentication, "
            "machine learning, TF-IDF, cosine similarity, scikit-learn, pandas, "
            "NumPy, and backend systems."
        ),
    )

    swe_resume = create_demo_resume(
        db=db,
        demo_user=demo_user,
        resume_version="Software Engineer Resume v1",
        resume_text=(
            "Software engineer with experience in Java, Python, SQL, REST APIs, "
            "backend development, cloud integration, debugging, Git, PostgreSQL, "
            "system design fundamentals, and enterprise integrations."
        ),
    )

    create_demo_application(
        db=db,
        demo_user=demo_user,
        demo_job=google_job,
        demo_resume=backend_resume,
        status=ApplicationStatus.applied,
    )

    create_demo_application(
        db=db,
        demo_user=demo_user,
        demo_job=microsoft_job,
        demo_resume=swe_resume,
        status=ApplicationStatus.applied,
    )


def main():
    db = SessionLocal()

    try:
        print("Database session created successfully.")
        db.execute(text("SELECT 1"))
        print("Database connection test passed.")

        print_table_counts(db, "Before seed")

        if RESET_DATABASE:
            reset_database(db)

        seed_database(db)

        print_table_counts(db, "After seed")

        print("\nSeed completed successfully.")
        print(f"Demo login email: {DEMO_EMAIL}")
        print(f"Demo login password: {DEMO_PASSWORD}")

    except Exception as error:
        db.rollback()
        print("\nSeed failed.")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    main()