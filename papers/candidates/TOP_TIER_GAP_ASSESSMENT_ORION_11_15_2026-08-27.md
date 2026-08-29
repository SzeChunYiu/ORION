> **Superseded in part — read before using the ORION-11 row.**
>
> This assessment was written at `2026-08-27 09:32`. Everything below reflects the
> repository as it stood then, and it is retained unaltered as a record of that
> assessment. It is **not** current for ORION-11.
>
> Since it was written, `main` gained the entire ORION-11 falsification-and-retraction
> sequence:
>
> | commit | date | what |
> |---|---|---|
> | `8484c9e06` | 2026-08-28 09:38 | R4 result — `H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION` |
> | `59628c7b0` | 2026-08-28 09:40 | R4 note — withdraw unsupported component attribution |
> | `616c8207e` | 2026-08-28 15:25 | **retract the comparative necessity claim** |
> | `3a6da292e` | 2026-08-28 18:28 | resync the tracked PDF, which still rendered the retracted claim |
>
> `main` now carries `CLAIM_RETRACTION_LEDGER_V1.md`, and
> `papers/orion-11-recursive-epistemic-reconstruction/manuscript/sections/05b-necessity-successor.tex`
> reads *"That comparative reading is withdrawn."*
>
> This document mentions none of it — verified: zero occurrences of `R4`, `retract`,
> `withdraw` or `CLAIM_RETRACTION` (the 10 hits for "falsif" are generic methodology
> language, not the R4 event). Its cross-cutting synthesis therefore cites ORION-11's
> falsifier as a *strength*, not knowing that the same falsifier subsequently killed the
> comparative claim, and its ORION-11 verdict of `GAPS_FILLABLE` predates the retraction
> that closed that gap by withdrawal rather than by filling it.
>
> **The ORION-15 row is also superseded, in the opposite direction.** At
> `2026-08-27 21:50:09` — twelve hours after this assessment — `7e8e347f5` landed the
> Self-ORION V4 confirmatory execution with terminal
> `REVISION_LEVEL_DISCRIMINATION_SUPPORTED`. This document mentions revision-level
> discrimination zero times, so its ORION-15 gaps were assessed against a paper that has
> since gained a *positive* terminal. Staleness cuts both ways: the ORION-11 row is
> optimistic about a claim later retracted, and the ORION-15 row is pessimistic about
> evidence later supplied.
>
> **The ORION-11 row is superseded.** For ORION-11's current terminal see
> `papers/PUBLICATION_DISPOSITION_MATRIX_V1.md`. The ORION-12 to ORION-15 rows, the
> reviewer framing and the gap taxonomy are unaffected and remain useful — which is why
> this lands with a header rather than being dropped.

# Top-Tier Gap Assessment — orion-11 … orion-15

**Date:** 2026-08-27
**Tree assessed:** `main` @ `405247aad9b8fdda285b13590f6a5d4e96247d7e`
**Method:** `nature-reviewer` skill (vendored `nature-*` package, per `papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md`) — 3 reviewer reports + cross-review synthesis per paper, referee perspective, no author rebuttal.
**Scope:** `orion-11`, `orion-12`, `orion-13`, `orion-14`, `orion-15`. `orion-01`–`orion-04` are out of scope (owned by a concurrent session).
**Mode:** assessment only. No manuscript was edited. No test suite was run.

---

## Assessment boundary

Grounded in manuscript text at the pinned SHA: abstracts, related-work sections, results/limitations sections, and result-table stubs. Reviewers differ only in **emphasis** — no identities, specialties, or affiliations are invented. Where evidence is absent it is marked absent rather than inferred.

Two measurement notes, recorded because they changed findings:

- Prose quality was assessed by reading files directly. A token-compressing filter mangled `orion-14`'s related-work section into apparently broken English; the underlying file is well-formed. **No prose defect is reported for `orion-14`** — that reading was a tooling artifact, caught before it entered this ledger.
- Marker counts (`CANNOT_CHECK`, falsification vocabulary) were used only to locate text. Every finding below rests on the surrounding prose, not on a count.

## The pattern across all five

Every one of the five **self-disclaims generality in its own abstract**:

| Paper | Verbatim self-disclaimer |
|---|---|
| orion-11 | "establish a finite mechanism boundary, not naturalistic or inherent-expressivity superiority" |
| orion-12 | "open-world benefit remains unconfirmed" |
| orion-13 | "descriptive, not population evidence or general superiority"; "naturalistic validity and downstream gains remain prospective" |
| orion-14 | "support the factorization and attainability boundary, not naturalistic superiority" |
| orion-15 | "does not establish transferable self-improvement" |

This is unusual scientific honesty and it is the correct disposition of the evidence. It is also, under the programme's own doctrine — *a regime-conditional positive is INTERMEDIATE, not terminal* — the central top-tier obstacle. **No paper in this set is TOP_TIER_READY as it stands**, and the reason is uniform: the headline mechanism results are established on constructed finite batteries, while the naturalistic programme is negative, unconfirmed, or unexecuted.

The set splits into two very different situations, and the distinction drives every verdict below:

- **Honest scoping of a real finite result** (orion-11, orion-13, orion-14) — the result is measured, bounded, and correctly labelled. The gap is reach, not substance.
- **Headline claim not yet supported by executed evidence** (orion-12, orion-15) — the abstract itself reports the central question as unconfirmed or unmeasured. The gap is substance.

