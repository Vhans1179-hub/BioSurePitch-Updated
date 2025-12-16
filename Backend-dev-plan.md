
# Backend Development Plan - BioSure Carvykti Outcomes Desk

## 1️⃣ Executive Summary

**What Will Be Built:**
- FastAPI backend (Python 3.13, async) serving REST APIs for BioSure Carvykti Outcomes Desk
- MongoDB Atlas database storing patient cohort data, HCO information, and contract templates
- API endpoints supporting cohort analytics, ghost patient identification, and contract simulation
- Real-time chat assistant integration

**Constraints:**
- FastAPI with Python 3.13 runtime (async)
- MongoDB Atlas only (no local instance)
- No Docker containers
- Manual testing after every task via frontend UI
- Single-branch Git workflow (`main` only)
- Per-task testing before sprint completion

**Sprint Structure:**
- **S0:** Environment setup and frontend connection
- **S1:** Patient cohort data management
- **S2:** HCO and ghost patient analytics
- **S3:** Contract simulation engine
- **S4:** Chat assistant backend

---

## 2️⃣ In-Scope & Success Criteria

**In-Scope Features:**
- Patient cohort data retrieval with filtering and aggregation
- HCO (Healthcare Organization) data with ghost patient metrics
- Contract template management and simulation calculations
- Chat message handling with contextual responses
- Statistical aggregations for dashboard metrics
- CSV export data preparation

**Success Criteria:**
- All frontend pages display live data from backend
- Cohort Overview shows accurate patient statistics and charts
- Ghost Radar displays HCO rankings with filtering
- Contract Simulator performs calculations and returns results
- Chat widget sends/receives messages successfully
- All task-level manual tests pass via UI
- Each sprint's code pushed to `main` after verification

---

## 3️⃣ API Design

**Base Path:** `/api/v1`

**Error Envelope:** `{ "error": "message" }`

### Endpoints

#### Health Check
- **GET /healthz**
- Purpose: Verify backend and database connectivity
- Response: `{ "status": "ok", "database": "connected", "timestamp": "ISO8601" }`

#### Patient Cohort
- **GET /api/v1/patients**
- Purpose: Retrieve patient cohort data with optional filtering
- Query params: `region`, `state`, `payer_type`, `min_age`, `max_age`
- Response: `{ "patients": [...], "total": 847 }`
- Validation: Age range 0-120, valid region/state codes

- **GET /api/v1/patients/stats**
- Purpose: Get aggregated cohort statistics
- Response: `{ "total_patients": 847, "avg_age": 67, "male_percent": 60, "avg_prior_lines": 3.2, "payer_dist": {...}, "region_dist": {...}, "age_buckets": {...} }`

#### HCO & Ghost Patients
- **GET /api/v1/hcos**
- Purpose: Retrieve HCO data with ghost patient metrics
- Query params: `region`, `state`, `min_ghost_patients`, `sort_by`
- Response: `{ "hcos": [...], "total": 50 }`
- Validation: Valid region/state, sort_by in [ghost_patients, leakage_rate, name]

- **GET /api/v1/hcos/stats**
- Purpose: Get aggregated ghost patient statistics
- Response: `{ "total_ghost": 5234, "total_treated": 847, "avg_ghost_per_hco": 104, "leakage_rate": 86.1, "hco_count": 50 }`

#### Contract Simulation
- **GET /api/v1/contracts/templates**
- Purpose: Retrieve available contract templates
- Response: `{ "templates": [...] }`

- **POST /api/v1/contracts/simulate**
- Purpose: Run contract simulation with parameters
- Request: `{ "template_id": "survival-12m", "rebate_percent": 50, "therapy_price": 465000, "time_window": 12 }`
- Response: `{ "total_patients": 847, "failure_count": 212, "success_count": 635, "failure_rate": 25.0, "success_rate": 75.0, "rebate_per_patient": 232500, "total_rebate": 49290000, "low_rebate": 39432000, "high_rebate": 59148000, "avg_rebate_per_treated": 58200 }`
- Validation: rebate_percent 0-100, therapy_price > 0, time_window > 0

#### Chat Assistant
- **POST /api/v1/chat/message**
- Purpose: Send user message and receive bot response
- Request: `{ "message": "string", "session_id": "optional-uuid" }`
- Response: `{ "response": "string", "session_id": "uuid", "timestamp": "ISO8601" }`
- Validation: message length 1-1000 chars

---

## 4️⃣ Data Model (MongoDB Atlas)

