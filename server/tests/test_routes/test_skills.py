import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import Base
from app.models.job import JobExtraction
from app.services.skills_analytics import _cache

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_skills.db"
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


from main import app

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    _cache.clear()


def test_skills_summary_empty_database():
    response = client.get("/api/skills/summary")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["total_jobs"] == 0
    assert data["data"]["top_skills"] == []


def test_skills_summary_with_data():
    db = TestingSessionLocal()
    try:
        job1 = JobExtraction(
            id="1",
            source_type="url",
            source_url="http://example.com/job1",
            source_content="test",
            job_title="Backend Engineer",
            required_stack=["Python", "Django"],
            nice_to_have=["PostgreSQL"],
            location="NYC",
            seniority_level="Mid",
            confidence_score=0.95,
        )
        job2 = JobExtraction(
            id="2",
            source_type="url",
            source_url="http://example.com/job2",
            source_content="test",
            job_title="Full Stack",
            required_stack=["Python", "React"],
            nice_to_have=[],
            location="SF",
            seniority_level="Senior",
            confidence_score=0.92,
        )
        db.add(job1)
        db.add(job2)
        db.commit()

        response = client.get("/api/skills/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_jobs"] == 2
        assert len(data["data"]["top_skills"]) > 0
        assert data["data"]["distribution"]["required_count"] > 0
    finally:
        db.query(JobExtraction).delete()
        db.commit()
        db.close()


def test_skills_summary_with_seniority_filter():
    db = TestingSessionLocal()
    try:
        job1 = JobExtraction(
            id="1",
            source_type="url",
            source_url="http://example.com/job1",
            source_content="test",
            job_title="Junior Dev",
            required_stack=["JavaScript"],
            nice_to_have=[],
            location="NYC",
            seniority_level="Junior",
            confidence_score=0.9,
        )
        job2 = JobExtraction(
            id="2",
            source_type="url",
            source_url="http://example.com/job2",
            source_content="test",
            job_title="Senior Dev",
            required_stack=["Rust"],
            nice_to_have=[],
            location="SF",
            seniority_level="Senior",
            confidence_score=0.9,
        )
        db.add(job1)
        db.add(job2)
        db.commit()

        response = client.get("/api/skills/summary?seniority_level=Senior")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_jobs"] == 1
        assert len(data["data"]["top_skills"]) == 1
        assert data["data"]["top_skills"][0]["name"].lower() == "rust"
    finally:
        db.query(JobExtraction).delete()
        db.commit()
        db.close()


def test_skills_summary_response_schema():
    db = TestingSessionLocal()
    try:
        job = JobExtraction(
            id="1",
            source_type="url",
            source_url="http://example.com/job1",
            source_content="test",
            job_title="Dev",
            required_stack=["Python"],
            nice_to_have=[],
            location="NYC",
            seniority_level="Mid",
            confidence_score=0.9,
        )
        db.add(job)
        db.commit()

        response = client.get("/api/skills/summary")

        assert response.status_code == 200
        data = response.json()
        summary = data["data"]

        assert "top_skills" in summary
        assert "distribution" in summary
        assert "correlations" in summary
        assert "total_jobs" in summary
        assert "cached_at" in summary

        assert isinstance(summary["top_skills"], list)
        assert isinstance(summary["distribution"], dict)
        assert isinstance(summary["correlations"], list)
    finally:
        db.query(JobExtraction).delete()
        db.commit()
        db.close()
