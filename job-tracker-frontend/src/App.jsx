import { useEffect, useState } from "react";
import { apiRequest, clearToken, getToken, login, register } from "./api";

const STATUS_OPTIONS = ["Applied", "OA", "Interview", "Offer", "Rejected"];

function getErrorMessage(error) {
  return error?.message || "Something went wrong";
}

function EmptyState({ title, message }) {
  return (
    <div className="empty">
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  );
}

function PageHeader({ title, subtitle }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
    </div>
  );
}

function AuthPage({ onAuthSuccess }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("demo123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password);
        await login(email, password);
      }

      onAuthSuccess();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-card">
        <div className="brand">
          <div className="brand-mark">JT</div>
          <div>
            <h1>Job Tracker</h1>
            <p>Track applications and resume match scores.</p>
          </div>
        </div>

        <div className="tab-row">
          <button
            className={mode === "login" ? "tab active" : "tab"}
            onClick={() => setMode("login")}
            type="button"
          >
            Login
          </button>
          <button
            className={mode === "register" ? "tab active" : "tab"}
            onClick={() => setMode("register")}
            type="button"
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="form">
          <label>
            Email
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              type="email"
              required
            />
          </label>

          <label>
            Password
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Password"
              type="password"
              required
            />
          </label>

          {error && <div className="error-box">{error}</div>}

          <button className="primary-btn full" disabled={loading}>
            {loading ? "Please wait..." : mode === "login" ? "Login" : "Create account"}
          </button>
        </form>
      </section>
    </main>
  );
}

function Shell({ page, setPage, onLogout, children }) {
  const navItems = [
    ["dashboard", "Dashboard"],
    ["jobs", "Jobs"],
    ["resumes", "Resumes"],
    ["newApplication", "New Application"],
    ["preview", "Match Preview"],
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">JT</div>
          <div>
            <strong>Job Tracker</strong>
            <span>FastAPI + React</span>
          </div>
        </div>

        <nav>
          {navItems.map(([key, label]) => (
            <button
              key={key}
              className={page === key ? "nav-link active" : "nav-link"}
              onClick={() => setPage(key)}
              type="button"
            >
              {label}
            </button>
          ))}
        </nav>

        <button className="logout-btn" onClick={onLogout} type="button">
          Logout
        </button>
      </aside>

      <section className="content">{children}</section>
    </div>
  );
}

