import csv
import re
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Base
from app.models.job import JobExtraction


def parse_salary(salary_str):
  """Parse salary string like '$140,000-$160,000' into (min, max) integers."""
  if not salary_str or salary_str.strip() == "":
    return None, None
  match = re.search(r"\$?([\d,]+)\s*-\s*\$?([\d,]+)", salary_str)
  if match:
    min_val = int(match.group(1).replace(",", ""))
    max_val = int(match.group(2).replace(",", ""))
    return min_val, max_val
  return None, None


def parse_tech_stack(stack_str):
  """Parse comma-separated tech stack into list."""
  if not stack_str or stack_str.strip() == "":
    return []
  return [tech.strip() for tech in stack_str.split(",")]


def parse_responsibilities(resp_str):
  """Parse semicolon-separated responsibilities into list."""
  if not resp_str or resp_str.strip() == "":
    return []
  return [resp.strip() for resp in resp_str.split(";")]


def extract_seniority_level(job_title):
  """Extract seniority level from job title."""
  title_lower = job_title.lower()
  if "principal" in title_lower:
    return "Principal"
  elif "staff" in title_lower:
    return "Staff"
  elif "senior" in title_lower:
    return "Senior"
  elif "mid-level" in title_lower or "mid level" in title_lower:
    return "Mid-Level"
  elif "junior" in title_lower:
    return "Junior"
  return None


def seed_jobs(csv_path, db_url="sqlite:///./data.db"):
  """Load jobs from CSV and insert into database."""
  engine = create_engine(db_url)
  Base.metadata.create_all(engine)
  Session = sessionmaker(bind=engine)
  session = Session()

  try:
    with open(csv_path, "r", encoding="utf-8") as f:
      reader = csv.DictReader(f)
      jobs = []
      for row in reader:
        salary_min, salary_max = parse_salary(row["salary"])
        job = JobExtraction(
          source_type="csv",
          job_title=row["job_title"],
          required_stack=parse_tech_stack(row["tech_stack"]),
          location=row["location"],
          salary_min=salary_min,
          salary_max=salary_max,
          remote_policy=row["work_mode"],
          key_responsibilities=parse_responsibilities(
            row["key_responsibilities"]
          ),
          seniority_level=extract_seniority_level(row["job_title"]),
        )
        jobs.append(job)

      session.bulk_save_objects(jobs)
      session.commit()
      print(f"✓ Seeded {len(jobs)} jobs from {csv_path}")
  except Exception as e:
    session.rollback()
    print(f"✗ Error seeding database: {e}")
    raise
  finally:
    session.close()


if __name__ == "__main__":
  csv_path = Path(__file__).parent.parent / "fixtures" / "jobs.csv"
  seed_jobs(str(csv_path))
