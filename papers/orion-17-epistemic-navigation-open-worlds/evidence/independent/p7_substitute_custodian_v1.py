#!/usr/bin/env python3
"""Custodian unit for the P7 substitute navigation campaign (V1) — COMMIT phase.

This is the independent custodian required by the substitute protocol for the
P7.OPEN_WORLD.NAVIGATION.EMPIRICAL.V1 external gate.  It shares NO code with the
frozen local lane:

  * it does not import ``papers.candidates.reproducibility_generators_v3``;
  * it does not import ``benchmark/generate_instances_v2.py`` or any module of
    this paper outside ``evidence/independent/``;
  * its parameter streams are derived from sha256 domain strings, not from the
    ``random`` module, so no interpreter-version drift can move a byte.

What it does:

  1. Generate the frozen synthetic-grounded multi-domain corpus: 6 domains x
     9 families x 8 seeds = 432 instances, each domain with its own vocabulary.
  2. Derive each instance's latent ground truth and its sealed terminal from the
     label law frozen in the protocol.
  3. Emit the PUBLIC corpus (observable evidence only — no family, no latent,
     no negative-control flag, no terminal; ids assigned through a payload-hash
     shuffle so corpus order leaks no family structure).
  4. COMMIT the labels: write a sealed manifest binding the corpus digest, the
     digest of the (canonical) revealed-label payload, the protocol digest, the
     aggregate power counts, and an Ed25519 signature under the custodian key.
     The plaintext labels are NOT written in this phase.

Run from the repository root (commit phase):

    python papers/orion-17-epistemic-navigation-open-worlds/evidence/independent/p7_substitute_custodian_v1.py

The reveal file is written by the campaign unit at adjudication time and must
hash exactly to ``labels_payload_digest`` committed here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P7_SUBSTITUTE_CAMPAIGN_PROTOCOL_V1.md"
CORPUS = HERE / "P7_SUBSTITUTE_CORPUS_V1.jsonl"
SEALED = HERE / "P7_SUBSTITUTE_SEALED_LABELS_V1.json"

CUSTODIAN_DOMAIN_KEY = "P7-SUBSTITUTE-CUSTODIAN-V1-KEY"
SEED_STEM = "P7-SUBSTITUTE-V1"

DOMAINS = {
    "retrieval": {
        "route": "query-route",
        "censor": "licensed-database",
        "unknown_denominator": "unindexed-provider",
        "obligation": "recover-target-evidence",
    },
    "graph_navigation": {
        "route": "edge-frontier",
        "censor": "unlinked-hub",
        "unknown_denominator": "unindexed-provider",
        "obligation": "revisit-frontier-with-new-information",
    },
    "diagnosis": {
        "route": "test-order",
        "censor": "lab-turnaround",
        "unknown_denominator": "unrecorded-fault-mode",
        "obligation": "discharge-unknown-denominator",
    },
    "experimental_design": {
        "route": "design-move",
        "censor": "unparameterized-coordinate",
        "unknown_denominator": "confounded-blocking-factor",
        "obligation": "revalidate-preserved-obligations",
    },
    "workflow_orchestration": {
        "route": "service-call",
        "censor": "rate-limited-provider",
        "unknown_denominator": "unadvertised-capability",
        "obligation": "close-all-open-branches",
    },
    "goal_evolution": {
        "route": "objective-axis",
        "censor": "legacy-objective",
        "unknown_denominator": "unmapped-successor-goal",
        "obligation": "transport-support-to-new-objective",
    },
}

FAMILIES = [
    "hidden_useful_branch",
    "unknown_coverage",
    "censored_route",
    "deceptive_route_diversity",
    "dead_end_revisit",
    "topology_change",
    "unnecessary_reframe",
    "support_transport",
    "harmful_breadth",
]

NEGATIVE_CONTROL_FAMILIES = {"unnecessary_reframe", "harmful_breadth"}

SEEDS_PER_CELL = 8


# ---------------------------------------------------------------------------
# This unit's own primitives (no shared helpers with the local lane).
# ---------------------------------------------------------------------------


def _h(*parts: str) -> bytes:
    return hashlib.sha256("|".join(parts).encode("utf-8")).digest()


def _coin(*parts: str) -> int:
    """Deterministic 0/1 draw from a sha256 stream (no PRNG library)."""
    return _h("coin", *parts)[0] & 1


def _span(*parts: str, lo: int, hi: int) -> int:
    """Deterministic integer in [lo, hi] inclusive from a sha256 stream."""
    raw = int.from_bytes(_h("span", *parts), "big")
    return lo + raw % (hi - lo + 1)


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(obj) -> str:
    return "sha256:" + hashlib.sha256(obj if isinstance(obj, bytes) else _canon(obj)).hexdigest()


def _signing_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(CUSTODIAN_DOMAIN_KEY.encode()).digest())


def _public_key_hex() -> str:
    return (
        _signing_key()
        .public_key()
        .public_bytes(Encoding.Raw, PublicFormat.Raw)
        .hex()
    )


# ---------------------------------------------------------------------------
# Latent ground truth and the frozen label law.
# ---------------------------------------------------------------------------


def latent_of(domain: str, family: str, k: int) -> dict:
    stem = f"{SEED_STEM}|{domain}|{family}|{k}"
    requires_topology_change = family == "topology_change"
    coverage_denominator_known = family != "unknown_coverage"
    censoring_observed = family == "censored_route"
    share_backend = family == "deceptive_route_diversity"
    support_partial = family == "support_transport"
    goal_reachable_current_chart = not requires_topology_change
    return {
        "requires_topology_change": requires_topology_change,
        "goal_reachable_current_chart": goal_reachable_current_chart,
        "coverage_denominator_known": coverage_denominator_known,
        "censoring_observed": censoring_observed,
        "open_routes_share_critical_backend": share_backend,
        "prior_support_mapping_partial": support_partial,
        "negative_control": family in NEGATIVE_CONTROL_FAMILIES,
        "frontier_seed": _span(stem, "frontier", lo=2, hi=7),
        "route_count_seed": _span(stem, "routes", lo=2, hi=5),
        "stem": stem,
    }


def label_law(latent: dict) -> str:
    """Frozen custodian label law (protocol section 3)."""
    if latent["requires_topology_change"] and not latent["goal_reachable_current_chart"]:
        return "REFRAME"
    if not latent["coverage_denominator_known"]:
        return "CANNOT_CHECK"
    if latent["censoring_observed"]:
        return "CANNOT_CHECK"
    if latent["prior_support_mapping_partial"]:
        return "CANNOT_CHECK"
    if latent["open_routes_share_critical_backend"]:
        return "ROUTE_STOP"
    return "TASK_STOP"


# ---------------------------------------------------------------------------
# Observable projection (public corpus rows).
# ---------------------------------------------------------------------------


def observable_row(domain: str, family: str, k: int, latent: dict) -> dict:
    vocab = DOMAINS[domain]
    stem = latent["stem"]
    n_routes = latent["route_count_seed"]
    if latent["open_routes_share_critical_backend"]:
        # Deceptive diversity: distinct nominal routes, one shared critical backend.
        shared = f"{vocab['route']}-backend-shared"
        backends = [shared] * n_routes
    else:
        backends = [f"{vocab['route']}-backend-{i}" for i in range(n_routes)]
    return {
        "domain": domain,
        "goal_reached": False,  # every registered row is a live decision opportunity
        "solution_probe": "UNREACHABLE" if latent["requires_topology_change"] else "REACHABLE",
        "reframe_action_available": True,
        "coverage_denominator": "KNOWN" if latent["coverage_denominator_known"] else "UNKNOWN",
        "censoring_events": 1 if latent["censoring_observed"] else 0,
        "censoring_region": vocab["censor"] if latent["censoring_observed"] else None,
        "route_backend_signatures": backends,
        "outstanding_obligations": [vocab["obligation"]] if _coin(stem, "obligation") else [],
        "unexpanded_frontier_nonempty": _coin(stem, "frontier") == 1,
        "prior_closure_support_mapping": (
            "PARTIAL" if latent["prior_support_mapping_partial"] else
            ("COMPLETE" if _coin(stem, "support") else "NONE")
        ),
        "breadth_marginal_regions_relevant": False if latent["negative_control"] else bool(_coin(stem, "breadth")),
    }


def build_corpus() -> tuple[list[dict], list[dict]]:
    """Return (public_rows, label_records) in shuffled id order."""
    private: list[tuple[str, str, int, dict, dict]] = []
    for domain in DOMAINS:
        for family in FAMILIES:
            for k in range(SEEDS_PER_CELL):
                latent = latent_of(domain, family, k)
                terminal = label_law(latent)
                row = observable_row(domain, family, k, latent)
                record = {
                    "family": family,
                    "latent": {key: latent[key] for key in (
                        "requires_topology_change",
                        "goal_reachable_current_chart",
                        "coverage_denominator_known",
                        "censoring_observed",
                        "open_routes_share_critical_backend",
                        "prior_support_mapping_partial",
                        "negative_control",
                    )},
                    "negative_control": latent["negative_control"],
                    "terminal": terminal,
                }
                private.append((domain, family, k, row, record))

    # Opaque sequential ids: order derived from a payload-hash shuffle so the
    # corpus byte stream carries no family/block structure.
    ordered = sorted(private, key=lambda t: _h("order", t[3]["domain"], json.dumps(t[3], sort_keys=True)))
    public_rows: list[dict] = []
    label_records: list[dict] = []
    for seq, (domain, family, k, row, record) in enumerate(ordered):
        case_id = f"P7-SYN-{seq:04d}"
        public_rows.append({"id": case_id, **row})
        label_records.append({"id": case_id, "domain": domain, **record})
    return public_rows, label_records


# ---------------------------------------------------------------------------
# Commit phase.
# ---------------------------------------------------------------------------


def main() -> int:
    public_rows, label_records = build_corpus()
    if len(public_rows) != 432:
        raise SystemExit(f"custodian: expected 432 instances, generated {len(public_rows)}")

    corpus_bytes = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in public_rows
    ).encode("utf-8")

    revealed_payload = {
        "schema_version": "orion.p7.substitute-labels-revealed.v1",
        "labels": label_records,
    }
    labels_payload_digest = _digest(revealed_payload)

    per_domain = {d: 0 for d in DOMAINS}
    terminal_counts: dict[str, int] = {}
    negative_controls = 0
    for record in label_records:
        per_domain[record["domain"]] += 1
        terminal_counts[record["terminal"]] = terminal_counts.get(record["terminal"], 0) + 1
        negative_controls += int(bool(record["negative_control"]))
    if sorted(terminal_counts) != ["CANNOT_CHECK", "REFRAME", "ROUTE_STOP", "TASK_STOP"]:
        raise SystemExit(f"custodian: terminal coverage incomplete: {terminal_counts}")
    if sorted(per_domain.values()) != [72] * 6:
        raise SystemExit(f"custodian: per-domain power unequal: {per_domain}")
    if negative_controls != 2 * SEEDS_PER_CELL * len(DOMAINS):
        raise SystemExit(f"custodian: negative-control count unexpected: {negative_controls}")

    # The three path strings below are SIGNED CONTENT, not references. They record
    # where these artifacts lived when the labels were sealed on 2026-08-24, before
    # any prediction existed, and the Ed25519 signature is taken over exactly these
    # bytes. Rewriting them to the current directory names -- which the R0 namespace
    # unification did in 3a1a83178 -- changes the payload without changing the
    # signature, and the seal stops verifying. `paper_id` below is left at "P7" for
    # the same reason and was correctly not rewritten.
    #
    # papers/PAPER_ALIASES.md maps paper-07-... -> orion-17-... . That registry, not
    # this file, is where the current name belongs. Nothing resolves files through
    # these strings: the custodian and the independent checker both locate artifacts
    # relative to their own directory, and compare digests, never paths.
    #
    # Do not "fix" these to the new namespace. See SEAL_INTEGRITY_NOTE_V1.md.
    facts = {
        "schema_version": "orion.p7.substitute-sealed-manifest.v1",
        "commit_date": "2026-08-24",
        "paper_id": "P7",
        "custodian_unit": "p7_substitute_custodian_v1",
        "protocol_path": "papers/paper-07-epistemic-navigation-open-worlds/evidence/independent/P7_SUBSTITUTE_CAMPAIGN_PROTOCOL_V1.md",
        "protocol_sha256": _digest(PROTOCOL.read_bytes()),
        "corpus_path": "papers/paper-07-epistemic-navigation-open-worlds/evidence/independent/P7_SUBSTITUTE_CORPUS_V1.jsonl",
        "corpus_sha256": _digest(corpus_bytes),
        "corpus_rows": len(public_rows),
        "labels_payload_digest": labels_payload_digest,
        "labels_reveal_path": "papers/paper-07-epistemic-navigation-open-worlds/evidence/independent/P7_SUBSTITUTE_LABELS_REVEALED_V1.json",
        "generator": {
            "stem": SEED_STEM,
            "determinism": "sha256 domain streams; no PRNG library; version-stable bytes",
            "domains": sorted(DOMAINS),
            "families": FAMILIES,
            "seeds_per_cell": SEEDS_PER_CELL,
            "instances": len(public_rows),
        },
        "power_counts": {
            "per_domain": per_domain,
            "terminals": terminal_counts,
            "negative_controls": negative_controls,
        },
        "label_law_frozen": (
            "REFRAME if topology change required; CANNOT_CHECK if unknown denominator, "
            "censoring observed, or partial prior-support mapping; ROUTE_STOP if open routes "
            "share a critical backend; TASK_STOP otherwise"
        ),
        "labels_written_in_commit_phase": False,
    }
    manifest = {
        "facts": facts,
        "payload_digest": _digest(facts),
        "signature_ed25519_hex": _signing_key().sign(_canon(facts)).hex(),
        "public_key_hex": _public_key_hex(),
        "key_derivation": f"sha256('{CUSTODIAN_DOMAIN_KEY}') as Ed25519 seed",
        "outcome": "P7_SUBSTITUTE_LABELS_SEALED",
    }

    CORPUS.write_bytes(corpus_bytes)
    SEALED.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "outcome": manifest["outcome"],
                "corpus_rows": len(public_rows),
                "corpus_sha256": facts["corpus_sha256"],
                "labels_payload_digest": labels_payload_digest,
                "terminals": terminal_counts,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
