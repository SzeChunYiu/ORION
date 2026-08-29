# ORION-01–25 top-tier science-gap register V2

**Audit date:** 2026-08-29  
**Audited base:** `703b87db22dce3981f13b407b56f4a656310632f` (`main`)  
**Previous audit base:** `b04214b1076665aaaf3b3f78ae04f597bc403178`  
**Scope:** all twenty-five canonical papers  
**Policy:** additive audit only; no frozen experiment, adverse result, historical ledger, checksum, or active foreign branch is rewritten

## Scientific authority and review method

This register is a role-separated internal scientific audit, not independent external peer review. Six lenses were applied and cross-checked:

1. **Programme epistemology:** claim identity, falsification, frozen evidence, and the scientific value of negative terminals.
2. **Exact statistics:** inference units, small-sample uncertainty, paired designs, multiplicity, clustering, and power.
3. **Formal methods:** theorem boundaries, counterexamples, optimization estimands, and checker independence.
4. **Empirical systems:** interventions, ablations, external validity, identity-disjoint sampling, and safety gates.
5. **Reproducibility and custody:** immutable ledgers, content binding, provenance, and independent outcome authority.
6. **Journal editing:** title/abstract calibration, reader workflow, limitations, and reviewer-risk control.

`VERIFIED_*` below means reproduced from primary repository artifacts or current mainline terminals. It does not mean external replication, novelty clearance, or journal acceptance. No complete external literature search was performed.

## Latest-main reconciliation

The audit was rebased over every commit after the previous base:

| Commit | Mainline change | Consequence for this audit |
|---|---|---|
| `7e364d514b5957a2acab120e03027ff26ebdde87` | Correct ORION-08 Holm-adjusted revised intervals and set review-ready | ORION-08 remains bounded-closed, now under the corrected finite-family **joint** interval certificate rather than marginal interval language. |
| `f7780fb16aeca827a7a02534ae89ff6617239029` | Add ORION-08 interval regression gate | The uncertainty claim is executable rather than prose-only. |
| `ad61a71d226dd3aae1f5f83c8b259786aa01ea7b` | Reconcile ORION-08 claim registry | Paper and portfolio authority are aligned. |
| `703b87db22dce3981f13b407b56f4a656310632f` | Add ORION-08 claim-registry reconciliation gate | Registry drift is machine-detectable. |

No other primary diagnosis changed. Active PRs #1716 (ORION-17) and #1694 (ORION-05) were inspected as foreign experimental lanes and are not edited from this branch.

## Highest-impact exact findings

### ORION-17: prediction is supported; the unique mechanism is not identified

The prospectively stamped import-density threshold predicts all five held-out projects correctly. With **project** as the inference unit, the exact one-sided probability under a 50% null is `0.03125`, the two-sided value is `0.0625`, and the exact 95% accuracy interval is approximately `[0.4782, 1.0000]`. The 1,671,821 within-project certificate decisions are descriptive, not independent replications.

Across the three calibration and five evaluation projects, density is not uniquely identified. Import density, module count, and edge count each perfectly separate the eight observed outcomes. The safe terminal is therefore:

`PROSPECTIVE_RULE_SUPPORTED__UNIQUE_MECHANISM_NOT_IDENTIFIED`

The title-level statement should be no stronger than: **“A prospectively stamped import-density rule predicts closure-retention failures in five held-out Python repositories.”** The phrase “density, not size” requires a new rule-disagreement design.

A decisive successor uses 20 externally selected disagreement projects: 10 small-dense and 10 large-sparse. Require at least 15 density wins overall and at least 7 of 10 in each stratum. The overall directional gate has exact one-sided alpha `0.020694732666` and power `0.804207785460` if the true density-win probability is 0.8. Fewer than 20 usable projects, custody failure, or neither symmetric rule meeting its gate is CANNOT_CHECK/NO_DISCRIMINATION.

Custody rule for PR #1716: preserve historical V1 checksums and `CLAIM_LEDGER_V4.md`; bind successor evidence additively. Do not repair a documented self-binding circularity by weakening historical binding.

### ORION-05: controls and campaign optimize different domains

The R6O sharpness controls were proved for one fixed block matching, where support-one and support-two optima are 6 and 5. The global obstruction campaign instead minimizes over all 15 perfect matchings of an unordered six-target set. Under that campaign estimand, the three controls become 4/4, 5/5, and 6/6, so none demonstrates the expected strict gap.

The present checker validates witnesses and expected values but does not independently recompute the optimization optimum. The safe terminal is:

`CONTROL_DOMAIN_MISMATCH_IDENTIFIED__CURRENT_CENSUS_REMAINS_CANNOT_CHECK`

Two valid repairs are different experiment identities: either run a fixed-matching census with same-domain controls, or first establish all-matchings controls and then execute a disjoint confirmatory family. The current 5,005 rows cannot be retrospectively relabelled as confirmatory.

