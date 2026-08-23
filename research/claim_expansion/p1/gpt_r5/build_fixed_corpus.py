from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROTOCOL = json.loads((ROOT.parent / "gpt_r2" / "PROTOCOL_V1.json").read_text())
PROBE_TO_CLASS = dict(PROTOCOL["probes"])
CLASS_TO_PROBE = {v: k for k, v in PROBE_TO_CLASS.items()}
ALL_PROBES = tuple(PROBE_TO_CLASS)
CONTROL = "NO_HIGH_LEVEL_REFORMULATION"
UNRESOLVED = "UNRESOLVED"

#: The year every episode is stamped with, read from the frozen source set
#: rather than written here. It was the literal ``2020`` in two places, which is
#: how the corpus and the evaluator that checks it came to disagree with the
#: only file that declares what the primary year is.
PRIMARY_YEAR = int(json.loads((ROOT / "FIXED_SOURCE_SET_V1.json").read_text())["primary_year"])


def probe_map(*, support: tuple[str, ...] = (), refute: tuple[str, ...] = ()) -> dict[str, str]:
    out = {p: "INCONCLUSIVE" for p in ALL_PROBES}
    for cls in support:
        out[CLASS_TO_PROBE[cls]] = "SUPPORT"
    for cls in refute:
        out[CLASS_TO_PROBE[cls]] = "REFUTE"
    return out


def doi_url(source_id: str) -> str:
    if source_id.startswith("doi:"):
        return "https://doi.org/" + source_id[4:]
    if source_id.startswith("arxiv:"):
        return "https://arxiv.org/abs/" + source_id[6:]
    if source_id.startswith("pmlr:"):
        return "https://proceedings.mlr.press/v119/ma20c.html"
    raise ValueError(source_id)


