"""Tests for the reusable typed-merge evaluator.

Three groups:

1. Theorem corner cases from CLAIM_LEDGER.md / CLAIM_LEDGER_R2.md.
2. Regression against the committed ORION-03 round 1 and round 2 receipts.
3. Negative and no-alarm controls, so the evaluator is exercised on cases where
   it must stay silent as well as cases where it must fire.

Randomised tests use a fixed seed so failures are reproducible. Sizes are chosen
so the exhaustive fixed-point enumeration of MANUSCRIPT_V2.md section 11 stays
tractable: it costs (2^|Lambda|)^|Q| assignments.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import random
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
EVIDENCE = REPO / "papers" / "orion-03-typed-merge-falsification" / "evidence"
R1 = EVIDENCE / "round1-cedar-multipolicy"
R2 = EVIDENCE / "round2-x509-truststore"
sys.path.insert(0, str(ROOT))

from typed_merge_evaluator import (  # noqa: E402
    Instance, Problem, Report, Rule, SchemaError, all_fixed_points,
    check_expectations, least_fixed_point, proof_tree, retraction,
)

SEED = 20260828  # fixed so any failure is reproducible


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def problems(subdir):
    return sorted((ROOT / "examples" / subdir).glob("*.json"))


def random_instance(rng, n_claims=3, n_licenses=2, n_rules=3):
    claims = [f"q{i}" for i in range(n_claims)]
    licenses = [f"l{i}" for i in range(n_licenses)]
    seeds = {
        c: frozenset(x for x in licenses if rng.random() < 0.4)
        for c in claims
        if rng.random() < 0.7
    }
    rules = []
    for i in range(n_rules):
        body = rng.sample(claims, rng.randint(1, min(2, n_claims)))
        head = rng.choice(claims)
        cap = frozenset(x for x in licenses if rng.random() < 0.7)
        rules.append(Rule(id=f"r{i}", body=tuple(body), head=head, cap=cap))
    return Instance(
        licenses=frozenset(licenses), claims=frozenset(claims),
        seeds=seeds, rules=tuple(rules), refuted=frozenset(),
    )


# --------------------------------------------------------------------------
# 1. Theorem corner cases
# --------------------------------------------------------------------------

def test_unsupported_cycle_cannot_self_authorize():
    """D-C3 / D2-C3: a cycle is a derivation shape, not evidence."""
    inst = Instance(
        licenses=frozenset({"L"}), claims=frozenset({"a", "b"}), seeds={},
        rules=(Rule("ab", ("b",), "a", frozenset({"L"})),
               Rule("ba", ("a",), "b", frozenset({"L"}))),
        refuted=frozenset(),
    )
    assert least_fixed_point(inst).authorized == frozenset()


def test_seeded_cycle_does_propagate():
    """D-C3 second half: a seeded reachable cycle may close."""
    inst = Instance(
        licenses=frozenset({"L"}), claims=frozenset({"a", "b"}),
        seeds={"a": frozenset({"L"})},
        rules=(Rule("ab", ("b",), "a", frozenset({"L"})),
               Rule("ba", ("a",), "b", frozenset({"L"}))),
        refuted=frozenset(),
    )
    ev = least_fixed_point(inst)
    assert ev.label("a") == frozenset({"L"})
    assert ev.label("b") == frozenset({"L"})


def test_refutations_cannot_add_authority():
    """D-C4 / D2-C4 (Theorem 4): R subset R' implies Auth(R') subset Auth(R)."""
    rng = random.Random(SEED)
    for _ in range(300):
        inst = random_instance(rng)
        claims = sorted(inst.claims)
        extra = frozenset(rng.sample(claims, rng.randint(0, len(claims))))
        base = least_fixed_point(inst)
        wider = least_fixed_point(
            Instance(inst.licenses, inst.claims, inst.seeds, inst.rules, extra)
        )
        assert wider.pairs <= base.pairs, (sorted(extra), sorted(wider.pairs - base.pairs))


def test_retraction_is_exactly_the_lost_pairs_and_is_minimal():
    """D-C6 / D2-C5 (Theorem 5): Ret = A_pre \\ A_post, and A_post keeps every
    pair that still has an untainted proof tree."""
    rng = random.Random(SEED + 1)
    for _ in range(300):
        inst = random_instance(rng)
        claims = sorted(inst.claims)
        refute = rng.sample(claims, rng.randint(1, len(claims)))
        pre, post, lost = retraction(inst, refute)
        assert lost == pre.pairs - post.pairs
        assert post.pairs & lost == frozenset()
        # Nothing retained without a witness, and nothing withdrawn that has one.
        for claim, lic in post.pairs:
            assert proof_tree(
                Instance(inst.licenses, inst.claims, inst.seeds, inst.rules,
                         inst.refuted | frozenset(refute)),
                post, claim, lic,
            ) is not None
        for claim, lic in lost:
            assert lic not in post.label(claim)


def test_proof_tree_equivalence():
    """Theorem 2: a license is in the label iff a finite untainted tree exists."""
    rng = random.Random(SEED + 2)
    for _ in range(200):
        inst = random_instance(rng)
        ev = least_fixed_point(inst)
        for claim in sorted(inst.claims):
            for lic in sorted(inst.licenses):
                tree = proof_tree(inst, ev, claim, lic)
                assert (tree is not None) == (lic in ev.label(claim))
                if tree is not None:
                    assert _tree_is_valid(inst, tree, lic)


def _tree_is_valid(inst, tree, lic):
    if tree["claim"] in inst.refuted:
        return False
    if tree["kind"] == "seed":
        return lic in inst.seed_of(tree["claim"])
    rule = next(r for r in inst.rules if r.id == tree["rule"])
    if rule.head != tree["claim"] or lic not in rule.cap:
        return False
    return len(tree["premises"]) == len(rule.body) and all(
        child is not None and child["claim"] == atom and _tree_is_valid(inst, child, lic)
        for child, atom in zip(tree["premises"], rule.body)
    )


def test_iterative_result_is_the_unique_least_fixed_point():
    """MANUSCRIPT_V2.md section 11: compare iteration against exhaustive
    enumeration of every fixed point and confirm ours is the unique least one."""
    rng = random.Random(SEED + 3)
    for _ in range(60):
        inst = random_instance(rng, n_claims=3, n_licenses=2, n_rules=3)
        computed = dict(least_fixed_point(inst).labels)
        every = all_fixed_points(inst)
        assert computed in every
        for other in every:
            assert all(computed[c] <= other[c] for c in inst.claims)


def test_rule_order_does_not_change_the_fixed_point():
    """Theorem 1 second half: every fair rule order reaches the same lfp."""
    rng = random.Random(SEED + 4)
    for _ in range(200):
        inst = random_instance(rng, n_rules=4)
        rules = list(inst.rules)
        rng.shuffle(rules)
        shuffled = Instance(inst.licenses, inst.claims, inst.seeds,
                            tuple(rules), inst.refuted)
        assert least_fixed_point(inst).labels == least_fixed_point(shuffled).labels


def test_manuscript_case3_leaves_exact_d4_entirely_unlicensed():
    """D2-C7: bounded support-frontier evidence cannot prove exact D_4.

    Stronger than "no THEOREM reaches it": the label is empty, because the
    frontier and the analytic lemma share no license. The flat reading still
    derives it, which is exactly the error the typing is there to catch."""
    problem = Problem.load(
        ROOT / "examples" / "manuscript-cases" / "case3-d4-bounded-computation.json")
    report = Report(problem)
    assert report.typed_label("exact-D4") == frozenset()
    assert report.typed_label("31-in-C0") == frozenset()
    assert report.flat_authorized("exact-D4") is True
    assert report.first_mixing("exact-D4") is True
    assert report.typed_label("support-at-least-23") == frozenset(
        {"BOUNDED_COMPUTATION", "EXTERNAL_REPLAY"})


def test_cap_blocks_nonpromotion():
    """D2-C6: a post-outcome repair rule cannot manufacture PROSPECTIVE authority
    even when its premise carries it."""
    inst = Instance(
        licenses=frozenset({"THEOREM", "PROSPECTIVE", "POST_OUTCOME"}),
        claims=frozenset({"panel", "repair"}),
        seeds={"panel": frozenset({"THEOREM", "PROSPECTIVE"})},
        rules=(Rule("repair_rule", ("panel",), "repair",
                    frozenset({"THEOREM", "POST_OUTCOME"})),),
        refuted=frozenset(),
    )
    label = least_fixed_point(inst).label("repair")
    assert "PROSPECTIVE" not in label
    assert label == frozenset({"THEOREM"})


def test_theorem1_round_bound_holds():
    rng = random.Random(SEED + 5)
    for _ in range(200):
        inst = random_instance(rng)
        assert least_fixed_point(inst).rounds <= inst.pair_bound + 1


# --------------------------------------------------------------------------
# 2. Regression against committed ORION-03 receipts
# --------------------------------------------------------------------------

@pytest.mark.skipif(not R1.exists(), reason="round 1 evidence not present")
def test_round1_eight_controls_reproduced_exactly():
    """The eight committed (flat, typed) pairs must be reproduced exactly."""
    committed = {
        c["name"]: (c["flat"], c["typed"])
        for c in load(R1 / "RUST_ADJUDICATION_V1.json")["hostile_and_safe_controls"]["cases"]
    }
    assert len(committed) == 8
    seen = {}
    for path in problems("cedar-multipolicy"):
        problem = Problem.load(path)
        report = Report(problem)
        name = problem.id.split("/")[-1]
        target = problem.targets[0]
        seen[name] = (report.flat_authorized(target), report.typed_authorized(target))
    assert set(seen) == set(committed)
    assert seen == committed


@pytest.mark.skipif(not R1.exists(), reason="round 1 evidence not present")
def test_round1_receipt_digests_still_verify():
    """The committed receipts must still hash to their recorded digests."""
    results = load(R1 / "ROUND1_RESULTS_V1.json")
    for name, entry in results["receipts"].items():
        blob = (R1 / entry["path"]).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == entry["sha256"], name
        assert len(blob) == entry["bytes"], name


@pytest.mark.skipif(not R2.exists(), reason="round 2 evidence not present")
def test_round2_source_binding_digests_still_verify():
    binding = load(R2 / "SOURCE_BINDING_V2.json")
    third_party = R2 / "third_party" / "openssl-3.6.4-testcerts"
    checked = 0
    for group, root in (("vendored_files", third_party), ("vendored_recipe", third_party),
                        ("frozen_artifacts", R2), ("results_artifacts", R2)):
        for rel, digest in binding[group].items():
            blob = (root / rel).read_bytes()
            assert hashlib.sha256(blob).hexdigest() == digest, f"{group}/{rel}"
            checked += 1
    assert checked == 268


@pytest.mark.skipif(not R2.exists(), reason="round 2 evidence not present")
def test_round2_c6_decisions_reproduced_exactly():
    """C6-HOSTILE-SPLIT is the one committed hybrid the structural encoding can
    derive without an engine. Its M1/M5 decisions must come out exactly."""
    task = load(R2 / "ROUND2_RESULTS_V2.json")["hostile_control_C6"]["task"]
    problem = Problem.load(ROOT / "examples" / "x509-truststore" / "C6-HOSTILE-SPLIT.json")
    report = Report(problem)
    target = "chain:ee-cert"
    assert report.flat_authorized(target) is task["decisions"]["M1_FLAT_UNION"] is True
    assert report.typed_authorized(target) is task["decisions"]["M5_TYPED_WITNESS"] is False
    assert report.first_mixing(target) is task["hybrid"] is True
    assert task["vA"] is False and task["vB"] is False and task["vU"] is True


@pytest.mark.skipif(not R2.exists(), reason="round 2 evidence not present")
def test_round2_committed_aggregates_are_internally_consistent():
    results = load(R2 / "ROUND2_RESULTS_V2.json")
    fams = results["families"]
    assert sum(f["engine_hybrids"] for f in fams.values()) == results["engine_hybrids_total"] == 46
    assert sum(f["tasks"] for f in fams.values()) == results["total_tasks"] == 1962
    assert len(results["hybrid_tasks"]) == 46
    for name, fam in fams.items():
        # M1 authorizes the union, so it is unsafe on exactly the hybrids.
        assert fam["M1_FLAT_UNION"]["unsafe_merges"] == fam["engine_hybrids"], name
        # M5 allows exactly the parent-authorized tasks.
        assert fam["M5_TYPED_WITNESS"]["allows"] == fam["parent_authorized"], name
    det = results["obstruction_detection"]
    assert det["precision"] == det["recall"] == 1.0
    assert det["m5_flagged"] == det["engine_hybrids"] == 46
    assert results["invariants"]["m5_decision_equals_parent_authorization"] is True


def test_m5_optimality_is_an_identity_not_a_measurement():
    """Finding: with M5 := vA or vB and hybrid := vU and not (vA or vB), the
    round-2 headline numbers are analytic identities. `unsafe[M5]` and
    `needless[M5]` are identically false and precision = recall = 1.0 for *any*
    input whatsoever, so they carry no empirical content about the corpus.
    This test pins that reading by exhausting all 8 verdict triples."""
    flagged = hybrids = 0
    for v_a in (False, True):
        for v_b in (False, True):
            for v_u in (False, True):
                parent = v_a or v_b
                hybrid = v_u and not parent
                assert (parent and hybrid) is False      # unsafe[M5]
                assert ((not parent) and parent) is False  # needless[M5]
                hybrids += hybrid
                flagged += hybrid and not parent
    assert flagged == hybrids  # recall 1.0 and precision 1.0, by construction


# --------------------------------------------------------------------------
# 3. Negative and no-alarm controls
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path", problems("cedar-multipolicy") + problems("x509-truststore")
                         + problems("manuscript-cases"),
                         ids=lambda p: p.stem)
def test_every_shipped_example_meets_its_declared_expectations(path):
    problem = Problem.load(path)
    assert check_expectations(problem, Report(problem)) == []


def test_clean_instance_raises_no_alarm():
    """A detector must be silent when nothing is wrong."""
    inst = Instance(
        licenses=frozenset({"A"}), claims=frozenset({"seed", "derived"}),
        seeds={"seed": frozenset({"A"})},
        rules=(Rule("r", ("seed",), "derived", frozenset({"A"})),),
        refuted=frozenset(),
    )
    ev = least_fixed_point(inst)
    assert ev.label("derived") == frozenset({"A"})
    _, _, lost = retraction(inst, [])
    assert lost == frozenset()


def test_schema_violations_are_rejected_distinctly():
    """A malformed instance must fail loudly, never evaluate to 'fine'."""
    good = json.loads((ROOT / "examples" / "cedar-multipolicy"
                       / "single_origin_complete_record.json").read_text())
    for mutate in (
        lambda d: d.update(schema="WRONG"),
        lambda d: d.update(licenses=["A", "A"]),
        lambda d: d["seeds"].update({"nope": ["A"]}),
        lambda d: d["seeds"].update({"subject=alice": ["UNKNOWN"]}),
        lambda d: d["rules"].append({"body": [], "head": "__target__"}),
        lambda d: d.update(refuted=["ghost"]),
        lambda d: d.update(targets=["ghost"]),
    ):
        doc = json.loads(json.dumps(good))
        mutate(doc)
        with pytest.raises((SchemaError, ValueError)):
            Problem(doc)


def test_cli_exit_codes_distinguish_cannot_check_from_failure(tmp_path, capsys):
    from typed_merge_evaluator.cli import EXIT_CANNOT_CHECK, EXIT_EXPECTATION_FAILED, EXIT_OK, main
    ok = ROOT / "examples" / "cedar-multipolicy" / "single_origin_complete_record.json"
    assert main([str(ok)]) == EXIT_OK
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    assert main([str(broken)]) == EXIT_CANNOT_CHECK
    wrong = json.loads(ok.read_text())
    wrong["expect"]["typed_authorized"]["__target__"] = False
    bad = tmp_path / "wrong.json"
    bad.write_text(json.dumps(wrong), encoding="utf-8")
    assert main([str(bad)]) == EXIT_EXPECTATION_FAILED
