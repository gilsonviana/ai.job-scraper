import pytest
from pydantic import ValidationError

from app.schemas.job import (
    JobExtractionRequest,
    JobExtractionResponse,
    ErrorDetail,
    ExtractionListResponse,
)


class TestJobExtractionRequest:
    def test_url_source_valid(self):
        data = {"source": "url", "url": "https://example.com/job-posting"}
        req = JobExtractionRequest(**data)
        assert req.source == "url"
        assert str(req.url) == "https://example.com/job-posting"

    def test_url_source_missing_url(self):
        data = {"source": "url"}
        with pytest.raises(ValidationError) as exc_info:
            JobExtractionRequest(**data)
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert errors[0]["msg"] == "Value error, url is required when source is 'url'"

    def test_pdf_source_valid(self):
        data = {"source": "pdf"}
        req = JobExtractionRequest(**data)
        assert req.source == "pdf"
        assert req.url is None

    def test_invalid_source(self):
        data = {"source": "ftp"}
        with pytest.raises(ValidationError) as exc_info:
            JobExtractionRequest(**data)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("source",) for e in errors)

    def test_invalid_url_format(self):
        data = {"source": "url", "url": "not-a-valid-url"}
        with pytest.raises(ValidationError) as exc_info:
            JobExtractionRequest(**data)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("url",) for e in errors)


class TestJobExtractionResponse:
    def test_valid_response(self):
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "job_title": "Senior Backend Engineer",
            "required_stack": ["Python", "PostgreSQL"],
            "location": "San Francisco, CA",
            "salary_min": 150000,
            "salary_max": 200000,
            "availability": "Immediately",
            "seniority_level": "Senior",
            "remote_policy": "Hybrid",
            "key_responsibilities": ["Design APIs", "Lead architecture"],
            "nice_to_have": ["Kubernetes"],
            "confidence_score": 0.92,
            "created_at": "2026-07-09T12:34:56Z",
        }
        resp = JobExtractionResponse(**data)
        assert resp.id == "550e8400-e29b-41d4-a716-446655440000"
        assert resp.job_title == "Senior Backend Engineer"
        assert resp.confidence_score == 0.92

    def test_response_optional_fields(self):
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "job_title": "Engineer",
            "required_stack": ["Python"],
            "location": "Remote",
            "key_responsibilities": [],
            "nice_to_have": [],
            "confidence_score": 0.5,
            "created_at": "2026-07-09T12:34:56Z",
        }
        resp = JobExtractionResponse(**data)
        assert resp.salary_min is None
        assert resp.seniority_level is None
        assert resp.remote_policy is None


class TestErrorDetail:
    def test_error_with_details(self):
        err = ErrorDetail(
            code="INVALID_SOURCE",
            message="source must be 'url' or 'pdf'",
            details={"source": "ftp"},
        )
        assert err.code == "INVALID_SOURCE"
        assert err.details == {"source": "ftp"}

    def test_error_without_details(self):
        err = ErrorDetail(code="NOT_FOUND", message="Extraction not found")
        assert err.code == "NOT_FOUND"
        assert err.details == {}


class TestExtractionListResponse:
    def test_valid_list_response(self):
        data = {
            "items": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "job_title": "Senior Backend Engineer",
                    "required_stack": ["Python"],
                    "location": "Remote",
                    "salary_min": 150000,
                    "salary_max": 200000,
                    "confidence_score": 0.92,
                    "created_at": "2026-07-09T12:34:56Z",
                }
            ],
            "total": 1,
            "limit": 20,
            "offset": 0,
        }
        resp = ExtractionListResponse(**data)
        assert resp.total == 1
        assert len(resp.items) == 1
        assert resp.limit == 20
        assert resp.offset == 0
