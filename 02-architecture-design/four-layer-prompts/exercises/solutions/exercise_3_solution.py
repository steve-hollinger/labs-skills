"""Exercise 3 Solution: Multi-Template Composition."""

from dataclasses import dataclass, field
from typing import Any

from four_layer_prompts.composer import compose_layers


@dataclass
class WorkflowStep:
    """A single step in a document processing workflow."""

    name: str
    system: str
    context_template: str
    instruction: str
    constraint: str

    def render(self, document: str, variables: dict[str, Any] | None = None) -> str:
        """Render this step as a complete prompt."""
        vars_dict = variables or {}
        vars_dict["document"] = document

        # Simple variable substitution
        context = self.context_template
        for key, value in vars_dict.items():
            context = context.replace(f"${{{key}}}", str(value))
            context = context.replace(f"${key}", str(value))

        return compose_layers(
            system=self.system,
            context=context,
            instruction=self.instruction,
            constraint=self.constraint,
        )


class TemplateLibrary:
    """Library of document processing templates."""

    def __init__(self) -> None:
        """Initialize with default templates."""
        self._extraction_templates: dict[str, WorkflowStep] = {
            "contract": WorkflowStep(
                name="Contract Extraction",
                system="""You are a legal document analyst specializing in contract review.
You extract structured information accurately and completely.
You identify all parties, terms, dates, and obligations.""",
                context_template="""Document to analyze:
${document}

Document Type: Contract""",
                instruction="""Extract the following information from this contract:
1. Parties involved (names and roles)
2. Effective date and term/duration
3. Key financial terms (amounts, payment schedules)
4. Main obligations of each party
5. Termination conditions
6. Any unusual or notable clauses""",
                constraint="""Format output as structured data:
- Use clear section headers
- List items with bullet points
- Include exact quotes for critical terms
- Note any ambiguous or missing information""",
            ),
            "report": WorkflowStep(
                name="Report Extraction",
                system="You are a business analyst who extracts key information from reports.",
                context_template="Document:\n${document}",
                instruction="Extract key findings, metrics, and recommendations.",
                constraint="Format as bullet points with categories.",
            ),
            "email": WorkflowStep(
                name="Email Extraction",
                system="You are an executive assistant who summarizes communications.",
                context_template="Email content:\n${document}",
                instruction="Extract sender intent, action items, and deadlines.",
                constraint="Keep extraction concise and actionable.",
            ),
            "document": WorkflowStep(
                name="General Extraction",
                system="You are a document analyst who extracts key information.",
                context_template="Document:\n${document}",
                instruction="Identify and extract the main topics, facts, and conclusions.",
                constraint="Present information in a structured format.",
            ),
        }

        self._analysis_templates: dict[str, WorkflowStep] = {
            "sentiment": WorkflowStep(
                name="Sentiment Analysis",
                system="You are a sentiment analysis expert.",
                context_template="Content to analyze:\n${document}",
                instruction="Analyze the sentiment and emotional tone of this content.",
                constraint="Provide overall sentiment (positive/negative/neutral) with confidence.",
            ),
            "risk": WorkflowStep(
                name="Risk Analysis",
                system="""You are a risk assessment specialist.
You identify potential risks, liabilities, and concerns in documents.
You rate risks by severity and likelihood.""",
                context_template="""Content to assess:
${document}

Previous extraction (if available): ${extraction}""",
                instruction="""Identify and assess risks in this content:
1. Legal risks and liabilities
2. Financial risks
3. Operational risks
4. Compliance concerns
5. Reputational risks

For each risk, provide:
- Description
- Severity (High/Medium/Low)
- Likelihood
- Recommended mitigation""",
                constraint="Prioritize risks by severity. Be specific about concerns.",
            ),
            "compliance": WorkflowStep(
                name="Compliance Check",
                system="You are a compliance officer reviewing documents for regulatory adherence.",
                context_template="Document:\n${document}",
                instruction="Check for compliance with standard regulations and best practices.",
                constraint="Flag any compliance issues with references to relevant standards.",
            ),
        }

        self._summary_templates: dict[str, WorkflowStep] = {
            "brief": WorkflowStep(
                name="Brief Summary",
                system="You are an executive summarizer who creates concise overviews.",
                context_template="Content to summarize:\n${document}\n\nAnalysis: ${analysis}",
                instruction="Create a brief executive summary of the key points.",
                constraint="Maximum 3 sentences. Focus on most critical information.",
            ),
            "standard": WorkflowStep(
                name="Standard Summary",
                system="""You are a professional summarizer.
You create clear, comprehensive summaries that capture essential information.""",
                context_template="""Source content:
${document}

Extraction results:
${extraction}

Analysis results:
${analysis}""",
                instruction="""Create an executive summary including:
1. Overview (2-3 sentences)
2. Key findings
3. Critical issues or concerns
4. Recommended actions""",
                constraint="""Format as a professional report.
Use headers and bullet points.
Keep under 300 words.""",
            ),
            "detailed": WorkflowStep(
                name="Detailed Summary",
                system="You are a detailed analyst who creates comprehensive summaries.",
                context_template="Content:\n${document}\n\nAnalysis: ${analysis}",
                instruction="Create a detailed summary covering all significant aspects.",
                constraint="Include all relevant details. Maximum 500 words.",
            ),
        }

    def get_extraction_step(self, doc_type: str) -> WorkflowStep:
        """Get extraction step for a document type."""
        if doc_type in self._extraction_templates:
            return self._extraction_templates[doc_type]
        return self._extraction_templates["document"]

    def get_analysis_step(self, analysis_type: str) -> WorkflowStep:
        """Get analysis step for an analysis type."""
        if analysis_type not in self._analysis_templates:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        return self._analysis_templates[analysis_type]

    def get_summarization_step(self, length: str) -> WorkflowStep:
        """Get summarization step for a target length."""
        if length not in self._summary_templates:
            raise ValueError(f"Unknown summary length: {length}")
        return self._summary_templates[length]


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    step_name: str
    prompt: str


