from __future__ import annotations

from orion.knowledge.nearest_work import AbsorptionDecision, AbsorptionDisposition
from orion.novelty.certificate import (
    CertificateDraft,
    DiscriminatingExperiment,
    MechanismAtom,
    OverlapRecord,
    ScientificNoveltyCertificate,
    seal_certificate,
)
from orion.novelty.fixtures import documented_saturation, hostile_route, prior_work
from orion.novelty.types import MechanismOverlap, NoveltySearchRoute, SourceAccess

SNAPSHOT_DATE = "2026-08-17"


def _queries(**extra: tuple[str, ...]) -> dict[NoveltySearchRoute, tuple[str, ...]]:
    base = {
        NoveltySearchRoute.EXACT_TERM: extra.get("exact", ("documented exact-term audit",)),
        NoveltySearchRoute.SYNONYM_FUNCTION_ONLY: extra.get("function", ("documented function-only audit",)),
        NoveltySearchRoute.PROBLEM_DECOMPOSITION: extra.get("decomp", ("documented problem decomposition",)),
        NoveltySearchRoute.PARENT_DISCIPLINE_HISTORY: extra.get("parent", ("documented parent-discipline audit",)),
        NoveltySearchRoute.BENCHMARK_IMPLEMENTATION: extra.get("bench", ("documented benchmark/implementation audit",)),
        NoveltySearchRoute.CITED_BY_RELATED: extra.get("cited", ("documented cited-by/related-work audit",)),
        NoveltySearchRoute.HOSTILE_ALREADY_SOLVED: extra.get(
            "hostile",
            ("assume this is already solved — find it under parent-discipline vocabulary",),
        ),
    }
    return base


def _p1() -> CertificateDraft:
    diagnosability = prior_work(
        "arxiv:2509.04708",
        title="Bayesian Diagnosability and Active Fault Identification",
        mechanism_summary="Active inputs make undiagnosable faults distinguishable.",
    )
    arex = prior_work(
        "arxiv:2607.21461",
        title="AREX",
        mechanism_summary="Constraint-wise auditing of provisional answers and targeted follow-up.",
    )
    who_when = prior_work(
        "arxiv:2607.09996",
        title="Who&When Pro",
        mechanism_summary="Failure-attribution timing; full text not independently mapped this session.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    original = (
        "intervention-supported causal responsibility -> explicit permission over "
        "K/W/M mutation -> dependency-scoped reopening"
    )
    residual = (
        "diagnosability → active discriminator → responsibility-scoped permission "
        "to alter epistemic formulation/search-universe state"
    )
    return CertificateDraft(
        claim_id="orion:P1:#278",
        claim_text=original,
        problem_task_definition="P1 revival: license epistemic mutation only from intervention-backed responsibility.",
        claimed_mechanism_decomposition=(
            MechanismAtom("m:active-diagnosis", "Active diagnosability probes", "absorbed"),
            MechanismAtom("m:mutation-permission", "Responsibility-scoped K/W/M permission", "residual"),
        ),
        closest_prior_by_term=(arex, who_when),
        closest_prior_by_function=(diagnosability,),
        parent_discipline_mechanisms=(diagnosability,),
        benchmark_implementation_routes=(
            prior_work("github:orion/p1-v1", title="P1 V1 frozen suite", mechanism_summary="H1 null 1/48."),
        ),
        hostile_already_solved_route=hostile_route(
            findings=(diagnosability,),
            queries=(
                "assume already solved: active fault identification",
                "causal debugging change-impact authorization",
            ),
            residual_changed=True,
            note="Hostile parent-discipline search absorbed standalone active diagnosis.",
        ),
        overlap_classifications=(
            OverlapRecord(
                "m:active-diagnosis",
                "arxiv:2509.04708",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Active diagnosis is parent-discipline prior art.",
            ),
            OverlapRecord(
                "m:mutation-permission",
                "arxiv:2607.21461",
                MechanismOverlap.PARTIAL,
                "AREX audits answers; it does not bind diagnosis to typed epistemic mutation authority.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision(
                "m:active-diagnosis",
                AbsorptionDisposition.ADOPT,
                ("P1.DIAGNOSABILITY",),
                "Adopt Bayesian/active diagnosability; strike it from standalone novelty.",
            ),
            AbsorptionDecision(
                "m:mutation-permission",
                AbsorptionDisposition.COMPOSE,
                ("P1.LICENSING.v2",),
                "Compose responsibility-scoped permission; Who&When Pro/REFLECT/CAR unread in full.",
            ),
        ),
        original_claim_text=original,
        smallest_residual=residual,
        residual_implementation_evidence=(
            "research/paper-programme-v2/NEAREST_WORK_V2_AUDIT_2026-08-16.md",
        ),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:p1-responsibility-probe",
            hypothesis="Active probes convert 47/48 abstention into licensed mutations without false authority.",
            observation_if_novel="Responsibility-scoped permission improves H1 after diagnosis is identifiable.",
            observation_if_already_solved="AREX/Who&When already license the same mutations.",
            status="PROPOSED",
        ),
        unresolved_sources=("arxiv:2607.09996", "arxiv:2606.09071", "arxiv:2606.08275"),
        unresolved_search_routes=("Who&When Pro full text", "REFLECT full text", "Causal Agent Replay full text"),
        inaccessible_material_sources=("arxiv:2607.09996", "arxiv:2606.09071", "arxiv:2606.08275"),
        saturation=documented_saturation(
            _queries(
                exact=("causal epistemic responsibility", "intervention-backed responsibility licensing"),
                function=("agent failure localization", "active diagnosis", "change-impact authorization"),
                parent=("Bayesian diagnosability", "fault isolation", "adaptive testing"),
                hostile=("assume already solved: active fault identification licenses epistemic mutation",),
            )
        ),
        snapshot_date=SNAPSHOT_DATE,
    )


