"""
Solution 3: Data Extractor for Job Postings

A complete implementation using structured outputs to extract job posting data.
"""

import os
from typing import Optional
from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    entry = "entry"
    mid = "mid"
    senior = "senior"
    lead = "lead"
    executive = "executive"


class JobType(str, Enum):
    """Job type enumeration."""
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    internship = "internship"


class Location(BaseModel):
    """Location information."""
    city: Optional[str] = Field(None, description="City name")
    state_or_country: Optional[str] = Field(None, description="State or country")
    is_remote: bool = Field(False, description="Whether remote work is available")
    remote_details: Optional[str] = Field(None, description="Remote work details (hybrid, fully remote, etc.)")


class SalaryRange(BaseModel):
    """Salary range information."""
    min_salary: Optional[float] = Field(None, description="Minimum salary")
    max_salary: Optional[float] = Field(None, description="Maximum salary")
    currency: str = Field("USD", description="Currency code")
    period: str = Field("annual", description="Pay period: annual, monthly, hourly")


class JobPosting(BaseModel):
    """Complete job posting information."""
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    location: Location = Field(description="Job location details")
    salary: Optional[SalaryRange] = Field(None, description="Salary information if available")
    required_skills: list[str] = Field(default_factory=list, description="Required skills")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Required experience level")
    job_type: JobType = Field(description="Type of employment")
    description_summary: str = Field(description="Brief summary of the job")


class DataExtractor:
    """Extract structured data from unstructured text."""

    def __init__(self):
        """Initialize the extractor."""
        self._client = self._get_client()

    def _get_client(self):
        """Get OpenAI client or None for mock mode."""
        if not os.getenv("OPENAI_API_KEY"):
            return None
        from openai import OpenAI
        return OpenAI()

    def extract_job_posting(self, text: str) -> JobPosting:
        """Extract job posting information from text."""
        if self._client is None:
            return self._mock_extract(text)

        response = self._client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Extract job posting information from the text.
Be thorough but only include information explicitly stated.
For salary, convert to annual if given as hourly (assume 2080 hours/year).
For experience level, infer from context (entry for junior/0-2 years, mid for 3-5 years, senior for 5+)."""
                },
                {"role": "user", "content": text}
            ],
            response_format=JobPosting
        )

        return response.choices[0].message.parsed

    def _mock_extract(self, text: str) -> JobPosting:
        """Mock extraction for demonstration."""
        text_lower = text.lower()

        # Simple extraction logic
        is_remote = "remote" in text_lower
        is_hybrid = "hybrid" in text_lower

        # Determine job type
        if "contract" in text_lower:
            job_type = JobType.contract
        elif "part-time" in text_lower or "part time" in text_lower:
            job_type = JobType.part_time
        elif "intern" in text_lower:
            job_type = JobType.internship
        else:
            job_type = JobType.full_time

        # Determine experience level
        if "senior" in text_lower or "5+" in text_lower:
            exp_level = ExperienceLevel.senior
        elif "junior" in text_lower or "entry" in text_lower:
            exp_level = ExperienceLevel.entry
        elif "lead" in text_lower:
            exp_level = ExperienceLevel.lead
        else:
            exp_level = ExperienceLevel.mid

        # Extract skills (simple pattern matching)
        common_skills = [
            "python", "javascript", "react", "typescript", "aws", "kubernetes",
            "sql", "docker", "go", "java", "rust", "node.js", "next.js"
        ]
        found_skills = [s for s in common_skills if s in text_lower]

        return JobPosting(
            title="[Mock] Software Engineer",
            company="[Mock] Tech Company",
            location=Location(
                city="Unknown",
                is_remote=is_remote,
                remote_details="Hybrid" if is_hybrid else ("Fully Remote" if is_remote else None)
            ),
            salary=SalaryRange(
                min_salary=100000,
                max_salary=150000,
                currency="USD",
                period="annual"
            ),
            required_skills=found_skills if found_skills else ["Programming"],
            experience_level=exp_level,
            job_type=job_type,
            description_summary="[Mock] A software engineering position at a technology company."
        )

    def extract_multiple(self, texts: list[str]) -> list[JobPosting]:
        """Extract job postings from multiple texts."""
        return [self.extract_job_posting(text) for text in texts]


# Test data
SAMPLE_JOB_POSTINGS = [
    """
    Senior Software Engineer at TechCorp
    Location: San Francisco, CA (Hybrid - 3 days in office)

    We're looking for a Senior Software Engineer to join our platform team.
    Salary: $180,000 - $220,000 per year plus equity

    Requirements:
    - 5+ years of Python experience
    - Experience with distributed systems
    - Strong knowledge of AWS
    - Familiarity with Kubernetes
    - Excellent communication skills

    This is a full-time position with great benefits including health insurance,
    401k matching, and unlimited PTO.
    """,

    """
    Frontend Developer - Remote
    Company: StartupXYZ

    Join our growing team as a Frontend Developer! We're a fully remote company
    building the future of e-commerce.

    Pay: $70-90/hour (Contract position, 6 months with possibility of extension)

    What we need:
    - React and TypeScript expertise
    - Experience with Next.js
    - Understanding of web accessibility
    - 3+ years of frontend development

    Work from anywhere in the US!
    """,

    """
    Junior Data Analyst
    Acme Analytics - New York, NY

    Entry-level position for recent graduates interested in data analysis.
    Competitive salary based on experience ($55,000 - $70,000).

    Skills needed:
    - SQL proficiency
    - Excel/Google Sheets
    - Basic Python or R
    - Statistics background preferred

    Full-time role with comprehensive training program.
    """
]


# Test the implementation
if __name__ == "__main__":
    print("Testing Data Extractor Implementation")
    print("=" * 60)

    extractor = DataExtractor()

    for i, posting in enumerate(SAMPLE_JOB_POSTINGS, 1):
        print(f"\n{'='*60}")
        print(f"Job Posting {i}")
        print(f"{'='*60}")
        print(f"Input preview: {posting[:100].strip()}...")

        result = extractor.extract_job_posting(posting)

        print(f"\nExtracted Data:")
        print(f"  Title: {result.title}")
        print(f"  Company: {result.company}")
        print(f"  Job Type: {result.job_type.value}")
        print(f"  Experience: {result.experience_level.value if result.experience_level else 'Not specified'}")

        print(f"\n  Location:")
        print(f"    City: {result.location.city or 'Not specified'}")
        print(f"    State/Country: {result.location.state_or_country or 'Not specified'}")
        print(f"    Remote: {result.location.is_remote}")
        if result.location.remote_details:
            print(f"    Remote Details: {result.location.remote_details}")

        if result.salary:
            print(f"\n  Salary:")
            print(f"    Range: {result.salary.currency} {result.salary.min_salary:,.0f} - {result.salary.max_salary:,.0f}")
            print(f"    Period: {result.salary.period}")

        print(f"\n  Required Skills: {', '.join(result.required_skills)}")
        print(f"\n  Summary: {result.description_summary}")

    # Test batch extraction
    print(f"\n{'='*60}")
    print("Testing Batch Extraction")
    print(f"{'='*60}")

    results = extractor.extract_multiple(SAMPLE_JOB_POSTINGS)
    print(f"\nExtracted {len(results)} job postings")
    for r in results:
        print(f"  - {r.title} at {r.company} ({r.job_type.value})")
