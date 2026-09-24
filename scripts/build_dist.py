#!/usr/bin/env python3
import hashlib
import html
import json
import shutil
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZIP_STORED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
RECIPES_DIR = ROOT / "recipes"
DIST_DIR = ROOT / "dist"
PACKAGE_DIR_NAME = "packages"
CATALOG_FORMAT = "neyadanote.recipe-catalog"
CATALOG_SCHEMA_VERSION = 1
PACKAGE_SUFFIX = ".neyada-recipe"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def safe_asset_path(recipe_dir: Path, asset: str) -> Path:
    relative = PurePosixPath(asset)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe asset path in {recipe_dir.name}: {asset}")

    target = (recipe_dir / Path(*relative.parts)).resolve()
    recipe_root = recipe_dir.resolve()
    if not target.is_relative_to(recipe_root):
        raise ValueError(f"Asset path escapes recipe directory in {recipe_dir.name}: {asset}")
    if not target.is_file():
        raise ValueError(f"Referenced asset does not exist in {recipe_dir.name}: {asset}")
    return target


def referenced_assets(recipe: dict, recipe_dir: Path) -> list[tuple[str, Path]]:
    asset_names: set[str] = set()
    cover_image = recipe.get("coverImage")
    if cover_image:
        asset_names.add(cover_image)

    for step in recipe.get("steps", []):
        image = step.get("image") if isinstance(step, dict) else None
        if image:
            asset_names.add(image)

    return [
        (asset, safe_asset_path(recipe_dir, asset))
        for asset in sorted(asset_names)
    ]


def zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def write_package(recipe_dir: Path, recipe: dict, destination: Path) -> None:
    readme = recipe_dir / "README.md"
    if not readme.is_file():
        raise ValueError(f"README.md is required for {recipe_dir.name}")

    entries: list[tuple[str, Path]] = [
        ("README.md", readme),
        ("recipe.json", recipe_dir / "recipe.json"),
        *referenced_assets(recipe, recipe_dir),
    ]

    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w") as archive:
        for archive_name, source in sorted(entries, key=lambda item: item[0]):
            archive.writestr(zip_info(archive_name), source.read_bytes())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def catalog_entry(recipe: dict, package_path: Path) -> dict:
    entry = {
        "id": recipe["id"],
        "title": recipe["title"],
        "summary": recipe["summary"],
        "tags": recipe["tags"],
        "packageUrl": f"{PACKAGE_DIR_NAME}/{package_path.name}",
        "sha256": sha256_file(package_path),
        "sizeBytes": package_path.stat().st_size,
    }
    if "locale" in recipe:
        entry["locale"] = recipe["locale"]
    if "servings" in recipe:
        entry["servings"] = recipe["servings"]
    return entry


def write_catalog(output_dir: Path, recipes: list[dict]) -> dict:
    catalog = {
        "format": CATALOG_FORMAT,
        "schemaVersion": CATALOG_SCHEMA_VERSION,
        "recipes": recipes,
    }
    (output_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return catalog


def write_index(output_dir: Path, catalog: dict) -> None:
    items = []
    for recipe in catalog["recipes"]:
        title = html.escape(recipe["title"])
        recipe_id = html.escape(recipe["id"])
        package_url = html.escape(recipe["packageUrl"], quote=True)
        items.append(
            f'<li><a href="{package_url}">{title}</a> '
            f'<code>{recipe_id}</code></li>'
        )

    body = "\n".join(items) or "<li>No recipes published.</li>"
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NeyadaNote Recipes</title>
</head>
<body>
  <main>
    <h1>NeyadaNote Recipes</h1>
    <p>Official recipe distribution for NeyadaNote.</p>
    <p><a href="catalog.json">catalog.json</a></p>
    <ul>
      {body}
    </ul>
  </main>
</body>
</html>
"""
    (output_dir / "index.html").write_text(document, encoding="utf-8")
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")


def build_distribution(output_dir: Path = DIST_DIR) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    packages_dir = output_dir / PACKAGE_DIR_NAME
    packages_dir.mkdir(parents=True, exist_ok=True)

    recipe_files = sorted(RECIPES_DIR.glob("*/recipe.json"))
    if not recipe_files:
        raise ValueError("No recipe files found under recipes/*/recipe.json")

    entries: list[dict] = []
    for recipe_file in recipe_files:
        recipe_dir = recipe_file.parent
        recipe = load_json(recipe_file)
        recipe_id = recipe.get("id")
        if recipe_id != recipe_dir.name:
            raise ValueError(
                f"Recipe id must match directory name: {recipe_id!r} != {recipe_dir.name!r}"
            )

        package_path = packages_dir / f"{recipe_id}{PACKAGE_SUFFIX}"
        write_package(recipe_dir, recipe, package_path)
        entries.append(catalog_entry(recipe, package_path))

    entries.sort(key=lambda recipe: recipe["id"])
    catalog = write_catalog(output_dir, entries)
    write_index(output_dir, catalog)
    return catalog


def main() -> int:
    try:
        catalog = build_distribution()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"Distribution build failed: {error}", file=sys.stderr)
        return 1

    print(f"Built {len(catalog['recipes'])} recipe package(s) in {DIST_DIR.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
