# API Specification

## Base URL

`http://localhost:8000/api`

## Response Format

All endpoints return JSON with this structure:

```json
{
  "data": {},
  "error": null
}
```

Or on error:

```json
{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": {}
  }
}
```

---

## Endpoints

### POST /extract

Extract job data from a URL or uploaded PDF file.

#### Request: URL-based extraction (application/json)

```json
{
  "source": "url",
  "url": "https://example.com/job-posting"
}
```

#### Request: PDF upload (multipart/form-data)

```
POST /extract
Content-Type: multipart/form-data

source=pdf
file=<binary PDF data>
```

**Constraints:**
- `source` — required, must be "url" or "pdf"
- `url` — required when source is "url"; must be a valid HTTP(S) URL
- `file` — required when source is "pdf"; must be a valid PDF file ≤ 10MB

#### Response (200)

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "job_title": "Senior Backend Engineer",
    "required_stack": ["Python", "PostgreSQL", "Docker", "AWS"],
    "location": "San Francisco, CA",
    "salary_min": 150000,
    "salary_max": 200000,
    "availability": "Immediately",
    "seniority_level": "Senior",
    "remote_policy": "Hybrid",
    "key_responsibilities": ["Design APIs", "Lead architecture", "Mentor junior engineers"],
    "nice_to_have": ["Kubernetes", "gRPC", "Rust"],
    "confidence_score": 0.92,
    "created_at": "2026-07-09T12:34:56Z"
  }
}
```

#### Errors

See [Error Codes Reference](#error-codes-reference) for complete list.

Common examples:

**400 — INVALID_SOURCE**
```json
{
  "error": {
    "code": "INVALID_SOURCE",
    "message": "source must be 'url' or 'pdf'",
    "details": { "source": "ftp" }
  }
}
```

**400 — MISSING_URL**
```json
{
  "error": {
    "code": "MISSING_URL",
    "message": "url is required when source is 'url'",
    "details": {}
  }
}
```

**413 — FILE_TOO_LARGE**
```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "PDF file exceeds maximum size of 10MB",
    "details": { "max_size": 10485760, "provided_size": 12000000 }
  }
}
```

**422 — PARSE_FAILED**
```json
{
  "error": {
    "code": "PARSE_FAILED",
    "message": "Could not extract text from PDF",
    "details": { "reason": "Corrupted or unsupported PDF format" }
  }
}
```

**500 — EXTRACTION_FAILED**
```json
{
  "error": {
    "code": "EXTRACTION_FAILED",
    "message": "NLP extraction timed out or failed",
    "details": {}
  }
}
```

---

### GET /extractions

List all job extractions with optional filtering and pagination.

**Query Parameters:**

| Parameter | Type | Default | Max | Notes |
|-----------|------|---------|-----|-------|
| `limit` | int | 20 | 100 | Number of results per page |
| `offset` | int | 0 | — | Number of results to skip |
| `source_type` | string | null | — | Filter by "url" or "pdf"; null = all |

**Response (200):**

```json
{
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "job_title": "Senior Backend Engineer",
        "required_stack": ["Python", "PostgreSQL"],
        "location": "Remote",
        "salary_min": 150000,
        "salary_max": 200000,
        "confidence_score": 0.92,
        "created_at": "2026-07-09T12:34:56Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "job_title": "Frontend Engineer",
        "required_stack": ["React", "TypeScript"],
        "location": "San Francisco, CA",
        "salary_min": 120000,
        "salary_max": 160000,
        "confidence_score": 0.88,
        "created_at": "2026-07-09T10:20:15Z"
      }
    ],
    "total": 142,
    "limit": 20,
    "offset": 0
  }
}
```

**Errors:**
- `400` — Invalid query parameters (e.g., limit > 100, invalid source_type)

---

### GET /extractions/:id

Retrieve a single extraction by ID.

**Path Parameters:**

| Parameter | Type | Notes |
|-----------|------|-------|
| `id` | UUID | Extraction ID |

**Response (200):**

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "source_type": "url",
    "source_url": "https://example.com/job-posting",
    "job_title": "Senior Backend Engineer",
    "required_stack": ["Python", "PostgreSQL", "Docker", "AWS"],
    "location": "San Francisco, CA",
    "salary_min": 150000,
    "salary_max": 200000,
    "availability": "Immediately",
    "seniority_level": "Senior",
    "remote_policy": "Hybrid",
    "key_responsibilities": ["Design APIs", "Lead architecture", "Mentor junior engineers"],
    "nice_to_have": ["Kubernetes", "gRPC", "Rust"],
    "confidence_score": 0.92,
    "created_at": "2026-07-09T12:34:56Z"
  }
}
```

