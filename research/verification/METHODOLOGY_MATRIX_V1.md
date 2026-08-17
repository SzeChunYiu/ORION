# Verification-method methodology matrix V1

**Status:** DESIGN_FROZEN for the #283 programme verifier.  
**Frozen date:** 2026-08-17.  
**Rule:** this matrix is frozen *before* audit outcomes are treated as confirmatory. Later searches may add rows; they cannot relax a detector or change a pass rule after a claim outcome has been inspected.

Disposition vocabulary matches the programme: `ADOPT / ADAPT / COMPOSE / DEFER / REJECT`.

| Mechanism / paper | What it contributes | Disposition in ORION verifier | Bound |
|---|---|---|---|
| Jacovi et al. 2023, *Stop Uploading Test Data in Plain Text* (EMNLP; arXiv:2305.10160) | Encrypt/isolate test labels; do not publish answers beside tasks | **ADAPT** — hidden-label / protected-path checks; fail-closed if gold is candidate-visible | Does not by itself prove a result is uncontaminated |
| Golchin & Surdeanu 2023/24, *Time Travel in LLMs* (ICLR; arXiv:2308.08493) | Guided completion as contamination probe | **DEFER** as a required P4/P5 detector — needs model logits/API not available for frozen mechanical P4 | Optional later for LLM arms |
| Sainz et al. 2023–24, NLP evaluation / contamination spectrum (ACL Findings; LM Contamination Index) | Contamination is a spectrum, not a boolean | **ADOPT** the spectrum: exact-label, lexical, metadata, template, split-overlap | Verifier reports detectors, not a single "clean" bit |
| Cheng et al. 2024, *Benchmark Data Contamination of LLMs* (arXiv:2406.04244) | Survey of BDC and alternative assessment | **ADAPT** leakage layer catalogue | Survey ≠ a detector |
| Yao et al. 2025, static→dynamic evaluation survey (arXiv:2502.17521) | Dynamic/time-sensitive benchmarks as structural fix | **DEFER** as a paper-method change; verifier holdout layer records whether a *fresh* split was actually run | Absence of a new holdout is `CANNOT_CHECK`, not PASS |
| GEM 2026 systematic review (55 studies; four-tier T1–T4 contamination; CTC) | No detector is reliable across tiers/access/training stage; instruction-tuning blind spot | **ADOPT** humility: leakage PASS never authorizes VERIFIED alone; CTC-style fields in the receipt | Inflation ranges 6–40% are not transferable to ORION batteries |
| arXiv:2606.03305 *Reliability Gap in Benchmark Auditing* | Distribution shift and small-n make membership inference fail in realistic audits | **ADOPT** — statistical contamination tests are not a substitute for provenance | Do not claim "no contamination" from a non-run MIA |
| Kapoor & Narayanan / leakage-as-methodology literature | Train/test leakage and shortcut features invalidate leaderboard claims | **ADAPT** lexical/metadata/template predictors as mandatory falsifiers | A high shortcut score bounds construct validity; it does not rewrite a correctly counted headline |
| Liao et al., construct validity for ML benchmarks | Measurement must match the claimed construct | **ADOPT** bounded-claim text on every receipt | Prevents P5 21/24 becoming "self-improvement" |
| RewardHackingAgents, arXiv:2603.11337 | Evaluator tampering vs train/test leakage as first-class outcomes; lock evaluator + deny held-out paths | **ADAPT** for P4 telemetry/hidden-label layer; independent scorer must not be the original evaluator | Public tree may lack strace; then CANNOT_CHECK, not PASS |
| Search-Time Contamination, arXiv:2606.05241 | Web search can retrieve benchmark answers at inference time | **ADAPT** for any live-search arm; P4 published telemetry of zero external IP is the available artifact | Cross-host search STC not re-run here |
| Proctor-style OS isolation + signed bundles | Attest inputs; log forbidden access | **COMPOSE** with P4 custody hashes; do not re-execute protected campaign | Signed Actions artifacts are evidence of custody, not of this verifier's re-run |
| Pineau et al. ML Reproducibility checklist; ACM artifact review; Peng 2011; National Academies *Reproducibility and Replicability* | Tracked code + tracked inputs must regenerate headlines; failed runs retained | **ADOPT** raw-artifact replay + fail-closed missing artifact | A closed GitHub issue is not an artifact |
| Holm / multiple-testing; Wilson score; percentile bootstrap | Predeclared margins; nested repeats must not inflate n | **ADOPT** independent stats reimplementation from written formulas | Independent CI from counts is weaker than case-level paired vectors |
| Stodden scientific-software reproducibility | Distinguish bit-reproducible, regenerable, and reviewable | **ADOPT** three replay grades in receipts | P4 protected JSONL absent ⇒ not bit-reproducible in public tree |

## Two consecutive rounds that did not change the planned diagnosis

Round 1 (issue #283 contract + paper protocols) already specified six layers, fail-closed missing artifacts, independent scorers, and CANNOT_CHECK for unrun holdouts. Round 2 (GEM 2026 review, reliability-gap auditing, RewardHackingAgents, STC) added humility about contamination detectors and evaluator-lock/deny-path mechanics, but **did not change** the planned diagnosis, discriminator, repair, or baseline: the verifier still (a) replays raw artifacts, (b) rescores from written specs, (c) runs shortcut falsifiers, (d) audits denominators, (e) pressures baselines honestly, (f) refuses to treat an unrun holdout as PASS.

## Frozen consequence

`VERIFIED` requires a actually-run independent holdout/cross-host layer. Shortcut-sensitive or aggregate-only replays are at most `BOUNDED_VERIFIED`. `INVALIDATED` remains a successful audit outcome.
