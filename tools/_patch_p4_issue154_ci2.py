from pathlib import Path


def rep(path: str, old: str, new: str, count: int = 1) -> None:
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    found = s.count(old)
    if found != count:
        raise SystemExit(f"{path}: expected {count} sites, found {found}")
    p.write_text(s.replace(old, new, count), encoding="utf-8")

# Aggregate missing host telemetry with other missing prerequisites rather than
# returning early, so CANNOT_CHECK explains the whole missing evidence surface.
rep(
    "src/orion/benchmarks/verified_discovery.py",
    '''    if require_observed_activity and observed_activity is None:\n        return BenchmarkReport(\n            paper_id="P4",\n            case_id="external-authority-gate",\n            status=BenchmarkStatus.CANNOT_CHECK,\n            metrics=(),\n            blockers=(\n                "observed activity was required and none was supplied; the "\n                "attestations alone cannot establish evaluator integrity",\n            ),\n            observations=(\n                "CANNOT_CHECK rather than FAIL: nothing here says the candidate "\n                "misbehaved, only that nothing observed whether it did.",\n            ),\n        )\n''',
    '''    if require_observed_activity and observed_activity is None:\n        missing.append(\n            "observed activity was required and none was supplied; the "\n            "attestations alone cannot establish evaluator integrity"\n        )\n''',
)

# If the repaired promotion path blocks an attack, the layer label must credit
# the kernel rather than the benchmark detector that also observes the case.
rep(
    "src/orion/benchmarks/authority_attacks.py",
    '''        detected_by=(\n            DefenceLayer.BENCHMARK_DETECTOR if detector_flags else DefenceLayer.NEITHER\n        ),\n''',
    '''        detected_by=(\n            DefenceLayer.KERNEL_PROMOTION_PATH\n            if not promoted\n            else DefenceLayer.BENCHMARK_DETECTOR\n            if detector_flags\n            else DefenceLayer.NEITHER\n        ),\n''',
)
rep(
    "src/orion/benchmarks/authority_attacks.py",
    '''        detected_by=(\n            DefenceLayer.BENCHMARK_DETECTOR if hostile_flag else DefenceLayer.NEITHER\n        ),\n''',
    '''        detected_by=(\n            DefenceLayer.KERNEL_PROMOTION_PATH\n            if not promoted\n            else DefenceLayer.BENCHMARK_DETECTOR\n            if hostile_flag\n            else DefenceLayer.NEITHER\n        ),\n''',
)
rep(
    "src/orion/benchmarks/authority_attacks.py",
    '''        detected_by=(\n            DefenceLayer.BENCHMARK_DETECTOR\n            if outcome is AttackOutcome.DETECTED\n            else DefenceLayer.NEITHER\n        ),\n''',
    '''        detected_by=(\n            DefenceLayer.KERNEL_PROMOTION_PATH\n            if gate_status is not BenchmarkStatus.PASS\n            else DefenceLayer.BENCHMARK_DETECTOR\n            if outcome is AttackOutcome.DETECTED\n            else DefenceLayer.NEITHER\n        ),\n''',
    2,
)

# Tests now encode the stricter default: attestations alone cannot PASS.
p = Path("tests/unit/benchmarks/test_authority_attacks.py")
s = p.read_text(encoding="utf-8")
old = '''    attested = {\n        "source_attribution_benchmark_run": True,\n        "search_time_contamination_audited": True,\n        "evaluator_locked": True,\n        "heldout_access_logged": True,\n        "matched_nearest_work_baseline_run": True,\n        "false_promotion_better_than_baseline": True,\n    }\n'''
new = '''    attested = {\n        "source_attribution_benchmark_run": True,\n        "search_time_contamination_audited": True,\n        "evaluator_locked": True,\n        "heldout_access_logged": True,\n        "matched_nearest_work_baseline_run": True,\n        "false_promotion_better_than_baseline": True,\n        "claim_evidence_support_established": True,\n        "behavioral_influence_established": True,\n    }\n'''
if s.count(old) != 2:
    raise SystemExit(f"attested blocks: {s.count(old)}")
s = s.replace(old, new, 2)
s = s.replace(
    '    assert external_authority_gate(**attested).status is BenchmarkStatus.PASS\n\n    caught = external_authority_gate(',
    '    assert external_authority_gate(**attested).status is BenchmarkStatus.CANNOT_CHECK\n\n    caught = external_authority_gate(',
    1,
)
s = s.replace(
    '''    assert external_authority_gate(**attested).status is BenchmarkStatus.PASS\n    required = external_authority_gate(**attested, require_observed_activity=True)\n    assert required.status is BenchmarkStatus.CANNOT_CHECK\n    clean = external_authority_gate(\n        **attested,\n        require_observed_activity=True,\n        observed_activity=CandidateActivity("c"),\n    )\n''',
    '''    assert external_authority_gate(**attested).status is BenchmarkStatus.CANNOT_CHECK\n    clean = external_authority_gate(\n        **attested,\n        observed_activity=CandidateActivity("c"),\n    )\n''',
    1,
)
p.write_text(s, encoding="utf-8")

# Existing verified-discovery tests supply explicit clean protected observations
# when they want to exercise downstream missing-field or tradeoff logic.
p = Path("tests/unit/benchmarks/test_verified_discovery.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    'from orion.benchmarks.result import BenchmarkStatus\n',
    'from orion.benchmarks.authority_attacks import CandidateActivity\nfrom orion.benchmarks.result import BenchmarkStatus\n',
    1,
)
s = s.replace(
    '''        false_promotion_better_than_baseline=None,\n    )\n    assert report.status is BenchmarkStatus.CANNOT_CHECK\n    assert len(report.blockers) == 6\n''',
    '''        false_promotion_better_than_baseline=None,\n        claim_evidence_support_established=None,\n        behavioral_influence_established=None,\n        observed_activity=None,\n    )\n    assert report.status is BenchmarkStatus.CANNOT_CHECK\n    assert len(report.blockers) == 9\n    assert any("observed activity" in blocker for blocker in report.blockers)\n    assert any("semantic support" in blocker for blocker in report.blockers)\n    assert any("behavioral influence" in blocker for blocker in report.blockers)\n''',
    1,
)
s = s.replace(
    '''        false_promotion_better_than_baseline=False,\n    )\n''',
    '''        false_promotion_better_than_baseline=False,\n        claim_evidence_support_established=True,\n        behavioral_influence_established=True,\n        observed_activity=CandidateActivity("clean-observed"),\n    )\n''',
    1,
)
p.write_text(s, encoding="utf-8")
print("patched")
