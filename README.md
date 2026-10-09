# AI Resume Analyzer & Career Guidance Portal

An AI-assisted web application that analyzes uploaded resumes, extracts candidate information and skills, evaluates resume quality, and provides job recommendations and career guidance.

**Project report:** [Download the project report (DOCX)](AI_Resume_Analyzer_Project_Report.docx)  
**Source code:** [Open the application folder](https://github.com/Mukeshkarn-DS/AI_Resume_Analyzer_Project_Report/tree/main/ai_resume_analyzer%202)

## Overview

The project is designed to help users understand how their resume presents their skills and experience. Users can upload a resume and review a generated analysis, suggested roles, and career-improvement guidance. Registered users can access a dashboard with previous analyses.

## Key Features

- **Resume upload and parsing** — accepts PDF and DOCX files, with file-type checks and a 5 MB upload limit.
- **Contact information extraction** — attempts to identify details such as name, email, phone number, LinkedIn, and GitHub.
- **Skill extraction** — identifies skills from the extracted resume text.
- **Resume scoring** — provides a score and grade with feedback; the application can use its ML pipeline or a rule-based fallback.
- **Job recommendations** — suggests roles based on resume content and extracted skills.
- **Career guidance** — presents tailored guidance and overall improvement suggestions.
- **User accounts** — signup and login with hashed passwords.
- **Dashboard and analysis history** — stores resume and analysis records for signed-in users when the database is available.
- **Health endpoint** — exposes basic application, database, and ML availability information at `/api/health`.

## Technology Stack

| Area | Technologies |
|---|---|
| Backend web framework | Python, Flask |
| User interface | HTML templates, CSS, JavaScript (project templates/static assets) |
| Resume processing | PDF/DOCX text extraction |
| NLP / machine learning | Sentence-BERT (`all-MiniLM-L6-v2`) and project ML pipeline, with a rule-based fallback |
| Database | SQLite, SQLAlchemy / Flask-SQLAlchemy |
| Authentication | Flask sessions and Werkzeug password hashing |

## Application Workflow

1. The user opens the portal and uploads a PDF or DOCX resume.
2. The application validates the file and extracts its text.
3. Contact details and skills are identified.
4. The ML pipeline evaluates the resume and generates recommendations when available; otherwise, the fallback analysis is used.
5. The application displays the score, skill information, job suggestions, and career guidance.
6. If the user is signed in and database storage is available, resume and analysis information can be saved for the dashboard history.

## Project Structure

```text
AI_Resume_Analyzer_Project_Report/
├── README.md
├── AI_Resume_Analyzer_Project_Report.docx
└── ai_resume_analyzer 2/
    ├── app.py
    ├── config.py
    ├── database.py
    ├── requirements.txt
    ├── modules/
    ├── ml_pipeline/
    ├── templates/
    ├── static/
    ├── data/
    ├── database/
    ├── uploads/
    └── screenshots/
```

The repository also contains screenshots of the application and its setup. The exact contents of generated folders may change when the application runs.

## Screenshots

The following screenshots are stored in the application folder:

| Screen | Screenshot |
|---|---|
| Home page | [View screenshot](ai_resume_analyzer%202/Homepage.png.png) |
| Signup page | [View screenshot](ai_resume_analyzer%202/Signuppage.png.png) |
| Page after login | [View screenshot](ai_resume_analyzer%202/Afterloginpage.png.png) |
| Analysis and AI page | [View screenshot](ai_resume_analyzer%202/AanalyisipageandAipage.png.png) |
| Dashboard and history | [View screenshot](ai_resume_analyzer%202/Dashboard%20and%20History%20result.png.png) |
| Project directory | [View screenshot](ai_resume_analyzer%202/File%20directory.png.png) |
| ML pipeline setup | [View screenshot](ai_resume_analyzer%202/Ml%20pipeline%20enable.png.png) |

## Setup and Run

### Prerequisites

- Python 3.10 or a compatible Python version supported by the installed project dependencies
- Git
- Internet access for the first download of the Sentence-BERT model, if the ML pipeline uses it

### 1. Clone the repository

```bash
git clone https://github.com/Mukeshkarn-DS/AI_Resume_Analyzer_Project_Report.git
cd AI_Resume_Analyzer_Project_Report
```

### 2. Open the application directory

The folder name contains a space, so keep it quoted when using shell commands.

**Windows PowerShell:**
```powershell
cd "ai_resume_analyzer 2"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
cd "ai_resume_analyzer 2"
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Install the packages required by the project modules. The repository's `requirements.txt` should be populated with the verified dependencies before using it as the installation source. For now, review the imports in `app.py`, `modules/`, and `ml_pipeline/` and install their required packages in the virtual environment.

### 4. Configure and start the application

Set a unique secret key before running the application. For local development:

**Windows PowerShell:**
```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
python app.py
```

**macOS / Linux:**
```bash
export SECRET_KEY="replace-with-a-long-random-secret"
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. The first ML startup may take longer while the model is downloaded or loaded.

> **Note:** The repository's current `requirements.txt` is empty. Dependency installation is therefore not yet fully reproducible from that file alone. Verify and add the packages used by the project before expecting a fresh environment to run successfully.

## API Health Check

Once the local server is running, visit:

```text
http://127.0.0.1:5000/api/health
```

The endpoint returns a JSON status indicating whether the application, ML pipeline, and database are available.

## Security and Responsible Use

- Use a strong, private `SECRET_KEY`; do not deploy with the development fallback.
- Resume files contain personal information. Do not commit real resumes, credentials, database files, or private user data to the repository.
- Keep uploaded files protected and define a retention/deletion policy before public deployment.
- Treat scores and job recommendations as decision-support suggestions, not guarantees of employability or hiring outcomes.
- Run with debug mode disabled in production and deploy behind a properly configured production server.

## Current Limitations

- Results depend on the quality and formatting of the uploaded resume and on the availability of the ML pipeline.
- The application can fall back to rule-based scoring when the ML pipeline is unavailable.
- Dependencies are not yet fully documented in `requirements.txt`.
- This repository documents a project implementation; production readiness, model quality, privacy controls, and deployment security require further validation.

## Future Improvements

- Add a complete, pinned dependency file and reproducible installation instructions.
- Add automated tests for parsing, scoring, recommendations, authentication, and file validation.
- Expand evaluation using representative resumes and documented metrics.
- Improve accessibility, explainability, privacy controls, and deployment configuration.

## Author

**Mukesh Karn**  
GitHub: [@Mukeshkarn-DS](https://github.com/Mukeshkarn-DS)

---

If you find this project useful, consider starring the repository or sharing constructive feedback through GitHub issues.
