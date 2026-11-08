# NeyadaNote shopping suggestions (Issue #18)

This directory contains **read-only suggested shopping items** for NeyadaNote.
It is not the user's shopping-list database.

## Publish / edit

Edit `shopping/items.json` and submit a pull request. Each entry has:

| Field | Purpose |
| --- | --- |
| `id` | Stable machine-readable identifier (lowercase letters, digits, underscore and dash) |
| `name_ko`, `name_en` | Display names in Korean and English |
| `category` | Existing NeyadaNote category value; must match the app's canonical categories |
| `sort_order` | Nonnegative integer display sort order |
| `is_active` | Set to `false` to hide from new suggestions without deleting the record |
| `default_quantity` | Optional string (up to 80 characters) or null; users can edit after adding |

Only active entries appear in the published catalog. Existing shopping list
items are stored locally in Room and never removed or modified when catalog
source records change.

The validator prevents duplicate IDs, malformed names, unknown categories,
out-of-range quantities and oversized outputs. Keep IDs stable when renaming items.

## Distribution

`scripts/build_dist.py` writes **`dist/shopping/catalog.json`** into the
same Pages artifact as the official recipe catalog:

`https://soontaeklim.github.io/NeyadaNoteRecipes/shopping/catalog.json`

The output is an array of active template objects containing
`id`, `name_ko`, `name_en`, `category`, `sort_order`, and
`default_quantity` (no `is_active`). It is sorted by `sort_order` then `id`.

The `main` branch's GitHub Actions Pages workflow runs validation and builds
the artifact. A pull request alone **does not** publish the catalog. The
operator must review and merge this change to the recipes repo and verify
the Pages URL before testing the app's online catalog.

The app checks for updates on entering item search after its successful cache
is older than 12 hours; Retry forces a refresh. Offline users retain the last
valid response. Manual item entry is always available.

## Validation

```bash
python -m pip install "jsonschema~=4.23"
python scripts/validate_recipes.py
python scripts/test_distribution.py
python scripts/build_dist.py
```

The recipe packages and existing `catalog.json` remain unchanged.

## Grain Products (2026-11-08)

The source now contains **351 items**: 330 retained IDs, plus **21 distinct Grain Products** items captured in the two additional reference screenshots. Six already-present IDs (`cereal`, `flour`, `oatmeal`, `instant_noodles`, `rice`, `tofu`) are assigned to the new first-party `곡물 및 가루류` (Grains & Flour) category. The existing `instant_noodles` item represents “ramen” in the screenshots, avoiding a duplicate ID.

The Android app adds the corresponding built-in category, local seed and vector icons via a separate PR. Existing local user modifications remain authoritative.
