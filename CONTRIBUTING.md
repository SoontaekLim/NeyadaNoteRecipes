# Contributing Recipes

Thank you for contributing to **NeyadaNoteRecipes**, the official public recipe repository for NeyadaNote.

This guide describes the expected structure, content quality, localization, image requirements, validation steps, and pull request workflow for official recipe contributions.

> [!IMPORTANT]
> The current JSON Schema at [`schema/recipe-v1.schema.json`](schema/recipe-v1.schema.json) is the final machine-readable authority. This guide adds repository conventions for **official recipes**, which may be stricter than the schema's minimum requirements.

## Before you start

Before creating a recipe contribution:

1. Update from the latest `main`.
2. Check [`schema/recipe-v1.schema.json`](schema/recipe-v1.schema.json).
3. Check the existing [`recipes/`](recipes/) directory for the same or a substantially equivalent recipe.
4. Check open pull requests to avoid duplicate work.
5. Review the current validation workflow in [`.github/workflows/validate.yml`](.github/workflows/validate.yml).

Do not create a duplicate official recipe when the same recipe already exists.

For a new recipe, create a branch from the latest `main`. A typical branch name is:

```text
recipe/kimchi-fried-rice
```

## Contribution flow

A normal new-recipe contribution follows this sequence:

1. Choose a stable recipe ID.
2. Write the default Korean (`ko-KR`) `recipe.json`.
3. Write the matching Korean `README.md`.
4. Add the English (`en`) locale.
5. Add the English `README.md`.
6. Add the cover image.
7. Run validation.
8. Run distribution tests.
9. Build the distribution locally.
10. Open a pull request.
11. Confirm the GitHub Actions checks pass.

Generated distribution files are not committed.

## Recipe writing principles

Official recipes should be:

- practical for a home kitchen;
- reproducible with commonly available ingredients;
- understandable to a beginner;
- specific about ingredient quantities when practical;
- ordered according to the actual cooking process;
- no more complicated than necessary.

If you consult other recipes for general cooking knowledge, write the final recipe independently. Do not copy recipe prose from another website or publication.

Unless the dish naturally calls for another amount, use **2 servings** as the default for a new recipe.

## Recipe ID

Use a meaningful, stable, lowercase English ID in kebab-case.

Examples:

```text
pork-kimchi-jjigae
kimchi-fried-rice
doenjang-jjigae
```

The v1 schema permits:

```text
a-z  0-9  .  _  -
```

The recipe directory name and every localized `recipe.json` must use the same ID.

Once an ID has been published, do not rename it without a specific compatibility reason.

## Directory structure

A normal bilingual official recipe uses this structure:

```text
recipes/
  <recipe-id>/
    recipe.json
    README.md
    images/
      cover.webp
    locales/
      en/
        recipe.json
        README.md
        images/
          cover.webp
```

The recipe at the recipe root is the default variant and is normally `ko-KR`.

The English translation lives under `locales/en/`.

Both variants use the same recipe ID.

## `recipe.json`

Always validate against the current [`schema/recipe-v1.schema.json`](schema/recipe-v1.schema.json).

A typical official Korean recipe looks like this:

```json
{
  "format": "neyadanote.recipe",
  "schemaVersion": 1,
  "id": "recipe-id",
  "locale": "ko-KR",
  "title": "레시피 이름",
  "summary": "짧은 설명",
  "servings": 2,
  "coverImage": "images/cover.webp",
  "tags": ["분류", "한식"],
  "ingredients": [
    {"name": "재료", "amount": "수량"}
  ],
  "steps": [
    {"id": 1, "description": "조리 방법"}
  ]
}
```

For recipe format v1, these values are fixed:

```json
"format": "neyadanote.recipe",
"schemaVersion": 1
```

Official recipes should also specify a locale.

For the root Korean recipe:

```json
"locale": "ko-KR"
```

For the English variant:

```json
"locale": "en"
```

The schema supports portable user recipes with some blank or optional fields for compatibility. That does **not** mean official repository recipes should intentionally omit useful content. Official recipes are expected to include meaningful titles, summaries, ingredients, steps, locale information, serving count, and the standard cover image unless there is a specific reason not to.

## Ingredients

Use:

```json
{"name": "돼지고기 앞다리살", "amount": "150g"}
```

Prefer concrete measurements when practical.

Examples:

```text
200g
1/2개
1큰술
1작은술
500ml
약간
```

The ingredient list and cooking steps must agree. Do not introduce ingredients in the steps that are missing from the ingredient list.

## Cooking steps

Step IDs must be sequential integers:

```text
1, 2, 3, ...
```

Break the method into natural units of work. Most basic recipes will fit well in roughly **4–8 steps**, but use the number that best matches the dish.

Each step should be clear enough for a beginner to perform without guessing important details.

## Tags

Prefer the established NeyadaNote categories when applicable.

Common Korean tags include:

- `메인 요리`
- `메인 반찬`
- `국/찌개`
- `반찬`
- `면요리`
- `간식/디저트`
- `야식`
- `술안주`
- `한식`
- `한그릇요리`

Normally use about **1–3 tags**.

Translate tags by meaning in the English locale, for example:

```text
국/찌개 -> Soup/Stew
한식 -> Korean
```

## `README.md`