### ORION-11: retired records cannot support a mechanism claim

The audited 2,880 records cannot support causal or ablation claims: `orion_no_adaptive`, `orion_no_dedup`, and `orion_no_recursion` are record-identical to `orion_full`, and the live model answer is discarded (`used_output=False`) before synthetic scoring. These records are instrument-validation material only. The smallest valid successor is the already frozen v2.2.4 intervention-policy study in which model output actually enters the treatment path and scoring remains outcome-blind.

### ORION-19 and ORION-24: favorable bounded results, insufficient comparative authority

Both primary artifacts contain four favorable discordant pairs and no adverse discordant pairs. In each case, exact paired McNemar inference gives one-sided `p=0.0625` and two-sided `p=0.125`.

- **ORION-19:** five task families; tailored arm 5/5 and baseline 1/5. The bounded paper is fileable, but five families do not establish broad comparative generalization.
- **ORION-24:** 28 adjudication cases; DAOSS 28/28 and ordinary multi-review 24/28. Every discordance is one of the four `RETAIN_NEGATIVE` controls, so broad superiority additionally requires external, stratified construct validation.

## Paper-by-paper closure and manuscript actions

| Paper | Evidence / current terminal | Strongest unresolved science gap | Immediate manuscript action now | Smallest decisive next evidence |
|---|---|---|---|---|
| **ORION-01** | Reported lead; theory/compute required | Characterize when finite certificate realization transfers normative credit. | State “finite certificate realization” in title/abstract; move normative-credit transfer to an explicit open theorem. | Machine-checkable characterization or a complete exact finite theorem/counterexample census. |
| **ORION-02** | Verified adverse bounded terminal | A stronger paired claim still lacks a genuinely new, case-level preregistered identity. | Publish the adverse terminal, including `p=0.092` and missing case flags, without rescue language. | One new outcome-blind paired study with frozen censoring, multiplicity, and stop rules. |
| **ORION-03** | External authority required | Typed-merge falsification lacks identity-disjoint external labels and cases. | Frame the present paper as an internally falsified formal instrument. | Independently selected corpus, blinded labels, frozen error analysis, and auditable identity separation. |
| **ORION-04** | Theory/compute required | Bounded/truncated completion is not yet an unrestricted lower bound. | Put the truncation domain in title/abstract; state the unrestricted claim only as a conjecture. | Complete stronger census or theorem reducing the unrestricted problem to a verified finite basis. |
| **ORION-05** | **Verified control-domain defect** | Fixed-matching controls do not validate an all-matchings obstruction census. | Separate the proved fixed-matching 6-versus-5 result from the unordered-set campaign; keep the latter CANNOT_CHECK. | Same-domain planted controls plus independent optimum recomputation under one frozen estimand. |
| **ORION-06** | External authority required | Recursive recovery lacks independently sourced families and preregistered failure criteria. | Report internal recovery as feasibility evidence with a predeclared failure taxonomy. | Identity-disjoint recovery families with comparator, minimum usable count, and exact stop rule. |
| **ORION-07** | External authority required | Dual-instrument agreement has not been separated from externally adjudicated correctness. | Present agreement and correctness as separate endpoints. | Blinded adjudication with frozen eligibility rules, strata, and calibrated error. |
| **ORION-08** | **Verified bounded closure** | Only external transport remains open. | Use the corrected finite-family joint interval certificate throughout; never revert to marginal interval wording. | Do not reopen the bounded identity; use family-level inference in an external multi-family successor. |
| **ORION-09** | Theory/compute required | Finite regime geometry is not a universal theorem. | Quantify the finite catalogue and convert universality language to theorem-or-counterexample form. | Proof under explicit premises or a verified counterexample. |
| **ORION-10** | Theory/compute/design required | Certified static forecasts lack multi-scale held-out coverage. | Report scale-stratified coverage and the worst stratum; do not average away a failed certificate stratum. | Frozen scale strata, holdout split, coverage envelope, and worst-stratum gate. |
| **ORION-11** | **Verified invalid confirmatory instrument** | Old records do not implement treatment contrast or use live model output. | Retitle the old table as instrument diagnosis and disclose identical ablations plus discarded output. | Execute frozen v2.2.4 intervention-policy experiment with real treatment-path use and outcome-blind scoring. |
| **ORION-12** | Design repair required | Two-endpoint multiplicity and a definition-encoding comparator weaken the claim. | Declare one primary endpoint; report the second under correction; call the current comparator a reference implementation. | Independently implemented behavioral comparator with frozen paired primary analysis. |
| **ORION-13** | **Verified bounded closure** | Only external-domain transport remains open. | Keep the bounded manuscript intact; foreground the multi-null battery and sampled-domain limit. | Do not reopen; use preregistered external domains and family-level transport criteria in a successor. |
| **ORION-14** | Inference repair required | Label-level counts ignore clustered source families and shared adjudication context. | Report independent-cluster count and replace label-level uncertainty with cluster-respecting uncertainty. | Frozen clusters, paired statistic, exact/cluster-bootstrap plan, and minimum independent clusters. |
| **ORION-15** | External programme authority required | Hardware, staffing, organization, and model-family contrasts are unavailable internally. | Publish the governance/measurement protocol; state autonomous-improvement efficacy is externally untested. | Independently operated programme with frozen contrasts, custody, endpoints, and safety gates. |
| **ORION-16** | Independent implementation required | Same-lineage verification is not implementation-independent correctness. | Call current replication same-lineage verification. | Separately authored language/kernel over a frozen interchange format and held-out certificate suite. |
| **ORION-17** | **Verified prediction; mechanism not identified** | Density is perfectly confounded with module/edge thresholds in eight projects. | Report five held-out repositories and project-level uncertainty; remove “density, not size.” | Twenty balanced rule-disagreement projects with independent custody and the frozen 15/20 plus 7/10-per-stratum gate. |
| **ORION-18** | External programme authority required | Autonomous-science authority has not transported to a second real programme. | Position the paper as a single-programme authority architecture. | Second independently governed programme with frozen intervention, comparator, endpoints, and guardian. |
| **ORION-19** | **Verified bounded result; small-N gap** | Four favorable discordances across five task families do not establish population-level superiority. | Report five families and exact paired `p=0.125`; use descriptive comparative language. | At least 20 identity-disjoint families with family-level paired inference and retained adverse cases. |
| **ORION-20** | External authority required | Broad structured problem-solving has not been tested across independent real solver families. | Name exact solver families and report family-level rather than pooled instance-level generalization. | Independent solver families, instance ground truth, family-level gate, and worst-family safety criterion. |
| **ORION-21** | Verified bounded exclusion; model family required | Current evidence excludes only a named high-capability regime. | Present an exclusion boundary, not a universal state-as-computation claim. | Non-tautological positive and negative model families, or an impossibility theorem. |
| **ORION-22** | Verified bounded terminal; provenance gap | Identity-disjoint examples are not yet implementation-disjoint and may retain latent leakage. | Report eight effective classes and generator lineage explicitly. | Independent generators, leakage probes, provenance audit, and family-level inference. |
| **ORION-23** | Verified construct-validity failure | V2 ground truth is generated by the responsibility rule itself. | Recast V2 as internal consistency against rule-derived labels. | External blinded adjudication of ambiguous native-DAG cases with paired comparator. |
| **ORION-24** | **Verified favorable controls; small-N construct gap** | All four discordances are planted `RETAIN_NEGATIVE` controls. | State this concentration, report exact paired `p=0.125`, and remove broad superiority language. | Externally guarded replication with independently sourced negative-retention and ordinary-positive strata. |
| **ORION-25** | External toolchain authority required | Internal harness controls are not native Cosign/TUF/in-toto interoperability. | Position the bounded paper as a research harness and list native interoperability as a successor. | Frozen versions/trust roots, hostile controls, authoritative verifiers, and independent operator custody. |