### Collection: `patients`
**Fields:**
- `_id`: ObjectId (auto-generated)
- `patient_id`: String (required, unique, e.g., "PT-000001")
- `age`: Integer (required, 18-120)
- `sex`: String (required, enum: ["M", "F"])
- `state`: String (required, 2-char code)
- `region`: String (required, enum: ["West", "South", "Northeast", "Midwest"])
- `payer_type`: String (required, enum: ["Commercial", "Medicare Advantage", "Medicaid", "Other"])
- `index_date`: Date (required)
- `treating_hco_id`: String (required, e.g., "HCO-001")
- `treating_hco_name`: String (required)
- `prior_lines`: Integer (required, 2-10)
- `has_event_12_month`: Boolean (required)
- `has_retreatment_18_month`: Boolean (required)
- `has_toxicity_30_day`: Boolean (required)
- `created_at`: Date (auto)
- `updated_at`: Date (auto)

**Example Document:**
```json
{
  "_id": "ObjectId(...)",
  "patient_id": "PT-000001",
  "age": 67,
  "sex": "M",
  "state": "CA",
  "region": "West",
  "payer_type": "Medicare Advantage",
  "index_date": "2024-03-15T00:00:00Z",
  "treating_hco_id": "HCO-012",
  "treating_hco_name": "Memorial Cancer Center - CA",
  "prior_lines": 3,
  "has_event_12_month": false,
  "has_retreatment_18_month": false,
  "has_toxicity_30_day": true,
  "created_at": "2024-12-15T20:00:00Z",
  "updated_at": "2024-12-15T20:00:00Z"
}
```

### Collection: `hcos`
**Fields:**
- `_id`: ObjectId (auto-generated)
- `hco_id`: String (required, unique, e.g., "HCO-001")
- `name`: String (required)
- `state`: String (required, 2-char code)
- `region`: String (required)
- `treated_patients`: Integer (required, >= 0)
- `ghost_patients`: Integer (required, >= 0)
- `created_at`: Date (auto)
- `updated_at`: Date (auto)

**Example Document:**
```json
{
  "_id": "ObjectId(...)",
  "hco_id": "HCO-001",
  "name": "Memorial Cancer Center - CA",
  "state": "CA",
  "region": "West",
  "treated_patients": 23,
  "ghost_patients": 87,
  "created_at": "2024-12-15T20:00:00Z",
  "updated_at": "2024-12-15T20:00:00Z"
}
```

### Collection: `contract_templates`
**Fields:**
- `_id`: ObjectId (auto-generated)
- `template_id`: String (required, unique)
- `name`: String (required)
- `description`: String (required)
- `outcome_type`: String (required, enum: ["12-month-survival", "retreatment", "toxicity"])
- `default_time_window`: Integer (required, months)
- `default_rebate_percent`: Integer (required, 0-100)
- `created_at`: Date (auto)
- `updated_at`: Date (auto)

**Example Document:**
```json
{
  "_id": "ObjectId(...)",
  "template_id": "survival-12m",
  "name": "12-Month Survival Warranty",
  "description": "Rebate if patient dies or escalates to new MM treatment before 12 months",
  "outcome_type": "12-month-survival",
  "default_time_window": 12,
  "default_rebate_percent": 50,
  "created_at": "2024-12-15T20:00:00Z",
  "updated_at": "2024-12-15T20:00:00Z"
}
```

### Collection: `chat_sessions`
**Fields:**
- `_id`: ObjectId (auto-generated)
- `session_id`: String (required, unique, UUID)
- `messages`: Array of embedded documents
  - `role`: String (enum: ["user", "bot"])
  - `content`: String
  - `timestamp`: Date
- `created_at`: Date (auto)
- `updated_at`: Date (auto)

**Example Document:**
```json
{
  "_id": "ObjectId(...)",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "bot",
      "content": "Hello! How can I help you today?",
      "timestamp": "2024-12-15T20:00:00Z"
    },
    {
      "role": "user",
      "content": "Tell me about the cohort",
      "timestamp": "2024-12-15T20:01:00Z"
    }
  ],
  "created_at": "2024-12-15T20:00:00Z",
  "updated_at": "2024-12-15T20:01:00Z"
}
```

---

## 5️⃣ Frontend Audit & Feature Map

### Cohort Overview Page (`/`)
- **Route:** CohortOverview component
- **Purpose:** Display patient cohort statistics and visualizations
- **Data Needed:** Patient list, aggregated statistics, distribution data
- **Backend Endpoints:** 
  - `GET /api/v1/patients` (for raw data)
  - `GET /api/v1/patients/stats` (for aggregations)
