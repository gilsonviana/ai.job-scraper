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
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models import Base

class JobExtraction(Base):
    __tablename__ = "job_extractions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_type = Column(String)
    source_url = Column(String, nullable=True)
    source_content = Column(String, nullable=True)
    job_title = Column(String)
    required_stack = Column(JSON)
    location = Column(String)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    # ... other fields
    created_at = Column(DateTime, server_default=func.now())
```
