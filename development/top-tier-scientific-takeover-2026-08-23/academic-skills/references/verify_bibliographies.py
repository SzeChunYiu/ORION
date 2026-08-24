#!/usr/bin/env python3
"""Crossref-first bibliographic identity audit for the five manuscripts."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ENTRY = re.compile(r"(?ms)^@(\w+)\s*\{\s*([^,]+),\s*(.*?)(?=^@|\Z)")
FIELD = re.compile(r"(?ms)^\s*(\w+)\s*=\s*[\{\"](.*?)[\}\"]\s*,?\s*$")


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"[{}\\]", "", value)
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def parse_bib(path: Path) -> list[dict]:
    rows = []
    for kind, key, body in ENTRY.findall(path.read_text(errors="replace")):
        fields = {name.lower(): value.strip() for name, value in FIELD.findall(body)}
        rows.append({"kind": kind, "key": key.strip(), "fields": fields})
    return rows


def crossref(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(url, headers={"User-Agent": "ORION-reference-audit/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return {"http_status": response.status, "message": json.load(response)["message"]}
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 3:
                time.sleep(1.5 * (attempt + 1))
                continue
            return {"http_status": exc.code, "error": str(exc)}
        except Exception as exc:  # network failures are typed rather than hidden
            return {"http_status": None, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError("unreachable")


def doi_resolver_status(doi: str) -> int | None:
    request = urllib.request.Request(
        "https://doi.org/" + urllib.parse.quote(doi, safe="/:().-"),
        method="HEAD",
        headers={"User-Agent": "ORION-reference-audit/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return None


def audit_entry(paper: str, entry: dict) -> dict:
    fields = entry["fields"]
    doi = fields.get("doi", "").strip().rstrip(".,").replace("https://doi.org/", "")
    row = {
        "paper": paper,
        "key": entry["key"],
        "kind": entry["kind"],
        "title": fields.get("title"),
        "year": fields.get("year"),
        "doi": doi or None,
    }
    if not doi:
        row.update(status="manual_needed", reason="no_doi_crossref_first_pass")
        return row
    result = crossref(doi)
    row["crossref_http_status"] = result["http_status"]
    if result["http_status"] != 200:
        resolver_status = doi_resolver_status(doi) if result["http_status"] == 404 else None
        row["doi_resolver_http_status"] = resolver_status
        if resolver_status is not None and resolver_status < 400:
            row.update(status="manual_needed", reason="doi_resolves_but_crossref_metadata_unavailable")
        else:
            row.update(status="not_found" if result["http_status"] == 404 else "manual_needed", reason=result.get("error"))
        return row
    message = result["message"]
    remote_title = (message.get("title") or [""])[0]
    remote_year = None
    for name in ("published-print", "published-online", "issued"):
        parts = message.get(name, {}).get("date-parts", [])
        if parts and parts[0] and isinstance(parts[0][0], int):
            remote_year = str(parts[0][0])
            break
    local_title, x_title = normalize(fields.get("title", "")), normalize(remote_title)
    title_match = bool(local_title and x_title and (local_title == x_title or local_title in x_title or x_title in local_title))
    year_match = not fields.get("year") or not remote_year or fields["year"].strip() == remote_year
    row["crossref"] = {
        "title": remote_title,
        "year": remote_year,
        "container_title": (message.get("container-title") or [None])[0],
        "volume": message.get("volume"),
        "issue": message.get("issue"),
        "page": message.get("page"),
        "author_count": len(message.get("author") or []),
    }
    row["field_match"] = {"title": title_match, "year": year_match}
    if not title_match:
        row.update(status="needs_fix", reason="doi_title_mismatch")
    elif not year_match:
        row.update(status="check_suggested", reason="year_mismatch_or_online_print_drift")
    else:
        row.update(status="verified", reason="doi_resolves_title_and_year_match")
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    bibs = sorted(args.root.glob("papers/paper-0[1-5]-*/manuscript/bibliography.bib"))
    jobs = []
    for path in bibs:
        paper = path.parts[-3].split("-")[1]
        jobs.extend((paper, entry) for entry in parse_bib(path))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(lambda job: audit_entry(*job), jobs))
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    payload = {
        "schema_version": "orion.p1-p5.crossref-reference-audit.v1",
        "captured_at_unix": int(time.time()),
        "source": "Crossref REST first pass",
        "entry_count": len(rows),
        "counts": counts,
        "entries": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"entry_count": len(rows), "counts": counts}, sort_keys=True))
    return 1 if counts.get("needs_fix") or counts.get("not_found") else 0


if __name__ == "__main__":
    raise SystemExit(main())
