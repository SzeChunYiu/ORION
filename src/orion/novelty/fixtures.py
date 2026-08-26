from __future__ import annotations

from orion.knowledge.nearest_work import AbsorptionDecision, AbsorptionDisposition
from orion.novelty.certificate import (
    CertificateDraft,
    DiscriminatingExperiment,
    HostileAlreadySolvedRoute,
    MechanismAtom,
    OverlapRecord,
    PriorWorkRef,
)
from orion.novelty.saturation import SearchRoundRecord, SearchSaturationProtocol
from orion.novelty.types import MechanismOverlap, NoveltySearchRoute, REQUIRED_SEARCH_ROUTES, SourceAccess


def prior_work(
    work_id: str = "arxiv:0000.00000",
    *,
    title: str = "Prior work",
    mechanism_summary: str = "A documented mechanism.",
    access: SourceAccess = SourceAccess.FULL_TEXT,
) -> PriorWorkRef:
    return PriorWorkRef(
        work_id=work_id,
        title=title,
        source_id=work_id,
        mechanism_summary=mechanism_summary,
        access_status=access,
        evidence_refs=(work_id,),
    )


def hostile_route(
    *,
    executed: bool = True,
    findings: tuple[PriorWorkRef, ...] = (),
    queries: tuple[str, ...] = ("already solved functional equivalent of claimed mechanism",),
    residual_changed: bool | None = None,
    note: str = "Hostile search executed against function-only vocabulary.",
) -> HostileAlreadySolvedRoute:
    changed = bool(findings) if residual_changed is None else residual_changed
    return HostileAlreadySolvedRoute(
        route_id="hostile:already-solved",
        assumption="assume this is already solved — find it",
        queries=queries,
        findings=findings,
        executed=executed,
        residual_changed=changed,
        note=note,
    )


def saturated_rounds(
    *,
    extra_finding_id: str = "arxiv:0000.00000",
    changing_until: int = 5,
) -> tuple[SearchRoundRecord, ...]:
    rounds: list[SearchRoundRecord] = []
    for index, route in enumerate(REQUIRED_SEARCH_ROUTES, start=1):
        findings = (extra_finding_id,) if route is not NoveltySearchRoute.HOSTILE_ALREADY_SOLVED else ()
        rounds.append(
            SearchRoundRecord(
                round_index=index,
                route=route,
                queries=(f"query for {route.value}",),
                finding_ids=findings,
                changed_residual_or_disposition=index <= changing_until,
            )
        )
    rounds.append(
        SearchRoundRecord(
            round_index=len(rounds) + 1,
            route=NoveltySearchRoute.CITED_BY_RELATED,
            queries=("cited-by expansion confirmation round",),
            finding_ids=(),
            changed_residual_or_disposition=False,
        )
    )
    rounds.append(
        SearchRoundRecord(
            round_index=len(rounds) + 1,
            route=NoveltySearchRoute.HOSTILE_ALREADY_SOLVED,
            queries=("hostile empty confirmation",),
            finding_ids=(),
            changed_residual_or_disposition=False,
        )
    )
    return tuple(rounds)


def documented_saturation(queries_by_route: dict[NoveltySearchRoute, tuple[str, ...]]) -> SearchSaturationProtocol:
    rounds: list[SearchRoundRecord] = []
    for index, route in enumerate(REQUIRED_SEARCH_ROUTES, start=1):
        rounds.append(
            SearchRoundRecord(
                round_index=index,
                route=route,
                queries=queries_by_route.get(route, (f"documented {route.value}",)),
                finding_ids=("documented-audit",) if index <= 5 else (),
                changed_residual_or_disposition=index <= 5,
            )
        )
    rounds.append(
        SearchRoundRecord(
            round_index=len(rounds) + 1,
            route=NoveltySearchRoute.CITED_BY_RELATED,
            queries=("related-work expansion; no residual change",),
            finding_ids=(),
            changed_residual_or_disposition=False,
        )
    )
    rounds.append(
        SearchRoundRecord(
            round_index=len(rounds) + 1,
            route=NoveltySearchRoute.HOSTILE_ALREADY_SOLVED,
            queries=queries_by_route.get(
                NoveltySearchRoute.HOSTILE_ALREADY_SOLVED,
                ("assume already solved; find the mechanism under parent-discipline vocabulary",),
            ),
            finding_ids=(),
            changed_residual_or_disposition=False,
        )
    )
    return SearchSaturationProtocol.from_rounds(tuple(rounds))


