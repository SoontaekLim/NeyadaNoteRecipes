# NeyadaNoteRecipes

Official public recipe repository for NeyadaNote.

NeyadaNoteRecipes defines the portable recipe format used by NeyadaNote and stores the source files for official recipes.

## Design principles

- `recipe.json` is the machine-readable source of truth.
- `README.md` is the human-readable representation of the same recipe.
- Images are optional assets referenced with relative paths.
- A distributable `.neyada-recipe` package is generated from the source files.
- A recipe is considered official because it is published through the official catalog, not because of a flag inside the recipe file.

## Repository layout

```text
schema/
  recipe-v1.schema.json
  catalog-v1.schema.json

recipes/
  <recipe-id>/
    recipe.json
    README.md
    images/          # optional, shared by locale variants
    locales/
      <locale>/
        recipe.json
        README.md

scripts/
  validate_recipes.py
  build_dist.py
  test_distribution.py

.github/workflows/
  validate.yml
  deploy-pages.yml
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
python scripts/test_distribution.py
```

Pull requests that change recipes, schema, scripts, or distribution workflows run these checks automatically.

## Packaging and distribution

Run:

```bash
python scripts/build_dist.py
```

The generated `dist/` directory contains:

```text
dist/
  catalog.json
  index.html
  packages/
    <recipe-id>.neyada-recipe
    <recipe-id>.<locale>.neyada-recipe
```

A `.neyada-recipe` file is a deterministic ZIP package whose archive root contains `recipe.json`, `README.md`, and the image assets referenced by the recipe. Generated files are not committed; GitHub Actions builds them from the reviewed source files.

The root `recipe.json` remains the legacy/default locale package for compatibility with older app versions. Additional official translations live under `locales/<locale>/` and keep the same stable recipe ID. Shared image assets remain under the recipe root.

The catalog contract is defined by [schema/catalog-v1.schema.json](schema/catalog-v1.schema.json). Each catalog entry keeps the legacy top-level package metadata and may also expose a `variants` array containing locale-specific package metadata. This lets older clients continue using the default package while newer clients select the best locale variant. Relative URLs intentionally keep the Android app independent of the current hosting origin.

After GitHub Pages is enabled with **Source: GitHub Actions**, pushes to `main` publish the generated distribution. The default Pages catalog URL is expected to be:

`https://soontaeklim.github.io/NeyadaNoteRecipes/catalog.json`