---

# Part I — Referee simulation

Reviewer emphases are held constant across all five papers:
**R1** — generality, significance, breadth of readership. **R2** — technical soundness, falsification design, statistical support. **R3** — novelty against nearest prior art, and claim-to-evidence match.

---

## orion-11 — Recursive Epistemic Reconstruction

### Review setup
- **Input scope:** abstract, related-work/boundary section, section inventory, limitations inventory.
- **Assessment boundary:** results read from the abstract's reported figures and the related-work positioning; per-table inspection not performed.
- **Shared claim summary:** typed responsibility-to-authority licensing — formalized via epistemic transition envelopes, exact interface factorization, and legal-action deficiency — determines which scientific layer evidence authorizes changing.
- **Visible evidence base:** two prospectively frozen runs of 2,882 mechanical worlds (primary + disjoint generator); hidden-shift success 1.0000 vs 0.4938 and 0.4833 for the strongest assimilated parents; 2,402 controls per run with no unnecessary high-level changes; 400 authored exact contracts, 400 correct decisions vs 275 for a donor-complete interface; an information-equivalent product ties at 400/400.
- **Missing materials affecting confidence:** naturalistic validation. The abstract reports 117,649 source-to-target maps yielding 116,929 rejections, 720 unresolved and **zero certifications**; the historical 48-case precursor remains negative; V13 has 0/7 signed outputs and 0/4 closed authority acts.

### Reviewer 1 — generality and significance
- **Overall assessment:** A clean, well-bounded mechanism result whose reach is not yet demonstrated.
- **Who would be interested:** researchers in autonomous scientific agents, failure attribution, and belief-revision authorization; the question of *what a diagnosis licenses you to change* is genuinely upstream of much current agent work.
- **Major strengths:** the separation between success at a task and authority to change a scientific layer is a real conceptual contribution; the control arm (2,402 controls with no unnecessary high-level changes) is the right shape of evidence, since it tests restraint rather than capability.
- **Major concerns:** the headline 1.0000 is on **mechanical worlds** — a constructed generator. A ceiling result on synthetic worlds does not establish that the licensing condition binds anything in naturalistic scientific practice, and the paper's own naturalistic arm returned **zero certifications out of 117,649 maps**. A referee will read that as the mechanism failing to fire where it would matter most.
- **Technical failings to address:** the near-total rejection rate in the naturalistic programme is not diagnosed in the abstract. Is it correct conservatism, a mis-specified admission condition, or an unpowered corpus? These have opposite implications and the paper must distinguish them.
- **Against Nature-style criteria:** originality good; interdisciplinary readership plausible; scientific importance currently limited by demonstrated reach.
- **Recommendation posture:** not yet — the generality gap is the blocking item.

### Reviewer 2 — technical soundness and falsification
- **Overall assessment:** Methodologically among the more disciplined submissions I have seen; the falsification apparatus is real.
- **Who would be interested:** methodologists concerned with pre-registration and control design in agent evaluation.
- **Major strengths:** prospective freezing is used and stated; a **disjoint generator run** replicates the primary result, which is a genuine independent-generation check rather than a reseed; negative controls are present; the paper reports a case where its own falsifier caught the central distinction being applied too loosely — that is falsification working, and it should be foregrounded rather than buried in related work.
- **Major concerns:** the 400-contract comparison includes an **information-equivalent product that ties at 400/400**. This is the most informative number in the abstract and it is under-discussed: it shows the advantage is not information-theoretic but structural. A referee will ask directly whether the licensing coupling is doing work beyond making the same information usable.
- **Technical failings to address:** no interval estimates are reported for the headline contrasts. 1.0000 vs 0.4938 across 2,882 worlds needs an explicit uncertainty statement; a saturated ceiling also invites a floor/ceiling analysis.
- **Against Nature-style criteria:** technical soundness strong within the constructed regime.
- **Recommendation posture:** revisions — quantitative reporting, plus promotion of the tie result to a first-class finding.

### Reviewer 3 — novelty and claim-evidence match
- **Overall assessment:** The positioning is exemplary and should be the model for the rest of this programme.
- **Who would be interested:** anyone who has tried to distinguish a genuine architectural contribution from a recombination of existing agent components.
- **Major strengths:** the related-work section names dozens of parents and explicitly assigns each component to its owner — state representation to Iris, diagnosis-to-scoped-repair to HarnessFix, reopening to EviGraph/EA-Graph/Doyle/change-impact analysis, recursive audit to AREX, attribution and replay to REFLECT, repair assignment to Model-or-Harness. The "Position" subsection then states the residual precisely: the rule governing *when* those outputs may be composed into a formulation change. This is assimilation-first done properly, and it pre-empts the most common novelty objection.
- **Major concerns:** the paper cites Bisht et al. recommending an explicit model of shifting objectives as future work, and correctly notes this shows the gap is real while identifying it is not the contribution. Good — but it raises the bar: the contribution must then be the *mechanism plus its demonstrated consequence*, and the demonstrated consequence is currently confined to mechanical worlds.
- **Technical failings to address:** the abstract's final sentences (48-case precursor negative; V13 0/7 and 0/4) read as an unresolved negative sitting underneath a positive headline. State explicitly whether these are superseded by the frozen runs or still stand against them.
- **Against Nature-style criteria:** originality well-established relative to prior art.
- **Recommendation posture:** revisions.