def example_supported_draft(**overrides: object) -> CertificateDraft:
    residual = "Authority-bearing residual certificate that an LLM score cannot set."
    body: dict[str, object] = dict(
        claim_id="claim:test",
        claim_text=residual,
        problem_task_definition="Decide whether a claimed scientific mechanism is new.",
        claimed_mechanism_decomposition=(
            MechanismAtom("m:residual", "Bounded residual certificate", "core"),
        ),
        closest_prior_by_term=(prior_work("arxiv:1111.11111"),),
        closest_prior_by_function=(prior_work("arxiv:2222.22222"),),
        parent_discipline_mechanisms=(prior_work("arxiv:3333.33333"),),
        benchmark_implementation_routes=(prior_work("github:example/bench"),),
        hostile_already_solved_route=hostile_route(),
        overlap_classifications=(
            OverlapRecord(
                mechanism_id="m:residual",
                prior_work_id="arxiv:2222.22222",
                classification=MechanismOverlap.PARTIAL,
                note="Shares evaluation framing, not the residual authority rule.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision(
                "m:prior-eval",
                AbsorptionDisposition.ADAPT,
                ("NOVELTY.CERTIFICATE.v1",),
                "Absorb evaluation framing; keep residual authority semantics.",
            ),
        ),
        original_claim_text=residual,
        smallest_residual=residual,
        residual_implementation_evidence=("src/orion/novelty/certificate.py",),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:rinobench-holdout",
            hypothesis="Certificate decisions match expert novelty labels better than LLM-as-judge.",
            observation_if_novel="Higher calibration with CANNOT_CHECK; fewer false novel claims.",
            observation_if_already_solved="No gain over RINoBench/axiomatic ensembles.",
            status="EXECUTED",
            result="residual survived matched baselines",
        ),
        unresolved_sources=(),
        unresolved_search_routes=(),
        inaccessible_material_sources=(),
        saturation=SearchSaturationProtocol.from_rounds(saturated_rounds()),
        snapshot_date="2026-08-17",
        llm_novelty_score=None,
        llm_proposed_state=None,
        confidence=None,
    )
    body.update(overrides)
    return CertificateDraft(**body)  # type: ignore[arg-type]


def new_terminology_for_old_mechanism_draft() -> CertificateDraft:
    old = prior_work(
        "arxiv:2509.04708",
        title="Bayesian Diagnosability and Active Fault Identification",
        mechanism_summary="Active inputs make otherwise undiagnosable faults distinguishable.",
    )
    claim = (
        "Epistemic Mutation Licensing via Causal Responsibility Belief States: "
        "an intervention-supported diagnosability operator that authorizes K/W/M edits."
    )
    return example_supported_draft(
        claim_id="adv:new-terminology-old-mechanism",
        claim_text=claim,
        original_claim_text=claim,
        smallest_residual="",
        claimed_mechanism_decomposition=(
            MechanismAtom(
                "m:active-diagnosis",
                "Active probes that distinguish responsibility classes",
                "core",
            ),
        ),
        closest_prior_by_term=(
            prior_work(
                "arxiv:2606.09071",
                title="REFLECT",
                mechanism_summary="Reflective failure localization under a new label.",
            ),
        ),
        closest_prior_by_function=(old,),
        parent_discipline_mechanisms=(old,),
        hostile_already_solved_route=hostile_route(
            findings=(old,),
            queries=(
                "assume already solved: active fault identification",
                "diagnosability intervention epistemic mutation",
            ),
            residual_changed=True,
            note="Hostile function-only search recovered active diagnosability under older vocabulary.",
        ),
        overlap_classifications=(
            OverlapRecord(
                mechanism_id="m:active-diagnosis",
                prior_work_id="arxiv:2509.04708",
                classification=MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                note="New terminology for active diagnosability / fault isolation.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision(
                "m:active-diagnosis",
                AbsorptionDisposition.ADOPT,
                ("P1.RESPONSIBILITY.v2",),
                "Adopt parent-discipline active diagnosability; do not rebrand it as novelty.",
            ),
        ),
        residual_implementation_evidence=(),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:rebrand-check",
            hypothesis="If the mechanism is only renamed, experts will mark it already solved.",
            observation_if_novel="Experts treat the licensing residual as distinct.",
            observation_if_already_solved="Experts identify active diagnosability.",
            status="EXECUTED",
            result="functional equivalent recovered",
        ),
    )