def _p2() -> CertificateDraft:
    bandit = prior_work(
        "arxiv:2412.06165",
        title="Conservative Contextual Bandits",
        mechanism_summary="Baseline-preserving exploration.",
    )
    arb = prior_work(
        "arxiv:2604.25256",
        title="AutoResearchBench",
        mechanism_summary="Wide+Deep literature discovery benchmark.",
    )
    original = (
        "A route may be exhausted, unavailable or censored without licensing global task closure; "
        "novelty is authority semantics under unknown coverage."
    )
    residual = (
        "earned route identity + censored provider unavailability + question-conditioned read "
        "state + non-authoritative route stopping"
    )
    return CertificateDraft(
        claim_id="orion:P2:#279",
        claim_text=original,
        problem_task_definition="P2 revival: stopping authority under censored open-world search.",
        claimed_mechanism_decomposition=(
            MechanismAtom("m:conservative-explore", "Conservative/safe exploration", "absorbed"),
            MechanismAtom("m:censored-stop", "Censored stopping without task-closure authority", "residual"),
        ),
        closest_prior_by_term=(arb,),
        closest_prior_by_function=(bandit,),
        parent_discipline_mechanisms=(
            prior_work(
                "arxiv:2002.00467",
                title="Safe Exploration for Optimizing Contextual Bandits",
                mechanism_summary="Safe exploration in information retrieval.",
            ),
        ),
        benchmark_implementation_routes=(arb,),
        hostile_already_solved_route=hostile_route(
            findings=(bandit,),
            queries=("assume already solved: conservative bandit literature search stopping",),
            residual_changed=True,
            note="Hostile search absorbed conservative exploration; censored-authority residual remains untested externally.",
        ),
        overlap_classifications=(
            OverlapRecord(
                "m:conservative-explore",
                "arxiv:2412.06165",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Conservative bandits/safe exploration are not novel.",
            ),
            OverlapRecord(
                "m:censored-stop",
                "arxiv:2604.25256",
                MechanismOverlap.PARTIAL,
                "ARB evaluates discovery; it does not separate route exhaustion from task-closure authority.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision(
                "m:conservative-explore",
                AbsorptionDisposition.ADAPT,
                ("P2.ALLOCATOR",),
                "Adapt conservative exploration; do not claim it as novelty.",
            ),
            AbsorptionDecision(
                "m:censored-stop",
                AbsorptionDisposition.COMPOSE,
                ("P2.ROUTE_STOP.v1",),
                "Compose censored stopping with earned route identity; Wide unexecuted.",
            ),
        ),
        original_claim_text=original,
        smallest_residual=residual,
        residual_implementation_evidence=("src/orion/knowledge/routes.py",),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:p2-wide",
            hypothesis="External Wide localizes failure to stopping vs candidate generation.",
            observation_if_novel="Censored stopping, not retrieval matching, carries any external gain.",
            observation_if_already_solved="Controlled-world construct validity explains the 390-task result.",
            status="PROPOSED",
        ),
        unresolved_sources=("arxiv:2603.00582", "autoresearchbench:wide-unexecuted"),
        unresolved_search_routes=("AutoResearchBench Wide official run", "Super Research full text"),
        inaccessible_material_sources=("arxiv:2603.00582", "autoresearchbench:wide-unexecuted"),
        saturation=documented_saturation(
            _queries(
                exact=("censored stopping authority", "route stop versus task stop"),
                function=("recall stopping", "retrieval censoring", "open set search stopping"),
                parent=("capture recapture", "conservative contextual bandits"),
                bench=("AutoResearchBench Wide", "SAGE", "AgentSLR", "MetaSyn"),
                hostile=("assume already solved: coverage estimator licenses task closure",),
            )
        ),
        snapshot_date=SNAPSHOT_DATE,
    )


