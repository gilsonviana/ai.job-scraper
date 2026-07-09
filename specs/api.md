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

## Endpoints (Placeholder)

### POST /extract

Extract job data from a URL or PDF file.

**Request:**

```json
{
  "source": "url | pdf",
  "url": "https://...",
  "file": "base64-encoded PDF (if pdf)"
}
```

**Response (200):**

```json
{
  "data": {
    "id": "uuid",
    "job_title": "Senior Developer",
    "required_stack": ["Python", "React"],
    "location": "Remote",
    "salary_min": 100000,
    "salary_max": 150000,
    "availability": "Immediate"
  }
}
```

**Error (400):**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "url is required when source is 'url'"
  }
}
```

---

## Rate Limiting

- **Limit:** 100 requests per IP per minute
- **Response Header:** `X-RateLimit-Remaining`

---

## Status Codes

- `200` — Success
- `400` — Validation error (malformed request, missing fields)
- `500` — Server error (unhandled exception)
