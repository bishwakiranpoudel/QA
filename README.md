# SAP TestOS - Intelligent SAP Testing Platform

A B2B SaaS platform for SAP consultancies featuring three integrated modules:
- **Pre-Sales Matchmaker** - Hybrid search for talent matching and SoW generation
- **Execution VLM Agent** - Multimodal DOM/vision for SAP Fiori test automation  
- **Operations Self-Healing Engine** - AST-based surgical patching for test maintenance

## Architecture

```
/workspace
├── backend/          # FastAPI Python backend (Git repo A)
│   ├── app/
│   │   ├── routers/  # API endpoints
│   │   ├── services/ # Business logic
│   │   └── models/   # Database models
│   └── run.sh        # Startup script
│
└── frontend/         # React + Vite frontend (Git repo B)
    ├── src/
    │   ├── pages/    # Module pages
    │   ├── services/ # API client
    │   └── components/
    └── package.json
```

## Quick Start

### Backend (Port 8000)
```bash
cd backend
./run.sh
# API docs at http://localhost:8000/docs
```

### Frontend (Port 3000)
```bash
cd frontend
npm install
npm run dev
# App at http://localhost:3000
```

## Features

### 1. Matchmaker Module
- Hybrid search (semantic + keyword) for SAP consultants
- Auto-generate professional Statements of Work
- Support for all SAP modules (FICO, MM, SD, PP, S/4HANA, etc.)

### 2. VLM Agent Module
- Convert manual test cases to Playwright scripts
- Hybrid DOM + Vision analysis for SAP Fiori
- Supports data-testid, aria-label selectors

### 3. Self-Healing Module
- Automatically fix broken test selectors
- AST-based surgical code patching
- Reduces test maintenance by 70%

## Tech Stack

**Backend:**
- FastAPI (Python)
- SQLite (MVP) / PostgreSQL (production)
- OpenAI/Claude APIs (optional - has fallbacks)

**Frontend:**
- React 18
- Vite
- React Router
- Axios

## Free Services Used
- SQLite for database (no setup required)
- Fallback logic works without API keys
- Optional: OpenAI free tier, Anthropic free tier

## License
MIT