## Portfolio disposition

The portfolio should not be represented as twenty-five uniformly “top-tier-ready” papers.

- **Bounded gap already closed:** ORION-08 and ORION-13. Reopening them to manufacture more favorable rows would weaken the programme.
- **Highest-value operational repair:** ORION-05, ORION-11, ORION-17, ORION-19, and ORION-24.
- **External authority is a real scientific dependency:** especially ORION-03, ORION-15, ORION-18, ORION-23, and ORION-25. Repository prose, mocks, or internally generated labels cannot supply it.
- **Theory/exact-compute route:** ORION-01, ORION-04, ORION-09, ORION-10, and ORION-21; ORION-05 joins this route after estimand repair.
- **Primary-artifact promotion still needed before final manuscript edits:** ORION-06, ORION-07, ORION-12, ORION-14, ORION-16, ORION-20, and parts of ORION-22.

## Non-negotiable publication gates

Until successor evidence exists:

1. Titles and abstracts state the bounded inference unit and sample size.
2. Conclusions distinguish prediction from mechanism, internal controls from external validity, and bounded closure from broad transport.
3. Exact adverse, null, ambiguous, and CANNOT_CHECK terminals remain visible.
4. No within-project, within-family, within-cluster, or same-generator pseudo-replication.
5. No historical checksum or claim-ledger mutation to absorb successor evidence.
6. No external-review, novelty, or production-interoperability claim is authorized by this audit.
7. One verified counterexample closes a universal claim unless the registered premises explicitly exclude it.

## Review terminal

This register fills every repository-contained scientific gap that can be filled without inventing observations or external authority: it corrects claim boundaries, exact inference units, manuscript language, experiment identities, acceptance rules, rejection rules, CANNOT_CHECK rules, and smallest falsifiers. It does **not** fabricate the external programmes, adjudicators, native toolchains, independent implementations, or new held-out outcomes required by several papers. Those dependencies are the science, not editorial residue.