### Cross-review synthesis
- **Consensus strengths:** exemplary prior-art absorption; genuine pre-registration and disjoint replication; a control arm that tests restraint; honest labelling of the boundary.
- **Consensus technical risks:** the entire positive result lives inside a constructed generator, while the naturalistic arm is near-totally negative and undiagnosed.
- **Where emphasis differs:** R1 treats the naturalistic zero as disqualifying for reach; R2 treats the 400/400 tie as the more revealing technical issue; R3 regards novelty as settled and the claim-evidence join as the residual risk.
- **Broad-interest readout:** the conceptual claim travels well; the evidence does not yet travel with it.
- **Most important to resolve:** (1) diagnose the 116,929/117,649 rejection rate; (2) report uncertainty on headline contrasts; (3) resolve the standing negatives explicitly.

### Risk / unsupported claims
- Any reading of 1.0000 as general capability is unsupported; the abstract itself forecloses it.
- The relationship between the frozen-run positives and the still-negative 48-case precursor is not assessable from the material read.

---

## orion-12 — Open-World Scientific Discovery

### Review setup
- **Input scope:** abstract, full section inventory, related-work search across the manuscript.
- **Assessment boundary:** results read from the abstract; per-gate inspection not performed.
- **Shared claim summary:** an acquisition–authority envelope compares controllers under matched access, budget and authority contracts, supporting acquisition-ceiling, closure-factorization and donor-saturation results.
- **Visible evidence base:** archived experiments that preserve rather than average heterogeneous authority; a descriptive controlled offline task index.
- **Missing materials affecting confidence:** substantial and self-reported — V7 has six locked gates failing and the full candidate **loses to its frozen u4 donor**; V8 admits no residual; V10 fails four gates; V13's provider-native fibre-separating coordinate is supported by only **4/7 reviews**; V15 binds a signed snapshot of 61 dataset blobs without index parsing, census or performance, and its template error was **never executed**; independent custody is **0/3**.

### Reviewer 1 — generality and significance
- **Overall assessment:** The paper states its own headline as unconfirmed. That is honest and it is also decisive.
- **Who would be interested:** researchers building open-world discovery systems, and evaluation methodologists concerned with staged acquisition/screening/closure.
- **Major strengths:** the framing — that acquisition, screening and closure are usually evaluated separately and should not be — is correct and useful. Preserving heterogeneous authority rather than averaging it is the right instinct and is rarer than it should be.
- **Major concerns:** the abstract's closing sentence is "open-world benefit remains unconfirmed." A top-tier venue cannot accept a paper whose central empirical question is reported as unanswered by the authors. Compounding this, the full candidate **loses to its own frozen donor** — the strongest single result in the paper is a negative one against the system's own baseline.
- **Technical failings to address:** the paper needs to decide what it is. If the contribution is the envelope formalism plus a negative empirical finding, that is publishable and should be framed that way. If the contribution is open-world benefit, the evidence is absent.
- **Against Nature-style criteria:** scientific importance not established on current evidence.
- **Recommendation posture:** not in current form.

### Reviewer 2 — technical soundness and falsification
- **Overall assessment:** The gate discipline is real; the results are mostly gate failures.
- **Who would be interested:** methodologists studying pre-registered gate structures.
- **Major strengths:** locked gates, prospective freezing and matched contracts are used. That the gates *fail* and are reported is evidence the apparatus is not decorative — this is a system that can say no to itself.
- **Major concerns:** "only 4/7 reviews support it" is reported as if it were a measurement. Review support is not an experimental outcome; a referee will ask what the 3 dissenting reviews objected to and whether the objection was adjudicated. As written it reads as a vote substituting for evidence.
- **Technical failings to address:** V15's template error was "never executed" and V15B corrects it "only for a successor." An unexecuted error path in a signed snapshot is an untested claim of custody. Independent custody at **0/3** means no external party has verified anything.
- **Against Nature-style criteria:** technical soundness of the *apparatus* is defensible; of the *claims*, not yet.
- **Recommendation posture:** not in current form.

### Reviewer 3 — novelty and claim-evidence match
- **Overall assessment:** I cannot assess novelty, because the paper does not position itself against prior art.
- **Major concerns:** **this manuscript has no related-work section.** A search across the manuscript returns a single incidental mention of "related work" and no dedicated section file, while its four sibling papers each carry a substantive one (`orion-11` 9.9K, `orion-13` 8.4K, `orion-14` 4.9K, `orion-15` 7.2K). For a paper claiming three named theoretical results — acquisition-ceiling, closure-factorization, donor-saturation — the absence of any prior-art positioning is disqualifying at a top venue independently of the empirical situation. A referee cannot determine whether these results are new.
- **Technical failings to address:** name the strongest parent for each of the three theorems and measure the delta, in the manner `orion-11` and `orion-15` already demonstrate within this same programme.
- **Against Nature-style criteria:** originality **not assessable** from the material provided.
- **Recommendation posture:** not in current form.

### Cross-review synthesis
- **Consensus strengths:** correct problem framing; genuine locked-gate discipline; authority preserved rather than averaged.
- **Consensus technical risks:** the central empirical claim is self-reported as unconfirmed; the candidate loses to its own donor; independent custody is zero; and novelty cannot be assessed at all.
- **Where emphasis differs:** R1 sees a framing decision (reframe as a negative result); R2 sees unexecuted custody paths; R3 sees an absent related-work section as independently disqualifying.
- **Broad-interest readout:** currently below the bar on evidence, and unassessable on novelty.
- **Most important to resolve:** (1) write the related-work section; (2) decide whether the paper's contribution is the formalism plus a negative finding, and frame accordingly; (3) close or explain independent custody 0/3.

