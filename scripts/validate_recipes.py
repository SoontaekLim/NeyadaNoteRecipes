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


def validate_asset(recipe_root: Path, asset: str, errors: list[str]) -> None:
    target = (recipe_root / asset).resolve()
    resolved_root = recipe_root.resolve()

    if not target.is_relative_to(resolved_root):
        errors.append(f"{recipe_root.name}: asset path escapes recipe directory: {asset}")
        return

    if not target.is_file():
        errors.append(f"{recipe_root.name}: referenced asset does not exist: {asset}")


def recipe_sources(recipe_dir: Path) -> list[tuple[Path, Path, str | None]]:
    sources = [(recipe_dir / "recipe.json", recipe_dir / "README.md", None)]
    locales_dir = recipe_dir / "locales"
    if locales_dir.is_dir():
        for recipe_file in sorted(locales_dir.glob("*/recipe.json")):
            sources.append((recipe_file, recipe_file.parent / "README.md", recipe_file.parent.name))
    return sources


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    recipe_dirs = sorted(
        path for path in RECIPES_DIR.iterdir()
        if path.is_dir() and (path / "recipe.json").is_file()
    )

    if not recipe_dirs:
        errors.append("No recipe files found under recipes/*/recipe.json")

    variant_count = 0
    for recipe_dir in recipe_dirs:
        seen_locales: set[str] = set()
        for recipe_file, readme_file, expected_locale in recipe_sources(recipe_dir):
            variant_count += 1
            try:
                recipe = load_json(recipe_file)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{recipe_file.relative_to(ROOT)}: invalid JSON: {exc}")
                continue

            for error in sorted(
                validator.iter_errors(recipe),
                key=lambda item: list(item.absolute_path),
            ):
                location = ".".join(str(part) for part in error.absolute_path) or "<root>"
                errors.append(
                    f"{recipe_file.relative_to(ROOT)}:{location}: {error.message}"
                )

            if recipe.get("id") != recipe_dir.name:
                errors.append(
                    f"{recipe_file.relative_to(ROOT)}: recipe id must match directory name "
                    f"({recipe_dir.name!r})"
                )

            locale = recipe.get("locale")
            if not locale:
                errors.append(
                    f"{recipe_file.relative_to(ROOT)}: official recipe locale is required"
                )
            elif locale in seen_locales:
                errors.append(
                    f"{recipe_file.relative_to(ROOT)}: duplicate locale {locale!r}"
                )
            else:
                seen_locales.add(locale)

            if expected_locale is not None and locale != expected_locale:
                errors.append(
                    f"{recipe_file.relative_to(ROOT)}: locale must match locale directory "
                    f"({expected_locale!r})"
                )

            if not readme_file.is_file():
                errors.append(
                    f"{readme_file.relative_to(ROOT)}: README.md is required"
                )

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

    print(
        f"Validated {len(recipe_dirs)} recipe(s) and "
        f"{variant_count} locale variant(s) successfully."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
