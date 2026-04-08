# AEROS Geospatial Monorepo

This monorepo contains the code for the AEROS geospatial application.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose

## Quick Start

### 1. Database

Start the PostGIS database:
```bash
docker compose up -d
```

### 2. Backend

Navigate to the `backend` directory, install requirements and start the server:

```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/MacOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
The FastAPI backend will be available at `http://localhost:8000`.

### 3. Frontend

Navigate to the `frontend` directory, install dependencies and start Vite:

```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:5173`.
