# Paper Q1 claim ledger V2 — All-n support ceiling with bounded regime history

**Supersedes for publication:** `CLAIM_LEDGER.md` V1  
**Publication cut:** `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
**Foundation:** `PUBLICATION_FOUNDATION_V2.md`

Status vocabulary:

- `PROVEN-ALL-N` — machine-checked theorem for every `n`/instance of the exact frozen grammar/objective named by the receipt.
- `THEOREM-GRADE-ON-DOMAIN` — proof/exhaustive complete finite-domain result or exact explicit counterexample on the stated domain.
- `MACHINE-EVIDENCED` — verified on stated finite frozen domains; not an all-`n` theorem.
- `PROSPECTIVE-BOUNDED` — prediction/claim frozen before a later bounded outcome, then tested on the named domain.
- `REFUTED` — an exact counterexample or theorem falsifies the stated claim in its declared scope.
- `OPEN` — not established at this publication cut.
- `COMPANION-BOUNDARY` — evidence owned scientifically by the QG companion programme and cited here only to delimit Q1's permissible claim.

No row grants R6 compiled-resource novelty, physical quantum advantage, or external novelty authority.

| ID | Publication claim | Authority | Scope | Status |
|---|---|---|---|---|
| Q1-C1 | R6M per-qubit support dominance: `TotalSavings <= FrameCost`, zero violations over 536,870,912 configurations; max savings/cost ratio 1.000. | `research/extensions/orion-q/MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json` | Complete registered local R6M domain | `THEOREM-GRADE-ON-DOMAIN` |
| Q1-C2 | Donor F3 letterwise exchange monotonicity has zero violations over 175,616 configurations. | same R6N receipt | Complete registered letterwise domain | `THEOREM-GRADE-ON-DOMAIN` |
| Q1-C3 | R6I per-qubit support-dominance check has zero violations over 150,994,944 configurations; max ratio 0.333. | same R6N receipt | Separate R6I local domain only | `THEOREM-GRADE-ON-DOMAIN` |
| Q1-C4 | R6I weight-one closure matches unrestricted exact DP on all 20 recorded subject partitions and seven synthetic panels. | R6N + `MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_RESULTS.json` | Recorded R6I instances only | `MACHINE-EVIDENCED` |
| Q1-C5 | **Tag-anchor splitting counterexample:** registered `n2_b` R6M instance has `C_DP=8 < 9=C_R6L`, realized by split weight-one frame anchors with a weight-two shared Tag. | R6N + `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` | Exact frozen instance/objective | `THEOREM-GRADE-ON-DOMAIN` |
| Q1-C6 | D+ repairs the first gap on all five R6N panels and exhaustive `n=1`; the minimum-Tag construction passes its registered exact checks. | R6O receipt | Stated finite domains | `MACHINE-EVIDENCED` |
| Q1-C7 | **Frame-for-Tag borrow counterexample:** D+ closure is false; the registered minimal structured-`n=2` witness has `C_DP=5 < 6=C_D+`, with central-branch support-two frame paying for a cheaper Tag. | R6O + R6P witness replay | Exact frozen instance plus registered counterexample panels | `THEOREM-GRADE-ON-DOMAIN` |
| Q1-C8 | Structural containments `C_DP <= C_D++ <= C_D+ <= C_R6L` and feasibility/soundness of registered borrow-family costs hold wherever evaluated. | R6P/R6O/R6Q protocols and receipts | Frozen family definitions | `THEOREM-GRADE-ON-DOMAIN` |
| Q1-C9 | R6P finite closure: `C_DP=C_D++` on 4,096 exhaustive `n=1`, 9,261 structured `n=2`, the seeded/random/panel cells and the recorded chemistry matchings; all 559 then-critical instances closed with verified witnesses. | `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` | Frozen finite domains | `MACHINE-EVIDENCED` |
| Q1-C10 | **All-`n` support-two sufficiency:** for every `n`, target six-tuple, matching, relative permutation and central choice in the frozen R6M grammar/raw support-count objective, an exact optimum exists with all frame supports ≤2, hence `C_DP=C_D++`. | `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`; authority `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N__NOT_R6` | Exact frozen R6M grammar/objective; explicitly excludes R6I and other objectives/grammars | **`PROVEN-ALL-N`** |
| Q1-C11 | The R6S exchange proof localizes the intrinsic boundary: support≥3 can be reduced at non-increasing cost, while the exact support-two failing class is the registered borrow pattern. | R6S theorem receipt | Same theorem scope | `PROVEN-ALL-N` for the reduction statement; boundary witnessed exactly |
| Q1-C12 | **Support-three necessity under the frozen R6M/raw-support objective** — existence of an optimum requiring frame support ≥3. | R6S theorem | Same theorem scope | **`REFUTED`** |
| Q1-C13 | Chemistry equality `C_DP=C_D++=C_D+=C_R6L` on all 30 originally recorded H4/equilibrium-N2 matchings. | R6P/R6M/R6N/R6O receipts | Named subjects/matchings only | `MACHINE-EVIDENCED` |
| Q1-C14 | Original R6Q predicate `P1(t)` classifies donor-exactness with zero error on the four registered panels (9,771 instances); its original two-trade identity holds on those panels. | `MAX_R6Q_REGIME_PREDICATE_RESULTS.json` | Exactly those frozen panels | `MACHINE-EVIDENCED` |
| Q1-C15 | **Original two-trade identity/predicate is an all-`n` complete characterization.** | QG5 exact refuting instance; later QG7 witnesses | The universal extension of the R6Q claim | **`REFUTED`** |
| Q1-C16 | **Prospective fresh-subject test:** prediction was digest-stamped before DP on one deterministically selected fresh Benzene DUCC batch; all 15 matchings matched predicted donor-exact regime and exact cost. | `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`; authority `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PREDICTION_CONFIRMED__TWO_TRADE_PREDICATE_HELD_ON_UNSEEN_SUBJECT__NOT_R6` | One fresh public subject, 15 frozen matchings | **`PROSPECTIVE-BOUNDED`** |
| Q1-C17 | The R6R confirmation proves the original two-trade predictor is universal. | Later QG5/QG7 exact counterexamples | Any extension beyond R6R's bounded domain | **`REFUTED`** |
| Q1-C18 | QG5 found a fresh exact `n=3` counterexample to the earlier simple forecaster/predicate: `C_DP=10 < 11=C_R6L=C_D+=f_B`; `C_D++=10` remains exact by the all-`n` theorem. | `QG5_CERTIFIED_FORECAST_RESULTS.json`, rebound in `QG5B_EXACT_FORECASTER_RESULTS.json` | Exact companion instance | `COMPANION-BOUNDARY` |
| Q1-C19 | Enlarged borrow family B′ repairs the QG5 refuting instance and closes the QG5b registered finite panels, but its closed-form identity remains a conjecture for all `n`. | `QG5B_EXACT_FORECASTER_RESULTS.json` | Frozen QG5b panels | `COMPANION-BOUNDARY` / finite evidence |
| Q1-C20 | QG7 found 64 exact fourth-regime witnesses with `C_D++ < min(C_D+,f_B′)`, identifying a weight-two-Tag/phantom-borrow hybrid inside the support-two world. | `QG7_BPRIME_COMPLETENESS_RESULTS.json` + generic verification | Frozen QG7 hostile panels | `COMPANION-BOUNDARY` / exact counterexamples |
| Q1-C21 | B″ closes all 10,481 registered QG7b finite instances with zero fifth-configuration candidates. | `QG7B_HYBRID_FAMILY_RESULTS.json` | Frozen finite panels only | `COMPANION-BOUNDARY` / `MACHINE-EVIDENCED` |
| Q1-C22 | `C_DP=min(C_D+,f_B′,f_B″)` for every `n` in the frozen grammar. | QG7c partial classification | All `n` | **`OPEN`**; pinned comm-s2 consolidation link remains unproved |
| Q1-C23 | R4B equal-size sorted-contiguous coefficient partition minimizes split-TARE outer-LCU subnormalization on its stated coefficient-coordinate theorem domain; 0/8,700 hostile checks fail. | `MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json` | Coefficient coordinate only | `THEOREM-GRADE-ON-DOMAIN` |
| Q1-C24 | R4D implementation-aware split-TARE compiler reduces the registered structural cost from 8,078 to 4,972 on one blob-locked public H2O/cc-pVTZ DUCC subject at the recorded normalization overhead. | `MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json` | One public subject; not full-circuit authority | `MACHINE-EVIDENCED` |
| Q1-C25 | Donor-owned primitives include TARE, Tag/Restore, anticommuting partitioning, Clifford/symplectic synthesis, global Pauli compilation, low-ancilla/second-quantized block encodings, non-Clifford fusion, controlled-Pauli grouping and the donor factoring machinery. | internal donor freeze + fresh submission search required | Donor subtraction | `BOUNDARY` |
| Q1-C26 | No external paper predating submission contains Q1's exact residual (all-`n` support-two ceiling + exact coupling counterexamples under the frozen shared-Tag grammar/objective). | submission-date literature search | External novelty proposition | `OPEN_UNTIL_FRESH_SEARCH_CLOSES` |

## Publication headline authorized by this ledger

> **In the frozen shared-Tag three-block TARE grammar under the raw support-count objective, weight-one donor restrictions fail by exact coupling counterexamples, yet frame support two is an exact all-`n` expressivity ceiling. A finite regime predicate and a prospectively frozen fresh-subject test succeed on their registered domains, while later companion counterexamples show that closed-form regime identity inside the support-two world is richer than the original two-trade description.**

## Forbidden promotions

1. Do not say “two coupling trades completely characterize the exact optimum.”
2. Do not say the original R6Q predicate is universal.
3. Do not say support two is sufficient for all TARE constructions/objectives; name the frozen R6M grammar/raw support-count objective.
4. Do not describe QG5/QG7 refutations as contradictions of R6S; they refine subfamily classification inside D++.
5. Do not use chemistry/Benzene panels as physical quantum-advantage evidence.
6. Do not describe direct D++ chemistry sweeps as executed where the receipt uses an exact containment pinch.
7. Do not grant novelty credit to donor-owned TARE/factoring/frame machinery.
8. Do not use `NOT_R6` receipts to imply R6 compiled-resource novelty.
9. Do not open or imply access to the protected stretched-N2 subject.
10. Do not freeze an external novelty sentence until the fresh primary-literature pass is complete.
# Paper Q1 claim ledger V2 — sharp support-two normal forms

**Manuscript:** `papers/Q-paper-01-tare-expressivity/MANUSCRIPT_SUBMISSION_DRAFT.md`
**Date:** 2026-08-22

Status vocabulary:
- `THEOREM`: all-instance statement within the explicitly frozen grammar/objective, proved analytically in the publication proof; machine checks are retained as independent corroboration where available.
- `EXACT_COUNTEREXAMPLE`: exact witnessed refutation of a broader statement.
- `MACHINE_EVIDENCED`: exact on stated finite panels only.
- `SUPPORTING`: application/diagnostic evidence that does not carry the main theorem.
- `BOUNDED_NOVELTY_RESEARCH`: dated search record, never a novelty certificate.

| ID | Maximum permitted claim | Evidence | Status |
|---|---|---|---|
| Q1V2-C1 | In the frozen R6M three-block TARE-M2 shared-one-bit-Tag grammar with donor-owned F3 factoring and the frozen support-count objective, every exact optimum has an equally good representative with every frame Pauli of support <=2 for every `n`, target six-tuple, matching, permutation and central choice: `C_DP = C_D++`. | Analytic proof: `HUMAN_PROOF_R6S_2026-08-22.md`; original machine receipt: `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` | THEOREM |
| Q1V2-C2 | The publication proof is analytic: (i) an odd-alpha multiset in `F_2^2` of support `w>=3` always contains a nonempty proper zero-sum singleton/equal pair preserving both frame anticommutation and Tag syndrome; (ii) zeroing one frame letter raises the three-way Restore cost by at most 2, never more than the minimum frame refund. The original R6S 18,432-case local table and 43,688 class-tuple census independently corroborate these lemmas but are not logically required. | `HUMAN_PROOF_R6S_2026-08-22.md`; `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`; `independent_human_proof_sanity.py` | THEOREM |
| Q1V2-C3 | The R6S exchange fails exactly at four `w=2` class tuples; the failure corresponds to a locally commuting coordinate that still anticommutes with the Tag, matching the R6O weight-two frame-for-Tag mechanism. | `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` (`claim_boundary.support_2_boundary`, `lemma_b.w2_*`); analytic interpretation in `HUMAN_PROOF_R6S_2026-08-22.md` | THEOREM + MECHANISTIC IDENTIFICATION |
| Q1V2-C4 | Support one is not uniformly sufficient: R6O structured `n=2`, `instance_index=16` has `C_DP=5 < C_D+=6`, where D+ exhausts the frozen all-support-one frame family with arbitrary anchors, all ordered anticommuting local pairs, both label orientations, all target permutations, and the minimum compatible Tag. | `research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`; completeness definition in `development/orion-q-max-r0/MAX_R6O_ENLARGED_TAG_DONOR_PROTOCOL.md`; witness cross-check in `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` | EXACT_COUNTEREXAMPLE |
| Q1V2-C5 | Defining `kappa_R6M` as the smallest uniform frame-support cap guaranteed to contain an optimum, C1 and C4 imply the sharp result `kappa_R6M = 2`; the bound is attained already at `n=2`. | Logical consequence of C1 and C4; derivations in `THEOREM_UPGRADE_2026-08-22.md` and `HUMAN_PROOF_R6S_2026-08-22.md` | THEOREM/COROLLARY |
| Q1V2-C6 | The support-two normal form contains at most `[3n + 9*C(n,2)]^6 = O(n^12)` raw frame tuples for the fixed six-slot grammar before constraints. A minimum Tag need not act outside the <=12-qubit union of frame supports. | Counting corollary from C1; `THEOREM_UPGRADE_2026-08-22.md` | THEOREM/COROLLARY (representation candidate count only) |
| Q1V2-C7 | R6N local support-dominance checks have zero violations over 688,041,472 complete local configurations across the R6M/R6I audit components; this does not by itself prove joint closure because Tag repair was an explicit declared gap. | `research/extensions/orion-q/MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json` | THEOREM-GRADE LOCAL LEMMAS |
| Q1V2-C8 | Tag-anchor splitting is an exact support-one-family counterexample to common-anchor donor closure: frozen `n2_b` has `C_DP=8 < C_R6L=9`, recovered by D+ with split anchors and a weight-two `Y⊗Y` Tag. | `MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json`; `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` | EXACT_COUNTEREXAMPLE |
| Q1V2-C9 | Frame-for-Tag borrowing is an exact counterexample to all-support-one D+ closure; R6O finds 486/9261 structured and 73/240 random strict gaps, including C4's minimal `5<6` witness. | `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` | EXACT_COUNTEREXAMPLE + MACHINE_EVIDENCED CENSUS |
| Q1V2-C10 | R6P support-two closure holds on every registered finite domain: 4096 exhaustive n=1, 9261 structured n=2, 240 seeded random, five panels and 30 chemistry matchings; all 559 previously critical instances close with reverified support-two witnesses. | `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` | MACHINE_EVIDENCED; superseded upward by C1 for support sufficiency |
| Q1V2-C11 | The R6Q split/borrow predicate, using no unrestricted DP call, has zero classification error on 9,771 registered instances: 9261 + 240 + 240 + 30. | `MAX_R6Q_REGIME_PREDICATE_RESULTS.json` | MACHINE_EVIDENCED, finite-domain only |
| Q1V2-C12 | On the same R6Q registered domains, `C_DP = min(C_R6L,C_D+,f_B)`. This is not an all-n theorem and not a complete taxonomy outside those domains. | `MAX_R6Q_REGIME_PREDICATE_RESULTS.json` | MACHINE_EVIDENCED |
| Q1V2-C13 | R6R prospectively selected a previously unread public benzene/cc-pVDZ DUCC2 subject under a frozen rule, printed the prediction digest before DP, and correctly predicted donor-exact regime and exact cost on all 15 matchings. | `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json` | MACHINE_EVIDENCED, prospective |
| Q1V2-C14 | Subsequent QG work found additional support-two subregimes at higher `n`; this does not affect `kappa_R6M=2` but forbids promotion of the R6Q two-trade finite classifier to a universal trade taxonomy. | `development/orion-qg-regime-geometry/QG_WAVE2_RECORD.md` | KNOWN LIMITATION / FOLLOW-UP CONTEXT |
| Q1V2-C15 | On the 30 recorded H4/equilibrium-N2 matchings, `C_DP=C_D++=C_D+=C_R6L`; R6Q diagnostics show the first two registered trade families are structurally unprofitable on those rows. | R6P/R6Q chemistry blocks | MACHINE_EVIDENCED |
| Q1V2-C16 | For equal-size split-TARE coefficient groups, sorting magnitudes and grouping contiguously minimizes `sqrt(m)*sum_g ||c_g||_2` by a direct majorization/Schur-concavity argument; deterministic verification reports zero failures across 8,700 partition evaluations. The classical majorization mechanism itself receives no novelty credit. | Analytic proof: `HUMAN_PROOF_R4B_MAJORISATION_2026-08-22.md`; receipt: `MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json` | THEOREM-GRADE SUPPORTING RESULT; coefficient coordinate only |
| Q1V2-C17 | Public H2O/cc-pVTZ DUCC (20 qubits, 8082 nonidentity Paulis) has a registered structural compiler point reducing `C 8078 -> 4972` (38.45%) at relative normalization overhead `9.087e-6`. | `MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json` | SUPPORTING real-Hamiltonian evidence; not full circuit/resource claim |
| Q1V2-C18 | The 2026-08-22 bounded hostile search did not locate a direct prior equivalent of the sharp `kappa_R6M=2` theorem, while identifying TARE, unitary partitioning, PCOAST, PHOENIX/Symphony and current block-encoding complexity papers as strong donor/adjacent literatures. | `NOVELTY_RESEARCH_2026-08-22.md` | BOUNDED_NOVELTY_RESEARCH |
| Q1V2-C19 | A standalone no-ORION-import sanity checker reconstructs the one-qubit phase-ignored Pauli algebra and independently reproduces the analytic finite cores: Restore `max ΔF3 = 2` over the 192 mathematically relevant cases with histogram `{-2:6,-1:48,0:84,1:48,2:6}`, and exactly four odd-alpha support-2 class failures with zero failures for supports 3 through 8. | `independent_human_proof_sanity.py`; `INDEPENDENT_HUMAN_PROOF_SANITY_RESULTS_2026-08-22.json` | INDEPENDENT IMPLEMENTATION SANITY; not external peer review |

## Forbidden promotions

- Do not describe TARE, Tag/Restore, anticommuting unitary partitioning, Pauli-frame compilation, BSF/Clifford support reduction, or generic Hamiltonian-simulation compilation as introduced here.
- `kappa_R6M=2` applies only to the frozen R6M grammar and frozen support-count objective. It is not a theorem for other objectives, R6I, larger Tag ranks, arbitrary TARE, or arbitrary Pauli/block-encoding compilers.
- R6Q/R6R do not establish an all-n two-trade taxonomy. Later QG counterexamples are already known and must be disclosed.
- The O(n^12) count is a cardinality bound on a direct normal-form frame candidate family, not a lower/upper bound on the complexity of the production DP.
- H2O, LiH, H4 and N2 results do not establish fault-tolerant physical-resource advantage.
- No internal authority string grants novelty or physical quantum advantage.

## Allowed flagship headline

> For the frozen three-block shared-Tag TARE-M2 compiler under its support-count objective, the exact optimum has a sharp intrinsic frame-support number of two for arbitrary system size: support >=3 can always be exchanged away without increasing cost, while an explicit two-qubit instance proves support one insufficient. The analytic proof fails precisely at the same weight-two coupling pattern realized by the optimal counterexample.
