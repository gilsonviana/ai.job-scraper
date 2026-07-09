# Data Model

## Job Extraction

### Extracted Fields

- **job_title** (string) — Role name (e.g., "Senior Backend Engineer")
- **required_stack** (array[string]) — Technologies/tools required
  - e.g., ["Python", "PostgreSQL", "Docker", "AWS"]
- **location** (string) — Work location (e.g., "Remote", "San Francisco, CA")
- **salary_range** (object)
  - `min` (number, nullable) — Minimum annual salary in USD
  - `max` (number, nullable) — Maximum annual salary in USD
- **availability** (string, nullable) — Start date or availability (e.g., "Immediately", "2 weeks notice")
- **seniority_level** (string, nullable) — Level inferred from JD (e.g., "Senior", "Junior", "Mid")
- **remote_policy** (string, nullable) — Remote, On-site, Hybrid
- **key_responsibilities** (array[string]) — Extracted top 3-5 responsibilities
- **nice_to_have** (array[string]) — Optional skills or experience

### Storage Model

**Table: job_extractions**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| source_type | ENUM | 'url' \| 'pdf' |
| source_url | VARCHAR | Nullable if source is PDF upload |
| source_content | TEXT | Raw HTML/PDF content (for audit trail) |
| job_title | VARCHAR | |
| required_stack | JSON | Array of strings |
| location | VARCHAR | |
| salary_min | INT | Nullable |
| salary_max | INT | Nullable |
| availability | VARCHAR | Nullable |
| seniority_level | VARCHAR | Nullable |
| remote_policy | VARCHAR | Nullable |
| key_responsibilities | JSON | Array of strings |
| nice_to_have | JSON | Array of strings |
| confidence_score | FLOAT | 0-1, how confident the extraction is |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

---

## NLP Extraction Pipeline

### Models Used

| Field | Model | Library | Notes |
|-------|-------|---------|-------|
| job_title | Named Entity Recognition (en_core_web_lg) | spaCy | Entity type: PERSON (in job context) or uses custom patterns |
| required_stack | Tech stack classifier | Hugging Face distilbert | Fine-tuned to recognize technology names and tools |
| location | Named Entity Recognition (en_core_web_lg) | spaCy | Entity types: GPE (geopolitical), LOC (location) |
| salary_range | Regex + NER | spaCy + custom patterns | Pattern matching for currency symbols and number ranges |
| seniority_level | Zero-shot classification | Hugging Face BART (facebook/bart-large-mnli) | Labels: "Junior", "Mid", "Senior", "Lead", "Not specified" |
| remote_policy | Zero-shot classification | Hugging Face BART | Labels: "Remote", "On-site", "Hybrid", "Not specified" |
| key_responsibilities | Extractive summarization | Hugging Face transformers (facebook/bart-large-cnn) | Top 3–5 sentences by importance |

### Confidence Scoring

- **Required fields** (job_title, location): If confidence < 0.7, still return but flag as uncertain in response
- **Optional fields** (salary, seniority, remote): If confidence < 0.5, return `null` instead of uncertain value
- **Overall confidence_score**: Weighted average of all field confidences, clamped to [0.0, 1.0]

### Performance Constraints

- **Timeout:** 30 seconds per extraction (abort and return 500 EXTRACTION_FAILED if exceeded)
- **Max input size:** 50KB of text (51,200 bytes)
- **Concurrency:** Single-worker by default (one extraction at a time); scale with Uvicorn `--workers` if needed
- **Memory:** Models loaded once on startup (spaCy en_core_web_lg ~40MB, BART ~1.6GB)

---

## Pydantic Schema (server/app/schemas/job.py)

```python
from pydantic import BaseModel, Field
from typing import Optional

class JobExtractionRequest(BaseModel):
    source: Literal["url", "pdf"]
    url: Optional[str] = Field(None, description="URL to job posting")
    # file: bytes  # For PDF upload (handled via multipart/form-data)

class JobExtractionResponse(BaseModel):
    id: str
    job_title: str
    required_stack: list[str]
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    availability: Optional[str]
    seniority_level: Optional[str]
    remote_policy: Optional[str]
    key_responsibilities: list[str]
    nice_to_have: list[str]
    confidence_score: float
    created_at: str
```

---

## SQLAlchemy Model (server/app/models/job.py)

```python
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Index, Uuid, func
from app.models import Base
import uuid

class JobExtraction(Base):
    __tablename__ = "job_extractions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    source_type = Column(String(10), nullable=False)  # "url" or "pdf"
    source_url = Column(String(2048), nullable=True)
    source_content = Column(String(50000), nullable=True)  # Raw HTML/PDF text
    
    # Extracted fields
    job_title = Column(String(255), nullable=False)
    required_stack = Column(JSON, nullable=False, default=list)
    location = Column(String(255), nullable=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    availability = Column(String(255), nullable=True)
    seniority_level = Column(String(100), nullable=True)
    remote_policy = Column(String(50), nullable=True)
    key_responsibilities = Column(JSON, nullable=False, default=list)
    nice_to_have = Column(JSON, nullable=False, default=list)
    
    confidence_score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_created_at', 'created_at'),
        Index('ix_source_type', 'source_type'),
    )
```
