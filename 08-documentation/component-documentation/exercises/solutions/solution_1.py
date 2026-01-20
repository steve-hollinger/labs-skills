"""Solution for Exercise 1: README for text-analyzer module."""


def solution() -> str:
    """Reference solution for Exercise 1.

    Returns:
        Complete README for text-analyzer.
    """
    return '''# text-analyzer

A Python library for analyzing text and extracting various metrics including word count, readability scores, and keyword frequency.

## Features

- **Word and sentence counting** - Accurate tokenization for multiple languages
- **Readability scoring** - Flesch reading ease score calculation
- **Keyword extraction** - Find most frequent meaningful words
- **Customizable analysis** - Filter stop words, set minimum word lengths
- **Efficient processing** - Lazy evaluation with caching

## Installation

```bash
pip install text-analyzer
```

## Quick Start

```python
from text_analyzer import analyze

text = """
Natural language processing is a field of computer science.
It focuses on the interaction between computers and humans.
NLP enables computers to understand human language.
"""

result = analyze(text)
print(f"Words: {result['word_count']}")
print(f"Sentences: {result['sentence_count']}")
print(f"Readability: {result['readability_score']}")
print(f"Top keywords: {result['top_keywords']}")
```

Output:
```
Words: 28
Sentences: 3
Readability: 42.5
Top keywords: [('language', 2), ('computers', 2), ('natural', 1)]
```

## Usage

### Basic Analysis

```python
from text_analyzer import TextAnalyzer

analyzer = TextAnalyzer("Your text goes here.")
print(analyzer.word_count())      # 4
print(analyzer.sentence_count())  # 1
```

### Readability Score

The readability score uses the Flesch Reading Ease formula:

```python
analyzer = TextAnalyzer(article_text)
score = analyzer.readability_score()

# Interpretation:
# 90-100: Very Easy (5th grade)
# 60-70:  Standard (8th-9th grade)
# 0-30:   Very Difficult (College graduate)
```

### Keyword Extraction

Extract the most frequent meaningful words:

```python
analyzer = TextAnalyzer(document_text)

# Get top 10 keywords
keywords = analyzer.keyword_frequency(top_n=10)

# Customize extraction
keywords = analyzer.keyword_frequency(
    top_n=5,
    min_length=4,           # Minimum word length
    exclude=["custom", "words"]  # Additional stop words
)
```

### Quick Analysis Function

For one-off analysis, use the convenience function:

```python
from text_analyzer import analyze

result = analyze(text, language="en")
# Returns dict with all metrics
```

## API Reference

### `TextAnalyzer` Class

```python
TextAnalyzer(text: str, language: str = "en")
```

**Parameters:**
- `text` - The text to analyze
- `language` - Language code (default: "en")

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `word_count()` | `int` | Number of words |
| `sentence_count()` | `int` | Number of sentences |
| `average_word_length()` | `float` | Mean word length |
| `readability_score()` | `float` | Flesch reading ease (0-100) |
| `keyword_frequency(top_n, min_length, exclude)` | `list[tuple]` | Top keywords with counts |

### `analyze()` Function

```python
analyze(text: str, language: str = "en") -> dict
```

Returns a dictionary with all metrics:
```python
{
    "word_count": int,
    "sentence_count": int,
    "avg_word_length": float,
    "readability_score": float,
    "top_keywords": list[tuple[str, int]]
}
```

## Configuration

The library uses sensible defaults but can be customized:

| Option | Default | Description |
|--------|---------|-------------|
| `language` | `"en"` | Language for tokenization |
| `top_n` | `10` | Number of keywords to return |
| `min_length` | `3` | Minimum keyword length |

## Error Handling

```python
from text_analyzer import TextAnalyzer

# Empty text returns zero counts
analyzer = TextAnalyzer("")
analyzer.word_count()  # Returns 0
analyzer.readability_score()  # Returns 0.0

# Unicode is handled correctly
analyzer = TextAnalyzer("Caf\\u00e9 \\u4e2d\\u6587 \\u0420\\u0443\\u0441\\u0441\\u043a\\u0438\\u0439")
analyzer.word_count()  # Returns 3
```

## Examples

### Analyzing a Document

```python
from text_analyzer import TextAnalyzer

with open("document.txt") as f:
    text = f.read()

analyzer = TextAnalyzer(text)

print("Document Statistics")
print("=" * 40)
print(f"Words: {analyzer.word_count()}")
print(f"Sentences: {analyzer.sentence_count()}")
print(f"Avg word length: {analyzer.average_word_length():.1f}")
print(f"Readability: {analyzer.readability_score():.1f}")
print()
print("Top 10 Keywords:")
for word, count in analyzer.keyword_frequency(10):
    print(f"  {word}: {count}")
```

### Comparing Multiple Texts

```python
from text_analyzer import analyze

texts = {
    "Technical": technical_doc,
    "Blog Post": blog_post,
    "Children's Book": kids_book,
}

for name, text in texts.items():
    result = analyze(text)
    print(f"{name}: Readability {result['readability_score']:.0f}")
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
'''


if __name__ == "__main__":
    from component_documentation.readme_builder import validate_readme
    from rich.console import Console

    console = Console()
    readme = solution()

    score = validate_readme(readme)

    console.print("[bold]Solution 1: text-analyzer README[/bold]\n")
    console.print(f"Score: [green]{score.score}/100[/green]")
    console.print(f"Word count: {len(readme.split())}")
