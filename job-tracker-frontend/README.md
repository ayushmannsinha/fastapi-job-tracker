# Job Tracker Frontend

Simple React + Vite frontend for the FastAPI Job Tracker backend.

## Pages included

- Login / Register
- Applications Dashboard
- Jobs
- Resumes
- New Application
- Application Details
- Manual Match Preview

## Run it

```bash
cd job-tracker-frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Backend URL

By default, the app calls:

```text
http://127.0.0.1:8000
```

To change it:

```bash
cp .env.example .env
```

Then edit:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Important FastAPI CORS setup

If the frontend says `Failed to fetch`, add this to your FastAPI `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Expected backend endpoints

This frontend assumes these routes exist:

```text
POST /auth/token
POST /users/
GET  /jobs/
POST /jobs/
GET  /resumes/
POST /resumes/
POST /applications/
GET  /applications/summary
GET  /applications/{application_id}/details
POST /match-scores/preview
POST /match-scores/applications/{application_id}
GET  /match-scores/applications/{application_id}
```

## Common field-name adjustments

If your backend schema uses different field names, adjust these in `src/App.jsx`:

Resume create payload currently sends:

```js
{
  version_name,
  content
}
```

If your backend expects `resume_text`, change `content` to `resume_text`.

Match preview currently sends:

```js
{
  resume_text,
  job_description
}
```

If your backend expects different names, update the `MatchPreviewPage` payload.
