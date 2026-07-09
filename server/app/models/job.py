import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Index, Integer, JSON, String, func

from app.models import Base


class JobExtraction(Base):
    __tablename__ = "job_extractions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_type = Column(String(10), nullable=False)
    source_url = Column(String(2048), nullable=True)
    source_content = Column(String(50000), nullable=True)

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
    created_at = Column(
        DateTime, server_default=func.now(), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        default=datetime.utcnow,
    )

    __table_args__ = (
        Index("ix_created_at", "created_at"),
        Index("ix_source_type", "source_type"),
        Index("ix_seniority_level", "seniority_level"),
    )
