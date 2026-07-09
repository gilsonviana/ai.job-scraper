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

## API Endpoints (to be defined)

- `POST /extract` — Extract job data from URL or PDF
- `GET /extractions/:id` — Retrieve saved extraction
- `GET /extractions` — List all extractions

---

## Database Schema (to be defined)

**Job Extractions Table**
- id (UUID)
- source_type (enum: url | pdf)
- source_url (nullable)
- job_title
- required_stack (array)
- location
- salary_min, salary_max
- availability
- created_at

---

## Error Handling

- Server validation errors (400) include field-level Pydantic errors
- Server exceptions (500) return generic message
- Client displays errors in modal/toast with retry option
