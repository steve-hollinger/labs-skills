"""System Prompts - Learn prompt engineering for AI system prompts.

This module provides tools and patterns for creating effective system prompts
that guide AI behavior consistently and effectively.
"""

from system_prompts.models import (
    SystemPrompt,
    PromptComponent,
    AnalysisResult,
    PromptIssue,
    IssueSeverity,
)
from system_prompts.builder import PromptBuilder
from system_prompts.analyzer import analyze_prompt, quick_score
from system_prompts.templates import (
    code_reviewer_template,
    technical_writer_template,
    coding_assistant_template,
)

__all__ = [
    "SystemPrompt",
    "PromptComponent",
    "AnalysisResult",
    "PromptIssue",
    "IssueSeverity",
    "PromptBuilder",
    "analyze_prompt",
    "quick_score",
    "code_reviewer_template",
    "technical_writer_template",
    "coding_assistant_template",
]
