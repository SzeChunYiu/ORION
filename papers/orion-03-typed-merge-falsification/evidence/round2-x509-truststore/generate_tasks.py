#!/usr/bin/env python3
"""ORION-03 Round 2: freeze the merge-task manifest from the pinned corpus.

Parses the upstream OpenSSL 3.6.4 labeled verify table (25-test_verify.t) into
upstream-authored store states, constructs the two frozen merge-task families
(F-U upstream pairs, F-P parity partition), and emits TASK_MANIFEST_V2.json.

No engine is invoked: the manifest is frozen before any merge evaluation.
Fail-closed: any parse anomaly aborts with a nonzero exit.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

FROZEN_ATTIME = 1759276800  # 2026-08-27T00:00:00Z
FAMILY_UPSTREAM = "UPSTREAM_PAIR"
FAMILY_PARITY = "PARITY_PARTITION"
FARITY_PURPOSES = ("sslserver", "")

# References to material that test/certs/setup.sh generates at test runtime
# (absent from the static tag snapshot). Rows citing only these are excluded
# from the usable table; the exclusion is itself frozen below.
RUNTIME_GENERATED_REFS = {"pc6-cert"}

CERT_MARKERS = (
    b"-----BEGIN CERTIFICATE-----",
    b"-----BEGIN TRUSTED CERTIFICATE-----",
)
PRIVATE_KEY_MARKER = b"PRIVATE KEY-----"


def fail(msg: str) -> None:
    print(f"FAIL-CLOSED: {msg}", file=sys.stderr)
    raise SystemExit(2)


def parse_verify_table(recipe_text: str) -> list[dict]:
    """Parse ok(verify("leaf","purpose",[trusted],[untrusted],opts...), "name") rows.

    Handles ok()/ok_nofips(), negation, [qw(a b)] lists, ["a"] lists and
    multi-line rows. Depth-scans nested parens (qw(...)) fail-closed.
    """
    cases: list[dict] = []
    # Rows inside a with({ exit_checker ... }) block assert a NONZERO engine
    # exit code (perl-level ok() over an expected verification failure), so
    # their engine-level expectation is INVALID even without a "!".
    m_with = re.search(r"with\(\{\s*exit_checker", recipe_text)
    span = None
    if m_with:
        close = recipe_text.find("});", m_with.end())
        if close == -1:
            fail("unterminated with(exit_checker) block")
        span = (m_with.start(), close)
    pattern = re.compile(r"ok(?:_nofips)?\((!?)\s*verify\(")
    flipped: list[str] = []
    for m in pattern.finditer(recipe_text):
        negated = m.group(1) == "!"
        flipped_row = False
        if span and span[0] <= m.start() <= span[1]:
            negated = not negated
            flipped_row = True
            flipped.append(len(cases))
        start = m.end()
        depth = 1
        i = start
        in_str = False
        while i < len(recipe_text) and depth > 0:
            ch = recipe_text[i]
            if in_str:
                if ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        if depth != 0:
            fail("unbalanced verify() row")
        body = recipe_text[start:i]
        rest = recipe_text[i + 1 :]
        name_m = re.match(r"\s*,\s*\"([^\"]*)\"", rest)
        name = name_m.group(1) if name_m else ""
        # Split top-level commas of the verify(...) body.
        parts: list[str] = []
        depth = 0
        cur = ""
        in_str = False
        for ch in body:
            if ch == '"' and depth == 0:
                in_str = not in_str
                cur += ch
                continue
            if not in_str:
                if ch in "([":
                    depth += 1
                elif ch in ")]":
                    depth -= 1
                elif ch == "," and depth == 0:
                    parts.append(cur.strip())
                    cur = ""
                    continue
            cur += ch
        if cur.strip():
            parts.append(cur.strip())
        if len(parts) < 4:
            fail(f"verify row with too few parts: {name!r}: {parts}")
        leaf = parts[0].strip().strip('"')
        purpose = parts[1].strip().strip('"')

        def parse_list(tok: str) -> list[str]:
            tok = tok.strip()
            if tok.startswith("[") and tok.endswith("]"):
                inner = tok[1:-1]
                if "qw(" in inner:
                    qw = re.search(r"qw\(([^)]*)\)", inner)
                    if not qw:
                        fail(f"unparsable qw list in {name!r}")
                    return qw.group(1).split()
                items = re.findall(r'"([^"]*)"', inner)
                if items:
                    return items
                return inner.split()
            return [tok.strip().strip('"')]

        trusted = parse_list(parts[2])
        untrusted = parse_list(parts[3])
        opts: list[str] = []
        for tok in parts[4:]:
            opts.append(tok.strip().strip('"'))
        cases.append(
            {
                "name": name,
                "leaf": leaf,
                "purpose": purpose,
                "trusted": sorted(trusted),
                "untrusted": sorted(untrusted),
                "opts": opts,
                "upstream_expected": "INVALID" if negated else "VALID",
                "exit_checker_flipped": flipped_row,
            }
        )
    if len(flipped) != 1:
        fail(f"expected exactly 1 exit_checker row, saw {len(flipped)}")
    if cases[flipped[0]]["leaf"] != "bad-othername-namec":
        fail(f"exit_checker row changed: {cases[flipped[0]]['leaf']!r}")
    return cases


def state_signature(state: dict) -> str:
    return json.dumps(
        {
            "trusted": state["trusted"],
            "untrusted": state["untrusted"],
            "opts": state["opts"],
        },
        sort_keys=True,
    )


def main() -> None:
    here = Path(__file__).resolve().parent
    corpus = here / "third_party" / "openssl-3.6.4-testcerts"
    certs_dir = corpus / "test" / "certs"
    recipe = corpus / "test" / "recipes" / "25-test_verify.t"
    if not recipe.is_file():
        fail(f"missing vendored recipe {recipe}")
    text = recipe.read_text(encoding="utf-8", errors="strict")

    n_ok_lines = len(re.findall(r"^ok\(", text, re.MULTILINE))
    cases = parse_verify_table(text)
    if not cases:
        fail("parsed zero upstream verify rows")
    print(f"upstream ^ok( lines: {n_ok_lines}; verify() rows parsed: {len(cases)}")

    # Every referenced material must exist in the vendored corpus; rows citing
    # only runtime-generated (setup.sh) material are excluded and recorded.
    corpus_files = sorted(p.name for p in certs_dir.iterdir() if p.is_file())
    excluded_rows: list[dict] = []
    usable_cases: list[dict] = []
    for c in cases:
        missing = [
            ref
            for ref in [c["leaf"], *c["trusted"], *c["untrusted"]]
            if ref and not ref.startswith("-")
            and not (certs_dir / f"{ref}.pem").is_file()
        ]
        if missing:
            if set(missing) <= RUNTIME_GENERATED_REFS:
                excluded_rows.append(
                    {
                        "name": c["name"],
                        "missing": missing,
                        "reason": "setup.sh-generated material absent from the tag snapshot",
                    }
                )
                continue
            fail(f"upstream row {c['name']!r} references missing {missing}")
        usable_cases.append(c)
    print(
        f"usable rows: {len(usable_cases)}; excluded runtime-material rows: "
        f"{len(excluded_rows)}"
    )
    cases = usable_cases

    # F-U: unordered pairs of distinct upstream states sharing (leaf,purpose,opts).
    groups: dict[tuple, list[dict]] = {}
    for c in cases:
        key = (c["leaf"], c["purpose"], tuple(c["opts"]))
        groups.setdefault(key, []).append(c)

    upstream_tasks: list[dict] = []
    for key in sorted(groups):
        states = groups[key]
        seen: dict[str, dict] = {}
        for c in states:
            sig = state_signature(c)
            if sig not in seen:
                seen[sig] = c
        uniq = [seen[s] for s in sorted(seen)]
        for i in range(len(uniq)):
            for j in range(i + 1, len(uniq)):
                a, b = uniq[i], uniq[j]
                upstream_tasks.append(
                    {
                        "family": FAMILY_UPSTREAM,
                        "task_id": f"FU-{len(upstream_tasks) + 1:04d}",
                        "leaf": key[0],
                        "purpose": key[1],
                        "opts": list(key[2]),
                        "state_a": {
                            "trusted": a["trusted"],
                            "untrusted": a["untrusted"],
                        },
                        "state_b": {
                            "trusted": b["trusted"],
                            "untrusted": b["untrusted"],
                        },
                        "upstream_case_a": a["name"],
                        "upstream_case_b": b["name"],
                    }
                )

    # F-P: parity partition of the vendored certificate set. CRL-only files
    # are not store certificates (the engine rejects them in -trusted/-untrusted)
    # and are excluded; any private-key bytes in the corpus are fail-closed.
    cert_pool = []
    for name in corpus_files:
        if not name.endswith(".pem"):
            continue
        blob = (certs_dir / name).read_bytes()
        if PRIVATE_KEY_MARKER in blob:
            fail(f"private-key material in vendored corpus: {name}")
        if not any(marker in blob for marker in CERT_MARKERS):
            continue
        cert_pool.append(name)
    cert_pool.sort()
    origin_a = cert_pool[0::2]
    origin_b = cert_pool[1::2]
    leaves = sorted(n[: -len(".pem")] for n in cert_pool if n.startswith("ee-"))
    if not leaves:
        fail("no ee-* leaf certificates found for parity family")
    parity_tasks: list[dict] = []
    for leaf in leaves:
        for purpose in FARITY_PURPOSES:
            parity_tasks.append(
                {
                    "family": FAMILY_PARITY,
                    "task_id": f"FP-{len(parity_tasks) + 1:04d}",
                    "leaf": leaf,
                    "purpose": purpose,
                    "opts": [],
                    "state_a": {"trusted": origin_a, "untrusted": origin_a},
                    "state_b": {"trusted": origin_b, "untrusted": origin_b},
                    "upstream_case_a": None,
                    "upstream_case_b": None,
                }
            )

    manifest = {
        "protocol": "ORION-03-Round2-TrustStoreMerge-V2",
        "frozen_attime": FROZEN_ATTIME,
        "vendored_files": len(corpus_files),
        "upstream_rows_parsed": len(cases) + len(excluded_rows),
        "upstream_rows_usable": len(cases),
        "upstream_rows_excluded_runtime_material": excluded_rows,
        "families": {
            FAMILY_UPSTREAM: {
                "tasks": len(upstream_tasks),
                "groups": len(groups),
            },
            FAMILY_PARITY: {
                "tasks": len(parity_tasks),
                "origin_a_size": len(origin_a),
                "origin_b_size": len(origin_b),
                "leaves": len(leaves),
            },
        },
        "tasks": upstream_tasks + parity_tasks,
    }
    blob = json.dumps(manifest, sort_keys=True, indent=1, ensure_ascii=False)
    (here / "TASK_MANIFEST_V2.json").write_text(blob + "\n", encoding="utf-8")
    digest = hashlib.sha256((blob + "\n").encode("utf-8")).hexdigest()
    print(f"TASK_MANIFEST_V2.json written; sha256={digest}")
    print(f"F-U tasks: {len(upstream_tasks)}; F-P tasks: {len(parity_tasks)}")
    # Also persist the parsed upstream table for the anchoring control.
    table = {
        "upstream_rows": cases,
        "excluded_rows": excluded_rows,
        "exit_checker_rows_flipped": [
            c["name"] for c in cases if c.get("exit_checker_flipped")
        ],
    }
    (here / "UPSTREAM_TABLE_V2.json").write_text(
        json.dumps(table, sort_keys=True, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"UPSTREAM_TABLE_V2.json written; rows={len(cases)}")


if __name__ == "__main__":
    main()