def _p3() -> CertificateDraft:
    sheaf = prior_work(
        "arxiv:2605.14033",
        title="Sheaf-Theoretic Transport and Obstruction",
        mechanism_summary="Transport/gluing/obstruction for scientific representational change.",
    )
    muse = prior_work(
        "arxiv:2608.10974",
        title="MUSE",
        mechanism_summary="Source-grounded cross-domain structured knowledge.",
    )
    scion = prior_work(
        "arxiv:2607.21610",
        title="SCOPE/SCION",
        mechanism_summary="Evidence-linked conservative schema induction and fusion.",
    )
    original = (
        "provenance-bound scientific obstruction / non-merge certificates that explain why "
        "two source-local representations must not be globally identified"
    )
    residual = (
        "typed referent/construct/measurement/context hypotheses plus GLUE-or-obstruction "
        "with source-projection recoverability, after absorbing standalone obstruction and schema fusion"
    )
    return CertificateDraft(
        claim_id="orion:P3:#280",
        claim_text=original,
        problem_task_definition="P3 expansion: obstruction certificates vs forced canonicalization.",
        claimed_mechanism_decomposition=(
            MechanismAtom("m:obstruction", "Scientific obstruction", "absorbed-as-standalone"),
            MechanismAtom("m:typed-coords", "Typed scientific coordinates with recoverability", "residual"),
        ),
        closest_prior_by_term=(sheaf, muse),
        closest_prior_by_function=(sheaf, scion),
        parent_discipline_mechanisms=(
            prior_work(
                "arxiv:2601.04573",
                title="Partial-State Lenses",
                mechanism_summary="Bidirectional multiple-view update preservation.",
            ),
        ),
        benchmark_implementation_routes=(
            prior_work(
                "orion:p3-confirmatory",
                title="P3 public-reference confirmatory n=32",
                mechanism_summary="ORION false merge 0 vs flat 0.1875.",
            ),
        ),
        hostile_already_solved_route=hostile_route(
            findings=(sheaf,),
            queries=("assume already solved: sheaf obstruction scientific theory shift",),
            residual_changed=True,
            note="Hostile search absorbed standalone obstruction; typed-coordinate residual remains.",
        ),
        overlap_classifications=(
            OverlapRecord(
                "m:obstruction",
                "arxiv:2605.14033",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Standalone scientific obstruction is prior art.",
            ),
            OverlapRecord(
                "m:typed-coords",
                "arxiv:2607.21610",
                MechanismOverlap.PARTIAL,
                "SCION fuses schemas; it does not emit provenance-bound non-merge certificates.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision(
                "m:obstruction",
                AbsorptionDisposition.ADOPT,
                ("P3.OBSTRUCTION",),
                "Adopt sheaf/transport obstruction; strike standalone obstruction novelty.",
            ),
            AbsorptionDecision(
                "m:typed-coords",
                AbsorptionDisposition.COMPOSE,
                ("P3.COORDINATES.v1",),
                "Compose typed coordinates with obstruction certificates.",
            ),
        ),
        original_claim_text=original,
        smallest_residual=residual,
        residual_implementation_evidence=(
            "papers/orion-13-global-knowledge-portrait/evidence/NEAREST_WORK_DISPOSITIONS_V1.md",
        ),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:p3-coordinate-atlas",
            hypothesis="Typed non-merge certificates beat sheaf/SCION on coordinate-targeted holdout.",
            observation_if_novel="False-merge drop localizes to typed coordinates, not generic obstruction.",
            observation_if_already_solved="Sheaf obstruction already explains the confirmatory gain.",
            status="PROPOSED",
        ),
        unresolved_sources=(),
        unresolved_search_routes=("coordinate-targeted adversarial atlas execution",),
        inaccessible_material_sources=(),
        saturation=documented_saturation(
            _queries(
                exact=("scientific obstruction certificate", "non-merge provenance"),
                function=("schema fusion", "ontology alignment", "transportability"),
                parent=("sheaf obstruction", "partial-state lenses", "measurement harmonization"),
                bench=("P3 public-reference confirmatory", "SciER", "SCOPE/SCION"),
                hostile=("assume already solved: sheaf-theoretic scientific obstruction",),
            )
        ),
        snapshot_date=SNAPSHOT_DATE,
    )


