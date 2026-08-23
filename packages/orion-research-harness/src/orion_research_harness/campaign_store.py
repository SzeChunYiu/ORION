from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .protocol import canonical_json, content_digest
from .workspace import ResearchWorkspace


def _write_create(path: Path, value: Mapping[str, Any]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp-{uuid4().hex}")
    try:
        with temp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp, path)
        except FileExistsError:
            return False
        return True
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _read(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict):
        raise TypeError("campaign artifact must contain an object")
    return raw


def _safe(identifier: str) -> str:
    if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 160:
        raise ValueError("invalid campaign identity")
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


class CampaignStore:
    """Immutable campaign state/cycle store rooted inside a hardened ResearchWorkspace."""

    def __init__(self, workspace: ResearchWorkspace) -> None:
        self.workspace = workspace
        self.root = workspace.meta_root / "campaign-control"
        self.manifests = self.root / "manifests"
        self.states = self.root / "states"
        self.cycles = self.root / "cycles"

    def freeze_manifest(self, campaign_id: str, manifest: Mapping[str, Any]) -> Path:
        payload = dict(manifest)
        if payload.get("campaign_id") != campaign_id:
            raise ValueError("campaign manifest identity mismatch")
        path = self.manifests / f"{_safe(campaign_id)}.json"
        if path.exists():
            if canonical_json(_read(path)) != canonical_json(payload):
                raise ValueError("campaign manifest is already frozen with different content")
            return path
        if _write_create(path, payload):
            return path
        if canonical_json(_read(path)) != canonical_json(payload):
            raise ValueError("campaign manifest publication raced with different content")
        return path

    def load_manifest(self, campaign_id: str) -> dict[str, Any]:
        return _read(self.manifests / f"{_safe(campaign_id)}.json")

    def _state_root(self, campaign_id: str) -> Path:
        return self.states / _safe(campaign_id)

    def save_state(self, campaign_id: str, state: Mapping[str, Any]) -> Path:
        payload = dict(state)
        if payload.get("campaign_id") != campaign_id:
            raise ValueError("campaign state identity mismatch")
        index = payload.get("cycle_index")
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise ValueError("campaign cycle_index must be non-negative integer")
        path = self._state_root(campaign_id) / f"{index:08d}.json"
        if path.exists():
            if canonical_json(_read(path)) != canonical_json(payload):
                raise ValueError("campaign state cycle already exists with different content")
            return path
        if _write_create(path, payload):
            return path
        if canonical_json(_read(path)) != canonical_json(payload):
            raise ValueError("campaign state publication raced with different content")
        return path

    def latest_state(self, campaign_id: str) -> dict[str, Any] | None:
        root = self._state_root(campaign_id)
        paths = sorted(root.glob("*.json")) if root.exists() else []
        if not paths:
            return None
        raw = _read(paths[-1])
        if raw.get("campaign_id") != campaign_id:
            raise ValueError("campaign state identity mismatch")
        return raw

    def save_cycle(self, campaign_id: str, transition: Mapping[str, Any]) -> Path:
        payload = dict(transition)
        if payload.get("campaign_id") != campaign_id:
            raise ValueError("campaign transition identity mismatch")
        index = payload.get("cycle_index")
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise ValueError("campaign transition cycle_index must be non-negative integer")
        root = self.cycles / _safe(campaign_id)
        path = root / f"{index:08d}-{content_digest(payload)[:16]}.json"
        if path.exists():
            if canonical_json(_read(path)) != canonical_json(payload):
                raise ValueError("campaign transition exists with different content")
            return path
        if _write_create(path, payload):
            return path
        if canonical_json(_read(path)) != canonical_json(payload):
            raise ValueError("campaign transition publication raced with different content")
        return path


__all__ = ["CampaignStore"]
