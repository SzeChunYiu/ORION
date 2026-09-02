#!/usr/bin/env python3
"""O01-P0-SRCRES-V1: Phase-0 source resolution of the frozen ORION-01 successor protocol.

Protocol: development/orion-01-phase0-source-resolution-v1-2026-09-03/O01_SRCRES_PROTOCOL_V1.md
(registered before this outcome run). Executes ONLY Phase 0 (resolve_source) of the frozen
successor protocol `orion-01-production-completeness-v1-2026-08-29`: every scientific
constant (prefix, remote, match count, terminal names, receipt/manifest/environment field
sets) is read at runtime from the frozen files; nothing is copied. The canonical versioned
checker is imported and executed as gate G0.

No semantic testing: the pinned source is never checked out, imported, or scanned; blob
bytes are read for hashing only. Exit 0 = a registered terminal (incl. adverse/cannot);
exit 3 = study-level consistency failure (no protocol terminal claimed).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import locale
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GIT = "/usr/bin/git"
REPO_ROOT = Path(__file__).resolve().parents[3]
FROZEN_DIR = REPO_ROOT / "development" / "orion-01-production-completeness-v1-2026-08-29"
LANE_DIR = REPO_ROOT / "development" / "orion-01-phase0-source-resolution-v1-2026-09-03"
PROTOCOL_FILE = LANE_DIR / "O01_SRCRES_PROTOCOL_V1.md"
DEFAULT_OUTPUT = REPO_ROOT / "research" / "extensions" / "orion01" / "O01_SRCRES_PHASE0_RESULTS.json"

# Registration pins: sha256 of the frozen predecessor artifacts at registration time.
# Gate G0 recomputes these and fails closed on drift (the frozen dir must stay pristine).
REGISTRATION_PINS = {
    "PROTOCOL.json": "116fefe48e470eea4cefb877c4ecf9ccf12e8e009573a162b2cf578bef9eabe4",
    "CORPUS_MANIFEST.json": "0fe44821212a30364608e56ca47ad0b675f5c33d018a213e2156eb9ac159ea12",
    "EXPECTED_TERMINALS.json": "a65148dcf4ab248c4c4bb0d075549926cd83d6825c83a45649765dd64343a60e",
    "registry_protocol_checker_v1.py": "3e34d0c2473fa8b0dd3817b7f46d83ec26553f2892e0483b0bd80a46329517ac",
}

STDLIB_WHITELIST = {
    "__future__", "argparse", "ast", "hashlib", "importlib", "json", "locale",
    "os", "platform", "shutil", "subprocess", "sys", "time", "datetime", "pathlib",
    "typing",
}

PACKAGING_NAMES = {"setup.py", "setup.cfg", "pyproject.toml", "MANIFEST.in", ".gitmodules"}
EXCLUDED_PREFIXES = (
    "tests/", "test/", "doc/", "docs/", "examples/", "benchmarks/", ".github/",
)


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_env() -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
    })
    env.pop("GIT_ALTERNATE_OBJECT_DIRECTORIES", None)
    env.pop("GIT_OBJECT_DIRECTORY", None)
    env.pop("GIT_GRAFTS", None)
    return env


def git_text(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run([GIT] + args, cwd=str(cwd) if cwd else None,
                          capture_output=True, env=git_env(), check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.decode('utf-8', 'replace')[:400]}")
    return proc.stdout.decode("utf-8", "surrogateescape")


# ---- G8: anti-instrument import gate -----------------------------------------

def anti_instrument_import_gate() -> dict[str, Any]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    roots = sorted({name.split(".")[0] for name in imported})
    forbidden = [r for r in roots if r not in STDLIB_WHITELIST]
    return {"import_roots": roots, "forbidden_imports": forbidden, "pass": not forbidden}


# ---- frozen machinery loading -------------------------------------------------

def load_frozen() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    pins_ok = {}
    for name, pinned in REGISTRATION_PINS.items():
        actual = sha256_file(FROZEN_DIR / name)
        pins_ok[name] = {"pinned": pinned, "actual": actual, "match": actual == pinned}
    protocol = json.loads((FROZEN_DIR / "PROTOCOL.json").read_text(encoding="utf-8"))
    corpus = json.loads((FROZEN_DIR / "CORPUS_MANIFEST.json").read_text(encoding="utf-8"))
    expected = json.loads((FROZEN_DIR / "EXPECTED_TERMINALS.json").read_text(encoding="utf-8"))
    return protocol, corpus, expected, pins_ok


def run_canonical_checker() -> dict[str, Any]:
    """Import the versioned checker from the frozen dir and execute it (never copy)."""
    checker_path = FROZEN_DIR / "registry_protocol_checker_v1.py"
    spec = importlib.util.spec_from_file_location("registry_protocol_checker_v1", checker_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_checks()


# ---- classification ------------------------------------------------------------

def classify(path: str, mode: str) -> str:
    if mode == "160000":
        return "GITLINK"
    if mode == "120000":
        return "SYMLINK"
    if path in PACKAGING_NAMES:
        return "PACKAGING"
    if path.startswith("pyzx/"):
        return "PYZX_PACKAGE_PYTHON" if path.endswith(".py") else "PYZX_PACKAGE_RESOURCE"
    if path.startswith(EXCLUDED_PREFIXES) or path.endswith((".md", ".rst")):
        return "EXCLUDED_TEST_DOCUMENTATION_EXAMPLE"
    return "OTHER_TRACKED_EXCLUDED"


# ---- receipt / manifest / environment ------------------------------------------

def build_environment_receipt(corpus: dict[str, Any]) -> dict[str, Any]:
    os_facts: dict[str, Any] = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "platform": platform.platform(),
    }
    if platform.system() == "Darwin":
        try:
            sw = subprocess.run(["sw_vers"], capture_output=True, check=True).stdout.decode()
            os_facts["sw_vers"] = dict(
                line.split(":", 1) for line in sw.strip().splitlines() if ":" in line
            )
        except Exception as exc:  # noqa: BLE001 - recorded, fail-open on optional fact source
            os_facts["sw_vers_error"] = repr(exc)
    git_version = git_text(["--version"]).strip()
    gh_path = shutil.which("gh")
    gh_version = None
    if gh_path:
        proc = subprocess.run([gh_path, "--version"], capture_output=True, check=False)
        gh_version = proc.stdout.decode("utf-8", "replace").strip().splitlines()[0] if proc.returncode == 0 else None
    receipt = {
        "schema": "ORION.ORION01.EnvironmentReceipt.v1",
        "protocol_identity": corpus["protocol_identity"],
        "phase": 0,
        "utc_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "operating_system_image_digest": sha256_bytes(canonical(os_facts).encode()),
        "operating_system_facts": os_facts,
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "dependency_lock_hash": sha256_file(LANE_DIR / "requirements-lock.txt"),
        "locale": {"getdefaultlocale": list(locale.getdefaultlocale()),
                   "LC_ALL": os.environ.get("LC_ALL"), "LANG": os.environ.get("LANG")},
        "timezone": {"tzname": list(time.tzname), "TZ": os.environ.get("TZ")},
        "hash_seed": os.environ.get("PYTHONHASHSEED", "unset"),
        "random_seed_policy": "no PRNG in phase 0: driver imports no random/numpy; all ordering is byte-deterministic",
        "optional_accelerators_disabled_or_pinned":
            "not_applicable_no_accelerators_git_and_gh_subprocess_only",
        "installation_source":
            "the uniquely resolved commit object only: no checkout, no install, no import in phase 0",
        "toolchain": {"git": git_version, "gh": gh_version},
        "required_fields_covered": corpus["environment_freeze"]["required_fields"],
    }
    return receipt


def build_manifest(clone: Path, full_commit: str) -> tuple[Path, dict[str, Any]]:
    # classic NUL-separated ls-tree record: "<mode> SP <type> SP <object> TAB <path>"
    # (-z disables path quoting; the object/path separator is a literal TAB).
    raw = subprocess.run([GIT, "ls-tree", "-r", "-z", full_commit],
                         cwd=str(clone), capture_output=True, env=git_env(), check=True).stdout
    entries = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        meta, _, path_b = record.partition(b"\t")
        mode, otype, oid = meta.decode("ascii").split(" ")
        path = path_b.decode("utf-8", "surrogateescape")
        entries.append((path, mode, otype, oid))
    entries.sort(key=lambda row: row[0].encode("utf-8", "surrogateescape"))  # frozen path_order

    rows: list[dict[str, Any]] = []
    for path, mode, otype, oid in entries:
        assert otype in ("blob", "commit"), f"unexpected ls-tree object type {otype} at {path}"
        if otype == "commit":  # gitlink: fail-closed handled by G7; row records the pin gap
            rows.append({"path": path, "git_mode": mode, "git_blob_object": oid,
                         "byte_length": None, "sha256": None, "classification": classify(path, mode)})
            continue
        blob = subprocess.run([GIT, "cat-file", "blob", oid], cwd=str(clone),
                              capture_output=True, env=git_env(), check=True).stdout
        cls = classify(path, mode)
        rows.append({"path": path, "git_mode": mode, "git_blob_object": oid,
                     "byte_length": len(blob), "sha256": sha256_bytes(blob),
                     "classification": cls})

    manifest_path = LANE_DIR / "SOURCE_FILE_MANIFEST.jsonl"
    with manifest_path.open("wb") as handle:
        for row in rows:
            handle.write(canonical(row).encode("utf-8", "surrogateescape") + b"\n")
    included = [row["path"] for row in rows
                if row["classification"].startswith(("PYZX_PACKAGE", "PACKAGING", "SYMLINK"))]
    stats = {"rows": len(rows),
             "included_in_byte_corpus": len(included),
             "by_classification": {c: sum(1 for r in rows if r["classification"] == c)
                                   for c in sorted({r["classification"] for r in rows})}}
    return manifest_path, {"stats": stats, "required_fields": [
        "path", "git_mode", "git_blob_object", "byte_length", "sha256", "classification"]}


# ---- main registered run --------------------------------------------------------

def emit_adverse_receipt(terminal: str, protocol: dict[str, Any], corpus: dict[str, Any],
                         evidence: dict[str, Any], stage: dict[str, Any]) -> None:
    """Adverse/cannot terminals also require SOURCE_RESOLUTION_RECEIPT.json (frozen rule)."""
    adv = evidence.get("ref_advertisement", {})
    res = evidence.get("resolution", {})
    obj = evidence.get("object", {})
    receipt = {
        "schema": "ORION.ORION01.SourceResolutionReceipt.v1",
        "protocol_identity": protocol["protocol_identity"],
        "remote": corpus["upstream"]["remote"],
        "ref_advertisement_sha256": adv.get("sha256"),
        "commit_prefix": protocol["source_resolution"]["commit_prefix"],
        "matching_commit_count": res.get("matching_commit_count", 0),
        "full_commit": obj.get("full_commit"),
        "commit_tree": None,
        "commit_parents": None,
        "commit_object_sha256": None,
        "source_file_manifest_sha256": None,
        "resolved_before_semantic_testing": True,
        "terminal": terminal,
        "utc_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "failure_stage": stage,
        "matching_commits": res.get("matching_commits", []),
        "matched_object_type": obj.get("type"),
        "semantic_testing_performed": False,
        "uniqueness_scope": res.get("uniqueness_scope"),
    }
    for field in corpus["source_resolution_receipt_required_fields"]:
        assert field in receipt, f"receipt missing required field {field}"
    write_json(LANE_DIR / "SOURCE_RESOLUTION_RECEIPT.json", receipt)


def run(workdir: Path) -> dict[str, Any]:
    t0 = time.time()
    gates: dict[str, Any] = {}

    import_gate = anti_instrument_import_gate()
    gates["g8_no_instrument_import"] = import_gate["pass"]
    if not import_gate["pass"]:
        return _finish("SOURCE_RESOLUTION_MACHINERY_INVALID", gates, {}, t0,
                       {"forbidden_imports": import_gate["forbidden_imports"]})

    protocol, corpus, expected, pins_ok = load_frozen()
    gates["g0_frozen_dir_pristine"] = all(v["match"] for v in pins_ok.values())
    checker_receipt = None
    if gates["g0_frozen_dir_pristine"]:
        checker_receipt = run_canonical_checker()
        gates["g0_canonical_checker"] = (
            checker_receipt.get("all_passed") is True
            and checker_receipt.get("terminal") == "PROTOCOL_FREEZE_VALIDATED__NO_SOURCE_OUTCOME"
        )
    if not all(v for k, v in gates.items() if k.startswith("g0")):
        return _finish("SOURCE_RESOLUTION_MACHINERY_INVALID", gates,
                       {"pins": pins_ok, "checker": checker_receipt}, t0, {})

    src = protocol["source_resolution"]
    prefix = src["commit_prefix"]
    remote = corpus["upstream"]["remote"]
    failure_map = corpus["resolution_failure_terminals"]
    evidence: dict[str, Any] = {"prefix": prefix, "remote": remote, "pins": pins_ok}

    def adverse(terminal: str, stage: dict[str, Any]) -> dict[str, Any]:
        emit_adverse_receipt(terminal, protocol, corpus, evidence, stage)
        return _finish(terminal, gates, evidence, t0, stage)

    # ---- G1: ref advertisement ----
    adv = subprocess.run([GIT, "ls-remote", remote], capture_output=True, env=git_env(), check=False)
    adv_refs = {}
    for line in adv.stdout.decode("utf-8", "surrogateescape").splitlines():
        if not line.strip():
            continue
        oid, _, name = line.partition("\t")
        adv_refs[name] = oid
    adv_heads = {k: v for k, v in adv_refs.items() if k.startswith("refs/heads/")}
    adv_tags = {k: v for k, v in adv_refs.items() if k.startswith("refs/tags/")}
    evidence["ref_advertisement"] = {
        "exit_code": adv.returncode,
        "sha256": sha256_bytes(adv.stdout),
        "refs_total": len(adv_refs),
        "refs_heads": len(adv_heads),
        "refs_tags_unpeeled": sum(1 for k in adv_tags if not k.endswith("^{}")),
        "refs_tags_peeled": sum(1 for k in adv_tags if k.endswith("^{}")),
    }
    gates["g1_advertisement_acquired"] = adv.returncode == 0 and (adv_heads or adv_tags)
    if not gates["g1_advertisement_acquired"]:
        return adverse(failure_map["network_or_ref_advertisement_unavailable"],
                       {"stage": "ls-remote", "stderr_head": adv.stderr.decode('utf-8', 'replace')[:400]})

    # ---- G2: fresh full bare clone ----
    # v1.1 correction: ls-remote advertises peeled pseudo-refs `refs/tags/X^{}`
    # (annotated-tag target commits). A bare clone never stores them as refs, so
    # they are excluded from the ref-name comparison; instead their target
    # objects must exist in the clone object database (cat-file -e).
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    clone = workdir / f"pyzx-bare-{stamp}"
    clone.parent.mkdir(parents=True, exist_ok=True)
    clone_proc = subprocess.run([GIT, "clone", "--bare", "--no-local", remote, str(clone)],
                                capture_output=True, env=git_env(), check=False)
    shallow = None
    clone_refs = {}
    if clone_proc.returncode == 0:
        shallow = git_text(["rev-parse", "--is-shallow-repository"], cwd=clone).strip()
        for line in git_text(["for-each-ref", "--format=%(refname) %(objectname)",
                              "refs/heads", "refs/tags"], cwd=clone).splitlines():
            name, _, oid = line.partition(" ")
            clone_refs[name] = oid
    adv_ht = {name: oid for name, oid in {**adv_heads, **adv_tags}.items()
              if not name.endswith("^{}")}          # real refs only
    peeled_targets = sorted({oid for name, oid in {**adv_heads, **adv_tags}.items()
                             if name.endswith("^{}")})
    missing_refs = sorted(name for name, oid in adv_ht.items() if clone_refs.get(name) != oid)
    missing_peeled_objects = sorted(
        oid for oid in peeled_targets
        if subprocess.run([GIT, "cat-file", "-e", oid + "^{commit}"], cwd=str(clone),
                          capture_output=True, env=git_env(), check=False).returncode != 0)
    gates["g2_fresh_full_bare_clone"] = (
        clone_proc.returncode == 0 and shallow == "false"
        and not missing_refs and not missing_peeled_objects
    )
    evidence["clone"] = {
        "path": str(clone), "exit_code": clone_proc.returncode,
        "shallow": shallow, "refs_heads_tags_in_clone": len(clone_refs),
        "advertised_refs_missing_in_clone": missing_refs,
        "advertised_peeled_targets_missing_in_object_db": missing_peeled_objects,
        "fetch_stderr_sha256": sha256_bytes(clone_proc.stderr),
    }
    if not gates["g2_fresh_full_bare_clone"]:
        return adverse(failure_map["network_or_ref_advertisement_unavailable"],
                       {"stage": "clone", "missing_refs": missing_refs,
                        "missing_peeled_objects": missing_peeled_objects,
                        "shallow": shallow})

    # ---- G3: prefix matches over commits reachable from all refs ----
    rev_list = [line for line in git_text(["rev-list", "--all"], cwd=clone).splitlines() if line]
    matches = sorted(oid for oid in rev_list if oid.startswith(prefix))
    disambig = [line for line in git_text(["rev-parse", "--disambiguate=" + prefix],
                                          cwd=clone).splitlines() if line.strip()]
    evidence["resolution"] = {
        "rev_list_total_commits": len(rev_list),
        "matching_commit_count": len(matches),
        "matching_commits": matches[:20],
        "disambiguate_all_object_types": disambig,
        "uniqueness_scope": "object database reachable from advertised refs/heads/* and refs/tags/* at the recorded advertisement",
    }
    required_count = src["required_match_count"]
    gates["g3_unique_prefix_match"] = len(matches) == required_count
    if len(matches) < required_count:
        return adverse(failure_map["zero_matches"], {"stage": "prefix_match"})
    if len(matches) > required_count:
        return adverse(failure_map["more_than_one_match"], {"stage": "prefix_match"})

    # ---- G4: object type commit, 40 lowercase hex ----
    full_commit = matches[0]
    is_hex40 = len(full_commit) == 40 and all(c in "0123456789abcdef" for c in full_commit)
    obj_type = git_text(["cat-file", "-t", full_commit], cwd=clone).strip()
    gates["g4_object_is_commit"] = is_hex40 and obj_type == src["required_object_type"]
    evidence["object"] = {"full_commit": full_commit, "type": obj_type, "hex40_lowercase": is_hex40}
    if not gates["g4_object_is_commit"]:
        return adverse(failure_map["unique_noncommit_object"], {"stage": "object_type"})

    commit_bytes = subprocess.run([GIT, "cat-file", "commit", full_commit], cwd=str(clone),
                                  capture_output=True, env=git_env(), check=True).stdout
    header, _, _ = commit_bytes.partition(b"\n\n")
    tree = parents = None
    for line in header.decode().splitlines():
        if line.startswith("tree "):
            tree = line.split()[1]
        elif line.startswith("parent "):
            parents = (parents or []) + [line.split()[1]]
    tag_refs = []
    for line in git_text(["for-each-ref", "--format=%(refname)%09%(objecttype)%09%(objectname)%09%(*objectname)",
                          "refs/tags"], cwd=clone).splitlines():
        parts = line.split("\t")
        refname, ref_type, oid, peeled = parts[0], parts[1], parts[2], parts[3] if len(parts) > 3 else ""
        if oid == full_commit or peeled == full_commit:
            tag_refs.append({"ref": refname, "object_type": ref_type, "peeled_to_commit": bool(peeled)})
    evidence["commit"] = {
        "commit_tree": tree, "commit_parents": parents or [],
        "commit_object_sha256": sha256_bytes(commit_bytes),
        "tags_pointing_at_commit": tag_refs,
    }

    # ---- G7: submodule fail-closed policy ----
    gitmodules = subprocess.run([GIT, "show", f"{full_commit}:.gitmodules"], cwd=str(clone),
                                capture_output=True, env=git_env(), check=False)
    submodule_entries: list[str] = []
    if gitmodules.returncode == 0:
        for line in gitmodules.stdout.decode("utf-8", "replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("[submodule "):
                submodule_entries.append(stripped[len("[submodule "):-1].strip('"'))
    gates["g7_no_unpinned_submodule"] = not submodule_entries
    evidence["submodule_check"] = {
        "gitmodules_present": gitmodules.returncode == 0,
        "declared_submodules": submodule_entries,
        "policy": corpus["byte_corpus"]["submodule_policy"],
    }
    if submodule_entries:
        return adverse(failure_map["network_or_ref_advertisement_unavailable"],
                       {"stage": "submodule_policy", "reason": "submodule_pinning_required",
                        "declared_submodules": submodule_entries})

    # ---- G5: independent channel agreement ----
    gh_path = shutil.which("gh")
    channel2 = {"tool": gh_path, "endpoint": f"repos/{src['repository']}/commits/{full_commit}"}
    if gh_path is None:
        gates["g5_channel2_agreement"] = False
        evidence["channel2"] = {**channel2, "available": False}
        return adverse(failure_map["network_or_ref_advertisement_unavailable"],
                       {"stage": "channel2", "reason": "channel2_unavailable_gh_not_found"})
    api = subprocess.run([gh_path, "api", channel2["endpoint"]], capture_output=True, check=False)
    api_sha = None
    if api.returncode == 0:
        try:
            api_sha = json.loads(api.stdout).get("sha")
        except json.JSONDecodeError:
            api_sha = None
    channel2.update({"available": api.returncode == 0, "returned_sha": api_sha,
                     "agreement": api_sha == full_commit})
    evidence["channel2"] = channel2
    if api.returncode != 0 or api_sha is None:
        gates["g5_channel2_agreement"] = False
        return adverse(failure_map["network_or_ref_advertisement_unavailable"],
                       {"stage": "channel2", "reason": "channel2_unavailable",
                        "stderr_head": api.stderr.decode("utf-8", "replace")[:300]})
    if api_sha != full_commit:
        gates["g5_channel2_agreement"] = False
        return _finish("SOURCE_RESOLUTION_CHANNEL_DISAGREEMENT", gates, evidence, t0,
                       {"git_channel": full_commit, "rest_channel": api_sha})
    gates["g5_channel2_agreement"] = True

    # ---- G6 + G9: environment receipt, manifest, receipt (no semantic testing) ----
    env_receipt = build_environment_receipt(corpus)
    write_json(LANE_DIR / "ENVIRONMENT_RECEIPT.json", env_receipt)
    manifest_path, manifest_report = build_manifest(clone, full_commit)
    tree_entries = len([r for r in subprocess.run(
        [GIT, "ls-tree", "-r", "-z", full_commit], cwd=str(clone),
        capture_output=True, env=git_env(), check=True).stdout.split(b"\0") if r])
    gates["g9_manifest_complete"] = manifest_report["stats"]["rows"] == tree_entries
    manifest_report["tree_entry_count"] = tree_entries
    evidence["manifest"] = manifest_report
    if not gates["g9_manifest_complete"]:
        return _finish("SOURCE_RESOLUTION_MACHINERY_INVALID", gates, evidence, t0,
                       {"stage": "manifest", "rows": manifest_report["stats"]["rows"],
                        "tree_entries": tree_entries})

    receipt = {
        "schema": "ORION.ORION01.SourceResolutionReceipt.v1",
        "protocol_identity": protocol["protocol_identity"],
        "remote": remote,
        "ref_advertisement_sha256": evidence["ref_advertisement"]["sha256"],
        "commit_prefix": prefix,
        "matching_commit_count": len(matches),
        "full_commit": full_commit,
        "commit_tree": tree,
        "commit_parents": parents or [],
        "commit_object_sha256": sha256_bytes(commit_bytes),
        "source_file_manifest_sha256": sha256_file(manifest_path),
        "resolved_before_semantic_testing": True,
        "terminal": "SOURCE_RESOLVED",
        "utc_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "resolution_channel1": "git ls-remote advertisement + fresh full bare clone + rev-list --all",
        "resolution_channel2": channel2,
        "git_version": git_text(["--version"]).strip(),
        "old_execution_commit": protocol["old_execution"]["source_commit"],
        "old_execution_commit_matches_resolved": (
            protocol["old_execution"]["source_commit"] == full_commit),
        "semantic_testing_performed": False,
        "blob_reads_for_hashing_only": True,
        "scratch_clone_path": str(clone),
        "environment_receipt_sha256": sha256_file(LANE_DIR / "ENVIRONMENT_RECEIPT.json"),
        "manifest_row_count": manifest_report["stats"]["rows"],
        "uniqueness_scope": evidence["resolution"]["uniqueness_scope"],
        "run_utc_timestamp": stamp,
    }
    for field in corpus["source_resolution_receipt_required_fields"]:
        assert field in receipt, f"receipt missing required field {field}"
    write_json(LANE_DIR / "SOURCE_RESOLUTION_RECEIPT.json", receipt)
    gates["g6_no_semantic_testing"] = True

    return _finish("SOURCE_RESOLVED", gates, evidence, t0, {})


def _finish(terminal: str, gates: dict[str, Any], evidence: dict[str, Any],
            t0: float, extra: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "ORION.ORION01.SrcResPhase0.v1",
        "study_id": "O01-P0-SRCRES-V1",
        "base_revision": git_text(["rev-parse", "HEAD"], cwd=REPO_ROOT).strip(),
        "protocol_sha256": sha256_file(PROTOCOL_FILE),
        "registration_pins": {k: v for k, v in (evidence.get("pins") or {}).items()},
        "gates": gates,
        "evidence": evidence,
        "extra": extra,
        "terminal": terminal,
        "authority": ("PHASE0_SOURCE_RESOLUTION_ONLY__NO_REGISTRY_AUTHORITY__"
                      "NO_MOVE_COMPLETENESS_UPGRADE__NO_SEMANTIC_TESTING__NO_PAPER_CLAIM"),
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "paper_authority_delta": "NONE",
        "wall_clock_seconds": round(time.time() - t0, 1),
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workdir", type=Path,
                        default=Path("/tmp/o01-srcres-scratch"))
    args = parser.parse_args()
    result = run(args.workdir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical({"terminal": result["terminal"], "digest": result["result_digest"],
                     "gates": result["gates"]}), flush=True)
    consistency = {"SOURCE_RESOLUTION_MACHINERY_INVALID", "SOURCE_RESOLUTION_CHANNEL_DISAGREEMENT"}
    return 0 if result["terminal"] not in consistency else 3


if __name__ == "__main__":
    raise SystemExit(main())