def _p4() -> CertificateDraft:
    pca = prior_work(
        "arxiv:2606.04104",
        title="Proof-Carrying Agent Actions",
        mechanism_summary="Certificate-bearing action governance.",
    )
    defeaters = prior_work(
        "arxiv:2606.11462",
        title="Defeater Cards",
        mechanism_summary="Assurance-case defeaters.",
    )
    fire = prior_work(
        "FIRE",
        title="FIRE",
        mechanism_summary="Iterative retrieve-or-verify control.",
    )
    original = "defeater-directed protected evidence acquisition under a non-escalating scientific-authority lattice"
    residual = (
        "protected defeater-directed evidence ordering under an unchanged P4 authority lattice "
        "that may AUTHORIZE, GATHER, or BLOCK/CANNOT_CHECK, never self-granting authority"
    )
    return CertificateDraft(
        claim_id="orion:P4:#281",
        claim_text=original,
        problem_task_definition="P4 H3 follow-up: which protected evidence to acquire next.",
        claimed_mechanism_decomposition=(
            MechanismAtom("m:proof-carrying", "Proof-carrying / defeater representation", "absorbed"),
            MechanismAtom("m:acquisition", "Defeater-directed protected acquisition", "residual"),
        ),
        closest_prior_by_term=(pca, defeaters),
        closest_prior_by_function=(fire, defeaters),
        parent_discipline_mechanisms=(
            prior_work(
                "arxiv:2411.03291",
                title="Assurance cases",
                mechanism_summary="Explicit assurance arguments guide required evidence.",
            ),
        ),
        benchmark_implementation_routes=(
            prior_work(
                "orion:p4-v2",
                title="P4 protected authority V2",
                mechanism_summary="H1 0/360 false promotions; H3 null preserved.",
            ),
        ),
        hostile_already_solved_route=hostile_route(
            findings=(pca, defeaters),
            queries=("assume already solved: proof-carrying evidence acquisition",),
            residual_changed=True,
            note="Hostile search absorbed proof-carrying/defeaters; acquisition-under-lattice residual remains.",
        ),
        overlap_classifications=(
            OverlapRecord(
                "m:proof-carrying",
                "arxiv:2606.04104",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Proof-carrying authority is not novel.",
            ),
            OverlapRecord(
                "m:acquisition",
                "FIRE",
                MechanismOverlap.PARTIAL,
                "FIRE iterates retrieve-or-verify; it does not sit under P4's non-escalating lattice.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision(
                "m:proof-carrying",
                AbsorptionDisposition.ADAPT,
                ("P4.AUTHORITY",),
                "Adapt proof-carrying/defeaters; do not claim them as novelty.",
            ),
            AbsorptionDecision(
                "m:acquisition",
                AbsorptionDisposition.COMPOSE,
                ("P4.ACQUISITION.v1",),
                "Compose defeater-directed acquisition under frozen P4 custody.",
            ),
        ),
        original_claim_text=original,
        smallest_residual=residual,
        residual_implementation_evidence=("src/orion/transfer/defeaters.py",),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:p4-h3-acquisition",
            hypothesis="Defeater-directed acquisition reduces unresolved critical risk without extra false promotions.",
            observation_if_novel="H3-class tasks separate from FIRE/proof-carrying baselines.",
            observation_if_already_solved="FIRE already chooses the next evidence item equivalently.",
            status="PROPOSED",
        ),
        unresolved_sources=(),
        unresolved_search_routes=("P4 H3 follow-up execution",),
        inaccessible_material_sources=(),
        saturation=documented_saturation(
            _queries(
                exact=("protected evidence acquisition", "defeater-directed verification"),
                function=("value of information", "assurance-guided evidence", "iterative retrieve or verify"),
                parent=("assurance cases", "proof-carrying code", "defeater cards"),
                bench=("P4 V2 hostile battery", "ProvenanceGuard", "CLAIM-BENCH"),
                hostile=("assume already solved: proof-carrying agent actions plus FIRE",),
            )
        ),
        snapshot_date=SNAPSHOT_DATE,
    )