### Risk / unsupported claims
- The three theoretical results cannot be credited as novel from the material provided — not because they are derivative, but because no positioning exists.
- "4/7 reviews support it" is not evidence of the underlying proposition.

---

## orion-13 — Global Knowledge Portrait

### Review setup
- **Input scope:** abstract, related-work section, section inventory, `CANNOT_CHECK` distribution by section.
- **Assessment boundary:** results read from the abstract and the results-section marker distribution; individual result tables not inspected.
- **Shared claim summary:** epistemic portrait envelopes — the global portraits compatible with source-local observations and licensed mapping constraints — separate point identification, information value and robust action before identification is complete.
- **Visible evidence base:** a prospectively frozen 32-case public-reference holdout, coordinate-governed mapping making no false merges vs 0.1875 for flat predicate canonicalization (paired difference −0.1875, 95% bootstrap interval [−0.34375, −0.0625]); a constructed 36-case corpus giving every deterministic observation-only rule an exact 27/36 ceiling; **one** historical OAEI 2004 test-103 case with BERTMap 33/33 common class pairs vs AML 8/33, full-task F1 33/62 vs 16/137, 58 property correspondences unmatched.
- **Missing materials affecting confidence:** **7 of the 9 `CANNOT_CHECK` markers sit inside `06-results.tex`** — i.e. within the results themselves, not quarantined into a limitations or future-work section.

### Reviewer 1 — generality and significance
- **Overall assessment:** A genuinely interesting partial-identification framing, undercut by the thinness of the external comparison.
- **Who would be interested:** knowledge-graph integration, ontology matching, scientific-claim harmonization, and anyone working on when *not* to merge.
- **Major strengths:** the insight that a hidden coordinate determines whether two claims agree — and that a single canonical graph is therefore overconfident — is a real and transferable idea. Allowing an integration record to carry a plural or obstructed outcome rather than forcing a canonical merge is a meaningful design position.
- **Major concerns:** the only comparison against established external systems is **a single historical case** (OAEI 2004 test-103, BERTMap vs AML). The paper labels this "descriptive, not population evidence or general superiority," which is correct — but a single case cannot support any comparative claim, and its presence in the abstract invites exactly the misreading the disclaimer forbids. Either run the full OAEI track or move the case out of the abstract.
- **Technical failings to address:** the 32-case frozen holdout is the paper's real result and it is small. Its interval [−0.34375, −0.0625] is wide and its lower bound is near zero.
- **Against Nature-style criteria:** importance plausible; breadth currently limited by evaluation scale.
- **Recommendation posture:** revisions.

### Reviewer 2 — technical soundness and falsification
- **Overall assessment:** Correct statistical hygiene on the main contrast; weak adversarial design around it.
- **Major strengths:** the headline comparison is prospectively frozen, reports a paired difference with a bootstrap interval, and declares a false-split guard **in advance** — the right structure. The constructed 36-case corpus establishing an exact 27/36 ceiling for every deterministic observation-only rule is a genuine impossibility result and stronger evidence than the empirical contrast.
- **Major concerns:** **no negative controls appear anywhere in the manuscript.** For a merge/no-merge discriminator this is a specific and serious omission: without a shuffled-label or coordinate-scrambled arm there is no evidence the calculus responds to scientific coordinates rather than to surface features that happen to correlate with them. A gate that refuses merges can score well on false merges by refusing often; the false-split guard mitigates but does not replace a null arm.
- **Technical failings to address:** add a shuffle/permutation null at matched refusal rate; report the refusal rate alongside the false-merge rate.
- **Against Nature-style criteria:** soundness good on what is tested, incomplete on what is not.
- **Recommendation posture:** revisions.

### Reviewer 3 — novelty and claim-evidence match
- **Overall assessment:** Well-positioned; the claim is appropriately narrow.
- **Major strengths:** the related-work section is thorough and correctly downstream-scoped — extraction, schema matching, entity resolution, fusion, stance and literature-based discovery are all explicitly treated as *available capability*, with the residual stated as: given two already-structured projections, which coordinate differences license a merge. Parents are named concretely (MUSE, Discovery Engine, SciER, SciSchema.org, SCOPE/SCION, LLMATCH, I-ADOPT, FAIR 2.0, DEC, OpenScholar, BioSage, Swanson). The closing paragraph restates the empirical claim in deliberately narrow terms.
- **Major concerns:** the seven in-results `CANNOT_CHECK` markers are load-bearing in a way the limitations text does not fully own. A referee reading the results section will encounter undetermined outcomes inline and ask why they are undetermined.
- **Technical failings to address:** for each in-results `CANNOT_CHECK`, state whether it is unanswerable in principle or merely unmeasured here, and if unmeasured, what would measure it.
- **Against Nature-style criteria:** originality established.
- **Recommendation posture:** revisions.

