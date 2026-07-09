import pytest

from app.services.nlp import NLPService


# NLPService requires models to be loaded; skip if models are not available
pytestmark = pytest.mark.skip(reason="NLP models not pre-loaded in test environment")


class TestNLPService:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Note: This will fail if models aren't pre-loaded
        # In a real CI environment, models should be downloaded beforehand
        try:
            NLPService.load_models()
        except RuntimeError:
            pytest.skip("NLP models not available")

    def test_extract_job_title(self):
        text = "We are hiring a Senior Python Engineer for our backend team"
        title, conf = NLPService.extract_job_title(text)
        assert isinstance(title, str)
        assert isinstance(conf, float)
        assert 0 <= conf <= 1

    def test_extract_location(self):
        text = "Location: San Francisco, CA or Remote"
        location, conf = NLPService.extract_location(text)
        if location:
            assert isinstance(location, str)
            assert isinstance(conf, float)
            assert 0 <= conf <= 1

    def test_extract_salary_range(self):
        text = "Salary range: $150,000 - $200,000"
        salary_min, salary_max, conf = NLPService.extract_salary_range(text)
        assert salary_min == 150000
        assert salary_max == 200000
        assert conf > 0.5

    def test_extract_tech_stack(self):
        text = "We use Python, PostgreSQL, Docker, and AWS for our infrastructure"
        stack, conf = NLPService.extract_tech_stack(text)
        assert isinstance(stack, list)
        assert "python" in [s.lower() for s in stack]
        assert isinstance(conf, float)
        assert 0 <= conf <= 1

    def test_calculate_overall_confidence(self):
        field_confidences = {
            "job_title": 0.9,
            "location": 0.8,
            "required_stack": 0.85,
            "salary_min": 0.75,
            "salary_max": 0.75,
            "seniority_level": 0.6,
            "remote_policy": 0.7,
        }
        overall = NLPService.calculate_overall_confidence(field_confidences)
        assert 0 <= overall <= 1
        assert overall > 0.6
