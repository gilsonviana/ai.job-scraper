# Architecture Overview

## System Design

### Components

**Job Scraper** processes job postings from HTML and PDF sources, extracting structured data using NLP.

- **Frontend:** React SPA for user interaction (upload PDF/URL)
- **Backend:** FastAPI REST API for job extraction
- **NLP Engine:** spaCy + transformers for entity extraction
- **Persistence:** SQLite for job records and extraction history

### Data Flow

```
User Input (URL/PDF)
    ↓
[Frontend] JobForm Component
    ↓
HTTP POST → /api/extract
    ↓
[Backend] FastAPI Route Handler
    ↓
{services/extraction.py} Parse + Extract
    ↓
{services/nlp.py} Entity Recognition
    ↓
Pydantic Validation
    ↓
[Database] Store Results
    ↓
JSON Response → [Frontend] Display Results
```

### Key Abstractions

1. **Extraction Service** — Coordinates PDF parsing and NLP
2. **NLP Service** — Encapsulates spaCy + transformers logic
3. **Database Models** — SQLAlchemy ORM for persistence
4. **Pydantic Schemas** — Request/response validation

---

## API Endpoints

Fully specified in `/specs/api.md`:

- `POST /extract` — Extract job data from URL or PDF (multipart/form-data or JSON)
- `GET /extractions` — List all extractions with pagination and filtering
- `GET /extractions/:id` — Retrieve a single extraction by ID

---

## Database Schema

Fully specified in `/specs/data-model.md`. Key table: **job_extractions**

Fields include: id, source_type, source_url, job_title, required_stack, location, salary_min/max, seniority_level, remote_policy, key_responsibilities, nice_to_have, confidence_score, created_at, updated_at, plus indexes on created_at and source_type.

---

## Error Handling

- Server validation errors (400) include field-level Pydantic errors
- Server exceptions (500) return generic message
- Client displays errors in modal/toast with retry option