### Cross-review synthesis
- **Consensus strengths:** strong conceptual contribution; correct pre-registration and interval reporting on the main contrast; a real impossibility result in the 27/36 ceiling; excellent positioning.
- **Consensus technical risks:** n=1 external comparison; no negative controls; seven undetermined outcomes inside the results section.
- **Where emphasis differs:** R1 focuses on evaluation scale, R2 on the missing null arm, R3 on the in-results undetermined outcomes.
- **Broad-interest readout:** the idea is broad; the evidence is narrow but honestly labelled.
- **Most important to resolve:** (1) negative-control/shuffle arm; (2) either expand the OAEI comparison or remove n=1 from the abstract; (3) classify each in-results `CANNOT_CHECK`.

### Risk / unsupported claims
- The BERTMap-vs-AML comparison supports no general claim; the paper says so, but its abstract placement works against the disclaimer.
- Absent a null arm, the false-merge advantage is not separable from a general propensity to refuse.

---

## orion-14 — Verified Scientific Discovery

### Review setup
- **Input scope:** abstract, related-work section (read directly), section inventory, `CANNOT_CHECK` distribution by section.
- **Assessment boundary:** results read from the abstract and marker distribution; individual battery tables not inspected.
- **Shared claim summary:** a benchmark score supports a competence claim only when the target is identifiable, compared interfaces can attain its terminal, and the panel is discriminating — formalized via fibrewise Bayes risk, a donor-factorization theorem, a terminal-adapter criterion, and data-processing/total-variation bounds.
- **Visible evidence base:** a protected 420-case battery — non-compensatory promotion relation with **0/360 false promotions vs 180/360** for the strongest frozen mechanism proxy, both promoting 60/60 clean positives; a registered abstention contrast that saturated; a distinct exact-axis battery where the governed pipeline selects the undetermined terminal **30/30** eligible with 0/360 false promotions vs 0/30 for the strongest frozen comparator (paired difference 1.0, 95% CI [1.0,1.0]), with the one comparator able to escalate selecting 15/30 (margin 0.5); 400 exact contracts scoring **400/400** vs 250/400 donor-complete and 50/400 compensatory, with an information-equivalent typed product tying at 400/400; paired improvement over donor-complete 0.375, domain-stratified 95% bootstrap [0.3275, 0.4225].
- **Missing materials affecting confidence:** the source programme has authenticated 76/80 publication–archive–revision bridges but **zero eligible natural pairs**.

### Reviewer 1 — generality and significance
- **Overall assessment:** The strongest evidence base in this set, with the same reach limitation as its siblings.
- **Who would be interested:** the benchmark-validity and agent-evaluation communities — the argument that a score licenses a competence claim only under identifiability, attainability and panel discrimination is directly actionable for anyone designing evaluations.
- **Major strengths:** the false-promotion contrast (0/360 vs 180/360) is a large, clean, decision-relevant effect on a protected battery, and the clean-positive control (60/60 for both arms) rules out the obvious explanation that the governed pipeline simply promotes less. That pairing — big gap on false promotions, no gap on true positives — is the single most persuasive result across all five papers.
- **Major concerns:** **zero eligible natural pairs.** The entire positive result is on constructed batteries and authored contracts; the naturalistic arm produced nothing to test on. The paper says so plainly ("not naturalistic superiority"), but the gap between "0/360 false promotions" and "no natural instance was eligible" is exactly where a top-tier referee will push.
- **Technical failings to address:** explain *why* zero of the natural pairs were eligible. If the eligibility criterion is so strict that nothing in nature qualifies, that is a finding about the criterion and should be reported as one.
- **Against Nature-style criteria:** importance high if reach can be shown; currently bounded.
- **Recommendation posture:** revisions.

### Reviewer 2 — technical soundness and falsification
- **Overall assessment:** Statistically the most complete of the five.
- **Major strengths:** interval estimates are reported for the headline contrasts, including a domain-stratified bootstrap ([0.3275, 0.4225]) rather than a naive one — the stratification matters and is correctly chosen. The battery is protected. Hostile-control language is used extensively and an ablation programme is present. Critically, the paper **reports the margin against the one comparator that can actually escalate (0.5)** separately from the margin against comparators that cannot (1.0). Most authors would have reported only the larger number.
- **Major concerns:** a paired difference of 1.0 with CI [1.0, 1.0] is a saturated measurement — the interval is degenerate and conveys no uncertainty information. It should be presented as a ceiling, not as a precise estimate. Relatedly, the registered abstention contrast is reported as "saturated," which forecloses inference from it; a referee will ask for a harder abstention battery.
- **Technical failings to address:** re-power the saturated contrasts so they can discriminate; state explicitly that [1.0,1.0] is a ceiling artifact.
- **Against Nature-style criteria:** technical soundness strong.
- **Recommendation posture:** revisions.

### Reviewer 3 — novelty and claim-evidence match
- **Overall assessment:** Properly positioned, and unusually disciplined about where its undetermined outcomes live.
- **Major strengths:** the related-work section names roughly nineteen parents across source attribution, provenance-sensitive authorization, auditability and citation fidelity, research-integrity provenance, evaluator integrity and contamination, and abstention — and states the residual as the empirical question of whether a *protected conjunction* of prerequisites behaves differently from its strongest single component under the same hostile battery. That is a well-formed, testable residual.
- **Major strengths (structural):** the `CANNOT_CHECK` markers are **quarantined out of the results**: zero appear in `05-results.tex`, with nine concentrated in `12-prospective-source-expansion.tex` — a section explicitly about a prospective programme — plus two in limitations and one each in availability and conclusion. This is the correct disposition: undetermined outcomes are declared where they belong and do not contaminate the headline. It is a marked contrast with `orion-13` (7 in results) and `orion-15` (H1–H4 undetermined).
- **Major concerns:** the abstract is dense to the point of impenetrability for a non-specialist — a Nature-style criterion in its own right. The exact-axis paragraph in particular carries three separate contrasts and two intervals in one breath.
- **Technical failings to address:** none on positioning.
- **Against Nature-style criteria:** originality established; readability for nonspecialists is the weak axis.
- **Recommendation posture:** revisions.

