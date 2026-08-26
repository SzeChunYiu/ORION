from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ROOT = ROOT / "research" / "paper-programme-v1" / "protocols"
STATS_MODULE = PROTOCOL_ROOT / "publication_stats.py"
SVG_MODULE = PROTOCOL_ROOT / "publication_svg.py"
PAPER_PROTOCOLS = {
    "P1": ROOT / "papers" / "orion-11-recursive-epistemic-reconstruction" / "protocol" / "PROTOCOL_V1.json",
    "P2": ROOT / "papers" / "orion-12-open-world-scientific-discovery" / "protocol" / "PROTOCOL_V1.json",
    "P3": ROOT / "papers" / "orion-13-global-knowledge-portrait" / "protocol" / "PROTOCOL_V1.json",
    "P4": ROOT / "papers" / "orion-14-verified-scientific-discovery" / "protocol" / "PROTOCOL_V1.json",
    "P5": ROOT / "papers" / "orion-15-self-orion" / "protocol" / "PROTOCOL_V1.json",
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register before executing. `@dataclass` resolves annotations through
    # `sys.modules[cls.__module__]`, which is absent for a spec-loaded module, so
    # the first dataclass added to any protocol module would fail here at class
    # creation with an AttributeError nowhere near its cause. Cheap insurance
    # against a confusing failure in a helper several test files share.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_common_protocol_schemas_are_json():
    for name in ("PUBLICATION_PROTOCOL_SCHEMA_V1.json", "RESULT_RECORD_SCHEMA_V1.json"):
        payload = json.loads((PROTOCOL_ROOT / name).read_text(encoding="utf-8"))
        assert payload["type"] == "object"
        assert payload["$schema"].endswith("2020-12/schema")


def test_all_five_protocols_are_outcome_blind_prospective_freezes():
    """Every paper protocol must be a valid prospective freeze at its own stage.

    This asserts the invariant rather than a snapshot of it. Pinning every paper
    to ``DESIGN_FROZEN`` would make the documented promotion in
    ``EXECUTION_FREEZE_CHECKLIST_V1.md`` step 6 unreachable: the first paper to
    legitimately bind its execution identities would fail the suite, and the
    cheapest way to make the suite pass again would be to un-freeze the paper.
    A test that punishes correct scientific progress is a test that will be
    satisfied by the wrong repair.

    What actually has to hold is stage-dependent, and is enforced here by the
    canonical validator so the rule cannot drift from the tooling:
    ``DESIGN_FROZEN`` keeps every execution identity ``UNBOUND``;
    ``EXECUTION_FROZEN`` resolves all of them against a real subject revision;
    and neither may have inspected an outcome.
    """

    manifest = _load_module("publication_manifest", PROTOCOL_ROOT / "publication_manifest.py")
    seen = set()
    for paper_id, path in PAPER_PROTOCOLS.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "orion.publication-protocol.v1"
        assert payload["paper_id"] == paper_id
        assert payload["primary_hypothesis"]["id"].startswith(f"{paper_id}.")
        assert payload["task_families"]
        assert payload["baselines"]
        assert payload["ablations"]
        assert payload["plots"]
        assert payload["tables"]

        status = payload["protocol_status"]
        assert status in {"DESIGN_FROZEN", "EXECUTION_FROZEN"}, (
            f"{paper_id} protocol must remain prospective; "
            f"an outcome-accessed or invalidated protocol needs its own record: {status}"
        )
        assert payload["outcome_accessed"] is False
        assert not manifest.validate_protocol(payload), (
            f"{paper_id} protocol fails canonical validation: "
            f"{manifest.validate_protocol(payload)}"
        )
        if status == "DESIGN_FROZEN":
            assert payload["execution_bindings"]["subject_revision"] == "UNBOUND"
        seen.add(payload["protocol_id"])
    assert len(seen) == 5


def test_execution_frozen_protocol_must_bind_every_identity():
    """The promotion path is only open to a fully bound protocol.

    Guards the loosening above: an ``EXECUTION_FROZEN`` protocol that still
    carries an ``UNBOUND`` identity, or a placeholder subject revision, must be
    rejected. Without this, relaxing the status check would let a half-frozen
    protocol pass as a prospective freeze.
    """

    manifest = _load_module("publication_manifest", PROTOCOL_ROOT / "publication_manifest.py")
    template = json.loads(PAPER_PROTOCOLS["P2"].read_text(encoding="utf-8"))

    half_frozen = json.loads(json.dumps(template))
    half_frozen["protocol_status"] = "EXECUTION_FROZEN"
    errors = manifest.validate_protocol(half_frozen)
    assert errors, "an execution freeze with UNBOUND identities must be rejected"
    assert any("UNBOUND" in item for item in errors)

    fully_frozen = json.loads(json.dumps(template))
    fully_frozen["protocol_status"] = "EXECUTION_FROZEN"
    fully_frozen["execution_bindings"] = {
        "subject_revision": "0" * 40,
        "dataset_revisions": {"offline_complete_gold": "a" * 64},
        "model_provider_revisions": "none/deterministic",
        "baseline_config_hashes": {"bm25_keyword": "b" * 64},
        "evaluator_hash": "c" * 64,
        "split_hashes": {"test": "d" * 64},
        "evaluation_epoch": "2026-08-16T00:00:00Z",
    }
    assert not manifest.validate_protocol(fully_frozen), (
        "a fully bound execution freeze must validate"
    )


def test_p3_annotation_and_p4_p5_protected_schemas_parse():
    paths = [
        ROOT / "papers" / "orion-13-global-knowledge-portrait" / "protocol" / "ANNOTATION_SCHEMA_V1.json",
        ROOT / "papers" / "orion-14-verified-scientific-discovery" / "protocol" / "ATTACK_CASE_SCHEMA_V1.json",
        ROOT / "papers" / "orion-15-self-orion" / "protocol" / "HIDDEN_CAUSE_CASE_SCHEMA_V1.json",
    ]
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["type"] == "object"
        assert payload["required"]


def test_publication_stats_wilson_and_precision():
    module = _load_module("publication_stats", STATS_MODULE)
    lo, hi = module.wilson_interval(50, 100)
    assert lo < 0.5 < hi

    # Assert the defining property, not a hand-typed constant. The previous
    # assertion was `>= 384`, which is both wrong (the answer is 385) and
    # unfalsifiable in the direction that matters: it would have passed for 384,
    # an off-by-one on a sample size the papers commit to, and equally for
    # 1,000,000. The property is that the returned N is the *smallest* integer
    # whose half-width meets the target, which cannot rot as the library changes.
    z = 1.959963984540054
    for half_width in (0.03, 0.05, 0.075, 0.10):
        n = module.required_n_for_proportion_half_width(half_width, 0.5)
        achieved = z * 0.5 / (n ** 0.5)
        one_fewer = z * 0.5 / ((n - 1) ** 0.5)
        assert achieved <= half_width, f"N={n} does not reach half-width {half_width}"
        assert one_fewer > half_width, f"N={n} is not minimal for half-width {half_width}"

    # A tighter target must never ask for fewer observations.
    tighter = module.required_n_for_proportion_half_width(0.03, 0.5)
    looser = module.required_n_for_proportion_half_width(0.05, 0.5)
    assert tighter > looser


def test_publication_stats_paired_bootstrap_is_deterministic():
    module = _load_module("publication_stats", STATS_MODULE)
    candidate = [1, 1, 0, 1, 1, 0]
    baseline = [0, 1, 0, 0, 1, 0]
    first = module.paired_bootstrap_difference_ci(candidate, baseline, resamples=1000, seed=7)
    second = module.paired_bootstrap_difference_ci(candidate, baseline, resamples=1000, seed=7)
    assert first == second
    assert first[0] > 0


def test_dependency_free_svg_builders_emit_real_svg():
    module = _load_module("publication_svg", SVG_MODULE)
    bars = module.bar_chart(
        [{"system": "baseline", "value": 0.4}, {"system": "orion", "value": 0.6}],
        label_key="system",
        value_key="value",
        title="Smoke",
        y_label="score",
    )
    assert bars.startswith("<svg")
    assert "baseline" in bars and "orion" in bars
    heatmap = module.heatmap(
        [
            {"truth": "A", "pred": "A", "value": 3},
            {"truth": "A", "pred": "B", "value": 1},
            {"truth": "B", "pred": "A", "value": 0},
            {"truth": "B", "pred": "B", "value": 4},
        ],
        row_key="truth",
        col_key="pred",
        value_key="value",
        title="Matrix",
    )
    assert heatmap.startswith("<svg")
    assert "Matrix" in heatmap