function DashboardPage({ setPage, setSelectedApplicationId }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadApplications() {
    setLoading(true);
    setError("");

    try {
      const data = await apiRequest("/applications/summary");
      setApplications(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadApplications();
  }, []);

  const total = applications.length;
  const interviews = applications.filter((app) => app.status === "Interview").length;
  const offers = applications.filter((app) => app.status === "Offer").length;
  const avgScore =
    applications
      .filter((app) => app.match_score !== null && app.match_score !== undefined)
      .reduce((sum, app) => sum + Number(app.match_score), 0) /
    Math.max(
      applications.filter((app) => app.match_score !== null && app.match_score !== undefined)
        .length,
      1
    );

  return (
    <>
      <PageHeader
        title="Applications Dashboard"
        subtitle="View your saved applications and resume match scores."
      />

      <div className="stats-grid">
        <div className="stat-card">
          <span>Total Applications</span>
          <strong>{total}</strong>
        </div>
        <div className="stat-card">
          <span>Interviews</span>
          <strong>{interviews}</strong>
        </div>
        <div className="stat-card">
          <span>Offers</span>
          <strong>{offers}</strong>
        </div>
        <div className="stat-card">
          <span>Average Match Score</span>
          <strong>{Number.isFinite(avgScore) ? avgScore.toFixed(1) : "0.0"}</strong>
        </div>
      </div>

      {loading && <div className="info-box">Loading applications...</div>}
      {error && <div className="error-box">{error}</div>}

      {!loading && !error && applications.length === 0 && (
        <EmptyState
          title="No applications yet"
          message="Create jobs and resumes first, then add your first application."
        />
      )}

      <div className="card-grid">
        {applications.map((application) => (
          <article className="application-card" key={application.id}>
            <div>
              <h3>{application.company_name}</h3>
              <p>{application.job_title}</p>
            </div>

            <div className="meta-row">
              <span className="status-pill">{application.status}</span>
              <span>
                Score:{" "}
                <strong>
                  {application.match_score !== null && application.match_score !== undefined
                    ? application.match_score
                    : "Not saved"}
                </strong>
              </span>
            </div>

            <p className="muted">Resume: {application.resume_version || "N/A"}</p>

            <button
              className="secondary-btn"
              onClick={() => {
                setSelectedApplicationId(application.id);
                setPage("details");
              }}
              type="button"
            >
              View details
            </button>
          </article>
        ))}
      </div>
    </>
  );
}

function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [form, setForm] = useState({
    company_name: "",
    job_title: "",
    job_description: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadJobs() {
    setError("");

    try {
      const data = await apiRequest("/jobs/");
      setJobs(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    loadJobs();
  }, []);

  async function handleCreateJob(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      await apiRequest("/jobs/", {
        method: "POST",
        body: JSON.stringify(form),
      });

      setForm({ company_name: "", job_title: "", job_description: "" });
      setMessage("Job added successfully.");
      await loadJobs();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <>
      <PageHeader title="Jobs" subtitle="Add job descriptions that you want to track." />

      <section className="two-column">
        <form className="panel form" onSubmit={handleCreateJob}>
          <h2>Add Job</h2>

          <label>
            Company Name
            <input
              value={form.company_name}
              onChange={(event) =>
                setForm({ ...form, company_name: event.target.value })
              }
              required
            />
          </label>

          <label>
            Job Title
            <input
              value={form.job_title}
              onChange={(event) => setForm({ ...form, job_title: event.target.value })}
              required
            />
          </label>

          <label>
            Job Description
            <textarea
              value={form.job_description}
              onChange={(event) =>
                setForm({ ...form, job_description: event.target.value })
              }
              rows={8}
              required
            />
          </label>

          {message && <div className="success-box">{message}</div>}
          {error && <div className="error-box">{error}</div>}

          <button className="primary-btn">Save Job</button>
        </form>

        <section className="panel">
          <h2>Saved Jobs</h2>

          {jobs.length === 0 ? (
            <p className="muted">No jobs saved yet.</p>
          ) : (
            <div className="list">
              {jobs.map((job) => (
                <div className="list-item" key={job.id}>
                  <strong>
                    {job.company_name} — {job.job_title}
                  </strong>
                  <p>{job.job_description || job.description || "No description"}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </section>
    </>
  );
}

function ResumesPage() {
  const [resumes, setResumes] = useState([]);
  const [form, setForm] = useState({
    resume_version: "",
    resume_text: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadResumes() {
    setError("");

    try {
      const data = await apiRequest("/resumes/");
      setResumes(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    loadResumes();
  }, []);

  async function handleCreateResume(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      await apiRequest("/resumes/", {
        method: "POST",
        body: JSON.stringify(form),
      });

      setForm({ resume_version: "", resume_text: "" });
      setMessage("Resume added successfully.");
      await loadResumes();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <>
      <PageHeader title="Resumes" subtitle="Store resume versions used for applications." />

      <section className="two-column">
        <form className="panel form" onSubmit={handleCreateResume}>
          <h2>Add Resume</h2>

          <label>
            Version Name
            <input
              value={form.resume_version}
              onChange={(event) =>
                setForm({ ...form, resume_version: event.target.value })
              }
              placeholder="Backend + ML Resume v1"
              required
            />
          </label>

          <label>
            Resume Content
            <textarea
              value={form.resume_text}
              onChange={(event) =>
                setForm({ ...form, resume_text: event.target.value })
              }
              rows={10}
              placeholder="Paste resume text here"
              required
            />
          </label>

          <p className="hint">
            This sends <code>resume_version</code> and <code>resume_text</code> to your backend.
          </p>

          {message && <div className="success-box">{message}</div>}
          {error && <div className="error-box">{error}</div>}

          <button className="primary-btn">Save Resume</button>
        </form>

        <section className="panel">
          <h2>Saved Resumes</h2>

          {resumes.length === 0 ? (
            <p className="muted">No resumes saved yet.</p>
          ) : (
            <div className="list">
              {resumes.map((resume) => (
                <div className="list-item" key={resume.id}>
                  <strong>{resume.resume_version || resume.name || `Resume ${resume.id}`}</strong>
                  <p>{resume.resume_text || resume.content || "No resume content shown"}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </section>
    </>
  );
}

function NewApplicationPage({ setPage, setSelectedApplicationId }) {
  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [form, setForm] = useState({
    job_id: "",
    resume_id: "",
    status: "Applied",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadOptions() {
    setError("");

    try {
      const [jobsData, resumesData] = await Promise.all([
        apiRequest("/jobs/"),
        apiRequest("/resumes/"),
      ]);

      setJobs(Array.isArray(jobsData) ? jobsData : []);
      setResumes(Array.isArray(resumesData) ? resumesData : []);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    loadOptions();
  }, []);

  async function handleCreateApplication(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      const data = await apiRequest("/applications/", {
        method: "POST",
        body: JSON.stringify({
          job_id: Number(form.job_id),
          resume_id: Number(form.resume_id),
          status: form.status,
        }),
      });

      setMessage("Application created successfully.");

      if (data?.id) {
        setSelectedApplicationId(data.id);
        setPage("details");
      }
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <>
      <PageHeader
        title="New Application"
        subtitle="Connect a saved job with a saved resume."
      />

      <section className="panel narrow">
        <form className="form" onSubmit={handleCreateApplication}>
          <label>
            Job
            <select
              value={form.job_id}
              onChange={(event) => setForm({ ...form, job_id: event.target.value })}
              required
            >
              <option value="">Select a job</option>
              {jobs.map((job) => (
                <option value={job.id} key={job.id}>
                  {job.company_name} — {job.job_title}
                </option>
              ))}
            </select>
          </label>

          <label>
            Resume
            <select
              value={form.resume_id}
              onChange={(event) =>
                setForm({ ...form, resume_id: event.target.value })
              }
              required
            >
              <option value="">Select a resume</option>
              {resumes.map((resume) => (
                <option value={resume.id} key={resume.id}>
                  {resume.resume_version || resume.name || `Resume ${resume.id}`}
                </option>
              ))}
            </select>
          </label>

          <label>
            Status
            <select
              value={form.status}
              onChange={(event) => setForm({ ...form, status: event.target.value })}
            >
              {STATUS_OPTIONS.map((status) => (
                <option value={status} key={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>

          {message && <div className="success-box">{message}</div>}
          {error && <div className="error-box">{error}</div>}

          <button className="primary-btn">Create Application</button>
        </form>
      </section>
    </>
  );
}

function ApplicationDetailsPage({ applicationId }) {
  const [details, setDetails] = useState(null);
  const [savedScore, setSavedScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scoreLoading, setScoreLoading] = useState(false);
  const [error, setError] = useState("");
  const [scoreError, setScoreError] = useState("");
  const [newStatus, setNewStatus] = useState("Applied");
  const [statusMessage, setStatusMessage] = useState("");
  const [statusError, setStatusError] = useState("");

  async function loadDetails() {
    if (!applicationId) return;

    setLoading(true);
    setError("");

    try {
      const data = await apiRequest(`/applications/${applicationId}/details`);
      setDetails(data);
      setNewStatus(data.status || "Applied");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function loadSavedScore() {
    if (!applicationId) return;

    setScoreError("");

    try {
      const data = await apiRequest(`/match_scores/applications/${applicationId}`);
      setSavedScore(data);
    } catch {
      setSavedScore(null);
    }
  }

  useEffect(() => {
    loadDetails();
    loadSavedScore();
  }, [applicationId]);

  async function handleGenerateScore() {
    setScoreLoading(true);
    setScoreError("");

    try {
      const data = await apiRequest(`/match_scores/applications/${applicationId}`, {
        method: "POST",
        body: JSON.stringify({}),
      });

      setSavedScore(data);
      await loadDetails();
    } catch (err) {
      setScoreError(getErrorMessage(err));
    } finally {
      setScoreLoading(false);
    }
  }

  if (!applicationId) {
    return (
      <EmptyState
        title="No application selected"
        message="Go to the dashboard and open an application."
      />
    );
  }

  async function handleStatusUpdate() {
    setStatusMessage("");
    setStatusError("");

    try {
      await apiRequest(`/applications/${applicationId}`, {
        method: "PUT",
        body: JSON.stringify({
          status: newStatus,
        }),
      });

      setStatusMessage("Status updated successfully.");
      await loadDetails();
    } catch (err) {
      setStatusError(getErrorMessage(err));
    }
  }

  return (
    <>
      <PageHeader
        title="Application Details"
        subtitle={`Application ID: ${applicationId}`}
      />

      {loading && <div className="info-box">Loading details...</div>}
      {error && <div className="error-box">{error}</div>}

      {!loading && details && (
        <section className="details-grid">
          <div className="panel">
            <h2>Details</h2>
            <dl className="details-list">
              <dt>Company</dt>
              <dd>{details.company_name || details.job?.company_name || "N/A"}</dd>

              <dt>Job Title</dt>
              <dd>{details.job_title || details.job?.job_title || "N/A"}</dd>

              <dt>Status</dt>
              <dd>{details.status || "N/A"}</dd>

              <dt>Resume</dt>
              <dd>
                {details.resume_version ||
                  details.resume?.resume_version ||
                  details.resume_name ||
                  "N/A"}
              </dd>
            </dl>

            <div className="status-update-box">
              <label>
                Update Status
                <select
                  value={newStatus}
                  onChange={(event) => setNewStatus(event.target.value)}
                >
                  {STATUS_OPTIONS.map((status) => (
                    <option value={status} key={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </label>

              {statusMessage && <div className="success-box">{statusMessage}</div>}
              {statusError && <div className="error-box">{statusError}</div>}

              <button
                className="secondary-btn"
                onClick={handleStatusUpdate}
                type="button"
              >
                Save Status
              </button>
            </div>
            
            <details className="raw-json">
              <summary>Show raw backend response</summary>
              <pre>{JSON.stringify(details, null, 2)}</pre>
            </details>
          </div>

          <div className="panel">
            <h2>Match Score</h2>

            {savedScore ? (
              <div className="score-box">
                <strong>{savedScore.score ?? "N/A"}</strong>
                <span>Saved Score</span>
              </div>
            ) : (
              <p className="muted">No saved match score yet.</p>
            )}

            {savedScore?.matched_skills && (
              <>
                <h3>Matched Skills</h3>
                <div className="chip-row">
                  {savedScore.matched_skills.map((skill) => (
                    <span className="chip" key={skill}>
                      {skill}
                    </span>
                  ))}
                </div>
              </>
            )}

            {savedScore?.missing_skills && (
              <>
                <h3>Missing Skills</h3>
                <div className="chip-row">
                  {savedScore.missing_skills.map((skill) => (
                    <span className="chip warning" key={skill}>
                      {skill}
                    </span>
                  ))}
                </div>
              </>
            )}

            {scoreError && <div className="error-box">{scoreError}</div>}

            <button
              className="primary-btn"
              onClick={handleGenerateScore}
              disabled={scoreLoading}
              type="button"
            >
              {scoreLoading ? "Calculating..." : "Generate / Save Match Score"}
            </button>
          </div>
        </section>
      )}
    </>
  );
}

function MatchPreviewPage() {
  const [form, setForm] = useState({
    resume_text:
      "Python, FastAPI, PostgreSQL, SQLAlchemy, REST APIs, JWT Authentication, Machine Learning, scikit-learn",
    job_description:
      "We are looking for a backend intern with Python, REST APIs, SQL, FastAPI, and machine learning experience.",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handlePreview(event) {
    event.preventDefault();
    setResult(null);
    setError("");

    try {
      const data = await apiRequest("/match_scores/preview", {
        method: "POST",
        body: JSON.stringify(form),
      });

      setResult(data);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <>
      <PageHeader
        title="Match Preview"
        subtitle="Test resume and job description matching without saving it to an application."
      />

      <section className="two-column">
        <form className="panel form" onSubmit={handlePreview}>
          <label>
            Resume Text
            <textarea
              value={form.resume_text}
              onChange={(event) =>
                setForm({ ...form, resume_text: event.target.value })
              }
              rows={10}
              required
            />
          </label>

          <label>
            Job Description
            <textarea
              value={form.job_description}
              onChange={(event) =>
                setForm({ ...form, job_description: event.target.value })
              }
              rows={10}
              required
            />
          </label>

          <p className="hint">
            If your backend expects different field names, adjust{" "}
            <code>resume_text</code> and <code>job_description</code> in this page.
          </p>

          {error && <div className="error-box">{error}</div>}

          <button className="primary-btn">Preview Match</button>
        </form>

        <section className="panel">
          <h2>Preview Result</h2>

          {!result ? (
            <p className="muted">Run a preview to see the score here.</p>
          ) : (
            <>
              <div className="score-box">
                <strong>{result.score}</strong>
                <span>Match Score</span>
              </div>

              <h3>Matched Skills</h3>
              <div className="chip-row">
                {(result.matched_skills || []).map((skill) => (
                  <span className="chip" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>

              <h3>Missing Skills</h3>
              <div className="chip-row">
                {(result.missing_skills || []).map((skill) => (
                  <span className="chip warning" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>

              <details className="raw-json">
                <summary>Show raw response</summary>
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </details>
            </>
          )}
        </section>
      </section>
    </>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getToken()));
  const [page, setPage] = useState("dashboard");
  const [selectedApplicationId, setSelectedApplicationId] = useState(null);

  function handleLogout() {
    clearToken();
    setIsAuthenticated(false);
    setPage("dashboard");
    setSelectedApplicationId(null);
  }

  if (!isAuthenticated) {
    return <AuthPage onAuthSuccess={() => setIsAuthenticated(true)} />;
  }

  let pageContent;

  if (page === "dashboard") {
    pageContent = (
      <DashboardPage
        setPage={setPage}
        setSelectedApplicationId={setSelectedApplicationId}
      />
    );
  } else if (page === "jobs") {
    pageContent = <JobsPage />;
  } else if (page === "resumes") {
    pageContent = <ResumesPage />;
  } else if (page === "newApplication") {
    pageContent = (
      <NewApplicationPage
        setPage={setPage}
        setSelectedApplicationId={setSelectedApplicationId}
      />
    );
  } else if (page === "details") {
    pageContent = <ApplicationDetailsPage applicationId={selectedApplicationId} />;
  } else if (page === "preview") {
    pageContent = <MatchPreviewPage />;
  }

  return (
    <Shell page={page} setPage={setPage} onLogout={handleLogout}>
      {pageContent}
    </Shell>
  );
}