def _p5() -> CertificateDraft:
    dgm = prior_work(
        "arxiv:2505.22954",
        title="Darwin Gödel Machine",
        mechanism_summary="Self-code modification, archive, sandbox, empirical validation.",
    )
    pace = prior_work(
        "arxiv:2606.08106",
        title="PACE",
        mechanism_summary="Anytime-valid acceptance tests for self-evolving agents.",
    )
    adias = prior_work(
        "arxiv:2608.06410",
        title="ADIAS",
        mechanism_summary="Persistent issue-centric self-improvement.",
    )
    original = (
        "causally supported repair decisions that survive independent fresh transfer and "
        "protected assurance, while harmful/null variants remain immutable and cannot be averaged away"
    )
    residual = (
        "STATIC → REPLAY → FRESH → PROTECTED with known harm dominating missing stages, "
        "append-only negative history, evaluator custody, and host-only promotion"
    )
    return CertificateDraft(
        claim_id="orion:P5:#282",
        claim_text=original,
        problem_task_definition="P5 revival: non-compensatory protected self-improvement.",
        claimed_mechanism_decomposition=(
            MechanismAtom("m:self-edit", "Archive/sandbox self-edit", "absorbed"),
            MechanismAtom("m:issue-state", "Persistent issue state", "absorbed"),
            MechanismAtom("m:noncompensatory", "Non-compensatory protected admission", "residual"),
        ),
        closest_prior_by_term=(adias, dgm),
        closest_prior_by_function=(pace, dgm),
        parent_discipline_mechanisms=(
            prior_work(
                "arxiv:2606.29713",
                title="SEVA",
                mechanism_summary="Self-evolution can create benchmark specialists with regression.",
            ),
        ),
        benchmark_implementation_routes=(
            prior_work(
                "orion:p5-glm52",
                title="P5 GLM-5.2 attribution",
                mechanism_summary="Honest 21/24 attribution; three adjacent-level errors.",
            ),
        ),
        hostile_already_solved_route=hostile_route(
            findings=(pace, adias, dgm),
            queries=("assume already solved: anytime-valid self-evolution certificates plus ADIAS",),
            residual_changed=True,
            note="Hostile search absorbed components; non-compensatory composition remains the residual.",
        ),
        overlap_classifications=(
            OverlapRecord(
                "m:self-edit",
                "arxiv:2505.22954",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Self-edit/archive/sandbox is prior art.",
            ),
            OverlapRecord(
                "m:issue-state",
                "arxiv:2608.06410",
                MechanismOverlap.IDENTICAL,
                "Persistent issue-centric optimization is ADIAS.",
            ),
            OverlapRecord(
                "m:noncompensatory",
                "arxiv:2606.08106",
                MechanismOverlap.PARTIAL,
                "PACE constrains false commits; it does not encode ORION's four-stage non-compensatory lattice.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision("m:self-edit", AbsorptionDisposition.ADAPT, ("P5.ARCHIVE",), "Adapt DGM self-edit."),
            AbsorptionDecision("m:issue-state", AbsorptionDisposition.ADOPT, ("P5.ISSUE",), "Adopt ADIAS issue state."),
            AbsorptionDecision(
                "m:noncompensatory",
                AbsorptionDisposition.COMPOSE,
                ("P5.ADMISSION.v1",),
                "Compose non-compensatory replay/fresh/protected gates.",
            ),
        ),
        original_claim_text=original,
        smallest_residual=residual,
        residual_implementation_evidence=("research/paper-programme-v1/P5_NEAREST_WORK_CLOSURE_2026-08-16.md",),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:p5-fresh-transfer",
            hypothesis="Non-compensatory gates reduce harmful transfer vs PACE/DGM under matched budgets.",
            observation_if_novel="Fresh/harm metrics improve without replay-only compensation.",
            observation_if_already_solved="PACE/SEA already enforce the same non-compensation.",
            status="PROPOSED",
        ),
        unresolved_sources=(),
        unresolved_search_routes=("hidden-cause fresh-transfer campaign",),
        inaccessible_material_sources=(),
        saturation=documented_saturation(
            _queries(
                exact=("non-compensatory protected self-improvement", "fresh transfer self-evolution"),
                function=("self-evolution regression", "evaluator overfitting", "negative transfer"),
                parent=("program repair", "continual learning", "anytime-valid testing"),
                bench=("PAST-Bench", "SEVA", "EvoAgentBench", "PACE", "SEA"),
                hostile=("assume already solved: PACE + ADIAS + DGM composition",),
            )
        ),
        snapshot_date=SNAPSHOT_DATE,
    )


