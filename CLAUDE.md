# Job Scraper Project Constitution

**Project:** AI-powered Job Description Scraper  
**Purpose:** Extract structured information from job postings (HTML/PDF) using NLP  
**Monorepo:** `/server` (Python/FastAPI) + `/client` (React/TypeScript) with pnpm workspaces

---

## Tech Stack

### Server
- **Runtime:** Python 3.11+
- **Framework:** FastAPI (async)
- **Validation:** Pydantic v2
- **ORM:** SQLAlchemy with SQLite
- **NLP:** spaCy + Hugging Face transformers
- **Testing:** pytest + pytest-cov

### Client
- **Runtime:** Node.js (pnpm)
- **UI Framework:** React 18+ (functional components only, no classes)
- **Language:** TypeScript (strict mode)
- **Build:** Vite
- **Styling:** TailwindCSS
- **UI Components:** Headless UI (all complex controls come from here)
- **Forms:** React Hook Form + Zod validation
- **Testing:** Vitest + React Testing Library
- **Linting:** ESLint (react, react-hooks, import plugins) + Prettier

---

## Architecture & Core Rules

### API Design
- **Protocol:** REST-only, JSON payloads
- **Response Format:** All endpoints return `{data?: T, error?: {code: string, message: string}}`
- **Response Time SLA:** <500ms (show client-side loaders for async work)
- **Status Codes:**
  - `200` — success
  - `400` — validation error (include field-level messages from Pydantic)
  - `500` — unhandled exception (generic "Internal error", no stack traces to client)

### Database
- **Engine:** SQLite (single-file database)
- **Access:** SQLAlchemy ORM only — **zero raw SQL**
- **Models Location:** `/server/app/models/` (one file per model or grouped by domain)
- **Migrations:** (Optional — track via `alembic/` if needed; if simple, version with code)

### Component Architecture (React)
- **UI Build Blocks:** Headless UI components only (no custom `<div>` controls for forms, dropdowns, modals, etc.)
- **Single Source of Truth:** `/client/src/styles/theme.ts` contains all colors, fonts, spacing, breakpoints
- **Component Pattern:**
  - Functional components with hooks only (no class components)
  - Custom hooks extracted to `/client/src/hooks/`
  - Props-based composition
  - One component per folder: `/client/src/components/ComponentName/ComponentName.tsx`
  - Type definitions in sibling file: `/client/src/components/ComponentName/types.ts`
  - Barrel export: `/client/src/components/ComponentName/index.ts`

### State Management
- **Global State:** React Context API
- **Form State:** React Hook Form only (no Redux, Zustand, or other form libs)
- **Data Fetching:** Async/await in effect hooks or custom hooks

### Error Handling
- **Server Validation:** Pydantic catches 100% of malformed requests → 400 with field-level messages
- **Server Exceptions:** Unhandled errors → 500 with generic message only (no stack traces exposed)
- **Client Async:** All API calls show spinner/loading state; display errors via toast/modal with user-friendly copy
- **Client Forms:** Zod validates before submission; show field-level errors inline

---

## Security & Data Validation

### Input Validation (Required)
- **Server:** Pydantic validates 100% of incoming requests — no exceptions
- **Client:** Zod validates all form inputs before submission
- **Both:** Sanitize/escape text before storage (prevent injection attacks)

### Rate Limiting
- **Limit:** 100 requests per IP per minute
- **Implementation:** FastAPI middleware (e.g., `slowapi` or custom)

### Authentication
- **Current:** None — public API (add auth layer before production use)

---

## Code Conventions

### Python (/server)
- **Formatter:** Black (line length: 88)
- **Import Order:** isort
- **Naming:** snake_case (files, variables, functions)
- **Docstrings:** Google style on all public functions
- **Type Hints:** Use for function signatures (Pydantic models for API validation)

### JavaScript/TypeScript (/client)
- **Formatter:** Prettier (print width: 80, semi: true, single quotes)
- **Linter:** ESLint with mandatory rules:
  - `react/exhaustive-deps` — catch missing hook dependencies
  - `react-hooks/rules-of-hooks` — enforce Hook rules
- **Naming:**
  - `camelCase` — variables, functions, files (except components)
  - `PascalCase` — React components only
- **Type Safety:**
  - Strict mode **mandatory** — no `any` type
  - Declare types in `types.ts` next to the component/hook/service
  - Export via `index.ts` barrel files
- **File Structure:**
  ```
  src/
    components/
      ComponentName/
        ComponentName.tsx
        types.ts
        index.ts
    hooks/
      useCustomHook.ts
      useCustomHook/
        types.ts
        index.ts
    services/
      apiService.ts
      types.ts
      index.ts
    pages/
      HomePage.tsx
    styles/
      theme.ts
      globals.css
    utils/
      helpers.ts
  ```