- **Models:** `patients` collection
- **Auth:** None (public dashboard)
- **Notes:** Frontend performs client-side aggregations; backend should provide pre-aggregated stats for performance

### Ghost Patient Radar Page (`/ghost-radar`)
- **Route:** GhostRadar component
- **Purpose:** Display HCO rankings with ghost patient metrics
- **Data Needed:** HCO list with ghost/treated patient counts, filtering by region/state
- **Backend Endpoints:**
  - `GET /api/v1/hcos` (with query params)
  - `GET /api/v1/hcos/stats` (for summary metrics)
- **Models:** `hcos` collection
- **Auth:** None
- **Notes:** Frontend handles CSV export client-side; backend provides filtered data

### Contract Simulator Page (`/simulator`)
- **Route:** ContractSimulator component
- **Purpose:** Model contract scenarios and calculate rebate exposure
- **Data Needed:** Contract templates, patient outcomes, simulation results
- **Backend Endpoints:**
  - `GET /api/v1/contracts/templates`
  - `POST /api/v1/contracts/simulate`
- **Models:** `contract_templates`, `patients` collections
- **Auth:** None
- **Notes:** Simulation logic runs on backend; frontend displays results

### Methodology Page (`/methodology`)
- **Route:** Methodology component
- **Purpose:** Static documentation page
- **Data Needed:** None (static content)
- **Backend Endpoints:** None required
- **Auth:** None
- **Notes:** Purely frontend content

### Chat Widget (Global)
- **Component:** ChatWidget
- **Purpose:** AI assistant for user queries
- **Data Needed:** Message history, bot responses
- **Backend Endpoints:**
  - `POST /api/v1/chat/message`
- **Models:** `chat_sessions` collection
- **Auth:** None (session-based)
- **Notes:** Frontend manages UI state; backend provides contextual responses

---

## 6️⃣ Configuration & ENV Vars

**Required Environment Variables:**
- `APP_ENV` — Environment (development, production)
- `PORT` — HTTP port (default: 8000)
- `MONGODB_URI` — MongoDB Atlas connection string (required)
- `CORS_ORIGINS` — Allowed frontend URLs (comma-separated, e.g., "http://localhost:5173,https://app.biosure.com")

**Optional (for future auth):**
- `JWT_SECRET` — Token signing key (not used in MVP)
- `JWT_EXPIRES_IN` — Token expiry in seconds (not used in MVP)

---

## 7️⃣ Background Work

**Not Required:** This MVP has no background tasks. All operations are synchronous request-response patterns.

---

## 8️⃣ Integrations

**Not Required:** This MVP has no external integrations (no payment gateways, file storage, email services, etc.).

---

## 9️⃣ Testing Strategy (Manual via Frontend)

**Validation Approach:**
- Every task includes a **Manual Test Step** with exact UI action and expected result
- Every task includes a **User Test Prompt** for copy-paste testing
- Testing performed through frontend UI only (no unit tests in MVP)
- After all tasks in a sprint pass → commit and push to `main`
- If any test fails → fix and retest before pushing

**Test Execution Flow:**
1. Complete task implementation
2. Start backend server
3. Open frontend in browser
4. Execute Manual Test Step
5. Verify expected result
6. If pass → proceed to next task
7. If fail → debug, fix, retest
8. After all sprint tasks pass → commit and push to `main`

---

## 🔟 Dynamic Sprint Plan & Backlog

---

## 🧱 S0 – Environment Setup & Frontend Connection

**Objectives:**
- Create FastAPI skeleton with `/api/v1` base path and `/healthz` endpoint
- Connect to MongoDB Atlas using `MONGODB_URI`
- `/healthz` performs DB ping and returns JSON status
- Enable CORS for frontend origin
- Replace dummy API URLs in frontend with real backend URLs
- Initialize Git at root, set default branch to `main`, push to GitHub
- Create single `.gitignore` at root (ignore `__pycache__`, `.env`, `*.pyc`, `venv/`, `.vscode/`)

**User Stories:**
- As a developer, I need a working FastAPI backend that connects to MongoDB Atlas
- As a frontend developer, I need CORS enabled so my app can call the backend
- As a team, we need version control on GitHub with a single `main` branch

**Tasks:**

### Task S0.1: Initialize FastAPI Project Structure
- Create `backend/` directory at project root
- Create `backend/main.py` with FastAPI app instance
- Create `backend/requirements.txt` with dependencies:
  - `fastapi==0.115.0`
  - `uvicorn[standard]==0.32.0`
  - `motor==3.6.0` (async MongoDB driver)
  - `pydantic==2.10.0`
  - `pydantic-settings==2.6.0`
  - `python-dotenv==1.0.1`
