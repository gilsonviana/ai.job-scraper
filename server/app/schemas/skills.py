from typing import Optional
from pydantic import BaseModel, Field


class SkillsFilter(BaseModel):
    seniority_level: Optional[str] = None


class SkillCount(BaseModel):
    name: str
    count: int
    percentage: float = Field(ge=0.0, le=100.0)


class SkillsDistribution(BaseModel):
    required_count: int
    nice_to_have_count: int


class SkillCorrelation(BaseModel):
    skill_a: str
    skill_b: str
    count: int


class SkillsSummary(BaseModel):
    top_skills: list[SkillCount]
    distribution: SkillsDistribution
    correlations: list[SkillCorrelation]
    total_jobs: int
    cached_at: str