### Cross-review synthesis
- **Consensus strengths:** the largest and cleanest effect in the set, with the right control; complete interval reporting; honest separate reporting of the weaker comparator margin; `CANNOT_CHECK`s correctly quarantined out of results.
- **Consensus technical risks:** zero eligible natural pairs; two saturated contrasts that cannot discriminate; abstract readability.
- **Where emphasis differs:** R1 on naturalistic eligibility, R2 on saturation, R3 on readability.
- **Broad-interest readout:** the closest of the five to a top-tier case on evidence quality.
- **Most important to resolve:** (1) explain or fix zero natural eligibility; (2) de-saturate the abstention and exact-axis contrasts; (3) rewrite the abstract for a general reader.

### Risk / unsupported claims
- The [1.0,1.0] interval should not be read as precision.
- No claim about naturalistic performance is supported; the natural arm produced zero eligible cases.

---

## orion-15 — Self-ORION

### Review setup
- **Input scope:** abstract, related-work section (read directly), results-attribution section, all seven `CANNOT_CHECK` result-table stubs, section inventory.
- **Assessment boundary:** formal proofs not verified line by line; assessed as stated results.
- **Shared claim summary:** *minimal method revision under observational equivalence* — a latent situation determines an admissible minimal revision front while a reviser sees only an evidence interface, with a family of exact if-and-only-if identification results and a protected-authority corollary.
- **Visible evidence base:** the formal results themselves; local hostile tests exercising registered implementation semantics only; a diagnostic glm-5.2 hidden-cause attribution archive scoring **21/24 with three residual errors retained**.
- **Missing materials affecting confidence:** severe and self-declared. **H1–H4 all remain `CANNOT_CHECK`.** P5-RD-01 and P5-RD-03 are unexecuted; P5-RD-02 supplies no protected or fresh evidence. Four execution preflights leave **12, 14, 15 and 15 blockers** (C1 SWE-agent, C2 MOSS, C3 DGM, C4 ADIAS).

### Reviewer 1 — generality and significance
- **Overall assessment:** A strong theory paper wearing an empirical paper's clothes.
- **Who would be interested:** self-improving-agent researchers, AI-safety researchers concerned with self-certification, and anyone designing promotion/adoption governance.
- **Major strengths:** the theoretical core is the most substantial in this set — a coherent family of exact characterizations (exact revision selection iff the evidence interface is constant on required-decision fibres; panel resolution iff every observationally equivalent pair requiring a different revision is covered, reducing minimum-cost non-adaptive discrimination to weighted set-cover; adaptive exactness iff every terminal leaf is decision-pure; exact transcript decoding iff decision-class laws are mutually singular). The protected-authority corollary — that if internally identical transcripts can require opposite promotion decisions then no internal rule is both sound and complete — is a genuine impossibility result with real safety consequence.
- **Major concerns:** the empirical programme is **entirely unexecuted**. Seven result tables (P5-2, P5-4, P5-5, P5-6, P5-7, P5-T2, P5-T3) contain no admissible rows. All four hypotheses are undetermined. The one empirical artifact — a 21/24 diagnostic archive — is explicitly disclaimed as not establishing transferable self-improvement.
- **Technical failings to address:** as an empirical contribution the case is not established. As a theory contribution it may already be strong enough.
- **Against Nature-style criteria:** importance of the theory high; empirical support absent.
- **Recommendation posture:** not as an empirical paper.

### Reviewer 2 — technical soundness and falsification
- **Overall assessment:** The undetermined outcomes are handled with real integrity; that does not make them fewer.
- **Major strengths:** the table stubs are exemplary in a way I rarely see. `P5-T2` states: "the archived attribution run has no matched baseline/ablation arms, round identities, or campaign-level outcomes. **Numbers are not imputed from the 21/24 diagnostic accuracy.**" The refusal to impute — and the explicit statement of what future run would populate the table — is exactly right, and the three residual attribution errors are *retained* rather than discarded.
- **Major concerns:** **these are unfilled gaps, not honest framings.** Every one of the seven stubs shares a single root cause: the archived attribution run was not instrumented to record round identities, motivating/replay/fresh splits, recurrence annotations, improvement/integrity outcomes, protected-improvement cost, matched baseline/ablation arms, or campaign interventions. That is a data-collection omission, recoverable by re-running the campaign with those fields recorded. It is categorically different from `orion-14`'s prospective-expansion `CANNOT_CHECK`s, which declare a future programme's boundary.
- **Technical failings to address:** run the campaign with the missing annotations. This needs new work, not new theory, and it is the single highest-value action across all five papers.
- **Major concerns (secondary):** **no negative controls** appear in the manuscript, and only one mention of prospective freezing — weak for a paper whose subject is whether a system can validly certify itself.
- **Against Nature-style criteria:** soundness of the formal results plausible; of the empirical claims, not established.
- **Recommendation posture:** revisions, or re-scope to theory.