---

## Testing Requirements

### Server (pytest)
- **Coverage Target:** 80%+ for `/app` and `/schemas`
- **Scope:** All FastAPI endpoints + Pydantic model validation
- **Tools:** pytest, pytest-cov
- **File Location:** `/server/tests/` (mirror `/app` structure)

### Client (Vitest + React Testing Library)
- **Coverage Target:** 50%+ minimum for components
- **Approach:** Behavioral tests (no snapshot tests — prefer assertions on rendered output)
- **Tools:** Vitest, React Testing Library, `@testing-library/user-event`
- **File Location:** Colocate `.test.ts(x)` files next to source

---

## Non-Negotiables

1. **Database:** All queries use SQLAlchemy ORM — zero raw SQL strings
2. **API Resilience:** Every API call includes error handling + retry logic (max 3 attempts, exponential backoff)
3. **Code Organization:**
   - Pydantic models → `/server/app/schemas/`
   - SQLAlchemy models → `/server/app/models/`
   - React components → `/client/src/components/`
   - Pages → `/client/src/pages/`
4. **Dependencies:** No external npm/pip packages without justification in PR/commit (keep surface minimal)
5. **Version Control:** All specs, architecture decisions, and runbooks live in `/specs/`
6. **Environment Variables:** Use `.env` files (python-dotenv on server, Vite env on client); never hardcode secrets

---

## Project Structure

```
ai.job-scraper/
├── server/
│   ├── app/
│   │   ├── models/
│   │   │   ├── job.py
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── job.py
│   │   │   └── __init__.py
│   │   ├── routes/
│   │   │   ├── job.py
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── extraction.py
│   │   │   ├── nlp.py
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   └── pdf_parser.py
│   │   ├── database.py
│   │   └── config.py
│   ├── tests/
│   │   ├── test_routes/
│   │   ├── test_schemas/
│   │   └── test_services/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── client/
│   ├── src/
│   │   ├── components/
│   │   │   ├── JobForm/
│   │   │   ├── ResultsDisplay/
│   │   │   └── ...
│   │   ├── pages/
│   │   │   └── HomePage.tsx
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── styles/
│   │   │   ├── theme.ts
│   │   │   └── globals.css
│   │   ├── utils/
│   │   └── App.tsx
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── package.json
│   └── tsconfig.json
├── specs/
│   ├── architecture.md
│   ├── api.md
│   └── data-model.md
├── pnpm-workspace.yaml
├── .env.example
└── CLAUDE.md (this file)
```

---

## Key Development Workflows

### Running the Project Locally
- **Server:** `cd server && python main.py` (FastAPI auto-reload on port 8000)
- **Client:** `cd client && pnpm dev` (Vite dev server on port 5173)
- **Database:** SQLite file created automatically on first run (`server/data.db` or similar)

### Adding a New Feature
1. **Spec it** → Write user story + API contract in `/specs/`
2. **Backend:** Add Pydantic model (schema), SQLAlchemy model (persistence), route handler, service logic
3. **Backend Tests:** Unit tests for model validation, route behavior, service extraction
4. **Frontend:** Add component(s) in `/client/src/components/`, fetch data via custom hook, display results
5. **Frontend Tests:** Test component rendering + user interactions (form submission, error states)
6. **PR:** Link to spec; reference test coverage

### Before Committing
- [ ] Run server tests: `pytest --cov=app tests/`
- [ ] Run client tests: `pnpm test --coverage`
- [ ] Format Python: `black . && isort .`
- [ ] Format JS/TS: `pnpm run format` (Prettier)
- [ ] Lint JS/TS: `pnpm run lint` (ESLint)
- [ ] Check TypeScript: `pnpm run type-check`

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| React Context instead of Redux | Simpler for this app's scope; no deeply nested state |
| Headless UI only | Consistency, accessibility built-in, minimal CSS |
| SQLite over PostgreSQL | Single-file deployment, no external DB server needed |
| Pydantic v2 | Validation, serialization, and type hints out of the box |
| spaCy + transformers for NLP | Pre-trained models, fast inference, no training needed |

---

## Future Considerations (Out of Scope Now)

- [ ] Add authentication (JWT) when multi-user support needed
- [ ] Migrate to PostgreSQL if single-file DB becomes bottleneck
- [ ] Add job posting persistence (save, filter, export)
- [ ] Implement webhooks for job feed integration
- [ ] Add analytics/monitoring (Sentry, LogRocket)

---

**Last Updated:** 2026-07-09  
**Maintainer:** Job Scraper Team
