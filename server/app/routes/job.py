from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import JobExtraction
from app.schemas.job import (
    ApiResponse,
    ErrorDetail,
    ExtractionListResponse,
    ExtractionListItem,
    JobExtractionDetailResponse,
    JobExtractionRequest,
    JobExtractionResponse,
)
from app.services.extraction import ExtractionService, ExtractionError
from app.utils.pdf_parser import PDFParseError
from app.config import settings

router = APIRouter(prefix="/api", tags=["jobs"])


@router.post("/extract")
async def extract_job_data(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Extract job data from URL or PDF.
    Accepts either JSON (for URL) or multipart/form-data (for PDF).
    """
    try:
        content_type = request.headers.get("content-type", "").lower()

        # Handle JSON requests
        if "application/json" in content_type:
            try:
                body = await request.json()
                req = JobExtractionRequest(**body)
            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "INVALID_REQUEST",
                            "message": "Invalid request body",
                            "details": {"error": str(e)},
                        }
                    },
                )

            source = req.source
            url = str(req.url) if req.url else None
            file = None

        # Handle multipart/form-data requests
        elif "multipart/form-data" in content_type:
            form = await request.form()
            source = form.get("source")
            url = form.get("url")
            file = form.get("file")

        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "UNSUPPORTED_CONTENT_TYPE",
                        "message": "Content-Type must be application/json or multipart/form-data",
                        "details": {"content_type": content_type},
                    }
                },
            )

        # Validate source
        if not source or source not in ("url", "pdf"):
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "INVALID_SOURCE",
                        "message": "source must be 'url' or 'pdf'",
                        "details": {"source": source},
                    }
                },
            )

        # Handle URL source
        if source == "url":
            if not url:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "MISSING_URL",
                            "message": "url is required when source is 'url'",
                            "details": {},
                        }
                    },
                )

            # Validate URL format (basic check)
            if not url.startswith(("http://", "https://")):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "INVALID_SOURCE",
                            "message": "url must be a valid HTTP(S) URL",
                            "details": {"url": url},
                        }
                    },
                )

            try:
                result = await ExtractionService.extract_from_url(url)
            except ExtractionError:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "code": "EXTRACTION_FAILED",
                            "message": "NLP extraction timed out or failed",
                            "details": {},
                        }
                    },
                )

        # Handle PDF source
        elif source == "pdf":
            if not file:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "MISSING_FILE",
                            "message": "PDF file required when source='pdf'",
                            "details": {},
                        }
                    },
                )

            # Validate file type
            if not file.content_type or "pdf" not in file.content_type.lower():
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "INVALID_FILE_TYPE",
                            "message": "File must be a valid PDF",
                            "details": {"content_type": file.content_type},
                        }
                    },
                )

            # Read and validate file size
            pdf_bytes = await file.read()
            if len(pdf_bytes) > settings.max_pdf_size:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "FILE_TOO_LARGE",
                            "message": "PDF file exceeds maximum size of 10MB",
                            "details": {
                                "max_size": settings.max_pdf_size,
                                "provided_size": len(pdf_bytes),
                            },
                        }
                    },
                )

            try:
                result = await ExtractionService.extract_from_pdf(pdf_bytes)
            except PDFParseError as e:
                return JSONResponse(
                    status_code=422,
                    content={
                        "error": {
                            "code": "PARSE_FAILED",
                            "message": "Could not extract text from PDF",
                            "details": {"reason": str(e)},
                        }
                    },
                )
            except ExtractionError:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "code": "EXTRACTION_FAILED",
                            "message": "NLP extraction timed out or failed",
                            "details": {},
                        }
                    },
                )

        # Persist to database
        extraction_id = str(uuid4())
        db_extraction = JobExtraction(
            id=extraction_id,
            source_type=result["source_type"],
            source_url=result["source_url"],
            source_content=result["source_content"],
            job_title=result["job_title"],
            required_stack=result["required_stack"],
            location=result["location"],
            salary_min=result["salary_min"],
            salary_max=result["salary_max"],
            availability=result["availability"],
            seniority_level=result["seniority_level"],
            remote_policy=result["remote_policy"],
            key_responsibilities=result["key_responsibilities"],
            nice_to_have=result["nice_to_have"],
            confidence_score=result["confidence_score"],
        )
        db.add(db_extraction)
        db.commit()
        db.refresh(db_extraction)

        response_data = JobExtractionResponse(
            id=str(db_extraction.id),
            job_title=db_extraction.job_title,
            required_stack=db_extraction.required_stack,
            location=db_extraction.location,
            salary_min=db_extraction.salary_min,
            salary_max=db_extraction.salary_max,
            availability=db_extraction.availability,
            seniority_level=db_extraction.seniority_level,
            remote_policy=db_extraction.remote_policy,
            key_responsibilities=db_extraction.key_responsibilities,
            nice_to_have=db_extraction.nice_to_have,
            confidence_score=db_extraction.confidence_score,
            created_at=db_extraction.created_at.isoformat() + "Z",
        )

        return JSONResponse(
            status_code=200, content={"data": response_data.model_dump()}
        )

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


@router.get("/extractions")
def list_extractions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all job extractions with optional filtering and pagination."""
    try:
        query = db.query(JobExtraction)

        if source_type:
            if source_type not in ("url", "pdf"):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "source_type must be 'url' or 'pdf'",
                            "details": {"source_type": source_type},
                        }
                    },
                )
            query = query.filter(JobExtraction.source_type == source_type)

        total = query.count()
        extractions = (
            query.order_by(JobExtraction.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        items = [
            ExtractionListItem(
                id=str(e.id),
                job_title=e.job_title,
                required_stack=e.required_stack,
                location=e.location,
                salary_min=e.salary_min,
                salary_max=e.salary_max,
                confidence_score=e.confidence_score,
                created_at=e.created_at.isoformat() + "Z",
            )
            for e in extractions
        ]

        list_response = ExtractionListResponse(
            items=items, total=total, limit=limit, offset=offset
        )

        return JSONResponse(
            status_code=200, content={"data": list_response.model_dump()}
        )

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


@router.get("/extractions/{id}")
def get_extraction(id: str, db: Session = Depends(get_db)):
    """Retrieve a single extraction by ID."""
    try:
        extraction = db.query(JobExtraction).filter(JobExtraction.id == id).first()

        if not extraction:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Extraction not found",
                        "details": {"id": id},
                    }
                },
            )

        response_data = JobExtractionDetailResponse(
            id=str(extraction.id),
            source_type=extraction.source_type,
            source_url=extraction.source_url,
            job_title=extraction.job_title,
            required_stack=extraction.required_stack,
            location=extraction.location,
            salary_min=extraction.salary_min,
            salary_max=extraction.salary_max,
            availability=extraction.availability,
            seniority_level=extraction.seniority_level,
            remote_policy=extraction.remote_policy,
            key_responsibilities=extraction.key_responsibilities,
            nice_to_have=extraction.nice_to_have,
            confidence_score=extraction.confidence_score,
            created_at=extraction.created_at.isoformat() + "Z",
        )

        return JSONResponse(
            status_code=200, content={"data": response_data.model_dump()}
        )

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
