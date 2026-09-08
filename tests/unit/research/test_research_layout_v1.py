"""research/archive/LAYOUT_V1.json is the archive index for top-level research dirs.

Frozen V1 programmes stay at their freeze paths. This test makes sure the
catalog stays complete so new folders cannot appear unindexed, and so
freeze-bound flags cannot silently drift.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research"
LAYOUT_PATH = RESEARCH / "archive" / "LAYOUT_V1.json"
BINDING_PATH = RESEARCH / "orion-v1-freeze" / "V1_COMPONENT_BINDING_V1.json"
CLASSES = {"live", "frozen_in_place", "control_plane"}


def _layout() -> dict:
    return json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))


def _freeze_tops() -> set[str]:
    binding = json.loads(BINDING_PATH.read_text(encoding="utf-8"))
    tops: set[str] = set()

    def walk(obj: object) -> None:
        if isinstance(obj, dict):
            path = obj.get("path")
            if isinstance(path, str) and path.startswith("research/"):
                rel = path[len("research/") :].strip("/")
                if rel:
                    tops.add(rel.split("/")[0])
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)

    walk(binding)
    return tops


def test_layout_file_exists_and_has_schema() -> None:
    data = _layout()
    assert data["schema"] == "ORION.V1.ResearchLayout.v1"
    assert data["policy"]["freeze_bound_paths_must_not_move"] is True
    assert (RESEARCH / "README.md").is_file()
    assert (RESEARCH / "archive" / "FROZEN_IN_PLACE.md").is_file()
    assert (RESEARCH / "archive" / "SPARSE_CHECKOUT").is_file()


def test_every_top_level_dir_except_archive_is_catalogued() -> None:
    data = _layout()
    disk = {p.name for p in RESEARCH.iterdir() if p.is_dir()}
    disk.discard("archive")
    catalogued = {row["path"].removeprefix("research/") for row in data["top_level"]}
    assert disk == catalogued, {
        "on_disk_not_in_layout": sorted(disk - catalogued),
        "in_layout_not_on_disk": sorted(catalogued - disk),
    }


def test_catalogued_paths_exist_and_classes_are_known() -> None:
    data = _layout()
    for row in data["top_level"] + data["extensions"]:
        assert row["class"] in CLASSES, row
        assert row["move"] == "forbidden", row
        assert (ROOT / row["path"]).exists(), row["path"]


def test_freeze_bound_flags_match_component_binding() -> None:
    data = _layout()
    freeze_tops = _freeze_tops()
    freeze_tops.discard("orion-v1-freeze")
    for row in data["top_level"]:
        name = row["path"].removeprefix("research/")
        if name == "orion-v1-freeze":
            continue
        assert row["freeze_bound"] is (name in freeze_tops), row


def test_frozen_in_place_listing_mentions_the_census_dump() -> None:
    text = (RESEARCH / "archive" / "FROZEN_IN_PLACE.md").read_text(encoding="utf-8")
    assert "orion-epistemic-state-v1" in text
    live = [row["path"] for row in _layout()["top_level"] if row["class"] == "live"]
    assert "research/extensions" in live
    assert "research/experiments" in live
