# Core Concepts

## Overview

Agent Skills are modular packages that extend Claude's capabilities by providing specialized knowledge, workflows, and tools. This document covers Anthropic's official guidelines for creating effective skills.

## Concept 1: YAML Frontmatter

### What It Is

Every SKILL.md starts with YAML frontmatter containing `name` and `description` fields. These are the ONLY fields Claude reads to determine when to use the skill.

### Why It Matters

The frontmatter is always loaded into context (~100 tokens). It's the primary triggering mechanism - Claude uses it to decide which skill to activate from potentially 100+ available skills.

### How It Works

```yaml
---
name: processing-pdfs
description: This skill teaches PDF text extraction and form filling. Use when working with PDF files or extracting document content.
---
```

**Name field rules:**
- Maximum 64 characters
- Lowercase letters, numbers, and hyphens only
- Use gerund form (verb-ing): `processing-pdfs`, `analyzing-data`
- No reserved words: "anthropic", "claude"

**Description field rules:**
- Maximum 1024 characters
- Start with "This skill teaches..."
- Include "Use when..." trigger conditions
- Write in third person (not "I can help you..." or "You can use this...")
- Be specific - include key terms users might mention

## Concept 2: Progressive Disclosure

### What It Is

Skills use a three-level loading system to manage context efficiently:
1. Metadata (name + description) - Always in context
2. SKILL.md body - When skill triggers
3. Bundled resources - As needed by Claude

### Why It Matters

The context window is a public good. Your skill shares it with conversation history, other skills, and user requests. Progressive disclosure minimizes token usage.

### How It Works

```
skill-name/
├── SKILL.md              # Main instructions (loaded when triggered)
├── reference/
│   ├── api.md            # API docs (loaded as needed)
│   └── schemas.md        # Data schemas (loaded as needed)
└── scripts/
    └── validate.py       # Executed without loading code
```

**Key guidelines:**
- Keep SKILL.md body under 500 lines
- Split content into separate files when approaching this limit
- Keep references one level deep from SKILL.md
- For files >100 lines, include a table of contents

## Concept 3: Conciseness

### What It Is

Skills should contain only information Claude doesn't already have. Claude is smart - don't explain basics.

### Why It Matters

Every token in your skill competes with conversation history and other context. Verbose skills waste tokens and dilute important information.

### How It Works

**Good - Concise (50 tokens):**
```markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

**Bad - Verbose (150 tokens):**
```markdown
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use...
```

**Test each piece of information:**
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

## Concept 4: Degrees of Freedom

### What It Is

Match the level of specificity to the task's fragility and variability.

### Why It Matters

Some tasks need exact instructions (database migrations), others benefit from Claude's judgment (code reviews). Matching specificity to task type improves outcomes.

### How It Works

**High freedom** (text-based instructions) - Multiple approaches valid:
```markdown
## Code review process
1. Analyze code structure
2. Check for potential bugs
3. Suggest improvements
```

**Medium freedom** (pseudocode/templates) - Preferred pattern exists:
```markdown
## Generate report
Use this template and customize:
```python
def generate_report(data, format="markdown"):
    # Process data, generate output
```
```

**Low freedom** (specific scripts) - Operations are fragile:
```markdown
## Database migration
Run exactly this script:
```bash
python scripts/migrate.py --verify --backup
```
Do not modify the command.
```

## Concept 5: Skill Structure

### What It Is

A skill is a directory containing SKILL.md and optional resources.

### Why It Matters

Consistent structure makes skills predictable and maintainable.

### How It Works

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/     # Executable code
    ├── references/  # Documentation loaded as needed
    └── assets/      # Files used in output (templates, etc.)
```

**What NOT to include:**
- README.md (except for labs-skills learning context)
- INSTALLATION_GUIDE.md
- CHANGELOG.md
- Any auxiliary documentation

The skill should only contain information needed for an AI agent to do the job.

## Summary

Key takeaways:

1. **Frontmatter is critical** - Name (gerund, 64 chars) + Description ("This skill teaches...", "Use when...")
2. **Be concise** - Claude is smart; only add what it doesn't know
3. **Progressive disclosure** - SKILL.md <500 lines, split into reference files
4. **Match freedom to task** - High freedom for flexible tasks, low for fragile ones
5. **Consistent structure** - SKILL.md + optional scripts/references/assets
