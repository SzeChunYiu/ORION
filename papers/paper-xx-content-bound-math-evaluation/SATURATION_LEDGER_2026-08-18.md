# P10 constructive saturation ledger — 2026-08-18

## Method and boundary

The object was tested against four neighboring literatures: versioned Lean
benchmarks, native verification and statement faithfulness, tactic/proof-pattern
mining, and repository/proof-state representations. Full papers, official
project documentation or official repositories were used where accessible.

The rule is **extract, assimilate, strength-check, then test the residual**.
Every close donor below has an adoption disposition; `CITED_ONLY` is forbidden.
This is a dated bounded pass, not a claim that every relevant work was found.

## Structure-extraction and assimilation receipts

| Donor | Strongest structure extracted | ORION assimilation receipt | Strength gained | Disposition |
|---|---|---|---|---|
| Yang et al., [LeanDojo](https://leandojo.org/leandojo.html), NeurIPS 2023 / v2 2025 | Repository tracing produces proof states, tactics, premises and dependencies; evaluation interacts with a real Lean environment and uses a novel-premise split rather than random leakage. | P10 labels the 457-file study a conservative source projection, not a native trace. The native audit is separate, and a Lean-native trace is a reopen trigger. | Prevents source text from masquerading as proof-state or elaborated dependency evidence. | `ABSORBED` |
| Letson et al., [SorryDB](https://arxiv.org/pdf/2603.02668), ICML 2026 | Each real-world task stores repository URL, branch, commit, Lean version, file location and goal; candidate repositories are rebuilt at the specific revision before evaluation. | `MathEvaluationEnvironment` types repository, branch, revision, toolchain, dependency manifest, source path and source digest into one identity; hostile revision/source substitutions fail. | P10 now binds the complete execution subject, not only statement text. | `ABSORBED` |
| Firsching et al., [Formal Conjectures](https://arxiv.org/pdf/2605.13171), 2026 | Benchmark-set version and Lean/Mathlib toolchain version are orthogonal; snapshots are immutable and fixes create a new version. | V2 is retained as invalid negative history; repaired parsing required a separately frozen V2.1 protocol, while the exact corpus revision remained fixed. | Corrections are auditable and cannot overwrite the original outcome. | `ABSORBED` |
| Xin et al., [VeriSoftBench](https://arxiv.org/pdf/2602.18307), 2026 | Fixed-commit tasks preserve realistic repository context and cross-file dependencies; repository dependence is an experimental variable. | P10 pins the full upstream revision and `lake-manifest.json`; the native audit runs inside the original Mathlib checkout rather than a detached file. | Native receipts retain ecosystem context and dependency identity. | `ABSORBED` |
| Ji, [CSLibPremiseBench](https://arxiv.org/pdf/2605.14549), 2026 | Pin commit/toolchain, make candidate policy explicit, quantify coverage, and distinguish source-visible proxy labels from elaborated Lean dependencies. | The corpus manifest accounts for all selected/excluded source bytes; the protocol calls tactic families a source-visible projection and makes native evidence a separate receipt. | Removes semantic overclaim from the transfer metrics and exposes unknown lines. | `ABSORBED` |
| Xin et al., [TacMiner](https://arxiv.org/pdf/2503.24036), OOPSLA 2025 | Tactic dependence graphs capture proof-state dependencies that surface order misses; reusable tactics require collapsible graph structure and are strength-tested by proof compression and downstream automation. | P10 does not promote adjacent coarse n-grams into executable tactics. A TacMiner-class/native dependency baseline is a named reopen requirement for any standalone macro-mining claim. | Converts a tempting positive sequence result into a bounded descriptive technical result. | `DEFERRED_WITH_TRIGGER` |
| Nawaz et al., [Proof Guidance in PVS with Sequential Pattern Mining](https://inria.hal.science/hal-03769130/), FSEN 2019 | Abstract proof commands into sequences, mine frequent sequential patterns, and evaluate them as proof guidance. | P10 removes sequential proof-pattern mining from novelty and treats its Markov/null study as a cross-module diagnostic only. | Defeats the hostile headline “proof sequences can be mined for reusable patterns.” | `ALREADY_PRESENT` |
| Gao et al., [LeanSearch v2](https://arxiv.org/pdf/2605.13137), 2026 | Extract elaborated declaration dependencies, retain source metadata, hold the prover loop fixed, and test retrieval downstream; empty retrieval is a meaningful signal. | P10 separates source-level n-gram recurrence from dependency/premise structure and makes any proof-utility claim contingent on downstream native evaluation. | Blocks inference from high pattern coverage to proof assistance. | `ABSORBED` |
| Zhang et al., [Beyond Compilation](https://arxiv.org/abs/2606.31002), 2026 | Lean compilation and semantic faithfulness are different gates; compile-pass but unfaithful statements require calibrated semantic/human checks. | `MathEvaluationEnvironment` and native receipts state that identity and acceptance are not faithfulness; P4/P8 remain the authority owners. | Native success cannot silently become a semantic or scientific claim. | `ABSORBED` |
| Wu et al., [ITPEval](https://arxiv.org/abs/2607.19407), 2026 | Preserve per-artifact native checking semantics across ITPs, while testing statement equivalence separately because type-checking can overestimate fidelity. | Native receipt, statement identity and authority are distinct typed/claim-ledger layers. | Reinforces the fail-closed three-layer boundary. | `ALREADY_PRESENT` |
| Ammanamanchi et al., [Faults in Our Formal Benchmarking](https://arxiv.org/abs/2606.29493), 2026 | Machine-checked proofs do not immunize datasets against vacuity, bad specifications, axioms or harness loopholes; release benchmark defects and corrected snapshots explicitly. | V2 contamination is published, not deleted; P10 makes no statement-faithfulness or theorem-quality claim and preserves all parser exclusions. | Turns a parser failure into auditable negative knowledge and constrains the remaining claim. | `ABSORBED` |
| Lean community, [Validating a Lean Proof](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) and [Did you prove it?](https://leanprover-community.github.io/did_you_prove_it.html) | A meaningful proof receipt requires a buildable repository, pinned dependencies, the intended file actually checked, and an explicit trust/axiom boundary. | Native subjects run in the exact upstream project with exact dependency/toolchain hashes; the receipt claim is only file acceptance. Axiom/statement audits are excluded rather than implied. | Makes runtime custody and the trust boundary reviewer-inspectable. | `ABSORBED` |

## Hostile already-solved test

The following candidate headlines fail after assimilation:

- “content-bound Lean benchmarks” — repository/commit/toolchain binding is
  standard in SorryDB, Formal Conjectures and repository-scale benchmarks;
- “native verifier receipts make a theorem claim trustworthy” — native
  acceptance and statement faithfulness are explicitly different gates;
- “coarse tactic sequences reveal reusable tactics” — sequential proof mining
  is old and TacMiner supplies a stronger proof-state dependency abstraction;
- “cross-module predictability establishes proof utility” — premise/dependency
  work requires a fixed downstream prover or native trace evaluation.

The residual is an engineering discipline: identity, native acceptance and
scientific authority must not collapse into one field. That discipline is now
implemented, but P4/P8 already own its formal authority meaning.

## No-material-change confirmation rounds

After the donor set stabilized, two further query rounds were run on
2026-08-18:

1. `Lean benchmark evaluation defects source revision native verifier statement identity`,
   `proof tactic macro mining dependence graph sequential patterns`, and
   `native kernel checking semantic faithfulness` returned the same three
   structures: pinned environments, graph/state-aware proof mining, and a
   separate faithfulness gate. `NO_MATERIAL_CHANGE`.
2. Exact-phrase queries for `source revision`, `immutable Lean toolchain`,
   `statement faithfulness native checking`, and `tactic sequence cross-module`
   returned Lean Eval/T²/Lean validation guidance plus the already-recorded
   mining works. They strengthened existing receipts but introduced no new P10
   residual. `NO_MATERIAL_CHANGE`.

## Residual decision

`TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME`.

The corrected empirical result and hostile invalidation are worth preserving.
They do not survive as a standalone novelty object. Reopening requires a
Lean-native trace, a TacMiner-class structural baseline on the same frozen
corpus, downstream proof utility, and an integrity residual not already owned
by P4/P8.
