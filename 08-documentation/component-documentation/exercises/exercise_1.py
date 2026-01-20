"""Exercise 1: Write a README for an Existing Code Module

Below is a Python module that needs documentation. Your task is to
write a complete README that would help users understand and use
this code.

The Module:
- Name: text-analyzer
- Purpose: Analyze text for various metrics
- Functions: word_count, sentence_count, readability_score, keyword_frequency

Requirements:
1. Include all essential README sections
2. Provide working code examples
3. Document configuration options
4. Explain error cases

Target:
- README validation score: 80+
- All essential sections present
- At least 3 code examples
"""

# The module to document
MODULE_CODE = '''
"""Text Analyzer - Analyze text for various metrics."""

from collections import Counter
import re
from typing import Optional


class TextAnalyzer:
    """Analyzer for text metrics and statistics."""

    def __init__(self, text: str, language: str = "en"):
        self.text = text
        self.language = language
        self._words = None
        self._sentences = None

    @property
    def words(self) -> list[str]:
        if self._words is None:
            self._words = re.findall(r\'\\b\\w+\\b\', self.text.lower())
        return self._words

    @property
    def sentences(self) -> list[str]:
        if self._sentences is None:
            self._sentences = re.split(r\'[.!?]+\', self.text)
            self._sentences = [s.strip() for s in self._sentences if s.strip()]
        return self._sentences

    def word_count(self) -> int:
        """Count the number of words in the text."""
        return len(self.words)

    def sentence_count(self) -> int:
        """Count the number of sentences in the text."""
        return len(self.sentences)

    def average_word_length(self) -> float:
        """Calculate average word length."""
        if not self.words:
            return 0.0
        return sum(len(w) for w in self.words) / len(self.words)

    def readability_score(self) -> float:
        """Calculate Flesch reading ease score.

        Returns:
            Score from 0-100. Higher = easier to read.
            - 90-100: Very Easy
            - 60-70: Standard
            - 0-30: Very Difficult
        """
        words = self.word_count()
        sentences = self.sentence_count()
        syllables = sum(self._count_syllables(w) for w in self.words)

        if words == 0 or sentences == 0:
            return 0.0

        return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)

    def keyword_frequency(
        self,
        top_n: int = 10,
        min_length: int = 3,
        exclude: Optional[list[str]] = None,
    ) -> list[tuple[str, int]]:
        """Get most frequent keywords.

        Args:
            top_n: Number of keywords to return.
            min_length: Minimum word length to consider.
            exclude: Words to exclude from results.

        Returns:
            List of (word, count) tuples.
        """
        exclude = exclude or []
        exclude_set = set(w.lower() for w in exclude)
        exclude_set.update(["the", "and", "is", "it", "to", "of", "in", "for"])

        filtered = [w for w in self.words
                    if len(w) >= min_length and w not in exclude_set]

        return Counter(filtered).most_common(top_n)

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower()
        count = len(re.findall(r\'[aeiouy]+\', word))
        if word.endswith(\'e\'):
            count -= 1
        return max(1, count)


def analyze(text: str, language: str = "en") -> dict:
    """Quick analysis of text.

    Args:
        text: Text to analyze.
        language: Language code (default "en").

    Returns:
        Dictionary with analysis results.
    """
    analyzer = TextAnalyzer(text, language)
    return {
        "word_count": analyzer.word_count(),
        "sentence_count": analyzer.sentence_count(),
        "avg_word_length": round(analyzer.average_word_length(), 2),
        "readability_score": round(analyzer.readability_score(), 2),
        "top_keywords": analyzer.keyword_frequency(top_n=5),
    }
'''


def exercise() -> str:
    """Write a complete README for the text-analyzer module.

    Returns:
        README content as a markdown string.
    """
    # TODO: Write your README here
    readme = """# text-analyzer

TODO: Write a complete README for this module.

## Installation

TODO: Add installation instructions

## Quick Start

TODO: Add quick start example

"""
    return readme


def validate_solution() -> None:
    """Validate your README."""
    from component_documentation.readme_builder import validate_readme
    from rich.console import Console

    console = Console()
    readme = exercise()

    console.print("\n[bold]Exercise 1: README for text-analyzer[/bold]\n")

    score = validate_readme(readme)

    console.print(f"Score: [{('green' if score.is_passing else 'red')}]{score.score}/100[/]")

    # Check specific requirements
    checks = [
        ("Has title", "# text-analyzer" in readme or "# Text Analyzer" in readme),
        ("Has installation", "install" in readme.lower()),
        ("Has quick start", "quick start" in readme.lower() or "getting started" in readme.lower()),
        ("Has code examples", readme.count("```") >= 6),  # At least 3 examples
        ("Has API reference", "api" in readme.lower() or "function" in readme.lower()),
    ]

    console.print("\n[bold]Checklist:[/bold]")
    for name, passed in checks:
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        console.print(f"  {status} - {name}")

    if score.issues:
        console.print("\n[red]Issues:[/red]")
        for issue in score.issues:
            console.print(f"  - {issue}")

    if all(passed for _, passed in checks) and score.is_passing:
        console.print("\n[bold green]All requirements met![/bold green]")
    else:
        console.print("\n[yellow]Keep working on it![/yellow]")


if __name__ == "__main__":
    validate_solution()
