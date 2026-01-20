"""Exercise 3: Multi-Template Composition.

In this exercise, you'll build a system that combines multiple templates
to create complex, multi-step prompts for a document processing workflow.

Requirements:
1. Create a TemplateLibrary class to manage domain templates
2. Implement a WorkflowComposer that chains multiple prompts
3. Support these document processing steps:
   - Extract: Pull key information from documents
   - Analyze: Analyze the extracted information
   - Summarize: Create a summary report

Each step should have its own four-layer template that can be customized.

The workflow should support:
- Sequential execution (output of one feeds into next)
- Parallel execution (multiple analyses of same content)
- Conditional steps (include/skip based on parameters)
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowStep:
    """A single step in a document processing workflow."""

    name: str
    system: str
    context_template: str
    instruction: str
    constraint: str


class TemplateLibrary:
    """Library of document processing templates.

    TODO: Implement this class

    Should provide templates for:
    - extraction: Extract structured data from documents
    - analysis: Analyze content for insights
    - summarization: Create summaries at different lengths
    - comparison: Compare multiple documents
    """

    def __init__(self) -> None:
        """Initialize with default templates."""
        # Your implementation here
        raise NotImplementedError("Implement __init__")

    def get_extraction_step(self, doc_type: str) -> WorkflowStep:
        """Get extraction step for a document type.

        Args:
            doc_type: Type of document (e.g., "contract", "report", "email")

        Returns:
            WorkflowStep configured for extraction
        """
        # Your implementation here
        raise NotImplementedError("Implement get_extraction_step")

    def get_analysis_step(self, analysis_type: str) -> WorkflowStep:
        """Get analysis step for an analysis type.

        Args:
            analysis_type: Type of analysis (e.g., "sentiment", "risk", "summary")

        Returns:
            WorkflowStep configured for analysis
        """
        # Your implementation here
        raise NotImplementedError("Implement get_analysis_step")

    def get_summarization_step(self, length: str) -> WorkflowStep:
        """Get summarization step for a target length.

        Args:
            length: Target length (e.g., "brief", "standard", "detailed")

        Returns:
            WorkflowStep configured for summarization
        """
        # Your implementation here
        raise NotImplementedError("Implement get_summarization_step")


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    step_name: str
    prompt: str
    # In a real system, this would also have the LLM response


class WorkflowComposer:
    """Composes multi-step document processing workflows.

    TODO: Implement this class

    Should support:
    - Adding steps to the workflow
    - Passing output from one step as input to next
    - Parallel branching (same input, multiple analyses)
    - Conditional step execution
    """

    def __init__(self, library: TemplateLibrary) -> None:
        """Initialize with a template library.

        Args:
            library: TemplateLibrary for step templates
        """
        # Your implementation here
        raise NotImplementedError("Implement __init__")

    def add_step(self, step: WorkflowStep) -> "WorkflowComposer":
        """Add a step to the workflow.

        Args:
            step: WorkflowStep to add

        Returns:
            Self for chaining
        """
        # Your implementation here
        raise NotImplementedError("Implement add_step")

    def add_parallel_steps(self, steps: list[WorkflowStep]) -> "WorkflowComposer":
        """Add parallel steps (all receive same input).

        Args:
            steps: List of steps to run in parallel

        Returns:
            Self for chaining
        """
        # Your implementation here
        raise NotImplementedError("Implement add_parallel_steps")

    def add_conditional_step(
        self,
        step: WorkflowStep,
        condition: str,
    ) -> "WorkflowComposer":
        """Add a conditional step.

        Args:
            step: WorkflowStep to conditionally add
            condition: Description of when to include this step

        Returns:
            Self for chaining
        """
        # Your implementation here
        raise NotImplementedError("Implement add_conditional_step")

    def compose(self, document: str, variables: dict[str, Any] | None = None) -> list[str]:
        """Compose all prompts for the workflow.

        Args:
            document: The document to process
            variables: Additional variables for templates

        Returns:
            List of composed prompts for each step
        """
        # Your implementation here
        raise NotImplementedError("Implement compose")


def create_contract_review_workflow(library: TemplateLibrary) -> WorkflowComposer:
    """Create a workflow for reviewing contracts.

    Args:
        library: TemplateLibrary to use

    Returns:
        Configured WorkflowComposer

    TODO: Implement this function

    The workflow should:
    1. Extract key terms, parties, dates, and obligations
    2. Analyze for risks and unusual clauses (parallel with compliance check)
    3. Generate executive summary
    """
    # Your implementation here
    raise NotImplementedError("Implement contract review workflow")


# Test cases
def test_template_library() -> None:
    """Test template library functionality."""
    library = TemplateLibrary()

    extraction = library.get_extraction_step("contract")
    print("Extraction Step:")
    print(f"  Name: {extraction.name}")
    print(f"  System: {extraction.system[:50]}...")

    analysis = library.get_analysis_step("risk")
    print(f"\nAnalysis Step: {analysis.name}")

    summary = library.get_summarization_step("brief")
    print(f"Summary Step: {summary.name}")


def test_workflow_composition() -> None:
    """Test workflow composition."""
    library = TemplateLibrary()
    workflow = create_contract_review_workflow(library)

    sample_contract = """
    SERVICE AGREEMENT

    This Agreement is entered into as of January 1, 2024, by and between
    Acme Corp ("Provider") and Client Inc ("Client").

    TERM: This agreement shall be effective for 12 months.

    PAYMENT: Client shall pay $10,000 monthly for services rendered.

    TERMINATION: Either party may terminate with 30 days written notice.
    """

    prompts = workflow.compose(sample_contract)

    print("\nGenerated Prompts:")
    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- Step {i} ---")
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)


def test_parallel_workflow() -> None:
    """Test parallel step execution."""
    library = TemplateLibrary()
    composer = WorkflowComposer(library)

    # Add extraction, then parallel analyses
    composer.add_step(library.get_extraction_step("document"))
    composer.add_parallel_steps([
        library.get_analysis_step("sentiment"),
        library.get_analysis_step("risk"),
        library.get_analysis_step("compliance"),
    ])
    composer.add_step(library.get_summarization_step("standard"))

    prompts = composer.compose("Sample document content...")

    print(f"\nParallel workflow generated {len(prompts)} prompts")


if __name__ == "__main__":
    test_template_library()
    test_workflow_composition()
    test_parallel_workflow()
    print("\nAll tests passed!")
