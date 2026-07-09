from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.skills import SkillsFilter, SkillsSummary
from app.services.skills_analytics import get_skills_summary

router = APIRouter(prefix="/api", tags=["skills"])


@router.get("/skills/summary")
def skills_summary(
    seniority_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        filters = SkillsFilter(seniority_level=seniority_level)
        summary = get_skills_summary(db, filters)

        return JSONResponse(status_code=200, content={"data": summary.model_dump()})

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Unhandled server error",
                    "details": {},
                }
            },
        )
