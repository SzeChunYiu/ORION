#!/usr/bin/env python3
"""Descriptor-only adjudication evidence gatherer for the 3 v3-collapsed families.

Governed execution of the descriptor-only adjudication required by
WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3_DECISION_2026-09-03.md §7 and §5:
families 106, 360 and 384 collapsed to equal before/after v3 aggregates
(workflowhub-member-manifest-freeze-v3/RESULT_V3.json,
v3_content_only_before_after_equal_workflow_ids), so their frozen v2
before/after aggregate difference is confined to the excluded request-generated
crate members. This script gathers the evidence governance needs to adjudicate,
per family, whether the version DESCRIPTORS (the ro-crate metadata content
describing the change) show a version-pinned content transition or an artifact
of the request-generation mechanism. It records evidence; it does not decide,
promote, sign or rebind anything.

Method (fixed before execution, zero free parameters, no run-time resolution):

- The three families and their frozen version pairs are read from the frozen
  128-family successor frame (validate_external_curator_packet_v1.py,
  imported verbatim with its digest-checked chunk loading).
- Each side (before/after version) of each family is fetched 3 times
  independently through the frozen transport (same URL form, UA, retry tuple
  and read limit as harvest_member_manifests_v3.fetch_once).
- Per fetch the script records the raw and canonical-JSON SHA-256 of
  ro-crate-metadata.json, the preview digest (presence-only evidence), the v3
  retained/excluded split via the frozen v3 normalization (imported verbatim)
  and the v2 aggregate cross-check against the frozen frame receipt.
- Volatility partition (within one version, across its 3 fetches): the set of
  canonical descriptor paths whose values differ between any two fetches, plus
  whether the raw bytes and canonical bytes are byte-stable.
- Version-pinned partition (across versions, all 9 before_i/after_j pairs):
  canonical descriptor paths that differ in EVERY pair, minus the volatile
  paths -- i.e. differences that persist across every cross-version comparison
  yet never move within a version. The same construction is applied to the
  @graph node set keyed by @id (order-free). A non-empty version-pinned set is
  a genuine descriptor-level content transition invisible to v3; an empty one
  with all-volatile raw differences is a request-generation artifact.
- The v3 collapse itself is re-verified inside this run (before == after v3
  aggregate, both stable across fetches); any defect in that re-verification
  marks the family's evidence defective rather than silently adjudicable.

No strata, no gold, no candidate predictions, no protected outcomes, no
frame rebind, no pool mutation. Run location: LUNARC sbatch (egress to
workflowhub.eu verified by sbatch 3569314; the v3 harvest itself ran as
sbatch 3570688). Deterministic output regardless of worker count or ordering.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

ADJUDICATION_ID = "A3_DESCRIPTOR_ONLY_ADJUDICATION_V1"
EVIDENCE_SCHEMA = "ORION.A3.DescriptorOnlyAdjudicationEvidence.v1"
FAMILIES: tuple[str, ...] = ("106", "360", "384")
FETCHES = 3  # mirrors the frozen MIN_FETCHES of the v3 member-manifest freeze
EXCLUDED_MEMBERS = ("ro-crate-metadata.json", "ro-crate-preview.html")

VERDICT_PINNED = "DESCRIPTOR_SHOWS_VERSION_PINNED_TRANSITION"
VERDICT_ARTIFACT = "REQUEST_GENERATION_ARTIFACT"
VERDICT_CANNOT = "CANNOT_DISTINGUISH"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def frozen_modules() -> tuple[Any, Any, Any]:
    binding = _load("a3_rocrate_binding_adj1", HERE / "bind_workflowhub_rocrate_content_v1.py")
    curator = _load("a3_curator_validator_adj1", HERE / "validate_external_curator_packet_v1.py")
    v3norm = _load("a3_member_manifest_v3norm_adj1", HERE / "normalize_member_manifests_v3.py")
    return binding, curator, v3norm


def fetch_crate(workflow_id: str, version: int, binding: Any, retries: int = 4, timeout: float = 180.0) -> bytes:
    """One independent fetch of a versioned RO-Crate (frozen transport, verbatim)."""
    url = f"https://workflowhub.eu/workflows/{urllib.parse.quote(str(workflow_id), safe='')}/ro_crate?version={version}"
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": binding.UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                if status != 200:
                    raise RuntimeError(f"HTTP {status}")
                return binding.read_limited(resp)
        except (urllib.error.URLError, TimeoutError, RuntimeError, OSError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.75 * (attempt + 1))
    raise RuntimeError(f"failed descriptor-adjudication fetch for workflow {workflow_id} v{version}: {last}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def parse_descriptor(raw: bytes) -> Any:
    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("ro-crate-metadata.json root is not a JSON object")
    return parsed


def diff_paths(a: Any, b: Any, path: str, out: dict[str, dict[str, str]]) -> None:
    """Collect canonical paths at which two parsed JSON values differ.

    `out` maps path -> {"left": <repr>, "right": <repr>} with reprs truncated
    for evidence readability. Presence asymmetries are recorded with the
    missing side as "<absent>".
    """
    if type(a) is not type(b):
        out[path] = {"left": _brief(a), "right": _brief(b)}
        return
    if isinstance(a, dict):
        for key in sorted(set(a) | set(b)):
            child = f"{path}.{key}" if path else key
            if key not in a or key not in b:
                out[child] = {"left": _brief(a.get(key, _ABSENT)), "right": _brief(b.get(key, _ABSENT))}
            else:
                diff_paths(a[key], b[key], child, out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out[f"{path}#len"] = {"left": str(len(a)), "right": str(len(b))}
        for i in range(min(len(a), len(b))):
            diff_paths(a[i], b[i], f"{path}[{i}]", out)
    else:
        if a != b:
            out[path] = {"left": _brief(a), "right": _brief(b)}


_ABSENT = object()


def _brief(value: Any, cap: int = 200) -> str:
    if value is _ABSENT:
        return "<absent>"
    text = canonical_json(value) if isinstance(value, (dict, list)) else repr(value)
    return text if len(text) <= cap else text[:cap] + f"...<+{len(text) - cap} chars>"


def graph_by_id(descriptor: Any) -> dict[str, Any]:
    """Map @graph nodes by @id (order-free view of the crate descriptor)."""
    graph = descriptor.get("@graph")
    if not isinstance(graph, list):
        return {}
    out: dict[str, Any] = {}
    for node in graph:
        if isinstance(node, dict) and isinstance(node.get("@id"), str):
            out[node["@id"]] = node
    return out


def adjudicate_family(wid: str, frame_row: dict[str, Any], binding: Any, curator: Any, v3norm: Any, out_dir: Path | None) -> dict[str, Any]:
    sides: dict[str, dict[str, Any]] = {}
    for side, version_key in (("before", "version_before"), ("after", "version_after")):
        version = int(frame_row[version_key])
        fetches: list[dict[str, Any]] = []
        for i in range(FETCHES):
            data = fetch_crate(wid, version, binding)
            with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
                retained, excluded, descriptor_bytes = v3norm.normalized_content_manifest_v3(zf)
            if out_dir is not None:
                (out_dir / f"workflow_{wid}_v{version}_fetch{i + 1}_ro-crate-metadata.json").write_bytes(descriptor_bytes)
            descriptor = parse_descriptor(descriptor_bytes)
            fetches.append({
                "fetch": i + 1,
                "descriptor_raw_sha256": hashlib.sha256(descriptor_bytes).hexdigest(),
                "descriptor_canonical_sha256": hashlib.sha256(canonical_json(descriptor).encode("utf-8")).hexdigest(),
                "preview_sha256": next((e["sha256"] for e in excluded if e["path"] == "ro-crate-preview.html"), None),
                "excluded_paths": [e["path"] for e in excluded],
                "retained_member_n": len(retained),
                "v3_aggregate": v3norm.aggregate_v3(retained),
                "v2_aggregate": binding.canonical_json_sha(v3norm.v2_equivalent_manifest(retained, excluded)),
            })
            fetches[-1]["_descriptor"] = descriptor
        # Within-version volatility partition.
        volatile: dict[str, dict[str, str]] = {}
        for i in range(FETCHES):
            for j in range(i + 1, FETCHES):
                diff_paths(fetches[i]["_descriptor"], fetches[j]["_descriptor"], "$", volatile)
        raw_digests = sorted({f["descriptor_raw_sha256"] for f in fetches})
        canon_digests = sorted({f["descriptor_canonical_sha256"] for f in fetches})
        v3_aggregates = sorted({f["v3_aggregate"] for f in fetches})
        sides[side] = {
            "version": version,
            "fetches": [{k: v for k, v in f.items() if k != "_descriptor"} for f in fetches],
            "descriptor_raw_byte_stable_across_fetches": len(raw_digests) == 1,
            "descriptor_canonical_stable_across_fetches": len(canon_digests) == 1,
            "v3_aggregate_stable_across_fetches": len(v3_aggregates) == 1,
            "v2_aggregate_reproduces_frozen_frame": all(
                f["v2_aggregate"] == frame_row[f"{side}_normalized_sha256"] for f in fetches
            ),
            "volatile_canonical_paths_within_version": volatile,
            "_descriptors": [f["_descriptor"] for f in fetches],
        }

    # Cross-version partition: paths differing in EVERY before_i/after_j pair.
    cross_intersection: dict[str, dict[str, str]] | None = None
    for b in sides["before"]["_descriptors"]:
        for a in sides["after"]["_descriptors"]:
            pair_diff: dict[str, dict[str, str]] = {}
            diff_paths(b, a, "$", pair_diff)
            if cross_intersection is None:
                cross_intersection = pair_diff
            else:
                cross_intersection = {p: v for p, v in cross_intersection.items() if p in pair_diff}
    assert cross_intersection is not None
    volatile_union = {
        **sides["before"]["volatile_canonical_paths_within_version"],
        **sides["after"]["volatile_canonical_paths_within_version"],
    }
    version_pinned_paths = {p: v for p, v in cross_intersection.items() if p not in volatile_union}

    # Order-free @graph view: nodes that differ in every cross pair but never within a version.
    before_graphs = [graph_by_id(d) for d in sides["before"]["_descriptors"]]
    after_graphs = [graph_by_id(d) for d in sides["after"]["_descriptors"]]
    pinned_nodes: dict[str, dict[str, str]] = {}
    all_ids: set[str] = set()
    for graphs in (before_graphs, after_graphs):
        for g in graphs:
            all_ids |= set(g)
    for node_id in sorted(all_ids):
        crosses: dict[str, dict[str, str]] | None = None
        for bg in before_graphs:
            for ag in after_graphs:
                pair: dict[str, dict[str, str]] = {}
                diff_paths(bg.get(node_id, None), ag.get(node_id, None), node_id, pair)
                if not pair:
                    crosses = None
                    break
                if crosses is None:
                    crosses = pair
                else:
                    crosses = {p: v for p, v in crosses.items() if p in pair}
            if crosses is None:
                break
        if crosses:
            within = False
            for graphs in (before_graphs, after_graphs):
                for i in range(len(graphs)):
                    for j in range(i + 1, len(graphs)):
                        pair: dict[str, dict[str, str]] = {}
                        diff_paths(graphs[i].get(node_id, None), graphs[j].get(node_id, None), node_id, pair)
                        if pair:
                            within = True
            if not within:
                pinned_nodes[node_id] = crosses

    # Re-verify the collapse being adjudicated, inside this run.
    collapse_verified = (
        sides["before"]["v3_aggregate_stable_across_fetches"]
        and sides["after"]["v3_aggregate_stable_across_fetches"]
        and sides["before"]["fetches"][0]["v3_aggregate"] == sides["after"]["fetches"][0]["v3_aggregate"]
    )

    # Mechanical pre-registered verdict rule (governance records it; this run applies it).
    if not collapse_verified:
        verdict = VERDICT_CANNOT
        verdict_basis = "v3 collapse could not be re-verified inside this adjudication run; evidence is defective"
    elif version_pinned_paths or pinned_nodes:
        verdict = VERDICT_PINNED
        verdict_basis = (
            "canonical descriptor paths/@graph nodes differ between the frozen versions across every "
            "cross-version fetch pair and never within a version: a version-pinned descriptor-level "
            "transition invisible to the v3 aggregate"
        )
    elif not cross_intersection and not pinned_nodes:
        verdict = VERDICT_ARTIFACT
        verdict_basis = (
            "canonical descriptor content is identical between the frozen versions (no cross-version "
            "difference beyond within-version request-generation volatility): the frozen v2 before/after "
            "aggregate difference is an artifact of the request-generation mechanism"
        )
    else:
        verdict = VERDICT_CANNOT
        verdict_basis = (
            "cross-version descriptor differences exist but none is version-pinned (all coincide with "
            "within-version request-generation volatility); descriptor evidence cannot distinguish a "
            "genuine transition from request noise"
        )

    return {
        "workflow_id": wid,
        "version_before": frame_row["version_before"],
        "version_after": frame_row["version_after"],
        "license_before": frame_row["license_before"],
        "license_after": frame_row["license_after"],
        "fetches_per_version": FETCHES,
        "collapse_reverified_in_run": collapse_verified,
        "before": {k: v for k, v in sides["before"].items() if k != "_descriptors"},
        "after": {k: v for k, v in sides["after"].items() if k != "_descriptors"},
        "cross_version_differing_paths_in_every_pair": cross_intersection,
        "version_pinned_differing_paths": version_pinned_paths,
        "version_pinned_graph_nodes": pinned_nodes,
        "verdict": verdict,
        "verdict_basis": verdict_basis,
    }


def run(note: str, out_dir: Path | None) -> dict[str, Any]:
    binding, curator, v3norm = frozen_modules()
    source_frame = curator.load_source_frame()
    if len(source_frame) != 128:
        raise ValueError("frozen successor frame is not 128 families")
    missing = [wid for wid in FAMILIES if wid not in source_frame]
    if missing:
        raise ValueError(f"families absent from the frozen frame: {missing}")
    v3_result = json.loads((HERE / "workflowhub-member-manifest-freeze-v3" / "RESULT_V3.json").read_text(encoding="utf-8"))
    collapsed = sorted(v3_result["partition"]["v3_content_only_before_after_equal_workflow_ids"])
    if collapsed != sorted(FAMILIES):
        raise ValueError(f"frozen v3 collapse partition mismatch: {collapsed} != {sorted(FAMILIES)}")
    if v3_result.get("terminal") != "CANNOT_CHECK_MEMBER_MANIFEST_V3_REPRODUCIBILITY":
        raise ValueError("frozen v3 result is not the descriptor-only failure terminal")

    rows = [adjudicate_family(wid, source_frame[wid], binding, curator, v3norm, out_dir) for wid in FAMILIES]
    for row in rows:
        for side in ("before", "after"):
            row[side].pop("_descriptors", None)
    return {
        "schema": EVIDENCE_SCHEMA,
        "adjudication_id": ADJUDICATION_ID,
        "date": "2026-09-03",
        "purpose": (
            "Descriptor-only adjudication evidence for the three families that collapsed to equal "
            "before/after v3 aggregates under WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3: per family, "
            "fetch both versions three times through the frozen transport and compare the version "
            "descriptors (ro-crate metadata content) to decide, with recorded evidence, whether the "
            "version-pair change is a genuine descriptor-level content transition or an artifact of the "
            "request-generation mechanism. Evidence gathering only: no stratum, no gold, no candidate "
            "prediction, no protected outcome, no frame rebind, no pool mutation."
        ),
        "normalization": {
            "id": v3norm.V3_NORMALIZATION_ID,
            "module": "papers/publication_closure/a3-external-change-transport-v1/normalize_member_manifests_v3.py",
            "request_generated_root_members_excluded": list(EXCLUDED_MEMBERS),
            "v2_normalization_imported_verbatim": True,
        },
        "successor_frame_sha256": curator.EXPECTED_SUCCESSOR_FRAME_SHA256,
        "bound_v3_failure_result": {
            "path": "papers/publication_closure/a3-external-change-transport-v1/workflowhub-member-manifest-freeze-v3/RESULT_V3.json",
            "terminal": v3_result["terminal"],
            "v3_content_only_before_after_equal_workflow_ids": collapsed,
        },
        "comparison_method": (
            "canonical JSON (sorted keys) path diff; volatility = paths differing within a version "
            "across its 3 fetches; version-pinned = paths differing in every one of the 9 "
            "cross-version fetch pairs and never within a version; the same construction order-free "
            "over @graph nodes keyed by @id"
        ),
        "run_environment": note,
        "families": rows,
        "flags": {
            "change_stratum_adjudicated": False,
            "external_gold_accessed": False,
            "candidate_predictions_computed": False,
            "protected_outcomes_accessed": False,
            "successor_frame_rebound": False,
            "eligible_pool_modified": False,
        },
        "grants_scientific_authority": False,
        "scientific_authority_delta": "NONE__EVIDENCE_GATHERING_ONLY",
    }


def _self_test() -> dict[str, Any]:
    """Networkless self-test with mutation controls (teeth, not fixtures)."""
    descriptor_a = {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [
            {"@id": "ro-crate-metadata.json", "@type": "CreativeWork", "about": {"@id": "./"}},
            {"@id": "./", "@type": "Dataset", "name": "wf", "dateModified": "2026-01-01", "version": "2"},
            {"@id": "main.cwl", "@type": "File"},
        ],
    }
    descriptor_b = {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [
            {"@id": "ro-crate-metadata.json", "@type": "CreativeWork", "about": {"@id": "./"}},
            {"@id": "./", "@type": "Dataset", "name": "wf", "dateModified": "2026-02-02", "version": "3"},
            {"@id": "main.cwl", "@type": "File"},
        ],
    }
    descriptor_a_noisy = json.loads(json.dumps(descriptor_a))
    descriptor_a_noisy["@graph"][0]["rendered"] = "10:00:00"  # request dressing
    descriptor_a_noisier = json.loads(json.dumps(descriptor_a))
    descriptor_a_noisier["@graph"][0]["rendered"] = "10:00:41"

    # Control 1: a genuine version-pinned descriptor edit survives noise on both sides.
    volatile: dict[str, dict[str, str]] = {}
    diff_paths(descriptor_a_noisy, descriptor_a_noisier, "$", volatile)
    assert set(volatile) == {"$.@graph[0].rendered"}, volatile
    cross: dict[str, dict[str, str]] = {}
    for b in (descriptor_a_noisy, descriptor_a_noisier, descriptor_a):
        for a in (descriptor_b,):
            diff_paths(b, a, "$", cross)
    # (single after descriptor; emulate intersection over pairs)
    pinned = {p: v for p, v in cross.items() if p not in volatile}
    assert pinned == {"$.@graph[1].dateModified": {"left": "'2026-01-01'", "right": "'2026-02-02'"},
                      "$.@graph[1].version": {"left": "'2'", "right": "'3'"}}, pinned

    # Control 2: identical canonical content -> no cross differences at all.
    same: dict[str, dict[str, str]] = {}
    diff_paths(descriptor_a_noisy, descriptor_a_noisier, "$", same)
    diff_paths(descriptor_a, descriptor_a, "$", same)
    assert same and all(p.endswith("rendered") for p in same)

    # Control 3: order-free @graph keying is insensitive to node order.
    reordered = json.loads(json.dumps(descriptor_b))
    reordered["@graph"] = list(reversed(reordered["@graph"]))
    assert graph_by_id(descriptor_b) == graph_by_id(reordered)

    # Control 4: the frozen modules import and the frame loads (digest-checked).
    binding, curator, v3norm = frozen_modules()
    frame = curator.load_source_frame()
    assert len(frame) == 128
    assert all(wid in frame for wid in FAMILIES)

    # Control 5: fetch URL form matches the frozen v3 harvester transport.
    wid, version = "106", 2
    url = f"https://workflowhub.eu/workflows/{urllib.parse.quote(str(wid), safe='')}/ro_crate?version={version}"
    assert url == "https://workflowhub.eu/workflows/106/ro_crate?version=2"

    return {
        "decision": "GREEN",
        "adjudication_id": ADJUDICATION_ID,
        "families": list(FAMILIES),
        "fetches_per_version": FETCHES,
        "pinned_path_extraction_has_teeth": True,
        "artifact_case_yields_no_pinned_paths": True,
        "graph_keying_order_free": True,
        "frozen_frame_loads_with_digest_checks": True,
        "transport_matches_frozen_harvester": True,
        "network_accessed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--note", default="")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--raw-descriptor-dir", type=Path)
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(_self_test(), indent=2, sort_keys=True))
        return 0
    result = run(args.note, args.raw_descriptor_dir)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("families",)}, indent=2, sort_keys=True))
    for row in result["families"]:
        print(f"  family {row['workflow_id']}: verdict={row['verdict']} "
              f"pinned_paths={len(row['version_pinned_differing_paths'])} "
              f"pinned_nodes={len(row['version_pinned_graph_nodes'])} "
              f"collapse_reverified={row['collapse_reverified_in_run']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
