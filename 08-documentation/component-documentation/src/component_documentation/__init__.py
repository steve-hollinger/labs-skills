"""Component Documentation - Learn to document APIs, READMEs, and code.

This module provides tools and patterns for creating effective documentation
for software components including libraries, APIs, and modules.
"""

from component_documentation.models import (
    ReadmeSection,
    ReadmeDocument,
    ApiEndpoint,
    ApiDocumentation,
    DocstringInfo,
    DocumentationScore,
)
from component_documentation.readme_builder import ReadmeBuilder, generate_readme
from component_documentation.api_docs import document_endpoint, generate_api_docs
from component_documentation.code_docs import analyze_docstring, check_documentation

__all__ = [
    "ReadmeSection",
    "ReadmeDocument",
    "ApiEndpoint",
    "ApiDocumentation",
    "DocstringInfo",
    "DocumentationScore",
    "ReadmeBuilder",
    "generate_readme",
    "document_endpoint",
    "generate_api_docs",
    "analyze_docstring",
    "check_documentation",
]
