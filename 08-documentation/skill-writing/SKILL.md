---
name: writing-agent-skills
description: Create effective Agent Skills with SKILL.md files following Anthropic's format. Use when creating new skills or improving skill documentation.
---

# Skill Writing

## Quick Start
```yaml
---
name: processing-pdfs
description: This skill teaches PDF extraction. Use when working with PDF files.
---

# PDF Processing

## Quick Start
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Key Points
- Text extraction
- Form filling
- Page merging

## More Detail
- [docs/concepts.md](docs/concepts.md)
```

## Key Points
- Gerund naming (verb-ing)
- Concise descriptions
- Progressive disclosure

## Common Mistakes
1. **Verbose descriptions** - Keep under 1024 chars, start with "This skill teaches..."
2. **Missing triggers** - Always include "Use when..." in description
3. **Over-explaining** - Claude is smart; only add what it doesn't know

## More Detail
- [docs/concepts.md](docs/concepts.md) - Anthropic's official guidelines
- [docs/patterns.md](docs/patterns.md) - Templates and examples
