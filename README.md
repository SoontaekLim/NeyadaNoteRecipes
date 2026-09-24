# NeyadaNoteRecipes

Official public recipe repository for NeyadaNote.

NeyadaNoteRecipes defines the portable recipe format used by NeyadaNote and stores the source files for official recipes.

## Design principles

- `recipe.json` is the machine-readable source of truth.
- `README.md` is the human-readable representation of the same recipe.
- Images are optional assets referenced with relative paths.
- A distributable `.neyada-recipe` package will be generated from the source files.
- A recipe is considered official because it is published through the official catalog, not because of a flag inside the recipe file.

## Repository layout

```text
schema/
  recipe-v1.schema.json

recipes/
  <recipe-id>/
    recipe.json
    README.md
    images/          # optional

scripts/
  validate_recipes.py

.github/workflows/
  validate.yml
```

## Recipe format v1

Every recipe declares:

- `format: "neyadanote.recipe"`
- `schemaVersion: 1`
- a stable recipe `id`
- title, summary and tags
- ingredients with name and amount
- ordered cooking steps
- optional serving count and image references

The JSON Schema lives at [schema/recipe-v1.schema.json](schema/recipe-v1.schema.json).

See [recipes/pork-kimchi-jjigae](recipes/pork-kimchi-jjigae) for a complete example.

## Validation

Install the validator and run the repository checks locally:

```bash
python -m pip install "jsonschema~=4.23"
python scripts/validate_recipes.py
```

Pull requests that change recipes, schema, or validation code run the same checks automatically.

## Packaging and distribution

Source files are kept easy to review in Git. Generated `.neyada-recipe` packages and `catalog.json` are intentionally not committed as duplicated source data. A later publishing workflow will build them and expose them to the NeyadaNote app.