### Reviewer 3 — novelty and claim-evidence match
- **Overall assessment:** The positioning is the best in this set, and it makes the empirical gap more conspicuous rather than less.
- **Major strengths:** the related-work section opens by stating that the neighbouring literature "is strongest exactly where this paper does not compete," and treats every mechanism as absorbable rather than rival. It then systematically forecloses its own novelty routes: archives and self-modification to ADAS/DGM/ADIAS; failure attribution to SAGE/CausalFlow/failure-driven self-improvement; acceptance statistics to PACE/SEA ("optional-stopping-safe commit acceptance is not a P5 novelty"); transfer measurement to PAST-Bench/SEVA; engineering-side self-evolution to MOSS/Ratchet/Verifier-as-Gatekeeper/MEGA. It cites a 1,250-paper RSI survey and concludes that generic claims like "the system learns from failure" are "mature targets rather than a defensible P5 breakthrough." The surviving residual is stated as one sharp question: *who has authority to turn an internally generated diagnosis into an adopted scientific method?*
- **Major concerns:** having correctly narrowed the contribution to the authority-separation result, the paper then asserts that "transferable fresh-task improvement... is not required to establish the authority-separation theorem." That is defensible for the *theorem* — but the manuscript still carries seven empty tables and four undetermined hypotheses that promise exactly the evidence it says is not required. A referee will read this as a paper that has not decided whether it is a theory paper.
- **Technical failings to address:** decide. Either cut the unexecuted empirical apparatus and submit the theory, or execute it.
- **Against Nature-style criteria:** originality clearly established.
- **Recommendation posture:** revisions.

### Cross-review synthesis
- **Consensus strengths:** the strongest formal results and the best prior-art absorption in the set; exceptional integrity in refusing to impute missing numbers; negatives retained rather than discarded.
- **Consensus technical risks:** all four hypotheses undetermined; seven empty result tables from one recoverable instrumentation omission; four preflights blocked (12/14/15/15); no negative controls.
- **Where emphasis differs:** R1 would re-scope to theory, R2 would run the campaign, R3 notes the paper has not chosen between those two.
- **Broad-interest readout:** the impossibility result is genuinely broad; the empirical frame currently detracts from it.
- **Most important to resolve:** (1) choose theory-only or execute; (2) if executing, re-run the attribution campaign with the seven missing annotation families; (3) add negative controls.

### Risk / unsupported claims
- No claim of transferable self-improvement is supported; the paper states this.
- The 21/24 diagnostic accuracy supports nothing about H1–H4 and is explicitly not imputed into them.
- Preflight binding (parsers, wallclocks, dependency locks) is not evidence of execution; C1–C4 remain blocked.

---

# Part II — Gap ledger

**Verdict key.** `TOP_TIER_READY` — submit as is. `GAPS_FILLABLE` — a top-tier case is reachable; the listed gaps are the work. `SECOND_TIER` — the headline claim is not currently supported by executed evidence; fall back unless the blocking gap is closed.

| Paper | Verdict | Blocking gap in one line |
|---|---|---|
| orion-11 | **GAPS_FILLABLE** | Naturalistic arm returns zero certifications from 117,649 maps, undiagnosed |
| orion-12 | **SECOND_TIER** | No related-work section at all; headline self-reported as unconfirmed; candidate loses to its own donor |
| orion-13 | **GAPS_FILLABLE** | No negative controls; external comparison is n=1 |
| orion-14 | **GAPS_FILLABLE** *(closest to ready)* | Zero eligible natural pairs; two saturated contrasts |
| orion-15 | **SECOND_TIER** | H1–H4 all undetermined; seven empty result tables from one recoverable instrumentation omission |

No paper is `TOP_TIER_READY`. The uniform reason is generality: all five establish finite-regime results and all five say so in their own abstracts.

## Gaps ranked by what closes them

### Tier A — fillable with existing evidence (analysis or writing only; no new runs)

| # | Paper | Gap | What closes it |
|---|---|---|---|
| A1 | orion-12 | **No related-work section.** One incidental mention across the manuscript; siblings carry 4.9–9.9K each. Novelty of the three named theorems is unassessable. | Write it. Name the strongest parent for acquisition-ceiling, closure-factorization and donor-saturation, and measure the delta. `orion-11`'s "Position" subsection and `orion-15`'s related work are in-programme templates. |
| A2 | orion-12 | Paper has not decided whether its contribution is the envelope formalism **plus a negative empirical finding**, or open-world benefit. The latter is unsupported. | Reframe as formalism + negative result. A candidate losing to its own frozen donor is publishable as a finding when framed as one. |
| A3 | orion-15 | Manuscript has not chosen between theory paper and empirical paper; it disclaims needing transfer evidence while carrying seven tables promising it. | Choose. Cutting the unexecuted apparatus makes the impossibility result submittable now. |
| A4 | orion-11 | Standing negatives (48-case precursor; V13 0/7 signed outputs, 0/4 authority acts) sit under a positive headline with no stated relation. | State whether the frozen runs supersede them or they still stand. |
| A5 | orion-14 | `[1.0, 1.0]` presented as an interval; abstention contrast "saturated". | Relabel as ceiling artifacts; do not present degenerate intervals as precision. |
| A6 | orion-13 | n=1 OAEI comparison sits in the abstract, inviting the misreading its own disclaimer forbids. | Move out of the abstract, or expand (Tier B). |
| A7 | orion-14 | Abstract impenetrable to a non-specialist — a Nature-style criterion in its own right. | Rewrite for a general reader; the exact-axis paragraph carries three contrasts and two intervals at once. |
| A8 | orion-13 | Seven in-results `CANNOT_CHECK`s not classified. | Mark each as unanswerable-in-principle vs unmeasured-here, and for the latter state what would measure it. |