PAIR_SPECS = [
    dict(query_id="SEARCH-P1", cls="SEARCH_OR_EVIDENCE", domain="meta_analysis", source_id="doi:10.1111/biom.13238",
         adverse="A random-effects meta-analysis uses study summaries from studies with modest participant counts. Individual participant records exist, while the inferential model, estimand, and study collection are otherwise unchanged.",
         control="The same random-effects setting has sufficiently large per-study samples and maximum-likelihood summaries under Gaussian random effects; no scientific objective or population boundary is changed.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("SEARCH_OR_EVIDENCE","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The source shows asymptotic equivalence of summary and individual-data inference, but appreciable summary-data efficiency loss when sample sizes are not sufficiently large."),
    dict(query_id="SEARCH-P2", cls="SEARCH_OR_EVIDENCE", domain="wildlife_ecology", source_id="doi:10.1002/ecy.3030",
         adverse="A spatial capture–recapture population study has sparse detections, imperfect individual identification, and low detection probability while several observation processes are available for the same population.",
         control="The same population-monitoring framework operates in a regime with better detection and more attributable detections, reducing the incremental value of adding observation processes without changing the ecological target.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("SEARCH_OR_EVIDENCE","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The study contrasts integrated multi-source SCR with subsets and reports greatest gains where detection is low and detections cannot be assigned to individuals."),
    dict(query_id="SEARCH-P3", cls="SEARCH_OR_EVIDENCE", domain="neuroimaging_ml", source_id="doi:10.1038/s41467-020-18037-z",
         adverse="Predictive models are compared on the same target while training size is limited enough that exploitable nonlinear structure may not yet be accessible; model families and imaging variables are otherwise fixed.",
         control="The same prediction task is evaluated across much larger training samples, allowing performance scaling to be assessed without changing the scientific prediction target or data representation family.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("SEARCH_OR_EVIDENCE","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The source systematically varies sample size and shows performance depends strongly on whether useful nonlinearities are accessible at the available sample size."),
    dict(query_id="SEARCH-P4", cls="SEARCH_OR_EVIDENCE", domain="epidemiology_missing_data", source_id="doi:10.1093/aje/kwaa124",
         adverse="An epidemiologic analysis drops records with missing values under a causal missingness structure where restricting to complete cases can distort the intended association; the estimand and scientific question remain fixed.",
         control="The same complete-case analysis is considered under a missingness structure satisfying conditions that preserve the target association, with no need to change the scientific objective or population boundary.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("SEARCH_OR_EVIDENCE","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The paper gives causal conditions under which complete-case analysis is valid and contrasting structures under which it is biased."),

    dict(query_id="REP-P1", cls="REPRESENTATION_OR_INTERFACE", domain="biostatistics_transformations", source_id="doi:10.1002/sim.8425",
         adverse="The same continuous outcome is analyzed under a distributional regime where the working transformation poorly matches the data geometry; sample, scientific endpoint, and fitted task are held fixed.",
         control="The same outcome-modeling task is evaluated in a regime where the transformation family fits the data-generating shape adequately, without changing the underlying scientific endpoint.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("REPRESENTATION_OR_INTERFACE","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The empirical comparison studies transformation-model performance across different distributional regimes while retaining the same modeling objective."),
    dict(query_id="REP-P2", cls="REPRESENTATION_OR_INTERFACE", domain="geodesy", source_id="doi:10.2478/bgeo-2020-0008",
         adverse="Coordinates from a local geodetic system are transformed in parts of the network where transformation parameters yield severely deteriorated positions despite the same physical locations and surveying objective.",
         control="The same transformation services are evaluated on West Bank network points where transformed coordinates are mutually consistent with the registered geodetic network.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("REPRESENTATION_OR_INTERFACE","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The study reports consistent transformation performance in the West Bank but extreme coordinate deterioration in Gaza and farther portions of the grid extent."),
    dict(query_id="REP-P3", cls="REPRESENTATION_OR_INTERFACE", domain="knowledge_graphs", source_id="doi:10.1155/2020/4741963",
         adverse="A knowledge-graph prediction task has sparse labeled triples and long-tail entities that are poorly served by directly trained conventional supervised embeddings, while abundant unlabeled entity text exists.",
         control="The same knowledge-representation task is considered where labeled structured data are sufficiently available for conventional supervised representations, leaving the scientific task itself unchanged.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("REPRESENTATION_OR_INTERFACE","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The paper projects pretrained entity-name vectors into a task-specific subspace and reports its advantage especially with relatively little labeled data and zero-shot entities."),
    dict(query_id="REP-P4", cls="REPRESENTATION_OR_INTERFACE", domain="structural_biology_data_integration", source_id="doi:10.1109/TCBB.2019.2913368",
         adverse="Commercial protein-crystallization screens encode equivalent chemicals and conditions with inconsistent schemas and naming conventions, making automated cross-screen analysis difficult for the same crystallization objective.",
         control="The same crystallization-screen content is represented after schema matching and consistent expert-preferred chemical naming, allowing formats to be mapped without changing the experimental objective.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("REPRESENTATION_OR_INTERFACE","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The study identifies inconsistent schema/naming as the integration obstacle and reports 97% schema-matching accuracy with transformation to a consistent user-defined representation."),

    dict(query_id="IMPL-P1", cls="IMPLEMENTATION_OR_ENVIRONMENT", domain="software_engineering", source_id="doi:10.1007/s10664-020-09888-7",
         adverse="A published software-engineering study artifact contains an implementation/reporting defect serious enough to require an official publisher correction while the research question itself is unchanged.",
         control="The corrected publication/artifact represents the same research question after the implementation/reporting defect is repaired, without changing the scientific objective or problem boundary.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("IMPLEMENTATION_OR_ENVIRONMENT","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The fixed source is the publisher correction to the same study, providing an adverse-versus-corrected artifact pair without changing its scientific target."),
    dict(query_id="IMPL-P2", cls="IMPLEMENTATION_OR_ENVIRONMENT", domain="climate_numerics", source_id="doi:10.1029/2020MS002246",
         adverse="A shallow-water weather/climate simulation is naively converted to 16-bit arithmetic and develops intolerable rounding errors, stalled dynamics, or instability under the same physical model and initial conditions.",
         control="The same shallow-water model uses suitable number formats and mitigation such as rescaling, reordering, or mixed precision, making 16-bit calculations successful without changing the physical scientific target.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("IMPLEMENTATION_OR_ENVIRONMENT","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The source directly contrasts naive low precision, which degrades simulations, with mitigated low-precision implementations that remain usable."),
    dict(query_id="IMPL-P3", cls="IMPLEMENTATION_OR_ENVIRONMENT", domain="climate_modeling", source_id="doi:10.5194/gmd-13-139-2020",
         adverse="The same coupled climate model is executed on different machines and shows short-run platform-dependent trajectory differences, despite a shared scientific configuration and experimental question.",
         control="Long coupled simulations using the same model/configuration are compared statistically across machines and yield indistinguishable climate distributions despite divergent trajectories.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("IMPLEMENTATION_OR_ENVIRONMENT","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The source separates machine-dependent bitwise/trajectory divergence from long-term climate reproducibility under the same coupled model."),
    dict(query_id="IMPL-P4", cls="IMPLEMENTATION_OR_ENVIRONMENT", domain="single_cell_genomics", source_id="doi:10.1038/s41467-020-17800-6",
         adverse="Single-cell long-read transcript records contain sequencing and barcode/UMI assignment errors that impair cell and transcript identification while the underlying biological profiling objective is unchanged.",
         control="The same sequencing workflow applies its error-correction and high-throughput assignment procedure to the same biological profiling target, improving usable transcript and cell information.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("IMPLEMENTATION_OR_ENVIRONMENT","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The source presents an error-corrected Nanopore single-cell transcriptome workflow and compares correction/assignment against uncorrected long-read limitations."),

    dict(query_id="MEAS-P1", cls="MEASUREMENT_OR_EVALUATOR", domain="microbiology_measurement", source_id="doi:10.1038/s42003-020-01127-5",
         adverse="Laboratories estimate bacterial culture density from optical-density readings produced by different instruments without a common calibration, so nominally similar readings are not directly comparable.",
         control="The same culture-density objective uses a silica-microsphere calibration protocol across instruments, producing a common cell-count scale and explicit quality-control range.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("MEASUREMENT_OR_EVALUATOR","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="Across 244 laboratories the paper states OD cannot be compared across instruments without calibration and demonstrates a precise standardized calibration."),
    dict(query_id="MEAS-P3", cls="MEASUREMENT_OR_EVALUATOR", domain="neuroimaging_measurement", source_id="doi:10.1117/1.NPh.7.3.035009",
         adverse="A task-evoked optical brain signal is analyzed while systemic cardiac, respiratory, and blood-pressure fluctuations contaminate the measured channel response.",
         control="The same task/signal setting uses short-separation regressors or the best available correction method to remove systemic physiological contribution while retaining the brain-activity objective.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("MEASUREMENT_OR_EVALUATOR","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The study quantitatively compares correction methods and reports short-separation regression as the best-performing method for separating systemic physiological signal from task response."),
    dict(query_id="MEAS-P4", cls="MEASUREMENT_OR_EVALUATOR", domain="scientometrics", source_id="doi:10.1016/j.joi.2019.101005",
         adverse="Citation-ranking algorithms are evaluated against milestone items using conventional retrieval metrics whose scores are confounded by interactions between item age and metric age bias.",
         control="The same ranking algorithms and citation datasets are evaluated with a procedure that explicitly penalizes age bias, revealing consistent performance patterns without changing the ranking objective.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"), control_refutes=("MEASUREMENT_OR_EVALUATOR","OBJECTIVE_OR_MODEL_CLASS","PROBLEM_BOUNDARY"),
         evidence="The source shows traditional evaluation outcomes are skewed by age bias and that bias-penalized evaluation recovers consistent metric rankings across datasets."),

    dict(query_id="OBJ-P1", cls="OBJECTIVE_OR_MODEL_CLASS", domain="behavioral_modeling", source_id="doi:10.1016/j.jbusres.2020.03.019",
         adverse="Several structural explanations fit the same behavioral data closely enough that choosing a single path model from raw information-criterion differences can create false confidence about the data-generating structure.",
         control="In simulation conditions where a correctly specified structural model is distinguishable from incorrect alternatives, the same model-comparison task can identify the adequate model without changing data access or study scope.",
         adverse_refutes=("SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","MEASUREMENT_OR_EVALUATOR","PROBLEM_BOUNDARY"), control_refutes=("OBJECTIVE_OR_MODEL_CLASS","SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","MEASUREMENT_OR_EVALUATOR","PROBLEM_BOUNDARY"),
         evidence="The study evaluates correctly versus incorrectly specified PLS-SEM models and model-selection uncertainty under a common simulation/comparison framework."),
    dict(query_id="OBJ-P2", cls="OBJECTIVE_OR_MODEL_CLASS", domain="pharmacometrics", source_id="doi:10.1007/s10928-020-09684-2",
         adverse="Observed concentration-time data are compared with simulations generated by a different physiological pharmacokinetic model while observation correlation and residual error are evaluated under the same validation procedure.",
         control="Observed data and simulations are generated by the same pharmacokinetic model in a positive-control study using the same validation procedure and data structure.",
         adverse_refutes=("SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","MEASUREMENT_OR_EVALUATOR","PROBLEM_BOUNDARY"), control_refutes=("OBJECTIVE_OR_MODEL_CLASS","SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","MEASUREMENT_OR_EVALUATOR","PROBLEM_BOUNDARY"),
         evidence="The source explicitly includes positive-control same-model and negative-control different-model simulations; NPDE reports congruency in the former and incongruency in the latter."),
    dict(query_id="OBJ-P3", cls="OBJECTIVE_OR_MODEL_CLASS", domain="machine_learning", source_id="pmlr:119:ma20c",
         adverse="A classification task is trained under heavy label corruption using a loss whose optimization behavior is not robust enough for that regime; architecture, inputs, and task labels available to training are otherwise fixed.",
         control="The same classification task is evaluated in clean or mild-noise regimes where ordinary loss behavior is adequate enough that high-level loss redesign is not required for validity of the task objective.",
         adverse_refutes=("SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","PROBLEM_BOUNDARY"), control_refutes=("OBJECTIVE_OR_MODEL_CLASS","SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","PROBLEM_BOUNDARY"),
         evidence="ICML 2020 identifies robustness/underfitting limitations of existing losses under noisy labels and evaluates normalized/active-passive losses across noise rates."),
    dict(query_id="OBJ-P4", cls="OBJECTIVE_OR_MODEL_CLASS", domain="causal_epidemiology", source_id="doi:10.1002/sim.8708",
         adverse="A causal-effect analysis includes mediation together with a mechanistic interaction regime that cannot be represented by the simpler decomposition while variables and causal target remain otherwise fixed.",
         control="The same counterfactual decomposition setting has no agonism; in that regime the six-way formulation reduces to the established four-way decomposition without needing a richer causal-effect object.",
         adverse_refutes=("SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","MEASUREMENT_OR_EVALUATOR","PROBLEM_BOUNDARY"), control_refutes=("OBJECTIVE_OR_MODEL_CLASS","SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","MEASUREMENT_OR_EVALUATOR","PROBLEM_BOUNDARY"),
         evidence="The paper proves the six-way decomposition extends the four-way case and explicitly reduces to four-way decomposition without agonism."),

    dict(query_id="BOUND-P2", cls="PROBLEM_BOUNDARY", domain="clinical_generalizability", source_id="doi:10.1038/s41746-020-0277-8",
         adverse="A trial treatment effect is considered for a real-world patient population whose baseline characteristics can differ materially from the trial population even after published eligibility criteria are applied.",
         control="The same trial effect is interpreted within the enrolled trial population for which randomization establishes internal validity, without extending it to a broader target population.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS",), control_refutes=("PROBLEM_BOUNDARY","OBJECTIVE_OR_MODEL_CLASS"),
         evidence="The study finds eligibility criteria often fail to identify a real-world population matching RCT participants and emphasizes the distinction between internal validity and transport beyond the study population."),
    dict(query_id="BOUND-P3", cls="PROBLEM_BOUNDARY", domain="statistical_physics", source_id="arxiv:2005.07481",
         adverse="A restricted molecular subsystem exchanges matter and energy with surroundings while a thermal gradient drives it out of equilibrium; treating that subsystem as a closed simulation omits those exchanges.",
         control="The same Lennard-Jones fluid response is simulated in a larger locally forced closed system whose extent explicitly includes the environment needed for the stationary response.",
         adverse_refutes=("SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","MEASUREMENT_OR_EVALUATOR","OBJECTIVE_OR_MODEL_CLASS"), control_refutes=("PROBLEM_BOUNDARY","SEARCH_OR_EVIDENCE","REPRESENTATION_OR_INTERFACE","IMPLEMENTATION_OR_ENVIRONMENT","MEASUREMENT_OR_EVALUATOR","OBJECTIVE_OR_MODEL_CLASS"),
         evidence="The source reports excellent agreement between an explicit open-boundary AdResS simulation and a larger locally forced closed-system reference for the same nonequilibrium fluid."),
    dict(query_id="BOUND-P4", cls="PROBLEM_BOUNDARY", domain="environmental_lca", source_id="doi:10.3389/fenrg.2020.00015",
         adverse="An environmental comparison of a carbon-utilization product omits upstream or downstream life-cycle processes even though composition, performance, feedstock supply, or end-of-life behavior can differ from its benchmark.",
         control="The same assessment goal is considered in a regime where downstream behavior is genuinely identical and a narrower boundary is sufficient for the comparison under the guideline's scope rules.",
         adverse_refutes=("OBJECTIVE_OR_MODEL_CLASS",), control_refutes=("PROBLEM_BOUNDARY","OBJECTIVE_OR_MODEL_CLASS"),
         evidence="The guideline requires goal-consistent system boundaries, includes upstream CO2 supply, and distinguishes cases where factory-gate boundaries are adequate from cases requiring full life-cycle coverage."),
]

UNRESOLVED_SPECS = [
    dict(query_id="UNRES-P1", domain="systems_biology", source_id="doi:10.1371/journal.pcbi.1008248", dossier="A dynamical biological model is only partially observed, and distinct quantitative parameter sets can generate exactly the same observable output even under ideal noise-free measurements.", evidence="The source defines structural unidentifiability as distinct parameter sets producing the same observable outcome and provides a rigorous scaling test."),
    dict(query_id="UNRES-P2", domain="genetic_biophysics", source_id="doi:10.1038/s41467-020-18694-0", dossier="Two mutations with known individual phenotypic effects can correspond to different hidden biophysical changes; the same measured single-mutant phenotype is compatible with multiple underlying parameter changes that predict different double-mutant outcomes.", evidence="The source shows perfect trait measurements and mechanistic knowledge can still leave biophysical ambiguity; extra measurements are required to identify the hidden changes."),
    dict(query_id="UNRES-P3", domain="causal_modeling", source_id="arxiv:2012.05603", dossier="Two causal models use different variable sets yet agree on all essential causal information expressible through their shared variables under the registered comparison, leaving multiple structurally different descriptions compatible with the shared observable causal content.", evidence="The source formally develops equivalent causal models that preserve essential structural and functional causal relations over common variables."),
    dict(query_id="UNRES-P4", domain="cognitive_development", source_id="doi:10.1016/j.jecp.2020.105080", dossier="Evidence for a causal claim is confounded because more than one candidate factor changes together, so the observed outcome cannot uniquely identify which candidate cause is responsible from the available comparison alone.", evidence="The source studies metacognitive awareness that confounded evidence provides insufficient knowledge for a causal inference."),
]


def make_pair(i: int, s: dict) -> dict:
    cls = s["cls"]
    adverse_refutes = tuple(s.get("adverse_refutes", ()))
    control_refutes = tuple(s.get("control_refutes", ()))
    return {
        "pair_id": f"R5-{s['query_id']}",
        "query_id": s["query_id"],
        "adverse_class": cls,
        "actual_domain": s["domain"],
        "source_id": s["source_id"],
        "source_url": doi_url(s["source_id"]),
        "source_year": PRIMARY_YEAR,
        "adverse": {"id": f"R5-{s['query_id']}-A", "dossier": s["adverse"], "probes": probe_map(support=(cls,), refute=adverse_refutes), "gold_class": cls},
        "control": {"id": f"R5-{s['query_id']}-C", "dossier": s["control"], "probes": probe_map(refute=control_refutes), "gold_class": CONTROL},
        "pair_evidence": {"source_claim": s["evidence"], "coding_rule": "Only source-isolated target/alternatives are SUPPORT/REFUTE; all others INCONCLUSIVE."},
    }


def make_unresolved(i: int, s: dict) -> dict:
    return {
        "id": f"R5-{s['query_id']}-U", "query_id": s["query_id"], "actual_domain": s["domain"], "source_id": s["source_id"], "source_url": doi_url(s["source_id"]), "source_year": PRIMARY_YEAR,
        "dossier": s["dossier"], "probes": probe_map(), "gold_class": UNRESOLVED,
        "admission_evidence": {"source_claim": s["evidence"], "coding_rule": "All generic responsibilities remain INCONCLUSIVE under the source-visible evidence."},
    }


def build() -> tuple[list[dict], list[dict]]:
    return [make_pair(i,s) for i,s in enumerate(PAIR_SPECS)], [make_unresolved(i,s) for i,s in enumerate(UNRESOLVED_SPECS)]


def main() -> None:
    pairs, unresolved = build()
    (ROOT / "PAIRS_V1.json").write_text(json.dumps(pairs, indent=2, sort_keys=True) + "\n")
    (ROOT / "UNRESOLVED_V1.json").write_text(json.dumps(unresolved, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pairs": len(pairs), "unresolved": len(unresolved), "episodes": 2*len(pairs)+len(unresolved)}, sort_keys=True))

if __name__ == "__main__": main()
