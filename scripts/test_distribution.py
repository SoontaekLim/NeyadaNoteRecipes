#!/usr/bin/env python3
import hashlib
import json
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from jsonschema import Draft202012Validator

from build_dist import ROOT, build_distribution

CATALOG_SCHEMA = ROOT / "schema" / "catalog-v1.schema.json"


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
            validator = Draft202012Validator(schema)
            validator.validate(catalog)

            ids = [entry["id"] for entry in catalog["recipes"]]
            self.assertEqual(sorted(ids), ids)
            self.assertEqual(len(ids), len(set(ids)))

            for entry in catalog["recipes"]:
                package = output_dir / entry["packageUrl"]
                self.assertTrue(package.is_file())
                self.assertEqual(package.stat().st_size, entry["sizeBytes"])
                self.assertEqual(
                    hashlib.sha256(package.read_bytes()).hexdigest(),
                    entry["sha256"],
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
                    self.assertEqual(entry["title"], recipe["title"])
                    self.assertEqual(entry["summary"], recipe["summary"])
                    self.assertEqual(entry["tags"], recipe["tags"])

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

            self.assertTrue((output_dir / "index.html").is_file())
            self.assertTrue((output_dir / ".nojekyll").is_file())


if __name__ == "__main__":
    unittest.main()