- Create `backend/.env.example` with template env vars
- Create `backend/config.py` for settings management using Pydantic BaseSettings

**Manual Test Step:**
- Run `pip install -r backend/requirements.txt` → verify no errors
- Run `python backend/main.py` → verify FastAPI starts on port 8000

**User Test Prompt:**
> "Install dependencies and start the backend. Confirm it runs without errors."

---

### Task S0.2: Implement Health Check Endpoint
- Add `GET /healthz` endpoint in `backend/main.py`
- Endpoint should ping MongoDB Atlas and return connection status
- Response format: `{ "status": "ok", "database": "connected", "timestamp": "ISO8601" }`
- Handle database connection errors gracefully

**Manual Test Step:**
- Start backend → open browser → navigate to `http://localhost:8000/healthz`
- Verify JSON response shows `"database": "connected"`

**User Test Prompt:**
> "Start the backend and visit /healthz. Confirm the database status shows 'connected'."

---

### Task S0.3: Configure MongoDB Atlas Connection
- Create `backend/database.py` with Motor async client setup
- Read `MONGODB_URI` from environment variables
- Implement connection pooling and error handling
- Create database instance named `biosure_db`

**Manual Test Step:**
- Set `MONGODB_URI` in `.env` → start backend → check `/healthz`
- Verify database connection succeeds

**User Test Prompt:**
> "Add your MongoDB Atlas URI to .env and restart the backend. Confirm /healthz shows successful database connection."

---

### Task S0.4: Enable CORS for Frontend
- Install `fastapi-cors` middleware
- Configure CORS to allow frontend origin (from `CORS_ORIGINS` env var)
- Allow credentials, all methods, and common headers

**Manual Test Step:**
- Start backend and frontend → open browser DevTools → check Network tab
- Verify no CORS errors when frontend makes requests

**User Test Prompt:**
> "Start both backend and frontend. Open DevTools Network tab and confirm no CORS errors appear."

---

### Task S0.5: Initialize Git Repository
- Run `git init` at project root (if not already initialized)
- Create `.gitignore` at root with:
  ```
  __pycache__/
  *.pyc
  *.pyo
  .env
  venv/
  .vscode/
  node_modules/
  dist/
  build/
  ```
- Set default branch to `main`: `git branch -M main`
- Create initial commit with project structure
- Create GitHub repository and push

**Manual Test Step:**
- Run `git status` → verify `.env` is ignored
- Run `git log` → verify initial commit exists
- Check GitHub → verify repository exists with `main` branch

**User Test Prompt:**
> "Run 'git status' and confirm .env is not tracked. Check GitHub to verify the repository exists."

---

### Task S0.6: Update Frontend API Base URL
- Locate frontend API configuration (likely in `frontend/src/` or environment file)
- Replace mock data imports with API calls to `http://localhost:8000/api/v1`
- Update `ChatWidget.tsx` to call `/api/v1/chat/message`
- Update `CohortOverview.tsx` to call `/api/v1/patients/stats`
- Update `GhostRadar.tsx` to call `/api/v1/hcos`
- Update `ContractSimulator.tsx` to call `/api/v1/contracts/simulate`

**Manual Test Step:**
- Start backend and frontend → open browser DevTools Network tab
- Navigate through all pages → verify API calls to `localhost:8000/api/v1/*`
- Expect 404 errors (endpoints not implemented yet) but confirm requests are made

**User Test Prompt:**
> "Start both servers and navigate through all pages. In DevTools Network tab, confirm API requests are being made to localhost:8000/api/v1 (even if they return 404)."

---

**Definition of Done:**
- Backend runs locally and connects to MongoDB Atlas
- `/healthz` returns success with database status
- CORS enabled for frontend origin
- Frontend makes API calls to backend (even if 404)
- Git repository initialized with `main` branch
- Single `.gitignore` at root ignoring sensitive files
- Repository pushed to GitHub

**Post-Sprint:**
- Commit all changes with message: "S0: Environment setup and frontend connection"
- Push to `main` branch

---

## 🧩 S1 – Patient Cohort Data Management

**Objectives:**
- Create Pydantic models for Patient data
- Implement database seeding script to populate 847 patients
- Build `GET /api/v1/patients` endpoint with filtering
- Build `GET /api/v1/patients/stats` endpoint with aggregations
- Frontend Cohort Overview displays live data