**Error (404) — NOT_FOUND:**

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Extraction not found",
    "details": { "id": "550e8400-e29b-41d4-a716-446655440099" }
  }
}
```

---

## Error Codes Reference

| Code | HTTP | Description | When It Occurs |
|------|------|-------------|-----------------|
| VALIDATION_ERROR | 400 | Generic validation failure | Malformed JSON, missing required fields not covered by specific codes |
| INVALID_SOURCE | 400 | source must be "url" or "pdf" | source field is not one of allowed values |
| MISSING_URL | 400 | URL required when source="url" | source is "url" but url field is empty or missing |
| MISSING_FILE | 400 | PDF file required when source="pdf" | source is "pdf" but file is not provided |
| INVALID_FILE_TYPE | 400 | File must be a valid PDF | File provided is not a PDF (wrong MIME type or format) |
| FILE_TOO_LARGE | 413 | File exceeds maximum size (10MB) | PDF file size > 10,485,760 bytes |
| PARSE_FAILED | 422 | Failed to extract text from file | PDF is corrupted, password-protected, or unsupported format |
| EXTRACTION_FAILED | 500 | NLP extraction timed out or errored | Model inference took > 30s, out of memory, or unexpected error |
| NOT_FOUND | 404 | Resource not found | GET /extractions/:id with non-existent ID |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests | More than 100 requests from same IP in 60-second window |
| INTERNAL_ERROR | 500 | Unhandled server error | Unexpected bug in backend not covered by specific codes |

---

## Rate Limiting

- **Limit:** 100 requests per IP per minute

**Response Headers:**
- `X-RateLimit-Limit: 100` — Total requests allowed per window
- `X-RateLimit-Remaining: 87` — Requests remaining in current window
- `X-RateLimit-Reset: 1625097600` — Unix timestamp when the limit resets

**When Limit Exceeded (429):**

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "details": {
      "retry_after": 45
    }
  }
}
```

Response also includes rate-limit headers above.

---

## Resilience & Retry Strategy

**Client-Side Retries** (to be implemented in `/client/src/services/apiClient.ts`):

- **Retryable errors:** 408 (timeout), 429 (rate limit), 5xx (server error)
- **Non-retryable:** 4xx except 408 and 429
- **Backoff:** Exponential — 1s, 2s, 4s (2^attempt)
- **Max attempts:** 3 retries (4 total requests if first fails immediately)
- **Client timeout:** 35 seconds per request (5s buffer above server 30s timeout)

**Server-Side Handling:**
- If extraction takes > 30 seconds, abort and return 500 EXTRACTION_FAILED
- Client will retry up to 3 times per strategy above
- Rate limiter applies to retries; each attempt counts

---

## Environment Variables

See `server/.env.example` for the complete list. Key variables:

| Variable | Example | Notes |
|----------|---------|-------|
| `NLP_MODEL_SPACY` | en_core_web_lg | spaCy model for NER |
| `NLP_MODEL_HF_STACK` | distilbert-base-uncased-finetuned-sst-2-english | Hugging Face model for tech stack detection |
| `NLP_MODEL_HF_CLASSIFIER` | facebook/bart-large-mnli | Zero-shot classifier for seniority/remote policy |
| `CONFIDENCE_THRESHOLD` | 0.7 | Minimum confidence for required fields |
| `MAX_INPUT_SIZE` | 51200 | Max bytes of text to process (50KB) |
| `EXTRACTION_TIMEOUT` | 30 | Timeout in seconds for NLP pipeline |
| `MAX_PDF_SIZE` | 10485760 | Max PDF file size in bytes (10MB) |
| `RATE_LIMIT_REQUESTS` | 100 | Requests allowed per window |
| `RATE_LIMIT_WINDOW` | 60 | Rate limit window in seconds |

---

## Status Codes Summary

- `200` — Success
- `400` — Validation/client error (VALIDATION_ERROR, INVALID_SOURCE, MISSING_URL, MISSING_FILE, INVALID_FILE_TYPE)
- `404` — NOT_FOUND
- `408` — Request timeout (client-side, triggers retry)
- `413` — FILE_TOO_LARGE
- `422` — PARSE_FAILED
- `429` — RATE_LIMIT_EXCEEDED
- `500` — Server error (EXTRACTION_FAILED, INTERNAL_ERROR)
