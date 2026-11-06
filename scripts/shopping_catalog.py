"""Validate reviewed shopping templates and publish only active entries to Pages."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "shopping" / "items.json"
OUTPUT_RELATIVE_PATH = Path("shopping") / "catalog.json"
MAX_ITEMS = 1_000
MAX_OUTPUT_BYTES = 512 * 1024
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
CATEGORIES = {
    "채소/과일",
    "정육/계란",
    "수산/건어물",
    "유제품/음료",
    "가공/냉동식품",
    "양념/소스",
    "과자/빵",
    "생활용품/기타",
    "기타",
}
REQUIRED_FIELDS = {"id", "name_ko", "name_en", "category", "sort_order", "is_active"}
ALLOWED_FIELDS = REQUIRED_FIELDS | {"default_quantity"}


def validated_items(raw: object) -> list[dict]:
    """Reject malformed catalog records before publication.

    The Android app's parser performs its own bounds/schema checks because
    published JSON is not a trusted local database.
    """
    if not isinstance(raw, list) or len(raw) > MAX_ITEMS:
        raise ValueError("Shopping items must be an array with at most 1000 entries.")

    ids: set[str] = set()
    checked: list[dict] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Shopping item {index} is not an object.")
        if not REQUIRED_FIELDS <= item.keys() or not item.keys() <= ALLOWED_FIELDS:
            raise ValueError(f"Shopping item {index} has missing or unexpected fields.")

        identifier = item["id"]
        if not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier):
            raise ValueError(f"Shopping item {index} has invalid id.")
        if identifier in ids:
            raise ValueError(f"Duplicate shopping id: {identifier}")
        ids.add(identifier)

        for name_field in ("name_ko", "name_en"):
            name = item[name_field]
            if not isinstance(name, str) or not (1 <= len(name.strip()) <= 120):
                raise ValueError(f"Shopping item {identifier} has invalid {name_field}.")

        category = item["category"]
        if not isinstance(category, str) or category not in CATEGORIES:
            raise ValueError(f"Shopping item {identifier} has invalid category.")

        order = item["sort_order"]
        if type(order) is not int or not 0 <= order <= 1_000_000:
            raise ValueError(f"Shopping item {identifier} has invalid sort_order.")
        if type(item["is_active"]) is not bool:
            raise ValueError(f"Shopping item {identifier} has invalid is_active.")

        quantity = item.get("default_quantity")
        if quantity is not None and (
            not isinstance(quantity, str) or len(quantity.strip()) > 80
        ):
            raise ValueError(f"Shopping item {identifier} has invalid default_quantity.")

        checked.append(
            {
                "id": identifier,
                "name_ko": item["name_ko"].strip(),
                "name_en": item["name_en"].strip(),
                "category": category,
                "sort_order": order,
                "is_active": item["is_active"],
                "default_quantity": quantity.strip() if quantity else None,
            }
        )
    return checked


def published_items(raw: object) -> list[dict]:
    """Exclude disabled items and management-only fields from the public feed."""
    active = []
    for item in validated_items(raw):
        if item["is_active"]:
            active.append({key: value for key, value in item.items() if key != "is_active"})
    active.sort(key=lambda item: (item["sort_order"], item["id"]))
    return active


def build_shopping_catalog(output_dir: Path, source_path: Path = SOURCE_PATH) -> list[dict]:
    raw = json.loads(source_path.read_text(encoding="utf-8"))
    catalog = published_items(raw)
    content = (json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(content) > MAX_OUTPUT_BYTES:
        raise ValueError("Published shopping catalog exceeds the Android response limit.")

    destination = output_dir / OUTPUT_RELATIVE_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return catalog