The README is the human-readable representation of `recipe.json`. Keep the two in sync.

A typical Korean README is:

```markdown
# 레시피 이름

![레시피 이름 대표 이미지](images/cover.webp)

레시피 요약

- 분량: 2인분
- 분류: 국/찌개, 한식

## 재료

- 재료 — 수량

## 조리 방법

1. 조리 과정
2. 조리 과정

---

The canonical data for this recipe is [recipe.json](recipe.json).
```

The localized README should represent the same recipe as its localized `recipe.json`.

## Localization

Unless there is a specific reason not to, new official recipes should include:

- `ko-KR`
- `en`

The localized variants must describe the same dish and keep the same meaning for:

- recipe ID;
- servings;
- ingredients and their quantities;
- cooking steps;
- cover image.

Translate naturally rather than word-for-word when needed.

For Korean-specific ingredients, add a short explanation where useful. For example:

```text
고춧가루
-> Korean red pepper flakes (gochugaru)
```

## Cover image

Every new official recipe should include a cover image with these specifications:

- **640 × 480 px**
- **4:3 aspect ratio**
- **WebP**
- finished dish as the main subject;
- natural, realistic food-photo style;
- no unnecessary props;
- no text, logos, or watermarks;
- no ingredients or garnishes that contradict the recipe.

Canonical path:

```text
recipes/<recipe-id>/images/cover.webp
```

For the English README preview on GitHub, mirror the same image at:

```text
recipes/<recipe-id>/locales/en/images/cover.webp
```

The two image files should be identical.

Both Korean and English `recipe.json` files use:

```json
"coverImage": "images/cover.webp"
```

The distribution builder takes referenced assets from the recipe root. The locale image copy exists for the localized README's relative Markdown preview.

Use only images you have the right to contribute. Do not add third-party watermarked or copied images.

## Validation

Install the validator dependency if needed:

```bash
python -m pip install "jsonschema~=4.23"
```

Then run the repository checks from the repository root:

```bash
python scripts/validate_recipes.py
python scripts/test_distribution.py
python scripts/build_dist.py
```

A contribution should confirm that:

- JSON Schema validation passes;
- each recipe ID matches its directory name;
- each locale matches its locale directory;
- every recipe variant has a `README.md`;
- referenced assets exist and remain inside the recipe directory;
- the cover image is the required 640 × 480 WebP;
- package generation succeeds;
- catalog generation succeeds;
- existing distribution tests continue to pass.

The pull request workflow in [`.github/workflows/validate.yml`](.github/workflows/validate.yml) runs recipe validation, distribution tests, and a distribution build for relevant source changes.

## Generated files

Do **not** commit generated distribution output such as:

```text
dist/catalog.json
dist/packages/*.neyada-recipe
```

The reviewed source of truth is:

```text
recipe.json
README.md
images/
locales/
```

GitHub Actions builds the distribution from these source files.

## Keep recipe PRs focused

A normal new recipe should not make unrelated changes to:

- recipe schema;
- catalog schema;
- build scripts;
- GitHub Actions workflows;
- existing recipes;
- the NeyadaNote Android app.

If the current format cannot represent the recipe correctly, explain the limitation in the pull request instead of changing infrastructure as part of an otherwise ordinary recipe contribution.

## Pull request

A recipe pull request should include at least:

- recipe name;
- recipe ID;
- confirmation that `ko-KR` and `en` are included;
- confirmation that the cover image is a 640 × 480 WebP;
- result of `python scripts/validate_recipes.py`;
- result of `python scripts/test_distribution.py`;
- result of `python scripts/build_dist.py`.

Example checklist:

```markdown
## Recipe

- Name: 돼지고기 김치찌개
- ID: pork-kimchi-jjigae
- Locales: ko-KR, en
- Cover: 640x480 WebP

## Validation

- [x] python scripts/validate_recipes.py
- [x] python scripts/test_distribution.py
- [x] python scripts/build_dist.py
```

Wait for the repository's GitHub Actions checks to complete before considering the contribution ready for merge.

## Merge and publication

Contributors should submit a pull request rather than pushing recipe changes directly to `main`.

Merging is a maintainer action. A passing pull request should not be assumed to merge automatically.

After a recipe is merged to `main`, the repository's distribution workflow publishes the generated catalog and packages through GitHub Pages.

## Final checklist

Before requesting review, verify all of the following:

- [ ] Started from the latest `main`.
- [ ] Checked for an existing or in-progress duplicate recipe.
- [ ] Recipe ID is meaningful and stable.
- [ ] Root `recipe.json` is `ko-KR`.
- [ ] English variant exists under `locales/en/`.
- [ ] Korean and English variants describe the same dish.
- [ ] Ingredient quantities are concrete where practical.
- [ ] Ingredients and cooking steps agree.
- [ ] Step IDs are sequential.
- [ ] README files match their corresponding JSON data.
- [ ] Cover image is 640 × 480, 4:3, and WebP.
- [ ] Canonical and English-preview cover images are identical.
- [ ] Validation passes.
- [ ] Distribution tests pass.
- [ ] Distribution build succeeds.
- [ ] Generated `dist/` files are not committed.
- [ ] Pull request is focused on the recipe contribution.
- [ ] GitHub Actions checks pass.