@dataclass
class WorkflowNode:
    """A node in the workflow graph."""

    step: WorkflowStep
    is_parallel: bool = False
    condition: str | None = None
    parallel_group: int = -1


class WorkflowComposer:
    """Composes multi-step document processing workflows."""

    def __init__(self, library: TemplateLibrary) -> None:
        """Initialize with a template library."""
        self._library = library
        self._nodes: list[WorkflowNode] = []
        self._parallel_group_counter = 0

    def add_step(self, step: WorkflowStep) -> "WorkflowComposer":
        """Add a step to the workflow."""
        self._nodes.append(WorkflowNode(step=step))
        return self

    def add_parallel_steps(self, steps: list[WorkflowStep]) -> "WorkflowComposer":
        """Add parallel steps (all receive same input)."""
        group_id = self._parallel_group_counter
        self._parallel_group_counter += 1

        for step in steps:
            self._nodes.append(WorkflowNode(
                step=step,
                is_parallel=True,
                parallel_group=group_id,
            ))
        return self

    def add_conditional_step(
        self,
        step: WorkflowStep,
        condition: str,
    ) -> "WorkflowComposer":
        """Add a conditional step."""
        self._nodes.append(WorkflowNode(step=step, condition=condition))
        return self

    def compose(self, document: str, variables: dict[str, Any] | None = None) -> list[str]:
        """Compose all prompts for the workflow."""
        prompts = []
        vars_dict = variables or {}
        vars_dict["document"] = document

        # Track outputs for chaining
        extraction_output = ""
        analysis_outputs: list[str] = []

        for node in self._nodes:
            # Build context variables
            step_vars = vars_dict.copy()
            step_vars["extraction"] = extraction_output
            step_vars["analysis"] = "\n---\n".join(analysis_outputs) if analysis_outputs else ""

            # Render the step
            prompt = node.step.render(document, step_vars)
            prompts.append(prompt)

            # Track outputs based on step type
            if "extraction" in node.step.name.lower():
                extraction_output = f"[Output of {node.step.name}]"
            elif "analysis" in node.step.name.lower():
                analysis_outputs.append(f"[Output of {node.step.name}]")

        return prompts


def create_contract_review_workflow(library: TemplateLibrary) -> WorkflowComposer:
    """Create a workflow for reviewing contracts."""
    composer = WorkflowComposer(library)

    # Step 1: Extract key information
    composer.add_step(library.get_extraction_step("contract"))

    # Step 2: Parallel analyses
    composer.add_parallel_steps([
        library.get_analysis_step("risk"),
        library.get_analysis_step("compliance"),
    ])

    # Step 3: Generate summary
    composer.add_step(library.get_summarization_step("standard"))

    return composer


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
    print("Test passed!")


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
        print(prompt[:300] + "..." if len(prompt) > 300 else prompt)

    assert len(prompts) == 4  # extraction + 2 parallel analyses + summary
    print("\nTest passed!")


def test_parallel_workflow() -> None:
    """Test parallel step execution."""
    library = TemplateLibrary()
    composer = WorkflowComposer(library)

    composer.add_step(library.get_extraction_step("document"))
    composer.add_parallel_steps([
        library.get_analysis_step("sentiment"),
        library.get_analysis_step("risk"),
    ])
    composer.add_step(library.get_summarization_step("standard"))

    prompts = composer.compose("Sample document content...")

    print(f"\nParallel workflow generated {len(prompts)} prompts")
    assert len(prompts) == 4
    print("Test passed!")


if __name__ == "__main__":
    test_template_library()
    test_workflow_composition()
    test_parallel_workflow()
    print("\nAll tests passed!")
