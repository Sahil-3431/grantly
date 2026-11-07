# GRANTLY — Ready-to-run hackathon starter

A polished, responsive scholarship discovery and application-tracking prototype based on the supplied GRANTLY Project Guide. Includes animated page changes, animated modal dialogs, responsive dashboard, animated login/signup screen, logout controls, per-account browser demo data, scholarship search/filter, save list, editable application tracker, document checklist, student profile editor and a scholarship-only assistant.

## Quick start (recommended: Docker)
1. Install Docker Desktop.
2. Extract this ZIP.
3. Open a terminal in the extracted `grantly-ready` folder.
4. Run:
   ```bash
   docker compose up --build
   ```
5. Open **http://localhost:5173** for the website.
6. Open **http://localhost:8000/docs** for interactive backend API documentation.

Stop with `Ctrl+C`, then optionally run `docker compose down`.

## Run without Docker
### Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## Included features
- Dashboard with scholarship highlights and deadline reminders
- Scholarship catalogue with search and category filter
- Scholarship detail modal, listed eligibility criteria, documents and official-source link
- Save / unsave scholarships
- Login and signup screens with logout from the sidebar, profile settings and top bar
- Application Tracker navigation, add/remove scholarship tracking, editable status, personal notes and applied date
- Demo accounts and each account’s saved scholarships, profile and tracker data persist in the same browser using localStorage
- Common document checklist
- Student profile editor
- Scholarship-only GRANTLY Assistant (rule-based FAQ responses)
- FastAPI backend with SQLite persistence, sample scholarship seed data and API docs
- Framer Motion page, modal and chatbot transitions

## API endpoints
- `GET /api/scholarships?q=&category=`
- `GET /api/scholarships/{id}`
- `POST /api/saved`, `GET /api/saved`, `DELETE /api/saved/{id}`
- `POST /api/applications`, `GET /api/applications`, `PATCH /api/applications/{id}`
- `POST /api/eligibility/check`
- `POST /api/chat`
- `GET /health`

## Important demo limitations
- Scholarship entries are sample records for the hackathon prototype. Confirm and replace them with current verified listings before public launch.
- The new login/signup is a hackathon demo account flow stored in the current browser. Password hashes are stored locally; this is not production authentication and accounts do not sync across devices or browsers. Do not reuse a real password.
- Application Tracker, saved scholarships and profile data persist in browser localStorage for each demo account. The included FastAPI SQLite endpoints are available separately, but frontend data is not yet connected to those APIs.
- Production-grade server authentication/authorization, real document upload/storage, email/SMS reminders and a live generative AI provider are not enabled. Do not enter real sensitive student data in this demo.
- The assistant is deliberately restricted to scholarship and GRANTLY help. It uses a curated rule-based knowledge set and will not invent official requirements.
- Eligibility is only preliminary guidance. Final rules and decisions belong to the official scholarship provider.

## Suggested next development steps
1. Connect frontend data actions and demo account identities to the included FastAPI endpoints.
2. Replace browser-only demo login with secure server authentication and per-student authorization.
3. Replace demo scholarship records with admin-verified listings and update timestamps.
4. Add private document storage with access controls.
5. Add scheduled deadline notifications and, if required, a grounded AI assistant connected only to verified scholarship records.

## Tech stack
React 18, Vite, Framer Motion, Lucide React, FastAPI, Pydantic and SQLite (easy local setup; can be migrated to PostgreSQL for deployment).
