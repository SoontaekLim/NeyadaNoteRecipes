#!/usr/bin/env python3
import hashlib
import json
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from jsonschema import Draft202012Validator

from build_dist import ROOT, build_distribution
from shopping_catalog import published_items, validated_items

CATALOG_SCHEMA = ROOT / "schema" / "catalog-v1.schema.json"
RECIPE_SCHEMA = ROOT / "schema" / "recipe-v1.schema.json"


def directory_hashes(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


class DistributionBuildTest(unittest.TestCase):
    def test_build_is_deterministic(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            build_distribution(Path(first))
            build_distribution(Path(second))
            self.assertEqual(directory_hashes(Path(first)), directory_hashes(Path(second)))

    def test_catalog_and_packages_match_source(self):
        with tempfile.TemporaryDirectory() as output:
            output_dir = Path(output)
            catalog = build_distribution(output_dir)
            schema = json.loads(CATALOG_SCHEMA.read_text(encoding="utf-8"))
            Draft202012Validator(schema).validate(catalog)

            ids = [entry["id"] for entry in catalog["recipes"]]
            self.assertEqual(sorted(ids), ids)
            self.assertEqual(len(ids), len(set(ids)))

            for entry in catalog["recipes"]:
                legacy_package = output_dir / entry["packageUrl"]
                self.assertTrue(legacy_package.is_file())

                variants = entry["variants"]
                locales = [variant["locale"] for variant in variants]
                self.assertEqual(sorted(locales), locales)
                self.assertEqual(len(locales), len(set(locales)))

                for variant in variants:
                    package = output_dir / variant["packageUrl"]
                    self.assertTrue(package.is_file())
                    self.assertEqual(package.stat().st_size, variant["sizeBytes"])
                    self.assertEqual(
                        hashlib.sha256(package.read_bytes()).hexdigest(),
                        variant["sha256"],
                    )

                    with ZipFile(package) as archive:
                        names = archive.namelist()
                        self.assertEqual(names, sorted(names))
                        self.assertIn("recipe.json", names)
                        self.assertIn("README.md", names)
                        for name in names:
                            path = PurePosixPath(name)
                            self.assertFalse(path.is_absolute())
                            self.assertNotIn("..", path.parts)

                        recipe = json.loads(archive.read("recipe.json"))
                        self.assertEqual(entry["id"], recipe["id"])
                        self.assertEqual(variant["locale"], recipe["locale"])
                        self.assertEqual(variant["title"], recipe["title"])
                        self.assertEqual(variant["summary"], recipe["summary"])
                        self.assertEqual(variant["tags"], recipe["tags"])

                        assets = set()
                        if recipe.get("coverImage"):
                            assets.add(recipe["coverImage"])
                        assets.update(
                            step["image"]
                            for step in recipe.get("steps", [])
                            if step.get("image")
                        )
                        for asset in assets:
                            self.assertIn(asset, names)

                default_variant = next(
                    variant for variant in variants
                    if variant["packageUrl"] == entry["packageUrl"]
                )
                self.assertEqual(entry["locale"], default_variant["locale"])
                self.assertEqual(entry["title"], default_variant["title"])
                self.assertEqual(entry["summary"], default_variant["summary"])

            self.assertTrue((output_dir / "index.html").is_file())
            self.assertTrue((output_dir / ".nojekyll").is_file())

    def test_recipe_schema_accepts_blank_legacy_user_fields(self):
        schema = json.loads(RECIPE_SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        base = {
            "format": "neyadanote.recipe",
            "schemaVersion": 1,
            "id": "legacy-user-recipe",
            "title": "Legacy recipe",
            "summary": "",
            "tags": [],
        }

        documents = [
            {
                **base,
                "ingredients": [{"name": "", "amount": ""}],
                "steps": [{"id": 1, "description": ""}],
            },
            {
                **base,
                "ingredients": [],
                "steps": [],
            },
        ]

        for document in documents:
            with self.subTest(document=document):
                validator.validate(document)

    def test_sample_recipe_publishes_korean_and_english(self):
        with tempfile.TemporaryDirectory() as output:
            catalog = build_distribution(Path(output))
            sample = next(
                item for item in catalog["recipes"]
                if item["id"] == "pork-kimchi-jjigae"
            )
            self.assertEqual(
                ["en", "ko-KR"],
                [variant["locale"] for variant in sample["variants"]],
            )


class ShoppingCatalogBuildTest(unittest.TestCase):
    @staticmethod
    def sample(identifier="onion", active=True):
        return {
            "id": identifier,
            "name_ko": "양파",
            "name_en": "Onion",
            "category": "채소/과일",
            "sort_order": 20,
            "is_active": active,
            "default_quantity": None,
        }

    def test_catalog_is_published_to_pages_artifact(self):
        with tempfile.TemporaryDirectory() as output:
            directory = Path(output)
            build_distribution(directory)
            catalog_path = directory / "shopping" / "catalog.json"
            self.assertTrue(catalog_path.is_file())
            published = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertTrue(any(item["id"] == "onion" for item in published))
            self.assertEqual(
                sorted(published, key=lambda item: (item["sort_order"], item["id"])),
                published,
            )
            self.assertTrue(all("is_active" not in item for item in published))

    def test_disabled_items_are_not_published(self):
        published = published_items([
            self.sample("onion", active=True),
            self.sample("milk", active=False),
        ])
        self.assertEqual(["onion"], [entry["id"] for entry in published])

    def test_invalid_source_is_rejected_before_pages_deployment(self):
        invalid_cases = [
            [self.sample(), self.sample()],
            [{**self.sample(), "category": "not-in-app"}],
            [{**self.sample(), "sort_order": True}],
            [{**self.sample(), "is_active": "true"}],
            [{**self.sample(), "name_ko": ""}],
            [{**self.sample(), "unknown": "unexpected"}],
            [{"id": "incomplete"}],
            {"items": [self.sample()]},
        ]
        for invalid in invalid_cases:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    validated_items(invalid)


if __name__ == "__main__":
    unittest.main()
