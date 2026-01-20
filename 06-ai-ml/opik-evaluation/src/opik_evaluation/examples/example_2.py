"""Example 2: Tracing LLM Calls

This example demonstrates how to trace LLM interactions for debugging
and analysis. Since we're not using real Opik here, we'll implement
a simple tracing pattern that mirrors Opik's approach.

Key concepts:
- Function-level tracing with decorators
- Span hierarchies for nested calls
- Recording inputs, outputs, and timing
- Analyzing trace data
"""

import functools
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class Span:
    """Represents a traced operation span.

    Attributes:
        id: Unique span identifier
        name: Name of the operation
        start_time: When the span started
        end_time: When the span ended
        inputs: Input arguments
        output: Return value
        parent_id: Parent span ID (for nested calls)
        metadata: Additional metadata
    """

    id: str
    name: str
    start_time: datetime
    end_time: datetime | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    output: Any = None
    parent_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Calculate span duration in milliseconds."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds() * 1000


class Tracer:
    """Simple tracer for recording function calls.

    This mimics Opik's tracing functionality for educational purposes.
    """

    _instance: "Tracer | None" = None
    _current_span_id: str | None = None

    def __init__(self) -> None:
        self.spans: list[Span] = []
        self._span_stack: list[str] = []

    @classmethod
    def get_instance(cls) -> "Tracer":
        """Get the global tracer instance."""
        if cls._instance is None:
            cls._instance = Tracer()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the global tracer."""
        cls._instance = None

    def start_span(
        self,
        name: str,
        inputs: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Span:
        """Start a new span."""
        parent_id = self._span_stack[-1] if self._span_stack else None

        span = Span(
            id=str(uuid.uuid4())[:8],
            name=name,
            start_time=datetime.now(),
            inputs=inputs or {},
            parent_id=parent_id,
            metadata=metadata or {},
        )

        self._span_stack.append(span.id)
        return span

    def end_span(self, span: Span, output: Any = None) -> None:
        """End a span and record its output."""
        span.end_time = datetime.now()
        span.output = output
        self.spans.append(span)

        if self._span_stack and self._span_stack[-1] == span.id:
            self._span_stack.pop()

    def get_trace_tree(self) -> dict[str, Any]:
        """Get spans organized as a tree structure."""
        root_spans = [s for s in self.spans if s.parent_id is None]
        return {
            "traces": [self._build_tree(s) for s in root_spans]
        }

    def _build_tree(self, span: Span) -> dict[str, Any]:
        """Build a tree structure from a span."""
        children = [s for s in self.spans if s.parent_id == span.id]
        return {
            "id": span.id,
            "name": span.name,
            "duration_ms": span.duration_ms,
            "inputs": span.inputs,
            "output": str(span.output)[:100] if span.output else None,
            "children": [self._build_tree(c) for c in children],
        }


def track(func: F) -> F:
    """Decorator for tracing function calls.

    This mimics Opik's @track decorator.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tracer = Tracer.get_instance()

        # Capture inputs
        inputs = {"args": args, "kwargs": kwargs}

        # Start span
        span = tracer.start_span(name=func.__name__, inputs=inputs)

        try:
            # Execute function
            result = func(*args, **kwargs)

            # End span with result
            tracer.end_span(span, output=result)

            return result
        except Exception as e:
            # End span with error
            tracer.end_span(span, output=f"Error: {e}")
            raise

    return wrapper  # type: ignore[return-value]


# Simulated LLM functions


@track
def retrieve_context(query: str) -> list[str]:
    """Retrieve relevant context documents (simulated)."""
    # Simulate retrieval
    time.sleep(0.05)

    contexts = {
        "capital": ["France is a country in Western Europe.", "Paris is the capital of France."],
        "planet": ["Jupiter is the largest planet.", "Saturn has beautiful rings."],
        "author": ["Shakespeare wrote many famous plays.", "Romeo and Juliet is a tragedy."],
    }

    for key, docs in contexts.items():
        if key in query.lower():
            return docs

    return ["No relevant context found."]


