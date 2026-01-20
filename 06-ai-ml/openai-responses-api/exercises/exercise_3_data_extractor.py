"""
Exercise 3: Build a Data Extractor

Create a data extraction system using structured outputs to parse
unstructured text into validated data models.

Requirements:
1. Define Pydantic models for extracted data
2. Use structured outputs for reliable JSON
3. Handle extraction errors gracefully
4. Support multiple extraction types

Data to extract from job postings:
- Job title
- Company name
- Location (city, state/country, remote option)
- Salary range (min, max, currency)
- Required skills
- Experience level
- Job type (full-time, part-time, contract)

Hints:
- Use Optional for fields that might not be present
- Use enums for constrained values
- Nested models for complex structures
- Handle cases where data is missing
"""

import os
from typing import Optional
from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


# TODO: Define your Pydantic models

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
    # TODO: Define fields
    # city: Optional[str]
    # state_or_country: Optional[str]
    # is_remote: bool
    pass


class SalaryRange(BaseModel):
    """Salary range information."""
    # TODO: Define fields
    # min_salary: Optional[float]
    # max_salary: Optional[float]
    # currency: str
    # period: str (annual, monthly, hourly)
    pass


class JobPosting(BaseModel):
    """Complete job posting information."""
    # TODO: Define all fields
    # title: str
    # company: str
    # location: Location
    # salary: Optional[SalaryRange]
    # required_skills: list[str]
    # experience_level: Optional[ExperienceLevel]
    # job_type: JobType
    # description_summary: str
    pass


class DataExtractor:
    """Extract structured data from unstructured text."""

    def __init__(self):
        """Initialize the extractor."""
        # TODO: Initialize OpenAI client
        pass

    def extract_job_posting(self, text: str) -> JobPosting:
        """Extract job posting information from text.

        Args:
            text: Unstructured job posting text

        Returns:
            Structured JobPosting object
        """
        # TODO: Implement extraction using structured outputs
        # 1. Create appropriate prompt
        # 2. Use client.beta.chat.completions.parse
        # 3. Return parsed object
        pass

    def extract_multiple(self, texts: list[str]) -> list[JobPosting]:
        """Extract job postings from multiple texts.

        Args:
            texts: List of job posting texts

        Returns:
            List of extracted JobPosting objects
        """
        # TODO: Implement batch extraction
        pass


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


# Test your implementation
if __name__ == "__main__":
    print("Testing Data Extractor Implementation")
    print("=" * 50)

    extractor = DataExtractor()

    for i, posting in enumerate(SAMPLE_JOB_POSTINGS, 1):
        print(f"\n--- Job Posting {i} ---")
        print(f"Input preview: {posting[:100].strip()}...")

        result = extractor.extract_job_posting(posting)

        if result:
            print(f"\nExtracted Data:")
            print(f"  Title: {result.title if hasattr(result, 'title') else 'N/A'}")
            print(f"  Company: {result.company if hasattr(result, 'company') else 'N/A'}")
            # Add more field prints as you implement them
        else:
            print("  [Extraction not implemented]")

    print("\n" + "=" * 50)
    print("Implementation complete!" if extractor.extract_job_posting(SAMPLE_JOB_POSTINGS[0]) else "Needs implementation")