**User Stories:**
- As a user, I want to view patient cohort statistics on the dashboard
- As a developer, I need patient data in MongoDB to power the frontend

**Tasks:**

### Task S1.1: Create Patient Pydantic Models
- Create `backend/models/patient.py`
- Define `PatientBase`, `PatientCreate`, `PatientInDB`, `PatientResponse` models
- Include all fields from data model specification
- Add field validators for age (18-120), sex (M/F), region, payer_type

**Manual Test Step:**
- Run `python -c "from backend.models.patient import PatientBase; print('Models loaded')"` → verify no errors

**User Test Prompt:**
> "Run the Python import command to verify patient models load without errors."

---

### Task S1.2: Create Database Seeding Script
- Create `backend/scripts/seed_patients.py`
- Generate 847 patient records matching frontend mock data structure
- Use realistic distributions: age 55-80, regions, payer types, outcomes
- Insert into `patients` collection with proper indexes

**Manual Test Step:**
- Run `python backend/scripts/seed_patients.py` → verify "847 patients inserted"
- Check MongoDB Atlas → verify `patients` collection has 847 documents

**User Test Prompt:**
> "Run the seed script and check MongoDB Atlas. Confirm 847 patient documents exist in the patients collection."

---

### Task S1.3: Implement GET /api/v1/patients Endpoint
- Create `backend/routers/patients.py`
- Implement `GET /api/v1/patients` with query params: `region`, `state`, `payer_type`, `min_age`, `max_age`, `limit`, `skip`
- Return paginated patient list
- Add to main app router

**Manual Test Step:**
- Start backend → open browser → navigate to `http://localhost:8000/api/v1/patients?limit=10`
- Verify JSON response with 10 patient records

**User Test Prompt:**
> "Visit /api/v1/patients?limit=10 in your browser. Confirm you see 10 patient records in JSON format."

---

### Task S1.4: Implement GET /api/v1/patients/stats Endpoint
- Create `GET /api/v1/patients/stats` in `backend/routers/patients.py`
- Calculate aggregations:
  - Total patients
  - Average age
  - Male percentage
  - Average prior lines
  - Payer distribution (counts per type)
  - Region distribution (counts per region)
  - Age buckets (50-59, 60-69, 70-79, 80+)
- Use MongoDB aggregation pipeline for performance

**Manual Test Step:**
- Start backend → open browser → navigate to `http://localhost:8000/api/v1/patients/stats`
- Verify JSON response with all aggregated statistics

**User Test Prompt:**
> "Visit /api/v1/patients/stats in your browser. Confirm you see aggregated statistics including total_patients, avg_age, and distribution data."

---

### Task S1.5: Connect Frontend Cohort Overview to Backend
- Update `frontend/src/pages/CohortOverview.tsx`
- Replace `getPatients()` mock call with `fetch('/api/v1/patients/stats')`
- Use React Query or fetch API
- Handle loading and error states

**Manual Test Step:**
- Start backend and frontend → navigate to Cohort Overview page
- Verify statistics cards show live data (847 patients, avg age ~67, etc.)
- Verify charts render with real data

**User Test Prompt:**
> "Open the Cohort Overview page. Confirm the statistics cards show 847 total patients and charts display real data from the backend."

---

**Definition of Done:**
- Patient models defined with validation
- 847 patients seeded in MongoDB Atlas
- `GET /api/v1/patients` returns filtered patient list
- `GET /api/v1/patients/stats` returns aggregated statistics
- Frontend Cohort Overview displays live backend data
- All manual tests pass

**Post-Sprint:**
- Commit all changes with message: "S1: Patient cohort data management"
- Push to `main` branch

---

## 🧱 S2 – HCO & Ghost Patient Analytics

**Objectives:**
- Create Pydantic models for HCO data
- Implement database seeding script for HCOs with ghost patient metrics
- Build `GET /api/v1/hcos` endpoint with filtering and sorting
- Build `GET /api/v1/hcos/stats` endpoint for summary metrics
- Frontend Ghost Radar displays live HCO rankings

**User Stories:**
- As a user, I want to see which HCOs have the most ghost patients
- As a commercial team member, I need to filter HCOs by region and state

**Tasks:**

### Task S2.1: Create HCO Pydantic Models
- Create `backend/models/hco.py`
- Define `HCOBase`, `HCOCreate`, `HCOInDB`, `HCOResponse` models
- Include fields: hco_id, name, state, region, treated_patients, ghost_patients
- Add validators for state codes and non-negative patient counts