def _gp() -> CertificateDraft:
    evo = prior_work(
        "arxiv:2606.03678",
        title="EvoDrive",
        mechanism_summary="Pareto archives preserve multi-objective trade-offs in driving.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    compound = prior_work(
        "arxiv:2607.14004",
        title="Do Agent Optimizers Compound?",
        mechanism_summary="Regression-controlled optimization compounds; others do not.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    original = (
        "protected, evidence-bound, non-compensatory Pareto admission of research/self-improvement "
        "changes across heterogeneous epistemic task families, with immutable negative history and no self-certification"
    )
    return CertificateDraft(
        claim_id="orion:GP:#285",
        claim_text=original,
        problem_task_definition="Globally positive ORION change under protected non-regression.",
        claimed_mechanism_decomposition=(
            MechanismAtom("m:pareto", "Pareto archive admission", "absorbed-family"),
            MechanismAtom("m:protected-global", "Protected non-compensatory global positivity", "residual"),
        ),
        closest_prior_by_term=(evo, compound),
        closest_prior_by_function=(compound,),
        parent_discipline_mechanisms=(
            prior_work(
                "safe-policy-improvement",
                title="Safe / conservative policy improvement",
                mechanism_summary="Non-regression constraints on policy updates.",
            ),
        ),
        benchmark_implementation_routes=(
            prior_work(
                "arxiv:2604.20087",
                title="SkillLearnBench",
                mechanism_summary="Continual skill learning does not lead on all tasks/LLMs.",
                access=SourceAccess.ABSTRACT_ONLY,
            ),
        ),
        hostile_already_solved_route=hostile_route(
            findings=(evo, compound),
            queries=("assume already solved: Pareto archive plus regression-controlled agent optimization",),
            residual_changed=True,
            note="Hostile search found Pareto archives and regression-controlled optimizers; full texts unread.",
        ),
        overlap_classifications=(
            OverlapRecord(
                "m:pareto",
                "arxiv:2606.03678",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Pareto archives are not novel.",
            ),
            OverlapRecord(
                "m:protected-global",
                "arxiv:2607.14004",
                MechanismOverlap.UNRESOLVED,
                "Regression-controlled compounding may already encode non-compensatory admission; full text unread.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision("m:pareto", AbsorptionDisposition.ADAPT, ("GP.ARCHIVE",), "Adapt Pareto archives."),
            AbsorptionDecision(
                "m:protected-global",
                AbsorptionDisposition.DEFER,
                (),
                "Defer until EvoDrive/compounding papers are independently full-text mapped.",
            ),
        ),
        original_claim_text=original,
        smallest_residual=original,
        residual_implementation_evidence=(),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:gp-cross-domain",
            hypothesis="Protected Pareto admission beats scalar/replay-only acceptance on fresh cross-domain harm.",
            observation_if_novel="Fewer hidden regressions at matched improvement rate.",
            observation_if_already_solved="Regression-controlled optimizers already satisfy the certificate.",
            status="PROPOSED",
        ),
        unresolved_sources=("arxiv:2606.03678", "arxiv:2607.14004", "arxiv:2604.20087"),
        unresolved_search_routes=("full-text mapping of Pareto/continual-optimizer cluster",),
        inaccessible_material_sources=("arxiv:2606.03678", "arxiv:2607.14004"),
        saturation=documented_saturation(
            _queries(
                exact=("global positive certificate", "protected Pareto admission"),
                function=("non-regression", "safe policy improvement", "catastrophic forgetting"),
                parent=("Pareto optimization", "change-impact analysis", "safety cases"),
                hostile=("assume already solved: EvoDrive Pareto archive plus compounding optimizers",),
            )
        ),
        snapshot_date=SNAPSHOT_DATE,
    )


def _tx() -> CertificateDraft:
    mtl = prior_work(
        "arxiv:2604.14004",
        title="Memory Transfer Learning",
        mechanism_summary="High-level meta-knowledge transfers; low-level traces often cause negative transfer.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    agentcl = prior_work(
        "arxiv:2606.02461",
        title="AGENTCL",
        mechanism_summary="Held-out settings can expose memory-induced degradation.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    original = (
        "content-addressed transfer of explicit mechanic contracts (obligations, assumptions, "
        "failure modes, verification hooks and authority boundaries), admitted only when source "
        "and target problem signatures satisfy frozen transfer conditions"
    )
    return CertificateDraft(
        claim_id="orion:TX:#286",
        claim_text=original,
        problem_task_definition="Cross-domain mechanic-cell transfer without negative transfer.",
        claimed_mechanism_decomposition=(
            MechanismAtom("m:memory-transfer", "Abstract insight / memory transfer", "absorbed-family"),
            MechanismAtom("m:mechanic-contract", "Contract-bound mechanic-cell transfer", "residual"),
        ),
        closest_prior_by_term=(mtl,),
        closest_prior_by_function=(mtl, agentcl),
        parent_discipline_mechanisms=(
            prior_work(
                "arxiv:2604.27003",
                title="When Continual Learning Moves to Memory",
                mechanism_summary="External memory relocates the stability-plasticity problem.",
                access=SourceAccess.ABSTRACT_ONLY,
            ),
        ),
        benchmark_implementation_routes=(
            prior_work(
                "arxiv:2604.20087",
                title="SkillLearnBench",
                mechanism_summary="Continual skill-learning gains are inconsistent.",
                access=SourceAccess.ABSTRACT_ONLY,
            ),
        ),
        hostile_already_solved_route=hostile_route(
            findings=(mtl,),
            queries=("assume already solved: abstract insight transfer of mechanic contracts",),
            residual_changed=True,
            note="Hostile search recovered high-level memory transfer; whether contracts are distinct is unread.",
        ),
        overlap_classifications=(
            OverlapRecord(
                "m:memory-transfer",
                "arxiv:2604.14004",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "High-level transfer vs trace transfer is already reported.",
            ),
            OverlapRecord(
                "m:mechanic-contract",
                "arxiv:2604.14004",
                MechanismOverlap.UNRESOLVED,
                "Mechanic-contract objects may be a species of abstract insight; full text unread.",
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision(
                "m:memory-transfer",
                AbsorptionDisposition.ADAPT,
                ("TX.MEMORY",),
                "Adapt high-level transfer; do not claim memory transfer as novelty.",
            ),
            AbsorptionDecision(
                "m:mechanic-contract",
                AbsorptionDisposition.DEFER,
                (),
                "Defer until MTL/AGENTCL full texts are mapped against mechanic-cell contracts.",
            ),
        ),
        original_claim_text=original,
        smallest_residual=original,
        residual_implementation_evidence=("src/orion/transfer/types.py",),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:tx-mechanic-cell",
            hypothesis="Mechanic-contract transfer reduces negative transfer vs insight/trajectory memory.",
            observation_if_novel="Held-out target improves without near-miss harm.",
            observation_if_already_solved="MTL-style abstract insights already transfer the same content.",
            status="PROPOSED",
        ),
        unresolved_sources=("arxiv:2604.14004", "arxiv:2606.02461"),
        unresolved_search_routes=("full-text mapping of memory-transfer cluster", "paired source-target episodes"),
        inaccessible_material_sources=("arxiv:2604.14004", "arxiv:2606.02461"),
        saturation=documented_saturation(
            _queries(
                exact=("mechanic-cell transfer", "contract-bound transfer"),
                function=("negative transfer", "procedural memory transfer", "skill transfer"),
                parent=("algorithm selection", "case-based reasoning", "transfer learning"),
                hostile=("assume already solved: memory transfer of abstract mechanic knowledge",),
            )
        ),
        snapshot_date=SNAPSHOT_DATE,
    )


