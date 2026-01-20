# Common Patterns

## Overview

This document covers patterns for writing effective Agent Skills, based on Anthropic's official best practices.

## Pattern 1: Minimal SKILL.md Format

### When to Use

When creating skills for the labs-skills repository.

### Implementation

```yaml
---
name: gerund-skill-name
description: [What it does]. Use when [trigger conditions].
---

# Skill Title

## Quick Start
```[language]
// Concise example (5-15 lines)
```

## Key Points
- Most important concept
- Second most important
- Third most important

## Common Mistakes
1. **Mistake name** - How to fix it

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts
- [docs/patterns.md](docs/patterns.md) - Code patterns
```

### Example

```yaml
---
name: validating-jwt-tokens
description: Validate JWT tokens with PyJWT. Use when implementing authentication or verifying tokens.
---

# JWT Validation

## Quick Start
```python
import jwt

payload = jwt.decode(
    token, secret,
    algorithms=["HS256"],
    options={"require": ["exp", "sub"]}
)
```

## Key Points
- Always specify algorithms
- Validate required claims
- Handle expiration

## Common Mistakes
1. **Not specifying algorithms** - Always set `algorithms=["HS256"]`
2. **Accepting expired tokens** - Include `exp` in required claims

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts
- [docs/patterns.md](docs/patterns.md) - Code patterns
```

### Pitfalls to Avoid

- Key Points should be concise phrases, not paragraphs
- Quick Start should be ~10-15 lines, not 50
- Description should be direct, not "This skill teaches..."

## Pattern 2: Progressive Disclosure

### When to Use

When SKILL.md approaches 500 lines or contains domain-specific details.

### Implementation

```markdown
# BigQuery Analysis

## Quick reference
- Finance queries: See [reference/finance.md](reference/finance.md)
- Sales metrics: See [reference/sales.md](reference/sales.md)
- Product data: See [reference/product.md](reference/product.md)

## Quick search
```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
```
```

### Example Directory Structure

```
bigquery-skill/
├── SKILL.md (overview, <200 lines)
└── reference/
    ├── finance.md (revenue, billing)
    ├── sales.md (pipeline, accounts)
    └── product.md (API usage)
```

### Pitfalls to Avoid

- Don't nest references more than one level deep
- Include table of contents for files >100 lines
- Don't duplicate information between SKILL.md and references

## Pattern 3: Workflow with Validation

### When to Use

For complex, multi-step tasks where errors are costly.

### Implementation

```markdown
## Document editing workflow

1. Make edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py dir/`
3. If validation fails:
   - Review the error message
   - Fix the issues
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python scripts/pack.py dir/ output.docx`
```

### Example

```markdown
## Form filling workflow

Copy this checklist:
```
- [ ] Step 1: Analyze form (run analyze_form.py)
- [ ] Step 2: Create mapping (edit fields.json)
- [ ] Step 3: Validate (run validate_fields.py)
- [ ] Step 4: Fill form (run fill_form.py)
- [ ] Step 5: Verify output
```

**Step 1: Analyze the form**
Run: `python scripts/analyze_form.py input.pdf`

**Step 2: Create field mapping**
Edit `fields.json` to add values.

**Step 3: Validate**
Run: `python scripts/validate_fields.py fields.json`
Fix any errors before continuing.
```

### Pitfalls to Avoid

- Always include validation steps for destructive operations
- Make scripts verbose with helpful error messages
- Don't skip verification even for "simple" tasks

## Pattern 4: Naming Conventions

### When to Use

Always, for consistency across skills.

### Implementation

**Skill names (gerund form):**
- `processing-pdfs`
- `analyzing-spreadsheets`
- `validating-jwt-tokens`
- `managing-databases`

**File paths:**
- Always use forward slashes: `reference/guide.md`
- Never Windows paths: `reference\guide.md`

**Terminology:**
- Pick one term and use it throughout
- Good: Always "API endpoint"
- Bad: Mix "endpoint", "URL", "route", "path"

## Pattern 5: Examples Pattern

### When to Use

When output quality depends on seeing examples.

### Implementation

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly
Output:
```
fix(reports): correct date formatting in timezone conversion
```

Follow this style: type(scope): brief description
```

### Pitfalls to Avoid

- Keep examples concrete, not abstract
- Show input AND output
- Include edge cases if relevant

## Anti-Patterns

### Anti-Pattern 1: Verbose Descriptions

```yaml
# Bad
description: I can help you process PDF files and extract text from them...

# Good
description: This skill teaches PDF text extraction. Use when working with PDF files.
```

### Anti-Pattern 2: Over-explaining Basics

```markdown
# Bad
PDF (Portable Document Format) is a file format developed by Adobe...

# Good
Use pdfplumber for text extraction:
```python
import pdfplumber
```
```

### Anti-Pattern 3: Too Many Options

```markdown
# Bad
You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image...

# Good
Use pdfplumber for text extraction.
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| New labs-skills skill | Pattern 1: Labs-Skills Format |
| Large skill (>300 lines) | Pattern 2: Progressive Disclosure |
| Multi-step risky task | Pattern 3: Workflow with Validation |
| All skills | Pattern 4: Naming Conventions |
| Output-sensitive tasks | Pattern 5: Examples Pattern |
