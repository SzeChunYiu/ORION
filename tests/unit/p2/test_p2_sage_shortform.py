"""Invariants for the SAGE short-form external family.

No test here touches the network: every provider is a fake transport. Each
invariant is tested in both directions -- the alarm fires when it should, and
stays silent when it should not -- because a checker that only ever fires is
indistinguishable from one that always fires.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path("papers/orion-12-open-world-scientific-discovery/scripts/run_sage_shortform.py")


def _module():
    spec = importlib.util.spec_from_file_location("p2_sage_shortform", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registered before exec: the script's dataclasses defer their annotations
    # (`from __future__ import annotations`), and dataclasses resolves them via
    # sys.modules[cls.__module__]. Without this the import dies in the stdlib.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# Synthetic upstream fixtures. Shaped like SAGE at the pinned commit: a JSON
# list per domain, gold in `ground_truth`, and `paper_id`/`paper_title`
# duplicating that gold under another name.
# --------------------------------------------------------------------------
def _record(index: int, domain: str, *, with_gold: bool = True, query: str | None = None) -> dict:
    title = f"Neuronal {domain} substrate {index} for adaptive routing"
    record = {
        "paper_id": f"pid{domain[:2]}{index:04d}",
        "paper_title": title,
        "complete_query": query
        or (
            f"Find me the paper that match this requirement. It appeared in 20{10 + index % 10} and "
            f"was presented at the Annual Meeting of the {domain.title()} Society. Its title ends "
            f"with 'routing'. A key table shows adaptive substrate {index} throughput. This paper "
            f'and "Unrelated Companion Study {index}" both cite "Foundational Prior Work {index}".'
        ),
    }
    if with_gold:
        record["ground_truth"] = {"paperId": record["paper_id"], "title": title}
    return record


def _write_upstream(root: Path, module, *, per_domain: int = 12, drop_gold_in: str | None = None) -> Path:
    source = root / "raw"
    source.mkdir(parents=True, exist_ok=True)
    for domain in module.SAGE_DOMAINS:
        records = [_record(index, domain) for index in range(per_domain)]
        if drop_gold_in == domain:
            records[3] = _record(3, domain, with_gold=False)
        (source / f"short_{domain}.json").write_text(json.dumps(records), encoding="utf-8")
    return source


def _prepared(tmp_path: Path, module, **kwargs):
    source = _write_upstream(tmp_path, module, **kwargs)
    public = tmp_path / "public.jsonl"
    gold = tmp_path / "gold.jsonl"
    pilot = tmp_path / "pilot.jsonl"
    manifest = module.prepare(
        source, public, gold, test_size=8, pilot_size=4, seed=7, pilot_path=pilot
    )
    return manifest, public, gold, pilot


# --------------------------------------------------------------------------
# Custody
# --------------------------------------------------------------------------
def test_gold_never_reaches_candidate_custody_and_detector_is_not_asleep(tmp_path: Path) -> None:
    module = _module()
    manifest, public, gold, _ = _prepared(tmp_path, module)

    public_text = public.read_text(encoding="utf-8")
    gold_records = [json.loads(line) for line in gold.read_text(encoding="utf-8").splitlines()]

    # A hostile system sees only the public file and searches it for any gold.
    for record in gold_records:
        assert record["gold_title"] not in public_text
        assert record["gold_paper_id"] not in public_text
    for line in public_text.splitlines():
        assert set(json.loads(line)) == module.PUBLIC_RECORD_KEYS
    assert manifest["custody"]["gold_visible_to_candidate"] is False
    assert manifest["custody"]["gold_key_paths_in_candidate_file"] == []

    # No-alarm counterpart: the same search DOES find gold in the host-only
    # file, so the search above is capable of failing.
    gold_text = gold.read_text(encoding="utf-8")
    assert gold_records[0]["gold_title"] in gold_text
    assert gold_records[0]["gold_paper_id"] in gold_text


def test_gold_alias_keys_are_treated_as_gold() -> None:
    module = _module()
    # paper_id/paper_title are byte-identical to ground_truth in upstream, so a
    # custody check that ignored them would leak the answer under another name.
    assert module._gold_paths({"task_id": "t", "paper_title": "x"}) == ["$.paper_title"]
    assert module._gold_paths({"nested": [{"ground_truth": {"paperId": "p"}}]}) == [
        "$.nested[0].ground_truth",
        "$.nested[0].ground_truth.paperId",
    ]
    # No-alarm: a legitimate candidate record trips nothing.
    assert module._gold_paths({"task_id": "t", "domain": "d", "complete_query": "q"}) == []


def test_run_refuses_a_candidate_file_carrying_gold(tmp_path: Path) -> None:
    module = _module()
    hostile = tmp_path / "hostile.jsonl"
    hostile.write_text(
        json.dumps(
            {
                "task_id": "sage-short-0001",
                "domain": "computer_science",
                "complete_query": "q",
                "paper_title": "the answer",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(AssertionError, match="gold"):
        module.run_systems(
            hostile, tmp_path / "out", budget=1, max_results=2,
            transport=lambda url: module.RawResponse(200, "{}", {}),
            clock=lambda: 0.0, sleeper=lambda seconds: None, progress_every=0,
        )


# --------------------------------------------------------------------------
# Subsample determinism and stratification
# --------------------------------------------------------------------------
def test_subsample_is_seeded_stratified_and_disjoint_from_pilot(tmp_path: Path) -> None:
    module = _module()
    first, _, _, _ = _prepared(tmp_path / "a", module)
    second, _, _, _ = _prepared(tmp_path / "b", module)
    assert first["subsample"]["task_ids"] == second["subsample"]["task_ids"]
    assert first["subsample"]["task_ids_sha256"] == second["subsample"]["task_ids_sha256"]

    ids = set(first["subsample"]["task_ids"])
    pilot_ids = set(first["subsample"]["pilot_task_ids"])
    assert ids and pilot_ids
    assert ids.isdisjoint(pilot_ids), "pilot tasks must not enter the final test"
    assert set(first["subsample"]["per_domain_test"].values()) == {2}

    # No-alarm: a different seed genuinely moves the draw, so the equality
    # above is evidence of determinism rather than of a constant.
    source = _write_upstream(tmp_path / "c", module)
    other = module.prepare(
        source, tmp_path / "c" / "p.jsonl", tmp_path / "c" / "g.jsonl",
        test_size=8, pilot_size=4, seed=99,
    )
    assert other["subsample"]["task_ids"] != first["subsample"]["task_ids"]


def test_pool_records_upstream_gaps_instead_of_dropping_them_silently(tmp_path: Path) -> None:
    module = _module()
    source = _write_upstream(tmp_path, module, drop_gold_in="healthcare")
    eligible, audit = module.build_eligible_pool(source)
    assert audit["records_parsed"] == 48
    assert audit["records_with_gold"] == 47
    assert len(audit["records_without_gold"]) == 1
    assert audit["records_without_gold"][0]["domain"] == "healthcare"
    assert len(eligible) == 47
    assert all("gold_title" in item for item in eligible)


def test_duplicate_queries_disagreeing_on_gold_stop_the_pool(tmp_path: Path) -> None:
    module = _module()
    source = tmp_path / "raw"
    source.mkdir(parents=True)
    for domain in module.SAGE_DOMAINS:
        records = [_record(index, domain) for index in range(4)]
        if domain == "humanities":
            # Same query text, two different answers: declared exact match has no
            # defined target, so building the pool must stop.
            records[1]["complete_query"] = records[0]["complete_query"]
        (source / f"short_{domain}.json").write_text(json.dumps(records), encoding="utf-8")
    with pytest.raises(ValueError, match="disagree"):
        module.build_eligible_pool(source)


# --------------------------------------------------------------------------
# Transport outcomes: failure, empty and absence are three different things
# --------------------------------------------------------------------------
def _crossref_body(titles: list[str]) -> str:
    return json.dumps({"message": {"items": [{"title": [t], "DOI": f"10.1/{i}"} for i, t in enumerate(titles)]}})


def test_transport_failure_empty_and_absence_stay_distinct() -> None:
    module = _module()
    status = module.SageFetchStatus

    ok = module.fetch_backend(
        "crossref", "q", transport=lambda url: module.RawResponse(200, _crossref_body(["A Real Title"]), {}), max_results=5
    )
    empty = module.fetch_backend(
        "crossref", "q", transport=lambda url: module.RawResponse(200, _crossref_body([]), {}), max_results=5
    )
    limited = module.fetch_backend(
        "crossref", "q", transport=lambda url: module.RawResponse(429, "slow down", {}), max_results=5
    )
    broken = module.fetch_backend(
        "crossref", "q", transport=lambda url: module.RawResponse(0, "URLError: no route", {}), max_results=5
    )
    server = module.fetch_backend(
        "crossref", "q", transport=lambda url: module.RawResponse(503, "", {}), max_results=5
    )
    garbage = module.fetch_backend(
        "crossref", "q", transport=lambda url: module.RawResponse(200, "not json at all", {}), max_results=5
    )

    assert ok.status is status.OK and ok.titles == ("A Real Title",)
    assert empty.status is status.EMPTY and empty.titles == ()
    assert limited.status is status.RATE_LIMITED
    assert broken.status is status.TRANSPORT_ERROR
    assert server.status is status.SERVICE_ERROR
    assert garbage.status is status.MALFORMED_RESPONSE

    observed = {ok.status, empty.status, limited.status, broken.status, server.status, garbage.status}
    assert len(observed) == 6, "collapsing these states would report a failure as an absence"

    # An empty result set is evidence the provider answered; only UNAVAILABLE
    # means no request happened at all.
    assert empty.request_was_issued is True
    assert module.BackendResult("dblp", status.UNAVAILABLE, ()).request_was_issued is False


def test_every_backend_parser_reads_its_own_shape() -> None:
    module = _module()
    dblp = module.fetch_backend(
        "dblp", "q",
        transport=lambda url: module.RawResponse(
            200, json.dumps({"result": {"hits": {"hit": [{"info": {"title": "Graph Title.", "key": "conf/x/y"}}]}}}), {}
        ),
        max_results=5,
    )
    openaire = module.fetch_backend(
        "openaire", "q",
        transport=lambda url: module.RawResponse(
            200,
            json.dumps(
                {"response": {"results": {"result": [
                    {"metadata": {"oaf:entity": {"oaf:result": {"title": {"$": "OpenAIRE Title"}}}}}
                ]}}}
            ),
            {},
        ),
        max_results=5,
    )
    assert dblp.titles == ("Graph Title.",)
    assert openaire.titles == ("OpenAIRE Title",)
    # DBLP's trailing full stop must not defeat the declared normalisation.
    assert module.strict_match("Graph Title.", "Graph Title")


# --------------------------------------------------------------------------
# Budget parity
# --------------------------------------------------------------------------
def test_both_systems_run_under_an_identical_budget(tmp_path: Path) -> None:
    module = _module()
    _, public, _, _ = _prepared(tmp_path, module)
    manifest = module.run_systems(
        public, tmp_path / "out", budget=3, max_results=5,
        transport=lambda url: module.RawResponse(200, _crossref_body(["Some Title"]), {})
        if "crossref" in url
        else module.RawResponse(200, json.dumps({"result": {"hits": {"hit": []}}}), {})
        if "dblp" in url
        else module.RawResponse(200, json.dumps({"response": {"results": {}}}), {}),
        clock=lambda: 0.0, sleeper=lambda seconds: None, progress_every=0,
    )
    parity = manifest["budget_parity"]
    assert parity["parity_holds"] is True
    assert len(set(parity["caps"].values())) == 1
    assert len(set(parity["budgets"].values())) == 1
    assert manifest["resource_limits"]["per_task_cap"] in module.FROZEN_QUERY_COUNT_LADDER
    assert manifest["resource_limits"]["identical_for_every_system"] is True
    assert manifest["arxiv_requests_issued"] == 0

    systems = manifest["systems"]
    issued = {name: value["max_provider_requests_observed"] for name, value in systems.items()}
    assert len(set(issued.values())) == 1, "one system got more provider requests than the other"

    # Systems are interleaved per task, so both candidate files cover exactly the
    # same tasks. Were the lanes sequential, an interruption would leave one file
    # complete and the other empty, which is no paired comparison at all.
    covered = {}
    for name in systems:
        rows = [
            json.loads(line)
            for line in (tmp_path / "out" / f"candidates_{name}.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        covered[name] = [row["task_id"] for row in rows]
    task_lists = list(covered.values())
    assert task_lists[0] == task_lists[1], "systems must cover the same tasks in the same order"
    assert len(task_lists[0]) == manifest["tasks_attempted"]
    assert systems["sage_single_backend"]["is_frozen_baseline"] is False
    assert systems["sage_governed_multiroute"]["backends"] == list(module.MULTIROUTE_BACKENDS)


def test_a_cap_mismatch_makes_the_family_invalid() -> None:
    module = _module()
    balanced = {
        "a": {"per_task_cap_from_frozen_ladder": 10, "per_task_request_budget": 3},
        "b": {"per_task_cap_from_frozen_ladder": 10, "per_task_request_budget": 3},
    }
    assert module.assert_budget_parity(balanced)["parity_holds"] is True  # no-alarm
    skewed = {
        "a": {"per_task_cap_from_frozen_ladder": 10, "per_task_request_budget": 3},
        "b": {"per_task_cap_from_frozen_ladder": 20, "per_task_request_budget": 6},
    }
    with pytest.raises(AssertionError, match="INVALID"):
        module.assert_budget_parity(skewed)


def test_budget_above_the_frozen_ladder_ceiling_is_refused(tmp_path: Path) -> None:
    module = _module()
    _, public, _, _ = _prepared(tmp_path, module)
    with pytest.raises(ValueError, match="ladder"):
        module.run_systems(
            public, tmp_path / "out", budget=201, max_results=2,
            transport=lambda url: module.RawResponse(200, _crossref_body([]), {}),
            clock=lambda: 0.0, sleeper=lambda seconds: None, progress_every=0,
        )


# --------------------------------------------------------------------------
# Route identity and independence
# --------------------------------------------------------------------------
def test_dedup_uses_content_identity_not_provider_ids() -> None:
    module = _module()
    # The same paper as DBLP renders it and as Crossref renders it.
    assert module.title_digest("Graph Title.") == module.title_digest("graph title")
    assert module.title_digest("Graph Title") != module.title_digest("Other Title")


def test_three_derivations_are_distinct_and_deterministic() -> None:
    module = _module()
    query = _record(1, "computer_science")["complete_query"]
    derived = {d.derivation_id: d.derive(query) for d in module.DERIVATIONS}
    assert len(set(derived.values())) == 3, "routes sharing a derivation are not independent"
    for derivation in module.DERIVATIONS:
        assert derivation.derive(query) == derived[derivation.derivation_id]
    # The content route must not search the co-cited titles the query quotes.
    assert "companion" not in derived["content_vocabulary"].lower()
    assert "foundational" not in derived["content_vocabulary"].lower()
    # The citation route is exactly the route that does use them.
    assert "companion" in derived["citation_neighbourhood"].lower()


# --------------------------------------------------------------------------
# Scoring against hand-computed values
# --------------------------------------------------------------------------
def _score_fixture(tmp_path: Path, module):
    gold = tmp_path / "gold.jsonl"
    gold.write_text(
        "".join(
            json.dumps(row) + "\n"
            for row in [
                {"task_id": "t1", "domain": "d", "gold_paper_id": "p1", "gold_title": "Alpha Beta Gamma Delta"},
                {"task_id": "t2", "domain": "d", "gold_paper_id": "p2", "gold_title": "Epsilon Zeta Eta Theta"},
                {"task_id": "t3", "domain": "d", "gold_paper_id": "p3", "gold_title": "Iota Kappa Lambda Mu"},
                {"task_id": "t4", "domain": "d", "gold_paper_id": "p4", "gold_title": "Nu Xi Omicron Pi"},
            ]
        ),
        encoding="utf-8",
    )
    # single: t1 exact at rank 1; t2 exact at rank 3; t3 relaxed-only at rank 1; t4 miss.
    single = tmp_path / "candidates_sage_single_backend.jsonl"
    single.write_text(
        "".join(
            json.dumps(row) + "\n"
            for row in [
                {"task_id": "t1", "system_id": "sage_single_backend", "candidate_titles": ["Alpha Beta Gamma Delta", "x"]},
                {"task_id": "t2", "system_id": "sage_single_backend", "candidate_titles": ["x", "y", "Epsilon Zeta Eta Theta"]},
                {"task_id": "t3", "system_id": "sage_single_backend", "candidate_titles": ["Iota Kappa Lambda Mu: A Sequel"]},
                {"task_id": "t4", "system_id": "sage_single_backend", "candidate_titles": ["nothing relevant"]},
            ]
        ),
        encoding="utf-8",
    )
    # multiroute: t1, t2, t3 exact at rank 1; t4 miss.
    multi = tmp_path / "candidates_sage_governed_multiroute.jsonl"
    multi.write_text(
        "".join(
            json.dumps(row) + "\n"
            for row in [
                {"task_id": "t1", "system_id": "sage_governed_multiroute", "candidate_titles": ["alpha beta gamma delta"]},
                {"task_id": "t2", "system_id": "sage_governed_multiroute", "candidate_titles": ["Epsilon Zeta Eta Theta"]},
                {"task_id": "t3", "system_id": "sage_governed_multiroute", "candidate_titles": ["Iota Kappa Lambda Mu"]},
                {"task_id": "t4", "system_id": "sage_governed_multiroute", "candidate_titles": ["still nothing"]},
            ]
        ),
        encoding="utf-8",
    )
    run_manifest = tmp_path / "run.json"
    run_manifest.write_text(json.dumps({"budget_parity": {"parity_holds": True}}), encoding="utf-8")
    return gold, run_manifest, {
        "sage_single_backend": single,
        "sage_governed_multiroute": multi,
    }


def test_declared_scoring_matches_hand_computed_rates(tmp_path: Path) -> None:
    module = _module()
    gold, run_manifest, candidates = _score_fixture(tmp_path, module)
    summary = module.score(gold, run_manifest, candidates, rank_cutoffs=(1, 10))

    strict1 = summary["metrics"]["strict_hit_at_1"]["per_system"]
    # single: only t1 matches exactly at rank 1 -> 1/4.
    assert strict1["sage_single_backend"]["point_estimate"] == pytest.approx(0.25)
    assert strict1["sage_single_backend"]["successes"] == 1
    # multiroute: t1, t2, t3 -> 3/4.
    assert strict1["sage_governed_multiroute"]["point_estimate"] == pytest.approx(0.75)

    # strict at k=10 lets t2's rank-3 hit count for the single system -> 2/4.
    assert summary["metrics"]["strict_hit_at_10"]["per_system"]["sage_single_backend"][
        "point_estimate"
    ] == pytest.approx(0.5)

    # relaxed adds t3 for the single system ("...: A Sequel" contains the gold
    # token run) -> 2/4 at rank 1.
    assert summary["metrics"]["relaxed_hit_at_1"]["per_system"]["sage_single_backend"][
        "point_estimate"
    ] == pytest.approx(0.5)

    difference = summary["metrics"]["strict_hit_at_1"]["paired_difference"]
    assert difference["contrast"] == "sage_governed_multiroute_minus_sage_single_backend"
    assert difference["absolute_effect_size"] == pytest.approx(0.5)
    assert difference["analysis_seed"] == module.ANALYSIS_SEED
    for field in ("point_estimate", "n", "aggregation_unit", "interval_95"):
        assert field in strict1["sage_single_backend"]


def test_contrast_orientation_comes_from_roles_not_alphabetical_order() -> None:
    module = _module()
    both = {"sage_governed_multiroute", "sage_single_backend"}
    candidate, baseline = module.contrast_orientation(both)
    assert candidate == "sage_governed_multiroute", "the system under test must be the minuend"
    assert baseline == "sage_single_backend"

    # The orientation is the declared role, not a position in a sorted list.
    # The earlier defect took sorted(names)[-1] as the minuend, which reported
    # baseline-minus-candidate and flipped the sign of every effect.
    declared = [spec.system_id for spec in module.SYSTEMS if spec.role == "system_under_test"]
    assert declared == [candidate]
    assert candidate != sorted(both)[-1]

    # No-alarm: an incomplete or unexpected system set yields no paired claim
    # rather than a guessed one.
    assert module.contrast_orientation({"sage_single_backend"}) is None
    assert module.contrast_orientation(both | {"third_system"}) is None


def test_relaxed_variant_does_not_match_a_merely_similar_title() -> None:
    module = _module()
    assert module.relaxed_match("Iota Kappa Lambda Mu: A Sequel", "Iota Kappa Lambda Mu")
    # No-alarm: a shared prefix that is not the whole gold token run is a miss.
    assert not module.relaxed_match("Iota Kappa Lambda", "Iota Kappa Lambda Mu")
    assert not module.relaxed_match("Completely Different Words Here", "Iota Kappa Lambda Mu")
    # Two-token golds are too weak to relax on, so they fall back to strict.
    assert not module.relaxed_match("Alpha Beta Extended Study", "Alpha Beta")


# --------------------------------------------------------------------------
# Refusal to report an invalid denominator
# --------------------------------------------------------------------------
def test_metrics_without_an_established_denominator_are_cannot_check(tmp_path: Path) -> None:
    module = _module()
    gold, run_manifest, candidates = _score_fixture(tmp_path, module)
    summary = module.score(gold, run_manifest, candidates, rank_cutoffs=(1, 10))

    invalid = summary["invalid_metrics_cannot_check"]
    for metric in (
        "route_stop_false_positive_rate",
        "route_stop_false_negative_rate",
        "premature_task_closure_rate",
        "complete_gold_recall",
    ):
        assert invalid[metric] == "CANNOT_CHECK", "an unmeasurable rate must not be reported as 0.0"
        assert metric not in summary["valid_metrics"]

    bindings = summary["required_bindings_emitted"]
    assert bindings["B8_oracle_route_residual_yield"] == "CANNOT_CHECK"
    assert bindings["B10_task_residual_discoverable_within_budget"] == "CANNOT_CHECK"
    # No-alarm: the bindings this family CAN carry are not blanket-refused.
    assert bindings["B1_result_record_task_id"] == "EMITTED"
    assert bindings["B7_captures_content_digest"] == "EMITTED"
    assert summary["valid_metrics"], "the valid column must not be empty either"


def test_score_refuses_when_no_task_is_common_to_gold_and_every_system(tmp_path: Path) -> None:
    module = _module()
    gold, run_manifest, candidates = _score_fixture(tmp_path, module)
    orphan = tmp_path / "orphan.jsonl"
    orphan.write_text(
        json.dumps({"task_id": "not-a-real-task", "system_id": "sage_single_backend", "candidate_titles": []}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="no task"):
        module.score(gold, run_manifest, {"sage_single_backend": orphan}, rank_cutoffs=(1, 10))


def test_a_floor_tie_is_cannot_discriminate_not_a_lexical_win() -> None:
    module = _module()
    # Both systems at zero. A bare `baseline >= candidate` boolean is vacuously
    # true here and would report the gate as firing on a comparison that
    # distinguished nothing.
    floor = module.discriminate(0.0, 0.0, [0.0, 0.0])
    assert floor["verdict"] == "CANNOT_DISCRIMINATE"
    assert floor["discriminating"] is False
    assert floor["at_floor"] is True
    assert floor["floor_artifact"] is True
    assert floor["candidate_at_least_matches_baseline"] is None, "no ordering may be claimed at floor"

    # An interval straddling zero above the floor is still not an ordering.
    straddle = module.discriminate(0.10, 0.08, [-0.04, 0.08])
    assert straddle["verdict"] == "CANNOT_DISCRIMINATE"
    assert straddle["at_floor"] is False
    assert straddle["candidate_at_least_matches_baseline"] is None

    # No-alarm: genuine separation in each direction is reported as such.
    ahead = module.discriminate(0.30, 0.10, [0.08, 0.32])
    assert ahead["verdict"] == "CANDIDATE_AHEAD"
    assert ahead["candidate_at_least_matches_baseline"] is True
    behind = module.discriminate(0.05, 0.25, [-0.31, -0.09])
    assert behind["verdict"] == "BASELINE_AHEAD"
    assert behind["candidate_at_least_matches_baseline"] is False


def test_gate_reports_no_direction_when_the_comparison_cannot_discriminate(tmp_path: Path) -> None:
    module = _module()
    gold = tmp_path / "gold.jsonl"
    gold.write_text(
        "".join(
            json.dumps({"task_id": f"t{i}", "domain": "d", "gold_paper_id": f"p{i}", "gold_title": f"Unfound Title Number {i}"}) + "\n"
            for i in range(6)
        ),
        encoding="utf-8",
    )
    paths = {}
    for system_id in ("sage_single_backend", "sage_governed_multiroute"):
        path = tmp_path / f"candidates_{system_id}.jsonl"
        path.write_text(
            "".join(
                json.dumps({"task_id": f"t{i}", "system_id": system_id, "candidate_titles": ["irrelevant result"]}) + "\n"
                for i in range(6)
            ),
            encoding="utf-8",
        )
        paths[system_id] = path
    run_manifest = tmp_path / "run.json"
    run_manifest.write_text(json.dumps({"budget_parity": {"parity_holds": True}}), encoding="utf-8")

    summary = module.score(gold, run_manifest, paths, rank_cutoffs=(1, 10))
    gate = summary["lexical_gate"]
    assert gate["discrimination"]["verdict"] == "CANNOT_DISCRIMINATE"
    assert gate["gate_fired"] is None, "a floor tie must not be recorded as the gate firing"
    assert gate["gate_informed"] is False
    assert gate["closes_the_frozen_gate"] is False
    assert "CANNOT_DISCRIMINATE" in gate["verdict_text"]
    # The gate rests on an ordering-insensitive cutoff, not on hit@1.
    assert gate["comparison_metric"] == module.GATE_COMPARISON_METRIC
    assert module.GATE_COMPARISON_METRIC != "strict_hit_at_1"
    assert "strict_hit_at_1" in summary["ordering_asymmetry"]["affects"]


def test_score_refuses_a_run_that_consumed_a_different_candidate_file(tmp_path: Path) -> None:
    module = _module()
    gold, run_manifest, candidates = _score_fixture(tmp_path, module)
    split = tmp_path / "split.json"
    split.write_text(
        json.dumps({"custody": {"public_sha256": "aaaa", "gold_sha256": "bbbb"}}), encoding="utf-8"
    )
    with pytest.raises(AssertionError, match="hash chain"):
        module.score(
            gold, run_manifest, candidates, rank_cutoffs=(1, 10), split_manifest_path=split
        )

    # No-alarm: a consistent chain scores normally and records that it checked.
    consistent = tmp_path / "consistent.json"
    manifest = json.loads(run_manifest.read_text(encoding="utf-8"))
    manifest["candidate_input_sha256"] = "cccc"
    run_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    consistent.write_text(
        json.dumps(
            {"custody": {"public_sha256": "cccc", "gold_sha256": module._sha256(gold)}}
        ),
        encoding="utf-8",
    )
    summary = module.score(
        gold, run_manifest, candidates, rank_cutoffs=(1, 10), split_manifest_path=consistent
    )
    assert summary["stage_hash_chain"]["checked"] is True


def test_nothing_is_ever_labelled_official(tmp_path: Path) -> None:
    module = _module()
    gold, run_manifest, candidates = _score_fixture(tmp_path, module)
    summary = module.score(gold, run_manifest, candidates, rank_cutoffs=(1, 10))
    assert summary["authority"] == "DECLARED_DEVIATION_NEVER_OFFICIAL"
    assert summary["official_scorer_used"] is False
    assert summary["family_carries_confirmatory_primary"] is False
    for metric in summary["metrics"].values():
        assert metric["official"] is False
        assert metric["declared_deviation"] is True
    gate = summary["lexical_gate"]
    assert gate["gate_id"] == "sage_lexical_gate"
    assert gate["closes_the_frozen_gate"] is False


# --------------------------------------------------------------------------
# Provenance of the frozen statistics library
# --------------------------------------------------------------------------
def test_intervals_come_from_the_frozen_library_not_a_local_copy(tmp_path: Path, monkeypatch) -> None:
    module = _module()
    stats = module.load_publication_stats()
    assert Path(stats.__file__).as_posix().endswith(module.PUBLICATION_STATS_PATH.as_posix())

    # Provenance, not numerical coincidence: replace the library's interval with
    # a sentinel and require it to appear in the output. A local reimplementation
    # that merely agreed with the library would fail this.
    sentinel = (0.123456, 0.876543)
    real_loader = module.load_publication_stats

    def loader_with_sentinel(repo_root=None):
        loaded = real_loader(repo_root)
        loaded.wilson_interval = lambda successes, total, **kwargs: sentinel
        return loaded

    monkeypatch.setattr(module, "load_publication_stats", loader_with_sentinel)
    gold, run_manifest, candidates = _score_fixture(tmp_path, module)
    summary = module.score(gold, run_manifest, candidates, rank_cutoffs=(1, 10))
    interval = summary["metrics"]["strict_hit_at_1"]["per_system"]["sage_single_backend"]["interval_95"]
    assert interval == [pytest.approx(sentinel[0]), pytest.approx(sentinel[1])]


def test_achieved_precision_labels_underpowered_and_refuses_an_empty_denominator() -> None:
    module = _module()
    tier_b = module.achieved_precision(385)
    assert tier_b["achieved_tier"] == "TIER_B_committed"
    assert tier_b["underpowered"] is True  # half-width 0.0497 exceeds delta_sup 0.03
    assert tier_b["family_carries_primary"] is False

    assert module.achieved_precision(1068)["achieved_tier"] == "TIER_A_full"
    assert module.achieved_precision(100)["achieved_tier"] == "TIER_D_minimum_inferential"
    tiny = module.achieved_precision(40)
    assert tiny["achieved_tier"] == "BELOW_TIER_D"
    assert tiny["descriptive_only"] is True
    assert module.achieved_precision(0)["achieved_tier"] == "CANNOT_CHECK"


# --------------------------------------------------------------------------
# Contamination is measured, not assumed away
# --------------------------------------------------------------------------
def test_contamination_is_measured_and_unmeasurable_exposure_is_cannot_check() -> None:
    module = _module()
    copied = [{"complete_query": "Find me Alpha Beta Gamma Delta please", "gold_title": "Alpha Beta Gamma Delta"}]
    report = module.contamination_report(copied)
    assert report["gold_title_verbatim_inside_query"] == 1
    assert report["gold_title_token_overlap_in_query"]["mean"] == pytest.approx(1.0)
    assert report["longest_common_token_run_with_gold_title"]["max"] == 4
    assert report["backend_index_ingested_sage"] == "CANNOT_CHECK"

    # No-alarm: an unrelated query is not flagged as a copy.
    clean = [{"complete_query": "Which study reports throughput on neuromorphic hardware?", "gold_title": "Alpha Beta Gamma Delta"}]
    clean_report = module.contamination_report(clean)
    assert clean_report["gold_title_verbatim_inside_query"] == 0
    assert clean_report["gold_title_token_overlap_in_query"]["mean"] == pytest.approx(0.0)


def test_declared_normalisations_are_checked_for_collisions_on_the_gold_set() -> None:
    module = _module()
    colliding = [
        {"gold_paper_id": "p1", "gold_title": "Deep Learning for Chest X Rays"},
        {"gold_paper_id": "p2", "gold_title": "deep learning for chest x-rays"},
    ]
    report = module.normalisation_collisions(colliding)
    assert report["strict"]["distinct_gold_titles_sharing_a_normalised_form"] == 1

    # No-alarm: distinct titles produce no collision under either variant.
    distinct = [
        {"gold_paper_id": "p1", "gold_title": "Alpha Beta Gamma Delta"},
        {"gold_paper_id": "p2", "gold_title": "Epsilon Zeta Eta Theta"},
    ]
    clean = module.normalisation_collisions(distinct)
    assert clean["strict"]["distinct_gold_titles_sharing_a_normalised_form"] == 0
    assert clean["relaxed"]["gold_titles_contained_in_another_gold_title"] == 0