def _nov() -> CertificateDraft:
    """#287's own claim, run through #287's own mechanism.

    The certificate machinery had been applied to seven other claims and never to
    itself, which is the one application where a novelty checker's result is also
    a test of the checker. Searched 2026-08-18 against live literature rather than
    the in-tree audits the other drafts reuse, because no in-tree nearest-work
    audit exists for novelty assessment itself.
    """

    rinobench = prior_work(
        "arxiv:2603.10303",
        title="Is this Idea Novel? An Automated Benchmark for Judgment of Research Ideas",
        mechanism_summary="Benchmarks automated novelty judgment of research ideas against expert labels.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    judge_limits = prior_work(
        "arxiv:2606.12071",
        title="On the Limits of LLM-as-Judge for Scientific Novelty Assessment",
        mechanism_summary=(
            "Documents that LLM novelty verdicts diverge from expert gold even when the "
            "rationale reads as human-like."
        ),
        access=SourceAccess.ABSTRACT_ONLY,
    )
    axiomatic = prior_work(
        "arxiv:2604.15145",
        title="An Axiomatic Benchmark for Evaluating Scientific Novelty Metrics",
        mechanism_summary="Evaluates novelty metrics against axioms and expert labels rather than model opinion.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    novbench = prior_work(
        "arxiv:2604.11543",
        title="NovBench: Evaluating Large Language Models on Academic Paper Novelty Assessment",
        mechanism_summary="Benchmarks LLM novelty assessment of full papers.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    screening_stop = prior_work(
        "doi:10.1186/s13643-020-01521-4",
        title="Statistical stopping criteria for automated screening in systematic reviews",
        mechanism_summary=(
            "Parent discipline: decides when a literature search may stop, with an explicit "
            "statistical criterion rather than a judgement call."
        ),
        access=SourceAccess.ABSTRACT_ONLY,
    )
    poisson_stop = prior_work(
        "arxiv:1909.06239",
        title="Modelling Stopping Criteria for Search Results using Poisson Processes",
        mechanism_summary="Parent discipline: models search-result exhaustion to time a stopping decision.",
        access=SourceAccess.ABSTRACT_ONLY,
    )
    original = (
        "verifiable scientific novelty certificates whose final state is computed only from an "
        "executed hostile already-solved route, route completeness, source accessibility, overlap "
        "absorption and claim shrinkage, with an LLM novelty score recordable but structurally "
        "unable to set the state, and CANNOT_CHECK mandatory when any of those is open"
    )
    residual = (
        "mandatory CANNOT_CHECK as a first-class novelty terminal, computed from route completeness "
        "and source accessibility rather than from a score"
    )
    return CertificateDraft(
        claim_id="orion:NOV:#287",
        claim_text=original,
        problem_task_definition=(
            "Assess the novelty of a scientific claim without letting a model's novelty opinion "
            "determine the verdict."
        ),
        claimed_mechanism_decomposition=(
            MechanismAtom("m:evidence-grounded-novelty", "Novelty judged against retrieved evidence", "absorbed-family"),
            MechanismAtom("m:llm-judge-distrust", "LLM novelty score cannot set the final state", "absorbed-family"),
            MechanismAtom("m:mandatory-cannot-check", "Abstention forced by route/accessibility state", "residual"),
        ),
        closest_prior_by_term=(rinobench, novbench, axiomatic),
        closest_prior_by_function=(judge_limits, rinobench),
        parent_discipline_mechanisms=(screening_stop, poisson_stop),
        benchmark_implementation_routes=(rinobench, novbench, axiomatic),
        hostile_already_solved_route=hostile_route(
            findings=(judge_limits, rinobench, axiomatic),
            queries=(
                "assume already solved: automated novelty assessment grounded in retrieved evidence",
                "assume already solved: benchmark showing LLM novelty judges disagree with experts",
            ),
            residual_changed=True,
            note=(
                "The hostile route recovered the two load-bearing parts of the claim. That LLM novelty "
                "verdicts are unreliable is documented (2606.12071); grounding novelty in retrieved "
                "evidence rather than model opinion is the stated motivation of the benchmark cluster. "
                "Neither is ORION's to claim."
            ),
        ),
        overlap_classifications=(
            OverlapRecord(
                "m:evidence-grounded-novelty",
                "arxiv:2603.10303",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Grounding novelty judgment in retrieved evidence is the benchmark cluster's own premise.",
            ),
            OverlapRecord(
                "m:llm-judge-distrust",
                "arxiv:2606.12071",
                MechanismOverlap.FUNCTIONAL_EQUIVALENT,
                "Distrust of LLM novelty verdicts is the finding of this work, not a consequence of ORION's design.",
            ),
            OverlapRecord(
                "m:mandatory-cannot-check",
                "arxiv:2604.15145",
                MechanismOverlap.UNRESOLVED,
                (
                    "Axiomatic evaluation scores metrics; whether any of these systems emits a "
                    "structurally-forced abstention rather than a low score is unread. The search "
                    "surfaced no work on abstention as a novelty terminal."
                ),
            ),
        ),
        absorption_decisions=(
            AbsorptionDecision(
                "m:evidence-grounded-novelty",
                AbsorptionDisposition.ADOPT,
                ("NOV.EVIDENCE",),
                "Adopt evidence-grounded novelty; strike it from ORION's novelty claim.",
            ),
            AbsorptionDecision(
                "m:llm-judge-distrust",
                AbsorptionDisposition.ADOPT,
                ("NOV.AUTHORITY",),
                "Adopt the documented unreliability of LLM novelty judges; ORION did not discover it.",
            ),
            AbsorptionDecision(
                "m:mandatory-cannot-check",
                AbsorptionDisposition.DEFER,
                (),
                "Defer until the benchmark cluster's full texts are read for a forced-abstention terminal.",
            ),
        ),
        original_claim_text=original,
        smallest_residual=residual,
        residual_implementation_evidence=(
            "src/orion/novelty/certificate.py",
            "src/orion/novelty/saturation.py",
        ),
        discriminating_experiment=DiscriminatingExperiment(
            experiment_id="exp:nov-forced-abstention",
            hypothesis=(
                "On claims whose nearest work is inaccessible, ORION's certificate abstains where "
                "score-based novelty metrics return a confident value."
            ),
            observation_if_novel="Score-based metrics rate the claim while ORION returns CANNOT_CHECK.",
            observation_if_already_solved=(
                "RINoBench or the axiomatic benchmark already emits an insufficient-evidence verdict "
                "on the same claims."
            ),
            status="PROPOSED",
        ),
        unresolved_sources=(
            "arxiv:2603.10303",
            "arxiv:2606.12071",
            "arxiv:2604.15145",
            "arxiv:2604.11543",
        ),
        unresolved_search_routes=(
            "full-text read of the novelty-benchmark cluster for a forced-abstention terminal",
            "OpenNovelty / GraphMind system behaviour under insufficient retrieved evidence",
        ),
        inaccessible_material_sources=(
            "arxiv:2603.10303",
            "arxiv:2606.12071",
            "arxiv:2604.15145",
            "arxiv:2604.11543",
        ),
        saturation=documented_saturation(
            _queries(
                exact=("scientific novelty certificate", "verifiable novelty assessment"),
                function=("LLM-as-judge novelty", "evidence-grounded novelty report", "novelty metric benchmark"),
                decomp=("novelty verdict authority", "who sets the novelty state"),
                parent=(
                    "systematic review stopping criteria",
                    "search saturation",
                    "selective prediction abstention",
                ),
                bench=("RINoBench", "NovBench", "axiomatic novelty benchmark"),
                hostile=("assume already solved: automated novelty assessment grounded in retrieved evidence",),
            )
        ),
        snapshot_date="2026-08-18",
    )


def apply_orion_residuals() -> tuple[ScientificNoveltyCertificate, ...]:
    return tuple(
        seal_certificate(draft)
        for draft in (_p1(), _p2(), _p3(), _p4(), _p5(), _gp(), _tx(), _nov())
    )
