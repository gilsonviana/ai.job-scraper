from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, model_validator


class JobExtractionRequest(BaseModel):
    source: Literal["url", "pdf"] = Field(description="Source type: 'url' or 'pdf'")
    url: Optional[HttpUrl] = Field(
        None, description="URL to job posting (required when source='url')"
    )

    @model_validator(mode="after")
    def validate_url_required_for_url_source(self):
        if self.source == "url" and self.url is None:
            raise ValueError("url is required when source is 'url'")
        return self


class JobExtractionResponse(BaseModel):
    id: str
    job_title: str
    required_stack: list[str]
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    availability: Optional[str] = None
    seniority_level: Optional[str] = None
    remote_policy: Optional[str] = None
    key_responsibilities: list[str]
    nice_to_have: list[str]
    confidence_score: float
    created_at: str


class JobExtractionDetailResponse(JobExtractionResponse):
    source_type: str
    source_url: Optional[str] = None


class ExtractionListItem(BaseModel):
    id: str
    job_title: str
    required_stack: list[str]
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    confidence_score: float
    created_at: str


class ExtractionListResponse(BaseModel):
    items: list[ExtractionListItem]
    total: int
    limit: int
    offset: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ApiResponse(BaseModel):
    data: Optional[dict] = None
    error: Optional[ErrorDetail] = None