**Manual Test Step:**
- Run `python -c "from backend.models.hco import HCOBase; print('HCO models loaded')"` → verify no errors

**User Test Prompt:**
> "Run the Python import command to verify HCO models load without errors."

---

### Task S2.2: Create HCO Seeding Script
- Create `backend/scripts/seed_hcos.py`
- Generate ~50 HCO records based on patient data
- Calculate treated_patients by counting patients per HCO
- Generate ghost_patients (2-5x treated count per HCO)
- Insert into `hcos` collection

**Manual Test Step:**
- Run `python backend/scripts/seed_hcos.py` → verify "~50 HCOs inserted"
- Check MongoDB Atlas → verify `hcos` collection exists with documents

**User Test Prompt:**
> "Run the HCO seed script and check MongoDB Atlas. Confirm the hcos collection has approximately 50 documents."

---

### Task S2.3: Implement GET /api/v1/hcos Endpoint
- Create `backend/routers/hcos.py`
- Implement `GET /api/v1/hcos` with query params: `region`, `state`, `min_ghost_patients`, `sort_by`, `limit`, `skip`
- Support sorting by: ghost_patients (desc), leakage_rate (desc), name (asc)
- Calculate leakage_rate on the fly: `ghost / (ghost + treated) * 100`
- Return paginated HCO list

**Manual Test Step:**
- Start backend → open browser → navigate to `http://localhost:8000/api/v1/hcos?sort_by=ghost_patients&limit=20`
- Verify JSON response with top 20 HCOs sorted by ghost patients

**User Test Prompt:**
> "Visit /api/v1/hcos?sort_by=ghost_patients&limit=20 in your browser. Confirm you see 20 HCOs sorted by ghost patient count."

---

### Task S2.4: Implement GET /api/v1/hcos/stats Endpoint
- Create `GET /api/v1/hcos/stats` in `backend/routers/hcos.py`
- Calculate aggregations:
  - Total ghost patients (sum)
  - Total treated patients (sum)
  - Average ghost patients per HCO
  - Overall leakage rate
  - HCO count
- Use MongoDB aggregation pipeline

**Manual Test Step:**
- Start backend → open browser → navigate to `http://localhost:8000/api/v1/hcos/stats`
- Verify JSON response with summary statistics

**User Test Prompt:**
> "Visit /api/v1/hcos/stats in your browser. Confirm you see aggregated statistics including total_ghost, leakage_rate, and hco_count."

---

### Task S2.5: Connect Frontend Ghost Radar to Backend
- Update `frontend/src/pages/GhostRadar.tsx`
- Replace `getHCOs()` mock call with `fetch('/api/v1/hcos')` and `fetch('/api/v1/hcos/stats')`
- Implement filtering by region and state using query params
- Handle loading and error states

**Manual Test Step:**
- Start backend and frontend → navigate to Ghost Radar page
- Verify summary cards show live data (total ghost patients, leakage rate, etc.)
- Verify HCO table displays with rankings
- Test region/state filters → verify table updates

**User Test Prompt:**
> "Open the Ghost Radar page. Confirm summary cards show live data and the HCO table displays rankings. Test the region filter and verify the table updates."

---

**Definition of Done:**
- HCO models defined with validation
- ~50 HCOs seeded in MongoDB Atlas with ghost patient metrics
- `GET /api/v1/hcos` returns filtered and sorted HCO list
- `GET /api/v1/hcos/stats` returns summary metrics
- Frontend Ghost Radar displays live HCO rankings with filtering
- All manual tests pass

**Post-Sprint:**
- Commit all changes with message: "S2: HCO and ghost patient analytics"
- Push to `main` branch

---

## 🧱 S3 – Contract Simulation Engine

**Objectives:**
- Create Pydantic models for contract templates
- Seed contract templates in MongoDB
- Build `GET /api/v1/contracts/templates` endpoint
- Build `POST /api/v1/contracts/simulate` endpoint with calculation logic
- Frontend Contract Simulator displays live simulation results

**User Stories:**
- As a contracts team member, I want to model different contract scenarios
- As a financial analyst, I need to see rebate exposure calculations

**Tasks:**

### Task S3.1: Create Contract Template Models
- Create `backend/models/contract.py`
- Define `ContractTemplateBase`, `ContractTemplateInDB`, `ContractTemplateResponse` models
- Define `SimulationRequest` and `SimulationResponse` models
- Add validators for rebate_percent (0-100), therapy_price (> 0), time_window (> 0)

