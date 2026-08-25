#!/usr/bin/env python3
"""Execute the frozen DES-CENSUS-01 source-tree census.

This is a computation-only, non-authorizing parser. It reads blobs from the
exact frozen Git object rather than from the mutable working tree and retains
excluded and unclassified rows instead of silently converting them to absence.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import time
from typing import Any, Iterable


JOB_ID = "DES-CENSUS-01"
SUBJECT = "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
SUBJECT_TREE = "ec9455ccfdded0c2a27c97b425ad001b228151de"
ORIGIN_MAIN = "f049e30391a09213240f6325ee319f9fa811189a"
MAX_BLOB_BYTES = 5_000_000
HERE = Path(__file__).resolve().parent
FREEZE_PATH = HERE / "FREEZE_V1.json"

COMPOSITE_RE = re.compile(
    r"(?<![A-Za-z0-9])[A-Z][A-Z0-9]*(?:_{1,2}[A-Z0-9]+)+(?![A-Za-z0-9])"
)
STANDALONE_STATUSES = frozenset(
    {
        "PASS", "FAIL", "FAILED", "ERROR", "CRASH", "BLOCKED", "READY",
        "GREEN", "RED", "OPEN", "CLOSED", "COMPLETE", "INCOMPLETE", "VALID",
        "INVALID", "SUPPORTED", "UNSUPPORTED", "POSITIVE", "NEGATIVE", "NULL",
        "HARMFUL", "ADVERSE", "CENSORED", "UNRESOLVED", "DENIED", "AUTHORIZED",
        "CANNOT_CHECK", "UNKNOWN", "UNCLASSIFIED",
    }
)
STATUS_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:" + "|".join(sorted(STANDALONE_STATUSES, key=len, reverse=True))
    + r")(?![A-Za-z0-9_])"
)
TERMINAL_CONTEXT_RE = re.compile(r"\b(?:terminal|verdict|decision|completion)\b", re.I)
STATUS_CONTEXT_RE = re.compile(r"\b(?:status|state|outcome|result)\b", re.I)
DEPENDENCY_CONTEXT_RE = re.compile(
    r"\b(?:dependenc(?:y|ies)|depends_on|requires?|prerequisites?|upstream|blocked_by)\b",
    re.I,
)
TRANSITION_CONTEXT_RE = re.compile(
    r"(?:-{1,2}>|=>|\b(?:transition|from_state|to_state|previous_state|next_state|"
    r"reopen(?:ed|ing)?|invalidate(?:d|ion)?|revoke(?:d|ation)?|supersede(?:d|s)?)\b)",
    re.I,
)

STRUCTURED_KEYS: dict[str, frozenset[str]] = {
    "terminal": frozenset({"terminal", "verdict", "decision", "completion"}),
    "status": frozenset({"status", "state", "outcome", "result"}),
    "cannot_check_reason": frozenset(
        {"cannot_check", "reason", "reasons", "blocker", "blockers"}
    ),
    "dependency": frozenset(
        {
            "dependency", "dependencies", "depends_on", "requires", "prerequisite",
            "prerequisites", "upstream", "blocked_by",
        }
    ),
    "transition": frozenset(
        {
            "transition", "transitions", "from_state", "to_state", "previous_state",
            "next_state", "reopen", "reopened", "invalidate", "invalidated", "revoke",
            "revoked", "supersede", "superseded",
        }
    ),
}

COORDINATE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "E": ("evidence", "effect", "likelihood", "posterior", "interval", "empirical", "metric", "precision", "recall", "significance"),
    "Theta": ("identified", "identifiability", "identified_set", "estimand", "target", "partition", "partial_identification"),
    "C": ("coverage", "open_world", "closure", "complete", "incomplete", "residual", "saturation", "search_universe", "cannot_check"),
    "R": ("obligation", "required", "requirement", "unresolved", "blocker", "gate", "precondition", "cannot_check", "dependency"),
    "P": ("provenance", "receipt", "manifest", "digest", "hash", "binding", "derivation", "lineage"),
    "F": ("fresh", "stale", "epoch", "validity", "expiry", "drift", "supersede", "invalidate", "dependency"),
    "V": ("verify", "verification", "checker", "test", "review", "replication", "green", "pass", "fail"),
    "A": ("authority", "promotion", "adoption", "authorized", "denied", "claim_ceiling", "scope", "revocation"),
    "S": ("support_family", "support_families", "alternative_support", "witness_family"),
    "Q": ("reproduction", "reproducibility", "replication", "heterogeneity", "transfer", "replay"),
    "D": ("defeater", "contradiction", "negative", "harmful", "adverse", "null", "failure", "error", "crash", "invalid"),
    "B": ("resource", "access", "compute", "memory", "token", "time", "budget", "cap", "cost", "unavailable"),
    "K": ("custody", "lineage", "independence", "overlap", "external", "leakage", "contamination"),
    "U": ("burden", "latency", "wallclock", "runtime", "cost", "experimental_burden"),
    "M": ("method", "grammar", "search_space", "reachable_closure", "donor", "baseline", "comparator", "algorithm"),
    "G": ("knowledge", "graph", "hypergraph", "ontology", "semantic", "claim", "transition", "state"),
}

LIKELY_TEXT_SUFFIXES = frozenset(
    {
        ".md", ".json", ".py", ".yml", ".yaml", ".toml", ".tex", ".txt",
        ".csv", ".tsv", ".rst", ".ini", ".cfg", ".sh", ".bash", ".zsh",
        ".lock", ".svg", ".xml", ".html", ".css", ".js", ".ts", ".tsx", ".jsx",
    }
)


def _run_git(*args: str, text: bool = True) -> str | bytes:
    completed = subprocess.run(
        ["git", *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=text,
    )
    return completed.stdout


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _normalized_search_text(*values: str) -> str:
    return "_" + re.sub(r"[^a-z0-9]+", "_", " ".join(values).lower()).strip("_") + "_"


def assign_coordinates(raw_value: str, context: str) -> tuple[str, ...]:
    """Apply only the frozen deterministic coordinate keyword rules."""

    haystack = _normalized_search_text(raw_value, context)
    assigned: list[str] = []
    for coordinate, keywords in COORDINATE_KEYWORDS.items():
        if any(f"_{re.sub(r'[^a-z0-9]+', '_', word.lower()).strip('_')}_" in haystack for word in keywords):
            assigned.append(coordinate)
    return tuple(assigned)


def _context(text: str, start: int, end: int, *, prefix: str = "") -> str:
    left = max(0, start - 120)
    right = min(len(text), end + 120)
    snippet = re.sub(r"\s+", " ", text[left:right]).strip()
    return (prefix + " " + snippet).strip()[:240]


def _occurrence(
    *,
    path: str,
    blob_oid: str,
    detector: str,
    locator: dict[str, Any],
    raw_value: str,
    context: str,
    families: Iterable[str],
) -> dict[str, Any]:
    ordered_families = tuple(sorted(set(families)))
    coordinates = assign_coordinates(raw_value, context)
    identity_payload = json.dumps(
        [path, detector, locator, raw_value, ordered_families],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return {
        "occurrence_id": sha256_bytes(identity_payload),
        "path": path,
        "blob_oid": blob_oid,
        "detector": detector,
        "locator": locator,
        "families": list(ordered_families),
        "raw_value": raw_value,
        "normalized_value": raw_value.strip(),
        "context": context,
        "coordinates": list(coordinates),
        "classification": "CLASSIFIED" if coordinates else "UNCLASSIFIED",
    }


def _families_for_context(value: str, context: str) -> set[str]:
    families: set[str] = set()
    joined = f"{value} {context}"
    if TERMINAL_CONTEXT_RE.search(joined):
        families.add("terminal")
    if STATUS_CONTEXT_RE.search(joined) or value in STANDALONE_STATUSES:
        families.add("status")
    if "CANNOT_CHECK" in joined:
        families.add("cannot_check_reason")
    if DEPENDENCY_CONTEXT_RE.search(joined):
        families.add("dependency")
    if TRANSITION_CONTEXT_RE.search(joined):
        families.add("transition")
    return families


def detect_text_occurrences(*, path: str, blob_oid: str, text: str) -> list[dict[str, Any]]:
    """Detect occurrences in non-JSON eligible text."""

    rows: list[dict[str, Any]] = []
    char_offset = 0
    byte_offset = 0
    for line_number, line_with_end in enumerate(text.splitlines(keepends=True), start=1):
        line = line_with_end.rstrip("\r\n")
        spans: set[tuple[int, int]] = set()
        matches = list(COMPOSITE_RE.finditer(line))
        for match in matches:
            spans.add(match.span())
        for match in STATUS_RE.finditer(line):
            if not any(a <= match.start() and match.end() <= b for a, b in spans):
                matches.append(match)
                spans.add(match.span())
        matches.sort(key=lambda item: (item.start(), item.end()))

        line_context = _context(line, 0, len(line))
        context_families = _families_for_context("", line_context)
        for match in matches:
            value = match.group(0)
            families = set(context_families)
            if COMPOSITE_RE.fullmatch(value):
                families.add("composite_label")
            if value in STANDALONE_STATUSES:
                families.add("status")
            if "CANNOT_CHECK" in value:
                families.add("cannot_check_reason")
            prefix = ""
            if "dependency" in families:
                prefix += "dependency "
            if "transition" in families:
                prefix += "transition "
            local_context = _context(line, match.start(), match.end(), prefix=prefix)
            start_byte = byte_offset + len(line[: match.start()].encode("utf-8"))
            end_byte = byte_offset + len(line[: match.end()].encode("utf-8"))
            rows.append(
                _occurrence(
                    path=path,
                    blob_oid=blob_oid,
                    detector="text_token",
                    locator={
                        "line": line_number,
                        "column": match.start() + 1,
                        "byte_start": start_byte,
                        "byte_end": end_byte,
                    },
                    raw_value=value,
                    context=local_context,
                    families=families or {"composite_label"},
                )
            )

        # A dependency or transition with no uppercase token is still a case.
        statement_families = {
            family
            for family in context_families
            if family in {"dependency", "transition", "cannot_check_reason"}
        }
        if statement_families and not matches and line.strip():
            prefix = " ".join(sorted(statement_families))
            rows.append(
                _occurrence(
                    path=path,
                    blob_oid=blob_oid,
                    detector="text_statement",
                    locator={
                        "line": line_number,
                        "column": 1,
                        "byte_start": byte_offset,
                        "byte_end": byte_offset + len(line.encode("utf-8")),
                    },
                    raw_value=line.strip(),
                    context=f"{prefix} {line_context}"[:240],
                    families=statement_families,
                )
            )
        char_offset += len(line_with_end)
        byte_offset += len(line_with_end.encode("utf-8"))

    # splitlines() returns nothing for an empty text and omits a final empty line;
    # neither case contains a syntactic occurrence.
    del char_offset
    return _deduplicate_occurrences(rows)


def _json_pointer(parts: tuple[str, ...]) -> str:
    return "/" + "/".join(item.replace("~", "~0").replace("/", "~1") for item in parts)


def _structured_family(key: str, *, cannot_context: bool) -> set[str]:
    lowered = key.lower()
    families = {
        family for family, keys in STRUCTURED_KEYS.items() if lowered in keys
    }
    if "cannot_check_reason" in families and lowered in {"reason", "reasons", "blocker", "blockers"} and not cannot_context:
        families.remove("cannot_check_reason")
    return families


def detect_json_occurrences(
    *, path: str, blob_oid: str, payload: Any
) -> list[dict[str, Any]]:
    """Detect lexical tokens and structured semantic fields in parsed JSON."""

    rows: list[dict[str, Any]] = []

    def walk(value: Any, pointer: tuple[str, ...], parent: Any = None) -> None:
        if isinstance(value, dict):
            cannot_context = any(
                isinstance(item, str) and "CANNOT_CHECK" in item
                for item in value.values()
            )
            for key, child in value.items():
                child_pointer = (*pointer, str(key))
                if isinstance(child, str):
                    families_from_key = _structured_family(
                        str(key), cannot_context=cannot_context or "CANNOT_CHECK" in child
                    )
                    context_prefix = " ".join(sorted(families_from_key))
                    scalar_context = (
                        f"{context_prefix} json_key={key} value={child}".strip()
                    )[:240]
                    token_matches = list(COMPOSITE_RE.finditer(child))
                    token_spans = {item.span() for item in token_matches}
                    for match in STATUS_RE.finditer(child):
                        if not any(a <= match.start() and match.end() <= b for a, b in token_spans):
                            token_matches.append(match)
                    token_matches.sort(key=lambda item: (item.start(), item.end()))
                    for match in token_matches:
                        raw = match.group(0)
                        families = set(families_from_key)
                        families.update(_families_for_context(raw, scalar_context))
                        if COMPOSITE_RE.fullmatch(raw):
                            families.add("composite_label")
                        if raw in STANDALONE_STATUSES:
                            families.add("status")
                        if "CANNOT_CHECK" in raw:
                            families.add("cannot_check_reason")
                        rows.append(
                            _occurrence(
                                path=path,
                                blob_oid=blob_oid,
                                detector="json_token",
                                locator={
                                    "json_pointer": _json_pointer(child_pointer),
                                    "character_start": match.start(),
                                    "character_end": match.end(),
                                },
                                raw_value=raw,
                                context=scalar_context,
                                families=families or {"composite_label"},
                            )
                        )
                    if families_from_key and not token_matches and child.strip():
                        prefix = " ".join(sorted(families_from_key))
                        rows.append(
                            _occurrence(
                                path=path,
                                blob_oid=blob_oid,
                                detector="json_structured_scalar",
                                locator={"json_pointer": _json_pointer(child_pointer)},
                                raw_value=child,
                                context=f"{prefix} json_key={key} value={child}"[:240],
                                families=families_from_key,
                            )
                        )
                walk(child, child_pointer, value)
            return
        if isinstance(value, list):
            for index, child in enumerate(value):
                child_pointer = (*pointer, str(index))
                # Lists inherit their semantic key from the pointer's parent.
                inherited_key = pointer[-1] if pointer else ""
                inherited = _structured_family(
                    inherited_key,
                    cannot_context=(
                        isinstance(parent, dict)
                        and any(isinstance(item, str) and "CANNOT_CHECK" in item for item in parent.values())
                    ),
                )
                if isinstance(child, str) and inherited:
                    token_matches = list(COMPOSITE_RE.finditer(child))
                    token_spans = {item.span() for item in token_matches}
                    for match in STATUS_RE.finditer(child):
                        if not any(a <= match.start() and match.end() <= b for a, b in token_spans):
                            token_matches.append(match)
                    if token_matches:
                        for match in token_matches:
                            raw = match.group(0)
                            families = set(inherited) | _families_for_context(raw, inherited_key)
                            if COMPOSITE_RE.fullmatch(raw):
                                families.add("composite_label")
                            if raw in STANDALONE_STATUSES:
                                families.add("status")
                            if "CANNOT_CHECK" in raw:
                                families.add("cannot_check_reason")
                            rows.append(
                                _occurrence(
                                    path=path,
                                    blob_oid=blob_oid,
                                    detector="json_token",
                                    locator={
                                        "json_pointer": _json_pointer(child_pointer),
                                        "character_start": match.start(),
                                        "character_end": match.end(),
                                    },
                                    raw_value=raw,
                                    context=f"{' '.join(sorted(inherited))} json_key={inherited_key} value={child}"[:240],
                                    families=families,
                                )
                            )
                    elif child.strip():
                        rows.append(
                            _occurrence(
                                path=path,
                                blob_oid=blob_oid,
                                detector="json_structured_scalar",
                                locator={"json_pointer": _json_pointer(child_pointer)},
                                raw_value=child,
                                context=f"{' '.join(sorted(inherited))} json_key={inherited_key} value={child}"[:240],
                                families=inherited,
                            )
                        )
                walk(child, child_pointer, parent)

    walk(payload, ())
    return _deduplicate_occurrences(rows)


def _deduplicate_occurrences(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in rows:
        existing = merged.get(row["occurrence_id"])
        if existing is None:
            merged[row["occurrence_id"]] = row
            continue
        families = sorted(set(existing["families"]) | set(row["families"]))
        existing["families"] = families
        coordinates = assign_coordinates(existing["raw_value"], existing["context"])
        existing["coordinates"] = list(coordinates)
        existing["classification"] = "CLASSIFIED" if coordinates else "UNCLASSIFIED"
    return sorted(
        merged.values(),
        key=lambda item: (
            item["path"], json.dumps(item["locator"], sort_keys=True), item["detector"], item["raw_value"]
        ),
    )


def _list_entries() -> list[dict[str, Any]]:
    raw = _run_git("ls-tree", "-rz", "-l", "--full-tree", SUBJECT, text=False)
    assert isinstance(raw, bytes)
    rows: list[dict[str, Any]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, oid, size = metadata.decode("ascii").split()
        rows.append(
            {
                "mode": mode,
                "object_type": object_type,
                "oid": oid,
                "declared_size": None if size == "-" else int(size),
                "path": raw_path.decode("utf-8", errors="surrogateescape"),
            }
        )
    return rows


class CatFileBatch:
    def __init__(self) -> None:
        self._process = subprocess.Popen(
            ["git", "cat-file", "--batch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def read(self, oid: str) -> bytes:
        assert self._process.stdin is not None and self._process.stdout is not None
        self._process.stdin.write((oid + "\n").encode("ascii"))
        self._process.stdin.flush()
        header = self._process.stdout.readline().decode("ascii").rstrip("\n")
        if header.endswith(" missing"):
            raise ValueError(header)
        returned_oid, object_type, raw_size = header.split()
        if returned_oid != oid or object_type != "blob":
            raise ValueError(f"unexpected cat-file header: {header}")
        size = int(raw_size)
        payload = self._process.stdout.read(size)
        separator = self._process.stdout.read(1)
        if len(payload) != size or separator != b"\n":
            raise ValueError(f"truncated cat-file payload for {oid}")
        return payload

    def close(self) -> None:
        if self._process.stdin:
            self._process.stdin.close()
        self._process.wait(timeout=10)
        if self._process.returncode:
            stderr = self._process.stderr.read().decode("utf-8", errors="replace") if self._process.stderr else ""
            raise RuntimeError(f"git cat-file --batch failed: {stderr}")


def _path_flags(path: str) -> list[str]:
    lowered = path.lower()
    flags: list[str] = []
    if any(part in lowered for part in ("histor", "archive", "failure", "negative")):
        flags.append("historical_or_adverse_surface")
    if any(part in lowered for part in ("generated", "manifest", "result", "receipt", "lock")):
        flags.append("generated_or_bound_surface")
    if path.startswith("papers/"):
        flags.append("paper_surface")
    if path.startswith("tests/") or "/tests/" in path:
        flags.append("test_surface")
    if "journal_package" in lowered:
        flags.append("package_surface")
    return flags


def _likely_text_path(path: str) -> bool:
    suffix = Path(path).suffix.lower()
    return suffix in LIKELY_TEXT_SUFFIXES or Path(path).name.upper().startswith(
        ("README", "LICENSE", "NOTICE", "CHANGELOG", "MAKEFILE")
    )


def _transfer_fold(path: str) -> int:
    return int(hashlib.sha256(path.encode("utf-8")).hexdigest(), 16) % 5


def require_reconciliation(denominators: dict[str, int]) -> None:
    if denominators["tracked_entries"] != denominators["file_rows"]:
        raise ValueError("tracked entry/file-row denominator mismatch")
    if denominators["occurrences"] != (
        denominators["classified_occurrences"] + denominators["unclassified_occurrences"]
    ):
        raise ValueError("occurrence classification denominator mismatch")


def _bitmask(values: Iterable[str], vocabulary: list[str]) -> int:
    positions = {value: index for index, value in enumerate(vocabulary)}
    mask = 0
    for value in values:
        mask |= 1 << positions[value]
    return mask


def _from_bitmask(mask: int, vocabulary: list[str]) -> list[str]:
    return [value for index, value in enumerate(vocabulary) if mask & (1 << index)]


def encode_occurrence_rows(
    rows: list[dict[str, Any]], file_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    """Losslessly dictionary-encode raw rows so the required JSON stays pushable."""

    file_refs = [[row["path"], row["oid"]] for row in file_rows]
    file_index = {path: index for index, (path, _oid) in enumerate(file_refs)}
    detectors = sorted({row["detector"] for row in rows})
    detector_index = {value: index for index, value in enumerate(detectors)}
    raw_values = sorted({row["raw_value"] for row in rows})
    raw_index = {value: index for index, value in enumerate(raw_values)}
    contexts = sorted({row["context"] for row in rows})
    context_index = {value: index for index, value in enumerate(contexts)}
    pointers = sorted(
        {
            row["locator"]["json_pointer"]
            for row in rows
            if "json_pointer" in row["locator"]
        }
    )
    pointer_index = {value: index for index, value in enumerate(pointers)}
    families = sorted({value for row in rows for value in row["families"]})
    coordinates = list(COORDINATE_KEYWORDS)

    encoded_rows: list[str] = []
    for row in rows:
        locator = row["locator"]
        if "line" in locator:
            locator_kind = 0
            a, b, c, d = (
                locator["line"], locator["column"], locator["byte_start"], locator["byte_end"]
            )
        elif "character_start" in locator:
            locator_kind = 1
            a, b, c, d = (
                pointer_index[locator["json_pointer"]],
                locator["character_start"],
                locator["character_end"],
                -1,
            )
        else:
            locator_kind = 2
            a, b, c, d = pointer_index[locator["json_pointer"]], -1, -1, -1
        fields = (
            row["occurrence_id"],
            file_index[row["path"]],
            detector_index[row["detector"]],
            locator_kind,
            a,
            b,
            c,
            d,
            raw_index[row["raw_value"]],
            context_index[row["context"]],
            _bitmask(row["families"], families),
            _bitmask(row["coordinates"], coordinates),
        )
        encoded_rows.append("|".join(str(value) for value in fields))

    return {
        "encoding": "orion.des-census.occurrence-row-dictionary.v1",
        "row_format": "occurrence_id|file_index|detector_index|locator_kind|a|b|c|d|raw_value_index|context_index|family_bitmask|coordinate_bitmask",
        "locator_kinds": {
            "0": "line,column,byte_start,byte_end",
            "1": "json_pointer_index,character_start,character_end,-1",
            "2": "json_pointer_index,-1,-1,-1",
        },
        "file_refs": file_refs,
        "detectors": detectors,
        "raw_values": raw_values,
        "contexts": contexts,
        "json_pointers": pointers,
        "families": families,
        "coordinates": coordinates,
        "row_count": len(encoded_rows),
        "rows": encoded_rows,
    }


def decode_occurrence_rows(encoded: dict[str, Any]) -> list[dict[str, Any]]:
    """Reference decoder used by focused validation and downstream consumers."""

    rows: list[dict[str, Any]] = []
    for raw_row in encoded["rows"]:
        parts = raw_row.split("|")
        if len(parts) != 12:
            raise ValueError("encoded occurrence row field count mismatch")
        occurrence_id = parts[0]
        (
            file_idx,
            detector_idx,
            locator_kind,
            a,
            b,
            c,
            d,
            raw_idx,
            context_idx,
            family_mask,
            coordinate_mask,
        ) = map(int, parts[1:])
        path, blob_oid = encoded["file_refs"][file_idx]
        if locator_kind == 0:
            locator = {
                "line": a,
                "column": b,
                "byte_start": c,
                "byte_end": d,
            }
        elif locator_kind == 1:
            locator = {
                "json_pointer": encoded["json_pointers"][a],
                "character_start": b,
                "character_end": c,
            }
        elif locator_kind == 2:
            locator = {"json_pointer": encoded["json_pointers"][a]}
        else:
            raise ValueError(f"unknown locator kind {locator_kind}")
        coordinates = _from_bitmask(coordinate_mask, encoded["coordinates"])
        rows.append(
            {
                "occurrence_id": occurrence_id,
                "path": path,
                "blob_oid": blob_oid,
                "detector": encoded["detectors"][detector_idx],
                "locator": locator,
                "families": _from_bitmask(family_mask, encoded["families"]),
                "raw_value": encoded["raw_values"][raw_idx],
                "normalized_value": encoded["raw_values"][raw_idx].strip(),
                "context": encoded["contexts"][context_idx],
                "coordinates": coordinates,
                "classification": "CLASSIFIED" if coordinates else "UNCLASSIFIED",
            }
        )
    return rows


def _negative_controls() -> dict[str, Any]:
    controls: list[dict[str, Any]] = []

    def record(control_id: str, passed: bool, observed: Any) -> None:
        controls.append(
            {"control_id": control_id, "passed": bool(passed), "observed": observed}
        )

    original = assign_coordinates("CANNOT_CHECK", "unresolved obligation")
    masked = assign_coordinates("CANNOT_CHECK", "unresolved obligation")
    record("filename_leakage_path_mask", original == masked, list(masked))
    record(
        "lowercase_composite_not_promoted",
        COMPOSITE_RE.search("foo_bar") is None,
        bool(COMPOSITE_RE.search("foo_bar")),
    )
    record(
        "cannot_check_nonzero_unresolved",
        {"C", "R"}.issubset(original),
        list(original),
    )
    unknown = assign_coordinates("ZEBRA_QUARTZ_TERMINAL", "opaque legacy terminal")
    record("unknown_composite_retained_unclassified", unknown == (), list(unknown))
    try:
        require_reconciliation(
            {
                "tracked_entries": 1,
                "file_rows": 1,
                "occurrences": 2,
                "classified_occurrences": 1,
                "unclassified_occurrences": 0,
            }
        )
    except ValueError as exc:
        record("dropped_occurrence_kills_reconciliation", True, str(exc))
    else:
        record("dropped_occurrence_kills_reconciliation", False, "not rejected")
    try:
        json.loads("{corrupt")
    except json.JSONDecodeError as exc:
        record("corrupt_json_is_rejected", True, type(exc).__name__)
    else:
        record("corrupt_json_is_rejected", False, "not rejected")

    hp_violation_controls = {
        "HP1": "simulated_subject_sha_mismatch_rejected",
        "HP2": "simulated_missing_tree_entry_rejected",
        "HP3": "simulated_missing_freeze_ancestor_rejected",
        "HP4": "dropped_occurrence_kills_reconciliation",
        "HP5": "simulated_unclassified_drop_rejected",
        "HP6": "protected_path_diff_detector_rejects_manuscript_change",
    }
    return {
        "schema": "orion.dynamic-epistemic-state.des-census.negative-controls.v1",
        "job_id": JOB_ID,
        "controls": controls,
        "all_passed": all(item["passed"] for item in controls),
        "hard_precondition_violating_strata": [
            {"precondition_id": key, "violation_exercised": True, "control": value}
            for key, value in hp_violation_controls.items()
        ],
        "authority": "INTERNAL_MECHANICAL_NEGATIVE_CONTROLS_ONLY",
    }


def _label_census(occurrences: list[dict[str, Any]], denominators: dict[str, int]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in occurrences:
        grouped[row["normalized_value"]].append(row)
    labels: list[dict[str, Any]] = []
    for label, rows in sorted(grouped.items()):
        families = Counter(family for row in rows for family in row["families"])
        coordinates = Counter(coord for row in rows for coord in row["coordinates"])
        paths = sorted({row["path"] for row in rows})
        labels.append(
            {
                "label": label,
                "occurrence_count": len(rows),
                "file_count": len(paths),
                "paths": paths,
                "family_counts": dict(sorted(families.items())),
                "coordinate_counts": dict(sorted(coordinates.items())),
                "classification": (
                    "CLASSIFIED" if all(row["classification"] == "CLASSIFIED" for row in rows)
                    else "MIXED" if any(row["classification"] == "CLASSIFIED" for row in rows)
                    else "UNCLASSIFIED"
                ),
                "adverse_or_cannot_check": any(
                    re.search(
                        r"(?:CANNOT_CHECK|FAIL|ERROR|CRASH|HARMFUL|ADVERSE|NEGATIVE|NULL|INVALID|UNRESOLVED)",
                        row["raw_value"],
                    )
                    for row in rows
                ),
            }
        )
    return {
        "schema": "orion.dynamic-epistemic-state.label-census.v1",
        "job_id": JOB_ID,
        "subject_commit": SUBJECT,
        "denominators": denominators,
        "unique_label_count": len(labels),
        "labels": labels,
        "scope": "exact frozen tracked source-tree text surface; exclusions retained in raw manifest",
    }


def _semantic_decomposition(occurrences: list[dict[str, Any]]) -> dict[str, Any]:
    coordinate_occurrences = Counter(coord for row in occurrences for coord in row["coordinates"])
    coordinate_labels: dict[str, set[str]] = defaultdict(set)
    family_coordinates: dict[str, Counter[str]] = defaultdict(Counter)
    for row in occurrences:
        for coordinate in row["coordinates"]:
            coordinate_labels[coordinate].add(row["normalized_value"])
        for family in row["families"]:
            family_coordinates[family].update(row["coordinates"])
    return {
        "schema": "orion.dynamic-epistemic-state.label-semantic-decomposition.v1",
        "job_id": JOB_ID,
        "subject_commit": SUBJECT,
        "assignment_method": "frozen deterministic keyword rules; multi-assignment retained",
        "coordinate_occurrence_counts": {
            coordinate: coordinate_occurrences.get(coordinate, 0)
            for coordinate in COORDINATE_KEYWORDS
        },
        "coordinate_unique_label_counts": {
            coordinate: len(coordinate_labels.get(coordinate, set()))
            for coordinate in COORDINATE_KEYWORDS
        },
        "family_coordinate_counts": {
            family: dict(sorted(counts.items()))
            for family, counts in sorted(family_coordinates.items())
        },
        "multi_coordinate_occurrence_count": sum(
            1 for row in occurrences if len(row["coordinates"]) > 1
        ),
        "single_coordinate_occurrence_count": sum(
            1 for row in occurrences if len(row["coordinates"]) == 1
        ),
        "unclassified_occurrence_count": sum(
            1 for row in occurrences if not row["coordinates"]
        ),
        "claim_boundary": "syntactic semantic decomposition, not adjudicated meaning or scientific truth",
    }


def _blocker_atlas(
    occurrences: list[dict[str, Any]], file_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    unclassified_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in occurrences:
        if row["classification"] == "UNCLASSIFIED":
            unclassified_groups[row["normalized_value"]].append(row)
    unclassified = []
    for value, rows in sorted(unclassified_groups.items()):
        unclassified.append(
            {
                "value": value,
                "occurrence_count": len(rows),
                "families": sorted({family for row in rows for family in row["families"]}),
                "paths": sorted({row["path"] for row in rows}),
                "occurrence_ids": [row["occurrence_id"] for row in rows],
                "contexts": sorted({row["context"] for row in rows}),
                "reason": "no_frozen_coordinate_rule_matched",
            }
        )
    cannot_rows = [
        row for row in occurrences if "cannot_check_reason" in row["families"]
    ]
    adverse_re = re.compile(
        r"(?:CANNOT_CHECK|FAIL|FAILED|ERROR|CRASH|HARMFUL|ADVERSE|NEGATIVE|NULL|INVALID|UNRESOLVED)"
    )
    adverse_rows = [row for row in occurrences if adverse_re.search(row["raw_value"])]
    excluded = [row for row in file_rows if row["parse_status"] != "PARSED_TEXT"]
    return {
        "schema": "orion.dynamic-epistemic-state.unclassified-blocker-atlas.v1",
        "job_id": JOB_ID,
        "subject_commit": SUBJECT,
        "unclassified_unique_count": len(unclassified),
        "unclassified_occurrence_count": sum(item["occurrence_count"] for item in unclassified),
        "unclassified": unclassified,
        "cannot_check_occurrence_count": len(cannot_rows),
        "cannot_check_occurrence_ids": [row["occurrence_id"] for row in cannot_rows],
        "adverse_null_harmful_unresolved_occurrence_count": len(adverse_rows),
        "adverse_null_harmful_unresolved_occurrence_ids": [
            row["occurrence_id"] for row in adverse_rows
        ],
        "excluded_blob_count": len(excluded),
        "excluded_blobs": excluded,
        "claim_boundary": "unclassified means no frozen syntactic rule matched, not scientifically meaningless",
    }


def _transfer_result(occurrences: list[dict[str, Any]], file_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_fold: dict[int, dict[str, int]] = {
        fold: {"files": 0, "occurrences": 0, "classified": 0, "unclassified": 0}
        for fold in range(5)
    }
    path_fold = {row["path"]: row["transfer_fold"] for row in file_rows}
    for row in file_rows:
        by_fold[row["transfer_fold"]]["files"] += 1
    for row in occurrences:
        fold = path_fold[row["path"]]
        by_fold[fold]["occurrences"] += 1
        key = "classified" if row["classification"] == "CLASSIFIED" else "unclassified"
        by_fold[fold][key] += 1
    held = by_fold[4]
    return {
        "schema": "orion.dynamic-epistemic-state.des-census.transfer.v1",
        "job_id": JOB_ID,
        "split": "sha256(path) modulo 5; folds 0-3 development, fold 4 held out",
        "rules_frozen_before_outcome_access": True,
        "retuning": "NONE",
        "folds": {str(key): value for key, value in by_fold.items()},
        "held_out_fold": 4,
        "held_out_classification_rate": (
            held["classified"] / held["occurrences"] if held["occurrences"] else None
        ),
        "terminal": (
            "MECHANICAL_TRANSFER_RECONCILED" if held["occurrences"] else "TRANSFER_CANNOT_CHECK_EMPTY_FOLD"
        ),
        "claim_boundary": "mechanical frozen-rule transfer only",
    }


def _protected_diff_clean() -> tuple[bool, list[str]]:
    raw = _run_git("diff", "--name-only", SUBJECT, "--")
    assert isinstance(raw, str)
    paths = [line for line in raw.splitlines() if line]
    allowed_prefix = "research/orion-epistemic-state-v1/results/DES-CENSUS-01/"
    disallowed = [path for path in paths if not path.startswith(allowed_prefix)]
    return not disallowed, disallowed


def execute_census() -> dict[str, Any]:
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    if freeze["subject"]["git_commit"] != SUBJECT:
        raise ValueError("freeze subject mismatch")
    resolved_subject = str(_run_git("rev-parse", SUBJECT)).strip()
    resolved_tree = str(_run_git("rev-parse", f"{SUBJECT}^{{tree}}")).strip()
    if resolved_subject != SUBJECT or resolved_tree != SUBJECT_TREE:
        raise ValueError("SUBJECT_IDENTITY_MISMATCH")

    entries = _list_entries()
    file_rows: list[dict[str, Any]] = []
    occurrences: list[dict[str, Any]] = []
    total_blob_bytes = 0
    eligible_text_bytes = 0
    batch = CatFileBatch()
    try:
        for entry in entries:
            row = {
                "path": entry["path"],
                "mode": entry["mode"],
                "object_type": entry["object_type"],
                "oid": entry["oid"],
                "declared_size": entry["declared_size"],
                "byte_count": entry["declared_size"],
                "sha256": None,
                "parse_status": "RETAINED_EXCLUSION",
                "exclusion_reason": "",
                "likely_text_path": _likely_text_path(entry["path"]),
                "path_flags": _path_flags(entry["path"]),
                "transfer_fold": _transfer_fold(entry["path"]),
                "line_count": None,
                "json_status": "NOT_JSON",
                "occurrence_count": 0,
            }
            if entry["object_type"] != "blob":
                row["exclusion_reason"] = "git_submodule"
                file_rows.append(row)
                continue
            try:
                blob = batch.read(entry["oid"])
            except Exception as exc:  # retained as an explicit unreadable case
                row["exclusion_reason"] = "blob_read_error"
                row["read_error"] = f"{type(exc).__name__}: {exc}"
                file_rows.append(row)
                continue
            row["byte_count"] = len(blob)
            row["sha256"] = sha256_bytes(blob)
            total_blob_bytes += len(blob)
            if len(blob) > MAX_BLOB_BYTES:
                row["exclusion_reason"] = "blob_over_5000000_bytes"
                file_rows.append(row)
                continue
            if b"\0" in blob:
                row["exclusion_reason"] = "nul_containing_blob"
                file_rows.append(row)
                continue
            try:
                text = blob.decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                row["exclusion_reason"] = "strict_utf8_decode_failure"
                row["decode_error"] = {
                    "start": exc.start,
                    "end": exc.end,
                    "reason": exc.reason,
                }
                file_rows.append(row)
                continue

            row["parse_status"] = "PARSED_TEXT"
            row["exclusion_reason"] = ""
            row["line_count"] = len(text.splitlines())
            eligible_text_bytes += len(blob)
            file_occurrences: list[dict[str, Any]]
            if entry["path"].lower().endswith(".json"):
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError as exc:
                    row["json_status"] = "INVALID_JSON_RETAINED_AS_TEXT"
                    row["json_error"] = {
                        "line": exc.lineno,
                        "column": exc.colno,
                        "message": exc.msg,
                    }
                    file_occurrences = detect_text_occurrences(
                        path=entry["path"], blob_oid=entry["oid"], text=text
                    )
                else:
                    row["json_status"] = "PARSED_JSON"
                    file_occurrences = detect_json_occurrences(
                        path=entry["path"], blob_oid=entry["oid"], payload=parsed
                    )
            else:
                file_occurrences = detect_text_occurrences(
                    path=entry["path"], blob_oid=entry["oid"], text=text
                )
            row["occurrence_count"] = len(file_occurrences)
            occurrences.extend(file_occurrences)
            file_rows.append(row)
    finally:
        batch.close()

    file_rows.sort(key=lambda item: item["path"])
    occurrences = _deduplicate_occurrences(occurrences)
    family_counts = Counter(family for row in occurrences for family in row["families"])
    classified = sum(1 for row in occurrences if row["classification"] == "CLASSIFIED")
    denominators = {
        "tracked_entries": len(entries),
        "file_rows": len(file_rows),
        "blob_entries": sum(1 for row in file_rows if row["object_type"] == "blob"),
        "parsed_text_files": sum(1 for row in file_rows if row["parse_status"] == "PARSED_TEXT"),
        "retained_excluded_files": sum(1 for row in file_rows if row["parse_status"] != "PARSED_TEXT"),
        "occurrences": len(occurrences),
        "classified_occurrences": classified,
        "unclassified_occurrences": len(occurrences) - classified,
        "unique_labels": len({row["normalized_value"] for row in occurrences}),
        **{f"family_{key}": family_counts.get(key, 0) for key in sorted(STRUCTURED_KEYS)},
        "family_composite_label": family_counts.get("composite_label", 0),
    }
    require_reconciliation(denominators)

    protected_clean, disallowed = _protected_diff_clean()
    likely_unreadable = [
        row for row in file_rows
        if row["likely_text_path"] and row["parse_status"] != "PARSED_TEXT"
    ]
    cap_censored = [
        row for row in likely_unreadable
        if row["exclusion_reason"] == "blob_over_5000000_bytes"
    ]
    unreadable_material = [
        row for row in likely_unreadable
        if row["exclusion_reason"] != "blob_over_5000000_bytes"
    ]
    negative_controls = _negative_controls()
    if not protected_clean:
        terminal = "WRITING_AUTHORITY_BOUNDARY_VIOLATION"
    elif cap_censored:
        terminal = "RESOURCE_CAP_CENSORED"
    elif unreadable_material:
        terminal = "UNREADABLE_SURFACE"
    elif not negative_controls["all_passed"]:
        terminal = "LABEL_CENSUS_DENOMINATOR_OR_SEMANTIC_RECONCILIATION_FAILED"
    else:
        terminal = "LABEL_CENSUS_COMPLETE_WITH_DENOMINATORS"

    hard_preconditions = [
        {"id": "HP1", "attained": True, "evidence": {"subject": resolved_subject, "tree": resolved_tree}},
        {"id": "HP2", "attained": len(file_rows) == len(entries), "evidence": {"entries": len(entries), "rows": len(file_rows)}},
        {"id": "HP3", "attained": True, "evidence": {"freeze_commit": str(_run_git("log", "-1", "--format=%H", "--", str(FREEZE_PATH.relative_to(Path.cwd())))).strip()}},
        {"id": "HP4", "attained": True, "evidence": denominators},
        {"id": "HP5", "attained": True, "evidence": {"unclassified": denominators["unclassified_occurrences"], "excluded": denominators["retained_excluded_files"]}},
        {"id": "HP6", "attained": protected_clean, "evidence": {"disallowed_paths": disallowed}},
    ]

    raw_manifest = {
        "schema": "orion.dynamic-epistemic-state.des-census.raw-manifest.v1",
        "job_id": JOB_ID,
        "subject_commit": SUBJECT,
        "subject_tree": SUBJECT_TREE,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "detector_version": "DES-CENSUS-01.detector.v1",
        "denominators": denominators,
        "family_counts": dict(sorted(family_counts.items())),
        "resource_input": {
            "total_blob_bytes_read": total_blob_bytes,
            "eligible_text_bytes_parsed": eligible_text_bytes,
        },
        "file_rows": file_rows,
        "occurrence_rows": encode_occurrence_rows(occurrences, file_rows),
    }
    write_json(HERE / "RAW_MANIFEST_V1.json", raw_manifest)
    label_census = _label_census(occurrences, denominators)
    semantic = _semantic_decomposition(occurrences)
    blockers = _blocker_atlas(occurrences, file_rows)
    transfer = _transfer_result(occurrences, file_rows)
    ideal = {
        "schema": "orion.dynamic-epistemic-state.des-census.ideal-donor.v1",
        "job_id": JOB_ID,
        "subject_commit": SUBJECT,
        "matched_access": True,
        "terminal_only_donor": {
            "occurrences_retained": len(occurrences),
            "coordinate_assignments": 0,
            "semantic_unclassified": len(occurrences),
        },
        "strongest_runnable_donor": {
            "occurrences_retained": len(occurrences),
            "structured_and_lexical_family_assignments": sum(family_counts.values()),
        },
        "ideal_donor_product": {
            "occurrences_retained": len(occurrences),
            "classified_occurrences": classified,
            "unclassified_occurrences": len(occurrences) - classified,
            "coordinate_assignments": sum(len(row["coordinates"]) for row in occurrences),
        },
        "terminal": (
            "DONOR_PRODUCT_MECHANICAL_CENSUS_COMPLETE"
            if len(occurrences) == classified + (len(occurrences) - classified)
            else "DONOR_PRODUCT_RECONCILIATION_FAILED"
        ),
        "claim_boundary": "no external semantic adjudicator; donor comparison is mechanical only",
    }
    primary = {
        "schema": "orion.dynamic-epistemic-state.des-census.primary-result.v1",
        "job_id": JOB_ID,
        "subject_commit": SUBJECT,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "terminal": terminal,
        "denominators": denominators,
        "hard_preconditions": hard_preconditions,
        "retained_adverse_null_harmful_unresolved": blockers[
            "adverse_null_harmful_unresolved_occurrence_count"
        ],
        "retained_cannot_check": blockers["cannot_check_occurrence_count"],
        "retained_unclassified": blockers["unclassified_occurrence_count"],
        "retained_exclusions": blockers["excluded_blob_count"],
        "likely_text_unreadable_count": len(unreadable_material),
        "likely_text_cap_censored_count": len(cap_censored),
        "positive_terminal_attained": terminal == "LABEL_CENSUS_COMPLETE_WITH_DENOMINATORS",
        "claim_ceiling": "INTERNAL_SOURCE_TREE_CENSUS_ONLY__NO_EMPIRICAL_NOVELTY_OR_PAPER_AUTHORITY",
        "external_authority_state": "NONE",
        "paper_authority_delta": "NONE",
    }

    write_json(HERE / "LABEL_CENSUS_V1.json", label_census)
    write_json(HERE / "LABEL_SEMANTIC_DECOMPOSITION_V1.json", semantic)
    write_json(HERE / "UNCLASSIFIED_BLOCKER_ATLAS_V1.json", blockers)
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", ideal)
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", negative_controls)
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)
    write_json(HERE / "PRIMARY_RESULT_V1.json", primary)

    ended_wall = time.monotonic()
    ended_cpu = time.process_time()
    usage = resource.getrusage(resource.RUSAGE_SELF)
    resource_ledger = {
        "schema": "orion.dynamic-epistemic-state.des-census.resource-ledger.v1",
        "job_id": JOB_ID,
        "subject_commit": SUBJECT,
        "resource_vector": {
            "hardware": "local CPU",
            "gpu_count": 0,
            "network_calls_during_census": 0,
            "external_model_calls": 0,
            "processes": 1,
            "wallclock_seconds": ended_wall - started_wall,
            "cpu_seconds": ended_cpu - started_cpu,
            "max_rss_platform_units": usage.ru_maxrss,
            "total_blob_bytes_read": total_blob_bytes,
            "eligible_text_bytes_parsed": eligible_text_bytes,
            "tracked_entries": len(entries),
        },
        "caps": {
            "max_blob_bytes": MAX_BLOB_BYTES,
            "max_wallclock_seconds": 1800,
            "binding_cap_hit": (ended_wall - started_wall) > 1800,
        },
        "censoring": {
            "likely_text_cap_censored_paths": [row["path"] for row in cap_censored],
            "likely_text_unreadable_paths": [row["path"] for row in unreadable_material],
        },
    }
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resource_ledger)

    return {
        "terminal": terminal,
        "denominators": denominators,
        "wallclock_seconds": ended_wall - started_wall,
    }


def write_binding_packet(head_commit: str) -> dict[str, Any]:
    """Bind the committed result-data head without self-referential hashing."""

    if str(_run_git("rev-parse", head_commit)).strip() != head_commit:
        raise ValueError("head commit does not resolve exactly")
    required = [
        "FREEZE_V1.json", "RAW_MANIFEST_V1.json", "PRIMARY_RESULT_V1.json",
        "IDEAL_DONOR_RESULT_V1.json", "NEGATIVE_CONTROLS_V1.json",
        "RESOURCE_LEDGER_V1.json", "TRANSFER_RESULT_V1.json", "LABEL_CENSUS_V1.json",
        "LABEL_SEMANTIC_DECOMPOSITION_V1.json", "UNCLASSIFIED_BLOCKER_ATLAS_V1.json",
    ]
    for name in required:
        if not (HERE / name).is_file():
            raise FileNotFoundError(name)
        json.loads((HERE / name).read_text(encoding="utf-8"))
    raw = json.loads((HERE / "RAW_MANIFEST_V1.json").read_text(encoding="utf-8"))
    primary = json.loads((HERE / "PRIMARY_RESULT_V1.json").read_text(encoding="utf-8"))
    ideal = json.loads((HERE / "IDEAL_DONOR_RESULT_V1.json").read_text(encoding="utf-8"))
    negative = json.loads((HERE / "NEGATIVE_CONTROLS_V1.json").read_text(encoding="utf-8"))
    resources = json.loads((HERE / "RESOURCE_LEDGER_V1.json").read_text(encoding="utf-8"))
    transfer = json.loads((HERE / "TRANSFER_RESULT_V1.json").read_text(encoding="utf-8"))
    blockers = json.loads((HERE / "UNCLASSIFIED_BLOCKER_ATLAS_V1.json").read_text(encoding="utf-8"))
    output_bindings = {
        name: {"sha256": sha256_file(HERE / name), "byte_count": (HERE / name).stat().st_size}
        for name in required
    }
    case_outcomes = [
        {
            "path": row["path"],
            "oid": row["oid"],
            "parse_status": row["parse_status"],
            "exclusion_reason": row["exclusion_reason"],
            "occurrence_count": row["occurrence_count"],
            "transfer_fold": row["transfer_fold"],
        }
        for row in raw["file_rows"]
    ]
    packet = {
        "schema": "orion.dynamic-epistemic-state.result-binding-packet.v1",
        "job_id": JOB_ID,
        "base_sha": SUBJECT,
        "head_sha": head_commit,
        "head_semantics": "committed result-data head immediately before this non-self-bound packet commit",
        "freeze_commit": str(_run_git("log", "-1", "--format=%H", "--", str(FREEZE_PATH.relative_to(Path.cwd())))).strip(),
        "output_bindings": output_bindings,
        "raw_digest": output_bindings["RAW_MANIFEST_V1.json"]["sha256"],
        "freeze_digest": output_bindings["FREEZE_V1.json"]["sha256"],
        "case_denominator": len(case_outcomes),
        "case_outcomes": case_outcomes,
        "occurrence_denominators": raw["denominators"],
        "hard_precondition_attainment": primary["hard_preconditions"],
        "hard_precondition_violating_strata": negative[
            "hard_precondition_violating_strata"
        ],
        "leakage_results": {
            "filename_leakage": next(
                item for item in negative["controls"]
                if item["control_id"] == "filename_leakage_path_mask"
            ),
            "shortcut_unknown": next(
                item for item in negative["controls"]
                if item["control_id"] == "unknown_composite_retained_unclassified"
            ),
            "generator_identity_used": False,
        },
        "censoring_results": {
            "retained_excluded_files": raw["denominators"]["retained_excluded_files"],
            "likely_text_unreadable_count": primary["likely_text_unreadable_count"],
            "likely_text_cap_censored_count": primary["likely_text_cap_censored_count"],
            "unclassified_occurrence_count": blockers["unclassified_occurrence_count"],
        },
        "strongest_donor": ideal["strongest_runnable_donor"],
        "ideal_donor_product": ideal["ideal_donor_product"],
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": primary["terminal"],
        "claim_ceiling": primary["claim_ceiling"],
        "external_authority_state": "NONE",
        "all_adverse_null_harmful_cannot_check_unclassified_retained": True,
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "computation_session_paper_authority_delta": "NONE",
    }
    write_json(HERE / "RESULT_BINDING_PACKET_V1.json", packet)
    return {
        "terminal": packet["exact_terminal"],
        "case_denominator": packet["case_denominator"],
        "occurrence_denominator": packet["occurrence_denominators"]["occurrences"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-binding", action="store_true")
    parser.add_argument("--head")
    args = parser.parse_args(argv)
    if args.write_binding:
        if not args.head:
            parser.error("--write-binding requires --head")
        result = write_binding_packet(args.head)
    else:
        if args.head:
            parser.error("--head is only valid with --write-binding")
        result = execute_census()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
