#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "recipe-v1.schema.json"
RECIPES_DIR = ROOT / "recipes"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_asset(recipe_dir: Path, asset: str, errors: list[str]) -> None:
    target = (recipe_dir / asset).resolve()
    recipe_root = recipe_dir.resolve()

    if not target.is_relative_to(recipe_root):
        errors.append(f"{recipe_dir.name}: asset path escapes recipe directory: {asset}")
        return

    if not target.is_file():
        errors.append(f"{recipe_dir.name}: referenced asset does not exist: {asset}")


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    recipe_files = sorted(RECIPES_DIR.glob("*/recipe.json"))

    if not recipe_files:
        errors.append("No recipe files found under recipes/*/recipe.json")

    for recipe_file in recipe_files:
        recipe_dir = recipe_file.parent

        try:
            recipe = load_json(recipe_file)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{recipe_file.relative_to(ROOT)}: invalid JSON: {exc}")
            continue

        for error in sorted(validator.iter_errors(recipe), key=lambda item: list(item.absolute_path)):
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            errors.append(
                f"{recipe_file.relative_to(ROOT)}:{location}: {error.message}"
            )

        if recipe.get("id") != recipe_dir.name:
            errors.append(
                f"{recipe_file.relative_to(ROOT)}: recipe id must match directory name "
                f"({recipe_dir.name!r})"
            )

        readme = recipe_dir / "README.md"
        if not readme.is_file():
            errors.append(f"{recipe_dir.name}: README.md is required")

        cover_image = recipe.get("coverImage")
        if cover_image:
            validate_asset(recipe_dir, cover_image, errors)

        for step in recipe.get("steps", []):
            step_image = step.get("image") if isinstance(step, dict) else None
            if step_image:
                validate_asset(recipe_dir, step_image, errors)

    if errors:
        print("Recipe validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(recipe_files)} recipe(s) successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