**Manual Test Step:**
- Run `python -c "from backend.models.contract import ContractTemplateBase; print('Contract models loaded')"` → verify no errors

**User Test Prompt:**
> "Run the Python import command to verify contract models load without errors."

---

### Task S3.2: Seed Contract Templates
- Create `backend/scripts/seed_contracts.py`
- Insert 3 contract templates:
  - 12-Month Survival Warranty
  - Retreatment Warranty
  - Toxicity Warranty
- Match frontend mock data structure

**Manual Test Step:**
- Run `python backend/scripts/seed_contracts.py` → verify "3 templates inserted"
- Check MongoDB Atlas → verify `contract_templates` collection has 3 documents

**User Test Prompt:**
> "Run the contract seed script and check MongoDB Atlas. Confirm 3 contract templates exist in the contract_templates collection."

---

### Task S3.3: Implement GET /api/v1/contracts/templates Endpoint
- Create `backend/routers/contracts.py`
- Implement `GET /api/v1/contracts/templates`
- Return all contract templates

**Manual Test Step:**
- Start backend → open browser → navigate to `http://localhost:8000/api/v1/contracts/templates`
- Verify JSON response with 3 contract templates

**User Test Prompt:**
> "Visit /api/v1/contracts/templates in your browser. Confirm you see 3 contract templates in JSON format."

---

### Task S3.4: Implement POST /api/v1/contracts/simulate Endpoint
- Create `POST /api/v1/contracts/simulate` in `backend/routers/contracts.py`
- Accept request body: `{ "template_id", "rebate_percent", "therapy_price", "time_window" }`
- Query patients collection based on template outcome_type:
  - "12-month-survival" → count patients where `has_event_12_month = true`
  - "retreatment" → count patients where `has_retreatment_18_month = true`
  - "toxicity" → count patients where `has_toxicity_30_day = true`
- Calculate simulation results:
  - `failure_count` = count of patients matching outcome
  - `success_count` = total_patients - failure_count
  - `failure_rate` = (failure_count / total_patients) * 100
  - `success_rate` = 100 - failure_rate
  - `rebate_per_patient` = (therapy_price * rebate_percent) / 100
  - `total_rebate` = failure_count * rebate_per_patient
  - `low_rebate` = total_rebate * 0.8 (sensitivity: -20%)
  - `high_rebate` = total_rebate * 1.2 (sensitivity: +20%)
  - `avg_rebate_per_treated` = total_rebate / total_patients
- Return SimulationResponse with all calculated fields

**Manual Test Step:**
- Start backend → use Postman or curl to POST to `http://localhost:8000/api/v1/contracts/simulate`
- Request body: `{ "template_id": "survival-12m", "rebate_percent": 50, "therapy_price": 465000, "time_window": 12 }`
- Verify JSON response with all simulation results

**User Test Prompt:**
> "Use Postman to POST a simulation request to /api/v1/contracts/simulate. Confirm you receive complete simulation results including failure_count, total_rebate, and sensitivity ranges."

---

### Task S3.5: Connect Frontend Contract Simulator to Backend
- Update `frontend/src/pages/ContractSimulator.tsx`
- Replace `CONTRACT_TEMPLATES` import with `fetch('/api/v1/contracts/templates')`
- Replace local calculation logic with `POST` to `/api/v1/contracts/simulate`
- Handle loading and error states
- Display returned simulation results

**Manual Test Step:**
- Start backend and frontend → navigate to Contract Simulator page
- Verify template dropdown loads from backend
- Select template, adjust sliders → verify simulation results update
- Verify all metrics display correctly (failure rate, rebate amounts, sensitivity analysis)

**User Test Prompt:**
> "Open the Contract Simulator page. Select a template and adjust parameters. Confirm simulation results update with live backend calculations."

---

**Definition of Done:**
- Contract template models defined with validation
- 3 contract templates seeded in MongoDB Atlas
- `GET /api/v1/contracts/templates` returns all templates
- `POST /api/v1/contracts/simulate` performs calculations and returns results
- Frontend Contract Simulator displays live simulation results
- All manual tests pass

**Post-Sprint:**
- Commit all changes with message: "S3: Contract simulation engine"
- Push to `main` branch

---

## 🧱 S4 – Chat Assistant Backend

**Objectives:**
- Create Pydantic models for chat messages
- Build `POST /api/v1/chat/message` endpoint with contextual responses
- Implement session management (optional persistence)
- Frontend Chat Widget uses live backend API

**User Stories:**
- As a user, I want to ask questions and receive helpful responses
- As a developer, I need the chat to provide contextual answers about the platform

