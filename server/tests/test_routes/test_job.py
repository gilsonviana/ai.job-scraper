import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import Base

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Import app after setting up the override
from main import app

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestExtractEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_extract_missing_source(self):
        response = client.post("/api/extract")
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_SOURCE"

    def test_extract_invalid_source(self):
        response = client.post(
            "/api/extract", data={"source": "ftp"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_SOURCE"

    def test_extract_url_missing_url(self):
        response = client.post(
            "/api/extract", data={"source": "url"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "MISSING_URL"

    def test_extract_url_invalid_format(self):
        response = client.post(
            "/api/extract", data={"source": "url", "url": "not-a-url"}
        )
        assert response.status_code == 400

    def test_extract_pdf_missing_file(self):
        response = client.post(
            "/api/extract", data={"source": "pdf"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "MISSING_FILE"

    def test_extract_pdf_invalid_type(self):
        response = client.post(
            "/api/extract",
            data={"source": "pdf"},
            files={"file": ("test.txt", b"not a pdf", "text/plain")},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"

    def test_extract_pdf_too_large(self):
        # Create a file larger than max size
        large_pdf = b"PDF" * (1024 * 1024 * 11)  # 33MB
        response = client.post(
            "/api/extract",
            data={"source": "pdf"},
            files={"file": ("test.pdf", large_pdf, "application/pdf")},
        )
        assert response.status_code == 413
        data = response.json()
        assert data["error"]["code"] == "FILE_TOO_LARGE"


class TestListExtractionsEndpoint:
    def test_list_extractions_empty(self):
        response = client.get("/api/extractions")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []
        assert data["data"]["limit"] == 20
        assert data["data"]["offset"] == 0

    def test_list_extractions_with_invalid_limit(self):
        response = client.get("/api/extractions?limit=101")
        assert response.status_code == 422  # Validation error

    def test_list_extractions_with_invalid_source_type(self):
        response = client.get("/api/extractions?source_type=invalid")
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_list_extractions_with_valid_source_type(self):
        response = client.get("/api/extractions?source_type=url")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data["data"]


class TestGetExtractionEndpoint:
    def test_get_nonexistent_extraction(self):
        response = client.get("/api/extractions/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
