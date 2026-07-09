import asyncio
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.services.nlp import NLPService
from app.utils.pdf_parser import extract_text_from_pdf, PDFParseError


class ExtractionError(Exception):
    """Raised when extraction fails."""

    pass


class ExtractionService:
    """Orchestrates job data extraction from URLs and PDFs."""

    @staticmethod
    async def extract_from_url(url: str) -> dict:
        """
        Extract job data from a URL.

        Args:
            url: HTTP(S) URL to job posting

        Returns:
            Dictionary with extracted fields

        Raises:
            ExtractionError: On timeout, network error, or NLP failure
        """
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, requests.get, url),
                timeout=10.0,
            )
            response.raise_for_status()

            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)

            return await ExtractionService._extract_fields(
                text, source_type="url", source_url=url, source_content=html_content
            )
        except asyncio.TimeoutError:
            raise ExtractionError("URL fetch timed out")
        except requests.RequestException as e:
            raise ExtractionError(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            raise ExtractionError(f"URL extraction failed: {str(e)}")

    @staticmethod
    async def extract_from_pdf(pdf_bytes: bytes) -> dict:
        """
        Extract job data from a PDF file.

        Args:
            pdf_bytes: Raw PDF file bytes

        Returns:
            Dictionary with extracted fields

        Raises:
            PDFParseError: If PDF is corrupted or unsupported
            ExtractionError: On NLP failure or timeout
        """
        try:
            text = extract_text_from_pdf(pdf_bytes)
        except PDFParseError:
            raise

        return await ExtractionService._extract_fields(
            text,
            source_type="pdf",
            source_url=None,
            source_content=text[:10000],
        )

    @staticmethod
    async def _extract_fields(
        text: str,
        source_type: str,
        source_url: Optional[str],
        source_content: Optional[str],
    ) -> dict:
        """
        Extract structured fields from job posting text.

        Args:
            text: Cleaned text from URL or PDF
            source_type: "url" or "pdf"
            source_url: URL if source_type is "url"
            source_content: Raw HTML/PDF content for audit trail

        Returns:
            Dictionary with extracted fields and confidence scores

        Raises:
            ExtractionError: On timeout or NLP failure
        """
        if not text or len(text.strip()) == 0:
            raise ExtractionError("No text content to extract from")

        if len(text.encode("utf-8")) > settings.max_input_size:
            text = text[: settings.max_input_size]

        try:
            loop = asyncio.get_event_loop()

            def do_extraction():
                job_title, job_title_conf = NLPService.extract_job_title(text)
                location, location_conf = NLPService.extract_location(text)
                salary_min, salary_max, salary_conf = NLPService.extract_salary_range(
                    text
                )
                seniority_level, seniority_conf = (
                    NLPService.classify_seniority_level(text)
                )
                remote_policy, remote_conf = NLPService.classify_remote_policy(text)
                required_stack, stack_conf = NLPService.extract_tech_stack(text)
                key_responsibilities, resp_conf = (
                    NLPService.extract_key_responsibilities(text)
                )

                field_confidences = {
                    "job_title": job_title_conf,
                    "location": location_conf,
                    "salary_min": salary_conf if salary_min else 0.0,
                    "salary_max": salary_conf if salary_max else 0.0,
                    "seniority_level": seniority_conf if seniority_level else 0.0,
                    "remote_policy": remote_conf if remote_policy else 0.0,
                    "required_stack": stack_conf,
                }

                overall_confidence = NLPService.calculate_overall_confidence(
                    field_confidences
                )

                return {
                    "job_title": job_title,
                    "required_stack": required_stack,
                    "location": location or "Not specified",
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "availability": None,
                    "seniority_level": seniority_level,
                    "remote_policy": remote_policy,
                    "key_responsibilities": key_responsibilities,
                    "nice_to_have": [],
                    "confidence_score": overall_confidence,
                    "source_type": source_type,
                    "source_url": source_url,
                    "source_content": source_content,
                }

            result = await asyncio.wait_for(
                loop.run_in_executor(None, do_extraction),
                timeout=float(settings.extraction_timeout),
            )
            return result

        except asyncio.TimeoutError:
            raise ExtractionError("NLP extraction timed out")
        except Exception as e:
            raise ExtractionError(f"Extraction pipeline failed: {str(e)}")