@track
def generate_response(query: str, context: list[str]) -> str:
    """Generate response using context (simulated LLM call)."""
    # Simulate LLM generation
    time.sleep(0.1)

    # Simple response generation based on query and context
    if "capital" in query.lower() and "Paris" in str(context):
        return "The capital of France is Paris."
    elif "planet" in query.lower() and "Jupiter" in str(context):
        return "Jupiter is the largest planet in our solar system."
    elif "wrote" in query.lower() and "Shakespeare" in str(context):
        return "William Shakespeare wrote Romeo and Juliet."

    return f"Based on the context, I can provide information about: {context[0]}"


@track
def format_response(response: str, style: str = "formal") -> str:
    """Format the response in a specific style."""
    time.sleep(0.02)

    if style == "formal":
        return f"I would like to inform you that {response.lower()}"
    elif style == "casual":
        return f"Hey! So, {response.lower()}"
    return response


@track
def rag_pipeline(query: str) -> str:
    """Complete RAG pipeline that combines retrieval and generation."""
    # This creates a hierarchy of traced spans
    context = retrieve_context(query)
    response = generate_response(query, context)
    formatted = format_response(response, style="formal")
    return formatted


def print_trace_tree(tree: dict[str, Any], indent: int = 0) -> None:
    """Pretty print a trace tree."""
    for trace in tree.get("traces", [tree]):
        prefix = "  " * indent
        name = trace.get("name", "unknown")
        duration = trace.get("duration_ms", 0)
        print(f"{prefix}- {name} ({duration:.1f}ms)")

        if trace.get("inputs"):
            inputs = trace["inputs"]
            args = inputs.get("args", ())
            kwargs = inputs.get("kwargs", {})
            if args:
                print(f"{prefix}  Inputs: {args}")
            if kwargs:
                print(f"{prefix}  Kwargs: {kwargs}")

        if trace.get("output"):
            print(f"{prefix}  Output: {trace['output'][:60]}...")

        for child in trace.get("children", []):
            print_trace_tree({"traces": [child]}, indent + 1)


def main() -> None:
    """Run the tracing example."""
    print("Example 2: Tracing LLM Calls")
    print("=" * 60)

    # Reset tracer
    Tracer.reset()

    # Run some traced operations
    print("\n1. Running RAG Pipeline:")
    print("-" * 40)

    queries = [
        "What is the capital of France?",
        "What is the largest planet?",
        "Who wrote Romeo and Juliet?",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        result = rag_pipeline(query)
        print(f"Result: {result}")

    # Analyze traces
    print("\n2. Trace Analysis:")
    print("-" * 40)

    tracer = Tracer.get_instance()
    print(f"Total spans recorded: {len(tracer.spans)}")

    # Group by function name
    from collections import Counter

    span_counts = Counter(s.name for s in tracer.spans)
    print("\nSpan counts by function:")
    for name, count in span_counts.most_common():
        print(f"  {name}: {count}")

    # Calculate average durations
    print("\nAverage durations by function:")
    from collections import defaultdict

    durations: dict[str, list[float]] = defaultdict(list)
    for span in tracer.spans:
        durations[span.name].append(span.duration_ms)

    for name, durs in sorted(durations.items()):
        avg = sum(durs) / len(durs)
        print(f"  {name}: {avg:.1f}ms")

    # Show trace tree
    print("\n3. Trace Tree:")
    print("-" * 40)

    tree = tracer.get_trace_tree()
    print_trace_tree(tree)

    # Find slowest operations
    print("\n4. Slowest Operations:")
    print("-" * 40)

    sorted_spans = sorted(tracer.spans, key=lambda s: s.duration_ms, reverse=True)
    for span in sorted_spans[:5]:
        print(f"  {span.name}: {span.duration_ms:.1f}ms")

    print("\n" + "=" * 60)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
