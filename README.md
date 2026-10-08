# EduPulse AI

## Predict. Explain. Intervene. Improve.

EduPulse AI is an AI-assisted student success and early-intervention platform for educational institutions. It combines academic, attendance, engagement, learning, skills and placement-related signals into student success scores, risk categories, explainable risk drivers, student segments and targeted intervention recommendations.

> **Demo / academic prototype:** the included dataset is synthetic/demo data and is not an official institutional record.

## Core capabilities

- Management and admin authentication
- Student authentication with student-level access control
- Student success score dashboard
- Risk distribution and student segmentation charts
- Search by Student ID or name
- Risk-level filtering
- Department filtering
- Academic Strong / Placement Unprepared identification
- Student 360° profile with risk drivers and intervention recommendations
- Server-side logout and session management
- Production-ready Flask + Gunicorn deployment configuration

## Architecture

```text
Synthetic / integrated student data
        ↓
Feature engineering + ML / scoring modules
        ↓
Success score + risk analysis + segmentation
        ↓
Explainability + intervention recommendations
        ↓
Flask REST API + session authentication
        ↓
Web dashboard / student dashboard
```

## Technology stack

- Python
- Flask
- Pandas / NumPy
- Scikit-learn
- SQLite
- HTML / CSS / JavaScript
- Chart.js
- Gunicorn for production serving

## Project structure

```text
EduPulse-AI/
├── backend/
│   ├── __init__.py
│   ├── app.py
│   └── auth.py
├── frontend/
│   ├── index.html
│   ├── login.html
│   └── student.html
├── data/
│   ├── raw/
│   └── processed/
├── ml/
│   ├── __init__.py
│   ├── explainability.py
│   ├── recommendations.py
│   ├── risk_model.py
│   ├── segmentation.py
│   └── success_score.py
├── generate_data.py
├── integrate_data.py
├── requirements.txt
├── Procfile
├── render.yaml
├── HacXLerate_Submission.md
└── README.md
```

`users.db` is generated automatically on first application startup and is intentionally not committed to the public repository.

## Local setup

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start the application

```powershell
python backend\app.py
```

The Flask app runs on `http://127.0.0.1:5000`.

Open:

`http://127.0.0.1:5000/login.html`

The app serves both the frontend and API from the same Flask service.

## Demo accounts

- Management: `manager01` / `manager123`
- Admin: `admin01` / `admin123`
- Student example: `student001` / `student123`

These credentials are for the synthetic demo only. For real deployments, use different credentials and a strong `SECRET_KEY`.

## API overview

- `POST /api/login` — authenticate
- `POST /api/logout` — clear the server session
- `GET /api/health` — deployment health check
- `GET /api/summary` — management summary
- `GET /api/students` — management student list
- `GET /api/student/<student_id>` — individual student profile with access control
- `GET /api/top-students` — top success-score students
- `GET /api/at-risk` — medium/high-risk students
- `GET /api/placement-unprepared` — Academic Strong / Placement Unprepared students
- `GET /api/search?q=...` — management search endpoint

## Deployment

This project is prepared for Render using Gunicorn.

- Runtime: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn backend.app:app`
- Environment variable: `SECRET_KEY`
- Environment variable: `SESSION_COOKIE_SECURE=1`

Render can deploy this repository directly as a Python web service. The `render.yaml` file contains the service configuration.

## HacXLerate Round 1 submission checklist

- [x] Working application
- [x] Functional dashboard
- [x] Authentication and access control
- [x] Student 360° profile
- [x] Search and filters
- [x] Placement-unprepared analysis
- [x] README / technical documentation
- [x] Production startup configuration
- [ ] Public GitHub repository URL
- [ ] Public deployment URL
- [ ] Challenge-specific mandatory criteria verified against the locked problem statement
- [ ] Final HacXLerate platform submission

The general HacXLerate rule book requires an accessible repository, documentation, deployment where specified, and completion of challenge-specific submission information.

## Security notes

- Do not commit `.env` or real secrets.
- Use synthetic/demo student data for a public demo repository.
- Use HTTPS in production.
- Change demo credentials before real institutional use.
- Set a strong `SECRET_KEY` in deployment environment variables.

## License

No license has been added yet. Add one if your team or institution requires a specific license.
