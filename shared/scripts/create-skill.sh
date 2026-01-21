#!/bin/bash
# Create a new skill from template
# Usage: ./create-skill.sh <type> <name> <category>
# Example: ./create-skill.sh python my-skill 01-language-frameworks/python

set -e

TYPE=$1
NAME=$2
CATEGORY=$3

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEMPLATE_DIR="$REPO_ROOT/shared/templates/$TYPE"
TARGET_DIR="$REPO_ROOT/$CATEGORY/$NAME"

if [ -z "$TYPE" ] || [ -z "$NAME" ] || [ -z "$CATEGORY" ]; then
    echo "Usage: $0 <type> <name> <category>"
    echo "  type: python, go, frontend, or ios"
    echo "  name: skill name (kebab-case)"
    echo "  category: path like 01-language-frameworks/python"
    exit 1
fi

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template not found for type '$TYPE'"
    echo "Available types: python, go, frontend, ios"
    exit 1
fi

if [ -d "$TARGET_DIR" ]; then
    echo "Error: Skill already exists at $TARGET_DIR"
    exit 1
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy template
cp -r "$TEMPLATE_DIR"/* "$TARGET_DIR/"

# Replace placeholders in all files
find "$TARGET_DIR" -type f -exec sed -i '' "s/{{SKILL_NAME}}/$NAME/g" {} \; 2>/dev/null || \
find "$TARGET_DIR" -type f -exec sed -i "s/{{SKILL_NAME}}/$NAME/g" {} \;

# Convert kebab-case to snake_case for Python module names
SNAKE_NAME=$(echo "$NAME" | tr '-' '_')
find "$TARGET_DIR" -type f -exec sed -i '' "s/{{SNAKE_NAME}}/$SNAKE_NAME/g" {} \; 2>/dev/null || \
find "$TARGET_DIR" -type f -exec sed -i "s/{{SNAKE_NAME}}/$SNAKE_NAME/g" {} \;

# Convert kebab-case to PascalCase for class names
PASCAL_NAME=$(echo "$NAME" | sed -r 's/(^|-)(\w)/\U\2/g')
find "$TARGET_DIR" -type f -exec sed -i '' "s/{{PASCAL_NAME}}/$PASCAL_NAME/g" {} \; 2>/dev/null || \
find "$TARGET_DIR" -type f -exec sed -i "s/{{PASCAL_NAME}}/$PASCAL_NAME/g" {} \;

# Rename directories if needed
if [ "$TYPE" = "python" ] && [ -d "$TARGET_DIR/src/skill_name" ]; then
    mv "$TARGET_DIR/src/skill_name" "$TARGET_DIR/src/$SNAKE_NAME"
fi

# Rename iOS directories if needed
if [ "$TYPE" = "ios" ]; then
    if [ -d "$TARGET_DIR/Sources/SkillName" ]; then
        mv "$TARGET_DIR/Sources/SkillName" "$TARGET_DIR/Sources/$PASCAL_NAME"
    fi
    if [ -d "$TARGET_DIR/Tests/SkillNameTests" ]; then
        mv "$TARGET_DIR/Tests/SkillNameTests" "$TARGET_DIR/Tests/${PASCAL_NAME}Tests"
    fi
fi

echo "Created skill: $TARGET_DIR"
