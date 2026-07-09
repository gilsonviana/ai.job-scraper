from collections import Counter
from datetime import datetime, timedelta
from itertools import combinations
from typing import Optional
from sqlalchemy.orm import Session

from app.models.job import JobExtraction
from app.schemas.skills import (
    SkillCount,
    SkillsDistribution,
    SkillCorrelation,
    SkillsFilter,
    SkillsSummary,
)

_cache: dict[tuple, tuple[float, SkillsSummary]] = {}
CACHE_TTL_SECONDS = 300


def normalize_skill(name: str) -> str:
    return name.strip().lower()


def get_skills_summary(db: Session, filters: SkillsFilter) -> SkillsSummary:
    cache_key = (filters.seniority_level,)

    if cache_key in _cache:
        timestamp, cached_summary = _cache[cache_key]
        if datetime.utcnow().timestamp() - timestamp < CACHE_TTL_SECONDS:
            return cached_summary

    query = db.query(JobExtraction)
    if filters.seniority_level:
        query = query.filter(JobExtraction.seniority_level == filters.seniority_level)

    extractions = query.all()
    total_jobs = len(extractions)

    skill_counter = Counter()
    required_counter = Counter()
    nice_to_have_counter = Counter()
    skill_display_names: dict[str, str] = {}

    jobs_normalized_skills: list[list[str]] = []

    for extraction in extractions:
        job_skills_normalized = []

        for skill in extraction.required_stack:
            normalized = normalize_skill(skill)
            skill_counter[normalized] += 1
            required_counter[normalized] += 1
            if normalized not in skill_display_names:
                skill_display_names[normalized] = skill
            job_skills_normalized.append(normalized)

        for skill in extraction.nice_to_have:
            normalized = normalize_skill(skill)
            skill_counter[normalized] += 1
            nice_to_have_counter[normalized] += 1
            if normalized not in skill_display_names:
                skill_display_names[normalized] = skill
            job_skills_normalized.append(normalized)

        jobs_normalized_skills.append(job_skills_normalized)

    total_skill_mentions = sum(skill_counter.values())
    top_skills_list = []

    if total_skill_mentions > 0:
        for normalized_name, count in skill_counter.most_common(20):
            display_name = skill_display_names[normalized_name]
            percentage = (count / total_skill_mentions) * 100
            top_skills_list.append(
                SkillCount(name=display_name, count=count, percentage=percentage)
            )

    distribution = SkillsDistribution(
        required_count=sum(required_counter.values()),
        nice_to_have_count=sum(nice_to_have_counter.values()),
    )

    correlations = calculate_skill_correlations(jobs_normalized_skills)

    summary = SkillsSummary(
        top_skills=top_skills_list,
        distribution=distribution,
        correlations=correlations,
        total_jobs=total_jobs,
        cached_at=datetime.utcnow().isoformat() + "Z",
    )

    _cache[cache_key] = (datetime.utcnow().timestamp(), summary)

    return summary


def calculate_skill_correlations(jobs_skills: list[list[str]]) -> list[SkillCorrelation]:
    correlation_counter: Counter[tuple[str, str]] = Counter()

    for skills in jobs_skills:
        unique_skills = list(set(skills))
        for skill_a, skill_b in combinations(sorted(unique_skills), 2):
            pair = (skill_a, skill_b)
            correlation_counter[pair] += 1

    correlation_list = []
    for (skill_a, skill_b), count in correlation_counter.most_common(50):
        correlation_list.append(SkillCorrelation(skill_a=skill_a, skill_b=skill_b, count=count))

    return correlation_list