**Tasks:**

### Task S4.1: Create Chat Message Models
- Create `backend/models/chat.py`
- Define `ChatMessageRequest` model with fields: `message` (str), `session_id` (optional str)
- Define `ChatMessageResponse` model with fields: `response` (str), `session_id` (str), `timestamp` (datetime)
- Add validators: message length 1-1000 chars

**Manual Test Step:**
- Run `python -c "from backend.models.chat import ChatMessageRequest; print('Chat models loaded')"` → verify no errors

**User Test Prompt:**
> "Run the Python import command to verify chat models load without errors."

---

### Task S4.2: Implement POST /api/v1/chat/message Endpoint
- Create `backend/routers/chat.py`
- Implement `POST /api/v1/chat/message` endpoint
- Generate contextual responses based on message keywords:
  - "help" → explain available features
  - "cohort" → describe Cohort Overview page
  - "contract" → describe Contract Simulator
  - "ghost" or "radar" → describe Ghost Radar
  - "hello" or "hi" → greeting
  - Default → generic helpful response
- Generate or reuse session_id (UUID)
- Return ChatMessageResponse with response text, session_id, timestamp
- Add router to main app

**Manual Test Step:**
- Start backend → use Postman to POST to `http://localhost:8000/api/v1/chat/message`
- Request body: `{ "message": "help" }`
- Verify JSON response with contextual answer about features

**User Test Prompt:**
> "Use Postman to POST a chat message with 'help'. Confirm you receive a contextual response explaining platform features."

---

### Task S4.3: Connect Frontend Chat Widget to Backend
- Update `frontend/src/components/chat/ChatWidget.tsx`
- Replace `generateBotResponse()` function with API call to `/api/v1/chat/message`
- Send POST request with user message
- Handle loading state during API request
- Handle error states with user-friendly messages
- Store session_id in component state for continuity

**Manual Test Step:**
- Start backend and frontend → open any page → click chat widget button
- Send message "help" → verify bot responds with contextual answer
- Check DevTools Network tab → verify POST to `/api/v1/chat/message`
- Send multiple messages → verify conversation flows naturally

**User Test Prompt:**
> "Open the chat widget and send a message. Confirm you receive a contextual response from the backend. Check Network tab to verify API calls."

---

**Definition of Done:**
- Chat message models defined with validation
- `POST /api/v1/chat/message` returns contextual responses
- Frontend Chat Widget uses live backend API
- Session management works (session_id persists across messages)
- All manual tests pass

**Post-Sprint:**
- Commit all changes with message: "S4: Chat assistant backend"
- Push to `main` branch

---

## ✅ FINAL CHECKLIST

**All Sprints Complete:**
- ✅ S0: Environment setup and frontend connection
- ✅ S1: Patient cohort data management
- ✅ S2: HCO and ghost patient analytics
- ✅ S3: Contract simulation engine
- ✅ S4: Chat assistant backend

**Success Criteria Verification:**
- ✅ All frontend pages display live data from backend
- ✅ Cohort Overview shows accurate patient statistics and charts
- ✅ Ghost Radar displays HCO rankings with filtering
- ✅ Contract Simulator performs calculations and returns results
- ✅ Chat widget sends/receives messages successfully
- ✅ All task-level manual tests passed via UI
- ✅ All sprint code pushed to `main` branch

**Technical Compliance:**
- ✅ FastAPI with Python 3.13 (async)
- ✅ MongoDB Atlas only (no local instance)
- ✅ No Docker containers
- ✅ Manual testing after every task via frontend UI
- ✅ Single-branch Git workflow (`main` only)
- ✅ API base path: `/api/v1/*`
- ✅ Error envelope: `{ "error": "message" }`

---

## 🎯 HANDOVER TO ORCHESTRATOR MODE

**Backend Development Plan Complete**

This document provides a complete, actionable backend development plan for SnapDev V1 (VS Code extension) to build the BioSure Carvykti Outcomes Desk backend.

**Next Steps:**
1. Switch to Orchestrator mode
2. Execute sprints S0 through S4 sequentially
3. Verify each task via manual frontend testing
4. Push completed sprints to `main` branch
5. Deliver fully functional backend connected to frontend

**Key Deliverables:**
- FastAPI backend with 10+ REST endpoints
- MongoDB Atlas database with 4 collections
- 847 patient records + 50 HCO records + 3 contract templates
- Full integration with existing frontend
- Chat assistant with contextual responses
- Complete manual test coverage via UI

---

**END OF BACKEND DEVELOPMENT PLAN**
