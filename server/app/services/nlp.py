import re
from typing import Optional

from app.config import settings


class NLPService:
    """Encapsulates NLP model loading and inference for job extraction."""

    _spacy_model: Optional[object] = None
    _classifier_pipeline: Optional[object] = None
    _summarizer_pipeline: Optional[object] = None
    _models_loaded: bool = False

    @classmethod
    def load_models(cls) -> None:
        """Load NLP models on startup (called once)."""
        if cls._models_loaded:
            return

        try:
            import spacy
            from transformers import pipeline

            cls._spacy_model = spacy.load(settings.nlp_model_spacy)
            cls._classifier_pipeline = pipeline(
                "zero-shot-classification",
                model=settings.nlp_model_hf_classifier,
                device=-1,
            )
            cls._summarizer_pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1,
            )
            cls._models_loaded = True
        except Exception as e:
            print(f"Warning: Failed to load NLP models: {str(e)}")

    @classmethod
    def _ensure_models_loaded(cls) -> None:
        if not cls._models_loaded:
            cls.load_models()

    @classmethod
    def extract_job_title(cls, text: str) -> tuple[str, float]:
        """
        Extract job title from text using NER patterns.
        Returns (title, confidence) where title may be uncertain.
        """
        cls._ensure_models_loaded()
        if cls._spacy_model is None:
            return "Job Title Not Found", 0.3
        doc = cls._spacy_model(text[:2000])

        for token in doc:
            if token.pos_ == "NOUN" and not token.is_stop:
                is_title_like = any(
                    keyword in token.text.lower()
                    for keyword in [
                        "engineer",
                        "developer",
                        "architect",
                        "manager",
                        "lead",
                        "senior",
                        "junior",
                        "analyst",
                        "scientist",
                        "specialist",
                        "officer",
                        "coordinator",
                    ]
                )
                if is_title_like:
                    if len(doc) > token.i + 3:
                        title = " ".join(
                            t.text
                            for t in doc[
                                max(0, token.i - 2) : min(len(doc), token.i + 3)
                            ]
                        )
                        return title, 0.85
                    else:
                        return token.text, 0.75

        for ent in doc.ents:
            if len(ent.text) > 3 and "engineer" in ent.text.lower():
                return ent.text, 0.80

        lines = text.split("\n")
        for line in lines[:10]:
            if len(line) < 100 and any(
                keyword in line.lower()
                for keyword in [
                    "position",
                    "role",
                    "opening",
                    "hiring",
                    "job",
                ]
            ):
                return line.strip(), 0.65

        return "Job Title Not Found", 0.30

    @classmethod
    def extract_location(cls, text: str) -> tuple[Optional[str], float]:
        """Extract location from text using NER."""
        cls._ensure_models_loaded()
        if cls._spacy_model is None:
            return None, 0.0
        doc = cls._spacy_model(text[:3000])

        locations = []
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC"):
                locations.append((ent.text, 0.85))

        for pattern in [
            r"\b(?:Remote|On-site|On site|Onsite|Hybrid)\b",
            r"\b\d{5}(?:-\d{4})?\b",
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                locations.append((match.group(0), 0.80))

        if locations:
            return locations[0][0], locations[0][1]

        return None, 0.0

    @classmethod
    def extract_salary_range(
        cls, text: str
    ) -> tuple[Optional[int], Optional[int], float]:
        """Extract salary min/max using regex patterns."""
        salary_pattern = r"\$[\d,]+(?:\s*-\s*\$[\d,]+)?"
        matches = re.findall(salary_pattern, text)

        if not matches:
            return None, None, 0.0

        try:
            salary_str = matches[0]
            numbers = re.findall(r"\d+", salary_str.replace(",", ""))

            if len(numbers) >= 2:
                salary_min = int(numbers[0])
                salary_max = int(numbers[1])
                return salary_min, salary_max, 0.80
            elif len(numbers) == 1:
                salary = int(numbers[0])
                return salary, salary, 0.70
        except (ValueError, IndexError):
            pass

        return None, None, 0.0

    @classmethod
    def classify_seniority_level(cls, text: str) -> tuple[Optional[str], float]:
        """Classify seniority level using zero-shot classification."""
        cls._ensure_models_loaded()
        if cls._spacy_model is None or cls._classifier_pipeline is None:
            return None, 0.0
        doc = cls._spacy_model(text[:2000])
        summary = " ".join(
            token.text
            for token in doc
            if not token.is_stop and token.is_alpha
        )

        if not summary:
            return None, 0.0

        try:
            labels = ["Junior", "Mid-level", "Senior", "Lead", "Not specified"]
            result = cls._classifier_pipeline(summary[:512], labels, multi_class=False)
            top_label = result["labels"][0]
            confidence = float(result["scores"][0])

            if confidence < 0.5:
                return None, confidence

            return top_label, confidence
        except Exception:
            return None, 0.0

    @classmethod
    def classify_remote_policy(cls, text: str) -> tuple[Optional[str], float]:
        """Classify remote policy using zero-shot classification."""
        cls._ensure_models_loaded()

        remote_keywords = ["remote", "on-site", "onsite", "hybrid", "office"]
        for keyword in remote_keywords:
            if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
                if keyword.lower() == "remote":
                    return "Remote", 0.95
                elif keyword.lower() in ("on-site", "onsite"):
                    return "On-site", 0.95
                elif keyword.lower() == "hybrid":
                    return "Hybrid", 0.95

        if cls._spacy_model is None or cls._classifier_pipeline is None:
            return None, 0.0

        try:
            doc = cls._spacy_model(text[:1000])
            summary = " ".join(
                token.text
                for token in doc
                if not token.is_stop and token.is_alpha
            )

            if not summary:
                return None, 0.0

            labels = ["Remote", "On-site", "Hybrid", "Not specified"]
            result = cls._classifier_pipeline(
                summary[:512], labels, multi_class=False
            )
            top_label = result["labels"][0]
            confidence = float(result["scores"][0])

            if confidence < 0.5:
                return None, confidence

            return top_label, confidence
        except Exception:
            return None, 0.0

    @classmethod
    def extract_key_responsibilities(
        cls, text: str, max_count: int = 5
    ) -> tuple[list[str], float]:
        """Extract key responsibilities using extractive summarization."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return [], 0.0

        if len(sentences) <= max_count:
            return sentences[:max_count], 0.70

        if cls._summarizer_pipeline is None:
            return sentences[:max_count], 0.5

        try:
            text_to_summarize = " ".join(sentences[: min(200, len(sentences))])

            if len(text_to_summarize.split()) < 30:
                return sentences[: min(3, len(sentences))], 0.60

            summary = cls._summarizer_pipeline(text_to_summarize, max_length=60)
            summary_text = summary[0]["summary_text"]
            summary_sentences = re.split(
                r"(?<=[.!?])\s+", summary_text
            )

            responsibilities = [s.strip() for s in summary_sentences if s.strip()]
            return responsibilities[:max_count], 0.75
        except Exception:
            return sentences[:max_count], 0.50

    @classmethod
    def extract_tech_stack(cls, text: str) -> tuple[list[str], float]:
        """Extract technology stack from text using keyword matching."""
        tech_keywords = {
            "python",
            "java",
            "javascript",
            "typescript",
            "golang",
            "rust",
            "csharp",
            "c#",
            "php",
            "ruby",
            "swift",
            "kotlin",
            "scala",
            "r",
            "sql",
            "postgresql",
            "mysql",
            "mongodb",
            "dynamodb",
            "redis",
            "elasticsearch",
            "docker",
            "kubernetes",
            "aws",
            "gcp",
            "azure",
            "terraform",
            "jenkins",
            "gitlab",
            "github",
            "react",
            "vue",
            "angular",
            "node.js",
            "nodejs",
            "fastapi",
            "django",
            "flask",
            "spring",
            "grpc",
            "rest",
            "graphql",
            "linux",
            "git",
            "terraform",
            "ansible",
            "prometheus",
            "grafana",
            "datadog",
        }

        found_techs = set()
        text_lower = text.lower()

        for tech in tech_keywords:
            if re.search(rf"\b{re.escape(tech)}\b", text_lower):
                found_techs.add(tech)

        if found_techs:
            return sorted(list(found_techs)), 0.75
        else:
            return [], 0.40

    @classmethod
    def calculate_overall_confidence(
        cls, field_confidences: dict[str, float]
    ) -> float:
        """Calculate overall confidence as weighted average."""
        if not field_confidences:
            return 0.0

        weights = {
            "job_title": 0.25,
            "location": 0.20,
            "required_stack": 0.15,
            "salary_min": 0.10,
            "salary_max": 0.10,
            "seniority_level": 0.10,
            "remote_policy": 0.10,
        }

        total_weight = 0.0
        weighted_score = 0.0

        for field, confidence in field_confidences.items():
            weight = weights.get(field, 0.0)
            weighted_score += confidence * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return min(1.0, weighted_score / total_weight)
