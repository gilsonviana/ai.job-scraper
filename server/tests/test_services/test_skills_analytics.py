import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.job import JobExtraction
from app.schemas.skills import SkillsFilter
from app.services.skills_analytics import (
    get_skills_summary,
    calculate_skill_correlations,
    normalize_skill,
    _cache,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

    _cache.clear()


def test_normalize_skill():
    assert normalize_skill("Python") == "python"
    assert normalize_skill("  JavaScript  ") == "javascript"
    assert normalize_skill("C++") == "c++"


def test_get_skills_summary_empty_database(db):
    filters = SkillsFilter(seniority_level=None)
    summary = get_skills_summary(db, filters)

    assert summary.total_jobs == 0
    assert summary.top_skills == []
    assert summary.distribution.required_count == 0
    assert summary.distribution.nice_to_have_count == 0
    assert summary.correlations == []
    assert summary.cached_at is not None


def test_get_skills_summary_with_data(db):
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

    filters = SkillsFilter(seniority_level=None)
    summary = get_skills_summary(db, filters)

    assert summary.total_jobs == 2
    assert len(summary.top_skills) == 4
    assert summary.top_skills[0].name.lower() == "python"
    assert summary.top_skills[0].count == 2
    assert summary.distribution.required_count == 4
    assert summary.distribution.nice_to_have_count == 1


def test_get_skills_summary_with_seniority_filter(db):
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
        required_stack=["Python", "Rust"],
        nice_to_have=[],
        location="SF",
        seniority_level="Senior",
        confidence_score=0.9,
    )
    db.add(job1)
    db.add(job2)
    db.commit()

    filters = SkillsFilter(seniority_level="Senior")
    summary = get_skills_summary(db, filters)

    assert summary.total_jobs == 1
    assert len(summary.top_skills) == 2
    skill_names = [s.name.lower() for s in summary.top_skills]
    assert "python" in skill_names
    assert "rust" in skill_names


def test_skill_normalization_deduplication(db):
    job = JobExtraction(
        id="1",
        source_type="url",
        source_url="http://example.com/job1",
        source_content="test",
        job_title="Backend",
        required_stack=["Python", "python", "PYTHON"],
        nice_to_have=[],
        location="NYC",
        seniority_level="Mid",
        confidence_score=0.9,
    )
    db.add(job)
    db.commit()

    filters = SkillsFilter(seniority_level=None)
    summary = get_skills_summary(db, filters)

    assert summary.total_jobs == 1
    assert len(summary.top_skills) == 1
    assert summary.top_skills[0].count == 3


def test_calculate_skill_correlations():
    jobs_skills = [
        ["python", "django"],
        ["python", "django", "postgresql"],
        ["javascript", "react"],
        ["python"],
    ]

    correlations = calculate_skill_correlations(jobs_skills)

    assert len(correlations) > 0
    python_django = next(
        (c for c in correlations if c.skill_a == "django" and c.skill_b == "python"),
        None,
    )
    assert python_django is not None
    assert python_django.count == 2

    django_postgresql = next(
        (c for c in correlations if set([c.skill_a, c.skill_b]) == {"django", "postgresql"}),
        None,
    )
    assert django_postgresql is not None
    assert django_postgresql.count == 1


def test_get_skills_summary_caching(db):
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

    filters = SkillsFilter(seniority_level="Mid")
    summary1 = get_skills_summary(db, filters)
    summary2 = get_skills_summary(db, filters)

    assert summary1.cached_at == summary2.cached_at