def composition_of_knowns_draft() -> CertificateDraft:
    original = (
        "A new self-improving scientific agent combining archive search, sandbox "
        "self-edit, causal attribution, evaluator locking, and fresh-transfer tests."
    )
    residual = (
        "Only the non-compensatory composition remains: replay gain cannot compensate "
        "fresh harm, and the host retains promotion authority."
    )
    dgm = prior_work(
        "arxiv:2505.22954",
        title="Darwin Gödel Machine",
        mechanism_summary="Self-code modification with archive, sandbox, and empirical validation.",
    )
    pace = prior_work(
        "arxiv:2606.08106",
        title="PACE",
        mechanism_summary="Anytime-valid acceptance tests for self-evolving agents.",
    )
    return example_supported_draft(
        claim_id="adv:composition-of-knowns",
        claim_text=original,
        original_claim_text=original,
        smallest_residual=residual,
        claimed_mechanism_decomposition=(
            MechanismAtom("m:archive", "Open-ended archive of self-edits", "component"),
            MechanismAtom("m:sandbox", "Sandboxed empirical validation", "component"),
            MechanismAtom("m:noncompensatory", "Non-compensatory admission", "residual"),
        ),
        closest_prior_by_term=(dgm, pace),
        closest_prior_by_function=(dgm, pace),
        overlap_classifications=(
            OverlapRecord(
                "m:archive",
                "arxiv:2505.22954",
                MechanismOverlap.IDENTICAL,
                "Archive/self-edit is prior art.",
            ),
            OverlapRecord(
                "m:sandbox",
                "arxiv:2505.22954",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Sandbox validation is prior art.",
            ),
            OverlapRecord(
                "m:noncompensatory",
                "arxiv:2606.08106",
                MechanismOverlap.PARTIAL,
                "Anytime-valid tests constrain false commits but do not encode ORION's stage lattice.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision("m:archive", AbsorptionDisposition.ADAPT, ("P5.ARCHIVE",), "Adapt DGM archive."),
            AbsorptionDecision("m:sandbox", AbsorptionDisposition.ADAPT, ("P5.SANDBOX",), "Adapt DGM sandbox."),
            AbsorptionDecision(
                "m:noncompensatory",
                AbsorptionDisposition.COMPOSE,
                ("P5.ADMISSION.v1",),
                "Compose non-compensatory gates around known components.",
            ),
        ),
        residual_implementation_evidence=("research/paper-programme-v2/NEAREST_WORK_V2_AUDIT_2026-08-16.md",),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:composition-holdout",
            hypothesis="The constrained composition improves integrity over component-wise baselines.",
            observation_if_novel="Fresh-transfer/harm trade-off improves under matched budgets.",
            observation_if_already_solved="PACE/DGM already produce the same admission behaviour.",
            status="PROPOSED",
            result="",
        ),
    )


def broad_claim_narrow_residual_draft() -> CertificateDraft:
    original = (
        "ORION invents scientific obstruction, schema fusion, provenance knowledge graphs, "
        "and typed mapping as a unified novelty."
    )
    residual = (
        "only provenance-bound typed-coordinate non-merge certificates, after absorbing "
        "schema fusion, provenance KGs, and standalone obstruction."
    )
    sheaf = prior_work(
        "arxiv:2605.14033",
        title="Sheaf-Theoretic Transport and Obstruction",
        mechanism_summary="Transport/gluing/obstruction for scientific representational change.",
    )
    muse = prior_work(
        "arxiv:2608.10974",
        title="MUSE",
        mechanism_summary="Source-grounded cross-domain structured knowledge extraction.",
    )
    return example_supported_draft(
        claim_id="adv:broad-claim-narrow-residual",
        claim_text=original,
        original_claim_text=original,
        smallest_residual=residual,
        claimed_mechanism_decomposition=(
            MechanismAtom("m:obstruction", "Scientific obstruction certificates", "core"),
            MechanismAtom("m:fusion", "Schema fusion", "absorbed"),
            MechanismAtom("m:provenance", "Provenance KG", "absorbed"),
        ),
        closest_prior_by_term=(sheaf, muse),
        closest_prior_by_function=(sheaf, muse),
        overlap_classifications=(
            OverlapRecord(
                "m:fusion",
                "arxiv:2608.10974",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Structured extraction/fusion is not novel.",
            ),
            OverlapRecord(
                "m:provenance",
                "arxiv:2605.14033",
                MechanismOverlap.PARTIAL,
                "Obstruction/transport is prior; typed non-merge certificates remain.",
            ),
            OverlapRecord(
                "m:obstruction",
                "arxiv:2605.14033",
                MechanismOverlap.PARTIAL,
                "Standalone obstruction is absorbed; provenance-bound typed coordinates remain.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision("m:fusion", AbsorptionDisposition.REJECT, (), "Reject fusion as novelty."),
            AbsorptionDecision("m:provenance", AbsorptionDisposition.ADAPT, ("P3.PROJECTION",), "Adapt provenance."),
            AbsorptionDecision(
                "m:obstruction",
                AbsorptionDisposition.COMPOSE,
                ("P3.OBSTRUCTION.v1",),
                "Compose typed-coordinate non-merge certificates.",
            ),
        ),
        residual_implementation_evidence=(
            "papers/orion-13-global-knowledge-portrait/evidence/NEAREST_WORK_DISPOSITIONS_V1.md",
        ),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:obstruction-atlas",
            hypothesis="Typed non-merge certificates reduce false merges beyond sheaf obstruction baselines.",
            observation_if_novel="False-merge drop survives a sheaf/SCION baseline.",
            observation_if_already_solved="Sheaf obstruction already explains the confirmatory gain.",
            status="PROPOSED",
            result="",
        ),
    )


def adversarial_fixtures() -> tuple[CertificateDraft, ...]:
    return (
        new_terminology_for_old_mechanism_draft(),
        composition_of_knowns_draft(),
        broad_claim_narrow_residual_draft(),
    )
