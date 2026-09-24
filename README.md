# NeyadaNoteRecipes

Official public recipe repository for NeyadaNote.

This repository defines the portable NeyadaNote recipe format and stores the source files for official recipes. Structured JSON is the source of truth for apps and tools, while Markdown provides a human-readable representation.

## Planned structure

```text
schema/        JSON Schema definitions
recipes/       Official recipe source files
.github/       Validation and publishing workflows
```

Distributable `.neyada-recipe` packages and the public catalog will be generated from these sources rather than maintained as duplicated source files.