### Tier B — needs new work (runs, instrumentation, or corpus)

| # | Paper | Gap | What closes it | Cost |
|---|---|---|---|---|
| B1 | orion-15 | **H1–H4 all `CANNOT_CHECK`; seven result tables empty.** Single root cause: the archived attribution run recorded no round identities, motivating/replay/fresh split, recurrence annotations, improvement/integrity outcomes, protected-improvement cost, matched baseline/ablation arms, or campaign interventions. | Re-run the attribution campaign with those seven annotation families recorded. Not new theory — new instrumentation. | Medium; highest value in the set |
| B2 | orion-11 | Naturalistic arm: 116,929 rejections / 720 unresolved / **0 certifications** from 117,649 maps, undiagnosed. | Determine whether this is correct conservatism, a mis-specified admission condition, or an unpowered corpus. These have opposite implications. | Medium |
| B3 | orion-14 | **Zero eligible natural pairs** despite 76/80 authenticated bridges. | Diagnose the eligibility criterion. If nothing natural can qualify, that is itself a reportable finding about the criterion. | Medium |
| B4 | orion-13 | **No negative controls anywhere.** For a merge/no-merge discriminator, nothing separates the false-merge advantage from a general propensity to refuse. | Shuffle/permutation null at matched refusal rate; report refusal rate beside false-merge rate. | Low |
| B5 | orion-15 | No negative controls; only one mention of prospective freezing — weak for a paper about valid self-certification. | Add null arms and pre-register the campaign in B1. | Low, if bundled with B1 |
| B6 | orion-14 | Two saturated contrasts cannot discriminate. | Re-power with a harder battery. | Medium |
| B7 | orion-11 | No interval estimates on headline contrasts (1.0000 vs 0.4938 over 2,882 worlds). | Add intervals; add a ceiling/floor analysis given saturation. | Low |
| B8 | orion-12 | Independent custody **0/3**; V15 template error never executed. | Obtain external custody; execute the error path. | High (needs external party) |
| B9 | orion-13 | 32-case holdout is small; interval lower bound near zero. | Expand the frozen holdout. | Medium |

### Tier C — structural, likely not closable for this submission round

| # | Paper | Gap |
|---|---|---|
| C1 | all five | Every headline is a finite-regime result and every abstract says so. Full naturalistic generality is a programme-scale objective, not a revision item. The realistic top-tier play is to make the **boundary itself** the contribution — as `orion-11` and `orion-14` already do — rather than to promise reach the evidence does not have. |

## Recommended disposition

1. **orion-14** — closest to a top-tier case. Do A5, A7, B3, B6. The 0/360-vs-180/360 contrast with a matched 60/60 clean-positive control is the strongest single result in the programme.
2. **orion-11** — do A4, B2, B7. Positioning is already exemplary; the naturalistic diagnosis is the pivot.
3. **orion-13** — do B4 first (cheapest, closes the most serious soundness objection), then A6/A8, then B9.
4. **orion-15** — decide A3. If theory-only, it is close to submittable on the impossibility result alone. If empirical, B1 is the single highest-value action across all five papers.
5. **orion-12** — do A1 before anything else; novelty is currently unassessable, which no amount of further evidence fixes. Then A2.

## Answers to the five commissioned questions

1. **Generality / regime-conditionality.** All five are regime-conditional, explicitly and by their own statement. Under the programme's doctrine each is therefore INTERMEDIATE. `orion-11` and `orion-14` convert this into a contribution by making the boundary the claim; `orion-12` and `orion-15` currently carry it as an unmet promise.
2. **Novelty vs nearest prior art.** Four of five have absorbed their strongest parents and stated a measured residual — `orion-11` and `orion-15` are exemplary, `orion-13` and `orion-14` solid. **`orion-12` has no positioning at all** and its novelty cannot be assessed.
3. **Falsification.** Genuine in `orion-11` (pre-registration, disjoint-generator replication, negative controls, a falsifier that caught its own distinction being applied too loosely) and structurally present in `orion-13`/`orion-14` (frozen holdouts, declared guards, hostile batteries). **Negative controls are absent from `orion-13` and `orion-15`** — a specific, cheap, high-value omission.
4. **Load-bearing CANNOT_CHECKs.** `orion-14` — **honest framing**: zero in results, concentrated in a prospective-expansion section. `orion-13` — **mixed**: seven sit inside `06-results.tex` and are unclassified. `orion-15` — **unfilled gap**: H1–H4 undetermined and seven empty tables, from one recoverable instrumentation omission. The refusal to impute numbers is exemplary; the absence of the numbers is still the gap.
5. **Negatives.** All five preserve negatives rather than hiding them, which is a genuine strength. Two carry unresolved negatives underneath positive headlines: **`orion-11`** (48-case precursor negative; V13 0/7 and 0/4) and **`orion-12`** (candidate loses to its own frozen donor; six locked gates fail). `orion-12`'s is severe enough to be the paper's real result if reframed.
