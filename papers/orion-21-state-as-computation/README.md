# P11 — State as Computation

**Stable ID:** ORION-P11  
**Paper issue:** #471  
**Shared tracks:** #664 accessibility-work accounting · #667 state optionality  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript. It supersedes the stale `papers/candidates/paper-11-state-as-computation/MANUSCRIPT.md` path on draft PR #715; that older file remains historical input and is not the canonical submission surface.

## Current evidence status

`PEER_REVIEW_PACKAGE_READY / CONTROLLED_THEORY_SYSTEMS_BOUNDARY_CHARACTERIZED`

Earned evidence includes:

- exact query-family rank lower bound for fixed linear-accessible state;
- 91×–1820× registered universal/compiled representation ratios;
- 4× to >32× dense-decoder sample-threshold gains in the original controlled cells;
- no-answer-laundering P11B result;
- exact compile/cache/recover/materialize optionality laws;
- P11D hostile sparse-decoder result: **permanently negative** against the preregistered ≥4×-in-both-cells gate, but retaining 2×/4× threshold gaps;
- P11E fresh deterministic replication of the sparse residual: sparse/compiled thresholds `128/64` and `256/64`, with +0.2912/+0.3307 accuracy gaps at `n=64` and byte-identical two-run payload SHA `1097d94b…a4536`;
- P11F historical nonlinear output, now **non-authoritative** because hostile PR review found a protocol mismatch (`n_jobs=-1` despite an otherwise-default frozen contract);
- P11G fresh deterministic nonlinear successor, retained only at its arm-scoped authority; the later attainability audit showed its hostile survival gate was unreachable in the losing direction, so P11G cannot license a general hostile-nonlinear claim;
- P11H/P11I width boundary: a pooled hostile attack wins at `r=3`, while the prospectively frozen `r=7` replication passes all nine prespecified seed×geometry cells with matched live narrow controls;
- NR-07 low-width capacity law (`top_tier/P11_LOW_WIDTH_GAP_REVIVAL_RECEIPT_V1.md`): the `r=3` attack win is a decoder-CAPACITY consequence, not a decoder-mechanism deficit — support recovery costs `n ~ 1/ρ(r)²` samples with `ρ(r) = C(r-1,(r-1)/2)/2^(r-1)` exactly, so `n* = 2 ln p / ρ(r)²` retrodicts the full P11H 15-rung ladder with no free parameters, both P11D gap gates are unattainable at `r=3` against the capacity-augmented pool (max attainable delta64 = 0.1741 < 0.20; ratio ≤ 2 < 4), and the `r=7` window survives the strictly stronger attack (max below 256 = 0.9421 over all 21 `r=7` readings);
- donor-complete compiler comparison (`P11_DONOR_COMPARATOR_RESULT_RECEIPT_V1.md`): the D5 mutual-information selection principle, raced at matched charged compiler work and matched `k`, does not beat the registered `f_classif` compiler on breast-cancer, wine or digits and is at accuracy parity on all three; the independent checker and byte replay are green;
- exact decoder frontier (`P11_DECODER_ATTACK_RESULT_RECEIPT_V1.md`): on the frozen parity family, constants/signed singles/odd-majority/axis decision lists do not realize the target, while the realizing character has degree `k` and decision trees require exactly `2^k` leaves; a structurally independent exact checker agrees;
- ten-responsibility real-data phase study (`P11_QUERY_FAMILY_PHASE_RESULT_RECEIPT_V1.md`): **authoritative negative retained without retuning**. The preregistered family-scale quality gate is not met — LINEAR `3/10`, RBF `5/10`, KNN `5/10` versus the frozen `>=8/10` requirement — while every registered resource identity is confirmed (memory crossover `U<=4`, break-even horizon `1917..19169`, nonzero future-query specialization cost).

`P11_ACTIVE_CLAIM_AUTHORITY_V2.json` is the sole active authority. It keeps P11I's supported `r=7` leaf separate from P11H's historical `r=3` boundary, binds the corrected execution-seed replication unit, and integrates the adverse ten-responsibility result as a non-retuned binding boundary. The gap-wave result forbids family-scale compilation support on digits unless the responsibility set is small and each member is individually compile-tolerant. Issue #1086 calls this missing integration “P11J”, but no artifact with that identity exists; the bound study is `P11_QUERY_FAMILY_PHASE_V1`.

Historical failures remain first-class artifacts. P11D, P11H and the ten-responsibility `P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET` result are never relabelled positive; P11F is not used as claim authority; P11G stays arm-scoped; and P11C carries no broad claim authority. Successor protocols do not rewrite those outcomes.

## Strongest paper-level claim

> **State is a computational placement decision, not a universal compression win.** Query-conditioned state construction can externalize structural search from bounded downstream access, but the benefit is jointly conditioned on state width, responsibility and access class. A pooled hostile attack wins at narrow `r=3` and loses across the prespecified wider `r=7` replication; separately, on non-synthetic digits a fixed 16/64 learned compilation is quality-supported for only `3/10` responsibilities under linear access and `5/10` under stronger access, below the preregistered family-scale bar. The resource phase algebra still holds exactly, locating a defensible compiled-state region at small responsibility sets (`U<=4`) whose members are individually compile-tolerant and whose service horizon exceeds the charged compiler break-even.

## Peer-review artifacts

- `MANUSCRIPT.md` — full paper
- `CLAIM_EVIDENCE_LEDGER.md` — claim authority and donor subtraction
- `PEER_REVIEW_READINESS.md` — five-lens hostile review/checklist
- `REVIEWER_SUMMARY.md` and `PR_SCOPE.md`
- P11/P11B/P11C/P11D/P11E/P11F/P11G/P11H/P11I protocols and harnesses — full evidence history
- `top_tier/P11_DONOR_COMPARATOR_RESULT_RECEIPT_V1.md` — donor-complete selection-principle comparison
- `top_tier/P11_DECODER_ATTACK_RESULT_RECEIPT_V1.md` — exact decoder-family frontier
- `top_tier/P11_QUERY_FAMILY_PHASE_RESULT_RECEIPT_V1.md` — bound ten-responsibility negative and phase boundary
- `top_tier/P11_QUERY_FAMILY_PHASE_LEDGER_ADDENDUM_V1.md` — additive authority update for the negative
- `top_tier/P11_LOW_WIDTH_GAP_REVIVAL_RECEIPT_V1.md` — NR-07 capacity attribution and proven width law for the `r=3` boundary
- P11D/P11H adverse results, P11E replicated sparse, P11G arm-scoped nonlinear and P11I wide high-width receipts
- `P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` — arm-axis adjudication and decoder/state decomposition
- `P11_EXTERNAL_VALIDATION_REQUIREMENTS_V1.md` — exact requirements, CANNOT_CHECK reasons and pass gate for the three open issue #1086 external-validation boxes (comparator breadth, resource matching, optionality/LOBO)

## Not authorized

No universal nonlinear lower bound, transformer/agent superiority, free preprocessing claim, family-scale claim that a 16/64 learned compilation works for arbitrary responsibilities, or broad statement that compiled state always dominates universal state. A future real-system claim must charge compiler work, respect the responsibility-conditioned negative, and beat strong state/search/decoder baselines under a common resource boundary.
