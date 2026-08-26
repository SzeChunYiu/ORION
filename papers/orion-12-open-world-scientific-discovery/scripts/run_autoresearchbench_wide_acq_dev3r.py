#!/usr/bin/env python3
"""Harness-corrected execution wrapper for the frozen Dev-3 acquisition system.

The Dev-3 acquisition policy itself is unchanged. The first Dev-3 execution
revealed that the repository-wide arXiv ``parse_atom`` helper labels every entry
whose title begins with the word "Error" as a service error. Several legitimate
scientific papers on error bounds/correction therefore opened false obligations.

This wrapper changes only response classification/identity extraction:
- an API error is recognized only by the documented ``arxiv.org/api/errors``
  entry identity;
- scorer candidates are still only Atom ``entry/id`` identities;
- query derivation, task order, request budget, ranking and candidate cap are
  inherited unchanged from the frozen Dev-3 implementation.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import urllib.parse
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Any

import defusedxml.ElementTree as SafeElementTree

HERE = Path(__file__).resolve().parent
DEV3_PATH = HERE / "run_autoresearchbench_wide_acq_dev3.py"
_ATOM = "{http://www.w3.org/2005/Atom}"


def _load_dev3():
    spec = importlib.util.spec_from_file_location("orion_p2_wide_dev3_frozen", DEV3_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen Dev-3 implementation at {DEV3_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


dev3 = _load_dev3()
cmp = dev3.cmp


def _text(node: ElementTree.Element | None) -> str:
    return " ".join(node.text.split()) if node is not None and node.text else ""


def parse_entry_ids(body: str, *, max_results: int) -> tuple[str, tuple[str, ...], str]:
    """Parse only returned Atom entry identities; titles never imply API error."""
    try:
        root = SafeElementTree.fromstring(body)
    except (ElementTree.ParseError, ValueError) as error:
        return "ERROR", (), f"unparseable_feed:{type(error).__name__}:{error}"
    ids: list[str] = []
    for entry in root.findall(f"{_ATOM}entry"):
        raw_id = _text(entry.find(f"{_ATOM}id"))
        if not raw_id:
            continue
        if "arxiv.org/api/errors" in raw_id:
            note = _text(entry.find(f"{_ATOM}summary")) or _text(entry.find(f"{_ATOM}title"))
            return "ERROR", (), f"arxiv_api_error:{note}"
        normalized = dev3.normalize_entry_id(raw_id)
        if normalized and normalized not in ids:
            ids.append(normalized)
    if len(ids) > max_results:
        raise AssertionError(
            f"entry-only parser returned {len(ids)} IDs above max_results={max_results}"
        )
    return "OK", tuple(ids), ""


def corrected_arxiv_entry_route(
    query: str, *, clock: Any, max_results: int
) -> tuple[str, tuple[str, ...], str]:
    clock.wait("arxiv", cmp.DECLARED_CONSTANTS["arxiv_min_interval_seconds"])
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": query, "start": 0, "max_results": max_results, "sortBy": "relevance"}
    )
    status, body, note, attempts = cmp._http_get(
        url, timeout=cmp.DECLARED_CONSTANTS["http_timeout_seconds"]
    )
    suffix = f"attempts:{attempts}" if attempts > 1 else ""
    if status != 200 or not body:
        kind = "UNAVAILABLE" if status in (0, 429, 503) else "ERROR"
        return kind, (), " ".join(x for x in (note or f"status:{status}", suffix) if x)
    parsed_status, ids, parsed_note = parse_entry_ids(
        body.decode("utf-8", "replace"), max_results=max_results
    )
    return parsed_status, ids, " ".join(x for x in (parsed_note, suffix) if x)


# Patch only the response-classification hook used by frozen Dev-3 run_system.
dev3.arxiv_entry_route = corrected_arxiv_entry_route


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--task-ids", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--progress-every", type=int, default=4)
    args = parser.parse_args(argv)
    payload = dev3.run_comparison(
        args.public, args.task_ids, args.out_dir, args.progress_every
    )
    payload["schema_version"] = "orion.p2.autoresearchbench-wide-acquisition-dev3r.v1"
    payload["harness_correction"] = {
        "frozen_dev3_blob": "4d2c6d08efa3cd79139968a439c4e08644b196d8",
        "change": "API error detection restricted to arxiv.org/api/errors entry identity; acquisition policy unchanged"
    }
    (args.out_dir / "DEV3R_RUN_MANIFEST.json").write_text(
        json.dumps(payload, sort_keys=True, indent=1) + "\n", encoding="utf-8"
    )
    print("ARB_WIDE_DEV3R=" + json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
