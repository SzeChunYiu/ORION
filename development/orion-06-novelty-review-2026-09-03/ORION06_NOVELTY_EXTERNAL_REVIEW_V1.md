# ORION-06 — gate [2] novelty / external-authority review (V1)

Date: 2026-09-03
Reviewer method: independent read-only pass over the repo records (session worktree,
no checked-out branch modified), followed by an external literature survey
(14 distinct web queries + 12 successful arXiv abstract fetches + 2 blocked
citation-API attempts; full log in Section 3).
Gate identity: `papers/orion-06-recursive-recovery/revival/ORION06_NEGATIVE_REVIVAL_R1_SUCCESSOR.json:39-43`,
`remaining_gates[2] = "current independent novelty and external-authority review"`.
This document discharges exactly that gate item and nothing else.

## 0. Authority boundary (read first)

- `novelty_authority = false` for this review, matching the receipts under review
  (`development/orion-06-r5b-prospective-fresh-subject-2026-09-02/O6R5BNS1_RESULTS.json`
  `novelty_authority: false`; PR #2169 `O6R4CNS1_RESULTS.json` `novelty_authority: false`).
- This review does **not** adjudicate venue-worthiness, submission decisions, paper
  acceptance, or the manuscript's framing. It answers one question only: *does published
  prior work already own the mathematical object that the R4C/R5B confirmations
  instantiate?*
- It is a bounded search statement, not a novelty certificate. Absence claims in
  Section 6 carry their justified scope; "could not check" is never reported as
  "checked and fine".

## 1. Claim distillation (what is actually being confirmed)

### 1.1 The mechanism

Both tier-B confirmations instantiate one mechanism, named
**controlled-select-aware exact-representation-and-rematching** in the R1 revival
protocol (`papers/orion-06-recursive-recovery/revival/ORION06_NEGATIVE_REVIVAL_R1_PROTOCOL.json`,
R5B attempt lever). Implementation:
`papers/orion-06-recursive-recovery/revival/orion06_negative_revival_r1.py` (on main).
The object decomposes as:

1. **Exact pair representations** for a Pauli-sum (Jordan–Wigner molecular) Hamiltonian
   batch of `2L` terms: for each pair of terms `(P_i, P_j)` with coefficients,
   - anticommute → `DIRECT_ANTI_UNITARY` representation, pair λ = `hypot(|a_i|,|a_j|)`;
   - commute → `TARE_M2` witness `(R0, R1, S, T0, T1)` with obligations
     `R0 ⊳ R1` (anticommute), `S ~ R0` (commute), `S ⊳ R1`, `T0·R0 = P_i`, `T1·R1 = P_j`,
     pair λ = `sqrt(2)·hypot(|a_i|,|a_j|)`
   (`orion06_negative_revival_r1.py:351` `_pair_lambda`; witness checks asserted, not logged).
   This is the m=2 case of the donor construction Tag→U_anti→Restore (Section 4, item 1).
2. **Canonical parent**: `canonical_pair_witness`
   (`orion06_negative_revival_r1.py:207`) = minimum-internal-cost witness per edge,
   orientation tie-broken.
3. **Controlled-select-aware frontier**: `controlled_pair_frontier`
   (`orion06_negative_revival_r1.py:330`, DP in `_controlled_orientation_frontier:285`)
   = an *exact multiobjective dynamic program over 8 symplectic parity states × 2
   orientations* that returns, per pair edge, a Pareto frontier of
   `(parity_CNOT, controlled_Pauli_support)` representations — not a single choice.
4. **7-coordinate resource vector** `POINT_COORDS`
   (`orion06_negative_revival_r1.py:31`) =
   `(Lambda_joint, parity_CNOT, controlled_Rz, controlled_H, controlled_Pauli_support,
   AND2_compute_uncompute_pairs, max_extra_conjunction_scratch)` — a non-scalar cost
   certificate, deliberately not projected to one number.
5. **Rematching**: the candidate space is *all perfect matchings of the batch × all
   products of per-edge frontier choices* (6 terms → 15 matchings; 14 terms → 135,135
   matchings), aggregated by `_aggregate_matching` (`:596`) and Pareto-pruned by
   `_pareto_points` (`:387`) under `_point_dominates` (`:377`).
6. **Strict parent dominance (the decision rule, frozen verbatim)**: budget =
   `1.01 × min parent Lambda_joint + 1e-12`; a candidate point is *strict* iff it is
   in budget, **not dominated by any parent point, and strictly dominates ≥1 parent
   point** on the 7 coordinates. Terminal vocabulary frozen
   (`O6R5BNS1_PROTOCOL_V1.md:148`, PR #2169 protocol Section 6).

### 1.2 What "prospective fresh-subject confirmation" means here

Frozen in `development/orion-06-r5b-prospective-fresh-subject-2026-09-02/O6R5BNS1_PROTOCOL_V1.md`
(merged to main via PR #2154; the R4C twin protocol is on the open PR #2169 branch):

- subject selection is deterministic and was frozen using **only git tree/blob
  metadata** (paths + blob ids, no coefficients) of an external public library
  before any mechanism quantity was computed (`O6R5BNS1_PROTOCOL_V1.md:36-48`);
- the **stage-1 parent envelope digest is printed before any candidate/frontier
  computation** (module-flag enforced; `:113-133`; receipts record
  `stage1_digest_before_candidates = true`);
- blob-verified fetch of the subject (observed git blob == pinned `ls-tree` blob);
- frozen machinery imports only (`:97-111`) — no local constants;
- frozen terminal vocabulary with no post-hoc weakening (`:148-161`);
- both runs disclaim: `novelty_authority=false`, `physical_quantum_advantage_claim=false`,
  `r6=false`, `new_molecule_family=false`.

### 1.3 The two confirmations and their exact measured quantities

**R5B — study O6R5BNS1 (PR #2154, merged; on main).**
Subject: `Benzene/cc-pVDZ/FrozenCoreCCSD_6Elec_6Orbs/DUCC3/...ducc.results.txt`
from `npbauman/DUCC-Hamiltonian-Library` @ `be306f58...` (blob `cd32e1e7...`,
12 qubits, 394 terms; 6-term pairwise-commuting window batch; never read before).
Measured (`O6R5BNS1_RESULTS.json`; anchors `:367` min λ, `:369` budget, `:633` terminal):
15 parent points (canonical witnesses × 15 matchings; pruned parent Pareto = 1 point,
`controlled_Pauli_support = 14`), 216 candidate points (15 matchings × per-edge
frontier products), 5 in-budget Pareto points, **exactly 1 strict parent-dominating
point**: `Lambda_joint = 0.46946892175304483` (identical to the parent minimum λ),
`controlled_Pauli_support = 13` (−1), `AND2 = 6`, `controlled_H = 9`, `controlled_Rz = 9`,
rematched matching `[[4,7],[11,72],[73,74]]`, all witness checks pass.
Terminal: `ORION06_R5B_NS1_PROSPECTIVE_STRICT_PARENT_DOMINANCE_CONFIRMED__ONE_FRESH_FILE_ONLY`.
Result digest `eb2d01aa...`.

**R4C — study O6R4CNS1 (PR #2169, OPEN; branch `tierb/o6r4c-ns1`, NOT on main).**
Files: `development/orion-06-r4c-prospective-fresh-subject-2026-09-03/{O6R4CNS1_PROTOCOL_V1.md,
O6R4CNS1_RESULTS.json, O6R4CNS1_RUN.log}` + `research/extensions/orion-q/max_o6_r4c_prospective_fresh_subject.py`.
Subject: `script.ipynb` cell 0 from the `SNIPRS/hamiltonian` public notebooks
(blob `dd8fd9df...`, 4 qubits, 14 terms; never read before; blob-verified).
Measured (fetched from the PR branch, `fresh_replay` block): 91 pair edges,
135,135 matchings, parent = min-`legacy_Lambda` point
(`Lambda_joint = 1.575097140091084`, `controlled_Pauli_support = 45`), and **exactly 1
strict point**: `Lambda_joint = 1.575097140091084` (identical), `controlled_Pauli_support = 41`
(−4), rematched matching `[[1,2],[3,4],[5,8],[6,7],[9,10],[11,12],[13,14]]`.
Terminal: `ORION06_R4C_NS1_PROSPECTIVE_STRICT_PARENT_DOMINANCE_CONFIRMED__ONE_FRESH_NOTEBOOK_ONLY`.
The committed-subject control in the same receipt terminates
`ORION06_R4C_ACTUAL_RESOURCE_PARENT_DOMINATED__OPEN_SUBJECT_ONLY` — the rule demonstrably
does not confirm everywhere (hostile control bites).

**What the confirmed claim therefore is** (narrow): *on a prospectively selected,
never-read external subject, exact enumeration of per-pair controlled-select-aware
representation frontiers crossed with perfect-matching re-pairing contains a point
that strictly Pareto-dominates the canonical-witness parent envelope on a 7-coordinate
resource vector at unchanged joint λ within a frozen 1.01× budget.* It is a claim
about an exact combinatorial certificate, **not** a λ-reduction claim (λ is equal in
both strict points) and not an asymptotic/physical-advantage claim (receipts disclaim both).

## 2. Survey scope and method

- Engine: general web search (Google-indexed arXiv/npj/Nature/journal pages), then
  per-hit `arxiv.org/abs/` abstract fetches. Date: 2026-09-03.
- Every query run is logged verbatim in Section 3, including null results.
- Follow-up: forward-citation trail of the closest donor (TARE) attempted via
  Semantic Scholar API — blocked (2× HTTP 429; page mirror 404). Recorded as
  *could-not-check*, not as a clean absence.
- Full texts were NOT read for any item; all mechanism assessments below are
  abstract-level plus (for TARE) repo-quoted donor conclusions
  (`development/orion-q-max-r0/MAX_R6_NOVELTY_SATURATION_PREAUDIT.md:30-47`).
  Where that matters it is flagged per item.

## 3. Query log (verbatim, ordered)

Web queries (14):
1. `unitary partitioning anticommuting Pauli strings grouping quantum chemistry Izmaylov Yen` → hit: Izmaylov et al., arXiv:1907.09040 (unitary partitioning, VQE measurement origin); Verteletskyi–Yen–Izmaylov arXiv:1908.11857; Motta et al. low-rank arXiv:1808.02625.
2. `anticommuting Pauli terms exponential single unitary quantum simulation low rank electronic structure` → hit: anticommuting-set simulation line (Motta et al.; Zhao–Yuan).
3. `grouped qubitization anticommuting groups LCU 1-norm lambda minimization quantum simulation` → hit: Loaiza et al. arXiv:2304.13772 (anticommuting grouping = greatest 1-norm reduction among studied techniques); BLISS arXiv:2409.18277; ORBIT line.
4. `pairing Pauli operators perfect matching Hamiltonian simulation cost minimization anticommuting pairs` → NULL for Pauli-pair LCU matching (matches surfaced only QEC-side matching uses).
5. `tradeoff between LCU normalization factor lambda and circuit gate cost block encoding exact compilation Pareto` → no per-pair exact-frontier work; perspective pieces (arXiv:2511.16738) and FOQCS-LCU tradeoff framing.
6. `DUCC downfolded Hamiltonian library quantum computing active space Bauman github` → verified external library `npbauman/DUCC-Hamiltonian-Library` (PNNL/Bauman line) — the R5B donor of subjects.
7. `SELECT oracle cost Pauli strings qubitization electronic structure Toffoli optimization Babbush` → Babbush et al. qubitization/low-rank SELECT-cost accounting line.
8. `Swierkowska Pareto optimality quantum circuit compilation multi-objective heuristic optimization` → multi-objective quantum compilation exists (heuristic, circuit-level), not per-pair representation frontiers.
9. `circuit implementation cost anticommuting Pauli group unitary partitioning simulation T gates exponentiation` → implementation-cost analyses of anticommuting groups (supports donor-owns-cost-accounting).
10. `"SNIPRS/hamiltonian" github quantum chemistry notebooks` → verified external repo (R4C subject/control source).
11. `"Tag-and-Restore" OR "TARE" block encoding Pauli 2026 follow-up improved auxiliary family selection` → TARE arXiv:2601.05740 (v4); no located follow-up paper optimizing auxiliary families.
12. `"perfect matching" Pauli terms pairs LCU lambda minimization assignment problem quantum chemistry Hamiltonian` → NULL (engine: "exact phrase combination didn't return a single paper matching all terms"); minimum-weight perfect matching appears only in QEC contexts (e.g. arXiv:2411.10406).
13. `arXiv 2601.05740 cited by Fraunhofer block encoding Pauli strings quantum circuits` → partial citation trail; surfaced Zhao–Yuan arXiv:2103.07988 as the anticommutation-LCU anchor.
14. `"Exploiting anticommutation in Hamiltonian simulation" Quantum Journal` → confirmed Zhao & Yuan, Quantum 5, 534 (2021).

Fetches (12 successful, all arXiv abstract pages; 2 blocked):
`arxiv.org/abs/2601.05740` (TARE) · `2507.20887` (FOQCS-LCU) · `2608.11579` (Symphony) ·
`2606.06070` (Fujiwara et al.) · `2601.11418` (matching-decomposition name collision) ·
`2605.23358` (ChannelIR) · `2607.01843` (Zhang–Shao) · `1803.06987` (Rengaswamy et al.) ·
`2103.07988` (Zhao–Yuan) · `2510.08644` (Liu et al.) · `2510.13573` (Li et al.) ·
`2511.16738` (perspective, search-mediated).
Blocked: `semanticscholar.org/arxiv/2601.05740` (404);
`api.semanticscholar.org/graph/v1/paper/arXiv:2601.05740/citations` and `.../paper` (HTTP 429 ×2).

## 4. Prior-art table

Overlap classes: **FAITHFUL (same object, component-level)** — the item owns that
component of the mechanism as its own contribution; **ADJACENT** — related mechanism,
different mathematical object; **NAME-COLLISION / SURFACE** — keyword overlap only.

| # | Item (authors, year, venue) | URL | Verified | Overlap |
|---|---|---|---|---|
| 1 | TARE — Schillo, Sturm, Quay (2026, arXiv v4; Fraunhofer IAF line) | https://arxiv.org/abs/2601.05740 | abstract fetched | **FAITHFUL (pair blocks, λ formula, composition)** |
| 2 | Exploiting anticommutation in Hamiltonian simulation — Zhao & Yuan (2021, Quantum 5, 534) | https://arxiv.org/abs/2103.07988 | abstract fetched | **FAITHFUL (anticommutation→LCU-cost insight)** |
| 3 | Unitary partitioning — Izmaylov et al. (2019, arXiv:1907.09040) + precursor arXiv:1908.11857 | https://arxiv.org/abs/1907.09040 | search-verified | FAITHFUL (Σa_jP_j = ‖a‖·U for anticommuting groups) |
| 4 | λ-minimization line — Loaiza et al. (2023, arXiv:2304.13772); BLISS (2024, arXiv:2409.18277); ORBIT | https://arxiv.org/abs/2304.13772 · https://arxiv.org/abs/2409.18277 | search-verified | ADJACENT (minimizes λ; ours holds λ frozen) |
| 5 | FOQCS-LCU — Dicke-state SELECT (2025) | https://arxiv.org/abs/2507.20887 | abstract fetched | FAITHFUL (controlled-SELECT layer) |
| 6 | Fujiwara, Yamamoto, Ishikawa — controlled time-evolution sign-flip grouping (2026) | https://arxiv.org/abs/2606.06070 | abstract fetched | ADJACENT (removes repeated ancilla control) |
| 7 | Symphony — global BSF Pauli-sequence compiler (2026) | https://arxiv.org/abs/2608.11579 | abstract fetched | ADJACENT (global compilation; Pareto-flavored claims) |
| 8 | Rengaswamy et al. — symplectic Clifford synthesis (2018) | https://arxiv.org/abs/1803.06987 | abstract fetched | ADJACENT (enumerate+optimize over symplectic realizations) |
| 9 | Zhang–Shao — low-ancilla block encodings (2026) | https://arxiv.org/abs/2607.01843 | abstract fetched | ADJACENT (ancilla-aware construction) |
| 10 | Liu, Zhu, Low, Lin, Yang — low-gate second-quantized block encoding (2025) | https://arxiv.org/abs/2510.08644 | abstract fetched | ADJACENT (different access model; no Pauli-pair/frontier objects) |
| 11 | Li, Tang, Hovland, Liu — Non-Clifford Fusion (2025) | https://arxiv.org/abs/2510.13573 | abstract fetched | ADJACENT (group conjugation + simultaneous synthesis; no pairwise matching, no LCU λ, no multi-objective vector) |
| 12 | ChannelIR — Huang, Gao, Zhou, Ying (2026) | https://arxiv.org/abs/2605.23358 | abstract fetched | ADJACENT (channel-first compilation; different object) |
| 13 | Motta et al. — low-rank electronic structure (2021, npj QI) | https://arxiv.org/abs/1808.02625 | search-verified | ADJACENT (different low-rank route) |
| 14 | "Matching decomposition" for quantum walks (2026) | https://arxiv.org/abs/2601.11418 | abstract fetched | NAME-COLLISION (graph-edge matching, not Pauli-term pairing) |
| 15 | `npbauman/DUCC-Hamiltonian-Library` (public library) | https://github.com/npbauman/DUCC-Hamiltonian-Library | search-verified | source of subjects (not a mechanism competitor) |
| 16 | `SNIPRS/hamiltonian` notebooks (public repo) | https://github.com/SNIPRS/hamiltonian | search-verified | source of subjects (not a mechanism competitor) |

## 5. Per-item mechanism-level assessment

1. **TARE (arXiv:2601.05740)** — closest item. The R4C/R5B `TARE_M2` witnesses ARE
   the m=2 instances of this donor's construction (tag → mutually anticommuting
   auxiliary frame `R_k` → `U_anti` → restore via `T_k R_k = P_k`), including the
   `sqrt(m)·‖α‖₂` normalization (m=2 → the `sqrt(2)·hypot` pair λ) and LCU
   composition of split encodings. Direct anticommute-pair handling
   (`DIRECT_ANTI_UNITARY`, λ = `hypot`) is the older anticommuting-unitary identity
   (items 2–3). **Owner of the pair-level mathematical object.** Repo-quoted donor
   conclusions (pre-audit lines 39–47; abstract verified directly, conclusion text
   repo-mediated): the donor itself flags splitting/partitioning as unexplored, fixes
   a canonical auxiliary family in its numerics, and names choosing `{R_k}` to
   maximize matches as future work — i.e. even the rematch/auxiliary-selection
   direction is donor-flagged open territory, which the paper must cite as the
   residual it instantiates, not as territory it discovered.
2. **Zhao & Yuan 2021 (Quantum 5, 534)** — owns the quantitative seed: mutually
   anticommuting Pauli sets are cheap to simulate; modified LCU methods exploit
   this, with numerics on electronic Hamiltonians. Abstract does not mention pair
   matching, controlled-SELECT cost, exact per-pair frontiers, or strict-dominance
   certificates (full text not read — see Limitations). **Owner of the
   "anticommutation reduces LCU cost" insight** that makes the whole λ-side meaningful.
3. **Unitary partitioning (Izmaylov et al. 1907.09040; Verteletskyi–Yen–Izmaylov
   1908.11857)** — owns `Σ_{j∈G} a_j P_j = ‖a_G‖·U_G` for anticommuting groups and
   clique/graph partitioning over Pauli sets. **Owner of group-level identity and
   the grouping-as-combinatorial-optimization viewpoint.**
4. **λ-minimization line (Loaiza 2304.13772; BLISS 2409.18277; ORBIT)** — owns
   "choose groupings/orbital frames to shrink the 1-norm". Orthogonal direction to
   the confirmed claim: those methods *change λ*; R4C/R5B hold λ frozen and improve
   the controlled-resource vector at equal λ. No frontier-of-representations object.
5. **FOQCS-LCU (2507.20887)** — owns fast one-qubit-controlled SELECT
   (Dicke-state-based) — the outer-control layer that makes "controlled-select-aware"
   a meaningful cost axis. Does not choose pair representations or rematch.
6. **Fujiwara et al. (2606.06070)** — recursive binary-symplectic grouping assigning
   sign-flip Paulis to remove repeated ancilla control in *controlled time
   evolution*. Same cost axis (control overhead), different object (no pair
   representations, no λ budget, no matching enumeration).
7. **Symphony (2608.11579)** — global binary-symplectic simplification/rescheduling
   of Pauli-exponential sequences with strong two-qubit reductions and
   dominance-flavored comparisons. Downstream compilation of a *given* sequence;
   does not re-pair terms or bound λ.
8. **Rengaswamy et al. (1803.06987)** — enumerate-and-optimize over symplectic
   realizations (Clifford synthesis). Same "exact DP over symplectic parity states"
   flavor as `_controlled_orientation_frontier`, different target (Clifford/CNOT
   synthesis vs controlled-Pauli-support of pair representations).
9–13. **Zhang–Shao / Liu / Li / ChannelIR / Motta** — adjacent routes (ancilla-aware
   constructions, second-quantized oracles, T-count group synthesis, channel-first
   compilation, low-rank). None contains the pair-frontier × rematch × strict
   dominance object.
14. **arXiv:2601.11418** — pure name collision ("matching decomposition" = graph-edge
   matching for quantum walks).

## 6. Verdict

**PARTIAL_OVERLAP.**

No located donor jointly owns the full confirmed conjunction —
*(a) exact per-pair multiobjective frontiers of controlled-select-aware
representations, (b) perfect-matching re-pairing as the candidate space, (c) a
7-coordinate strict parent-dominance certificate at frozen λ inside a
pre-registered 1.01× budget, (d) wrapped in prospective fresh-subject epistemics on
external public libraries* — but every major component has a donor owner:

- pair blocks + λ formula + LCU composition: **TARE** (arXiv:2601.05740);
- anticommutation→LCU-cost insight: **Zhao–Yuan 2021** (arXiv:2103.07988);
- anticommuting-group identity & grouping optimization: **unitary partitioning**
  (arXiv:1907.09040, arXiv:1908.11857), λ-line (arXiv:2304.13772, arXiv:2409.18277);
- controlled-SELECT layer: **FOQCS-LCU** (arXiv:2507.20887); control-overhead
  reduction: **Fujiwara et al.** (arXiv:2606.06070);
- global Pauli-sequence compilation: **Symphony** (arXiv:2608.11579);
- symplectic enumerate+optimize: **Rengaswamy et al.** (arXiv:1803.06987).

Residual (the part not found elsewhere in the searched neighborhood): the *exact
conjunction* — per-pair frontier DP × full rematch enumeration × non-scalar strict
dominance at unchanged λ × prospective external-subject confirmation contract.
Additionally, TARE's own stated future-work (auxiliary-frame selection to maximize
matches; splitting/partitioning) means the rematch direction is donor-anticipated;
the defensible residual is the *exact-frontier + strict-dominance certificate +
prospective epistemics packaging*, and the manuscript should claim exactly that
scope and cite TARE's future-work paragraph when doing so. This matches and
independently confirms the repo's own bounded statement
(`development/orion-q-max-r0/MAX_R6_NOVELTY_SATURATION_PREAUDIT.md:80-84`).

Consequence for the gate: gate [2] is discharged with PARTIAL_OVERLAP recorded;
the paper's tier-B record should present R4C/R5B as *mechanism confirmations on
donor-owned primitives* (as its receipts already do via `novelty_authority=false`),
not as new block-encoding primitives.

## 7. Limitations and justified-absence scope

- **Abstract-level assessment.** All items were assessed from fetched arXiv
  abstracts (plus repo-quoted TARE conclusions). Specific exposure: Zhao–Yuan 2021
  or TARE v4 body text could contain matching- or frontier-like constructions not
  visible in abstracts. This is a *could-not-check*, not a checked-and-fine.
- **Forward-citation trail of TARE blocked.** Semantic Scholar API returned HTTP 429
  twice and the page mirror 404; no systematic "who cites TARE" enumeration was
  possible. No Google Scholar / OpenAlex API was queried.
- **Absence scope.** "No located donor owns the conjunction" is relative to: the
  14 logged queries (Section 3) on 2026-09-03 over Google-indexed arXiv/journal
  pages, plus the 12 abstract fetches. It is not a claim over paywalled-only
  literature, non-indexed preprints, or post-2026-09-03 appearances.
- **Two confirmations, small subjects.** R5B = one 12-qubit benzene-family file
  (new blob, same molecule family — the protocol itself freezes this honest-scope
  note, `O6R5BNS1_PROTOCOL_V1.md:92-95`); R4C = one 4-qubit, 14-term notebook, and
  its artifacts are on an open PR branch, not main. Novelty of the mechanism is
  independent of subject size, but external validity of the confirmations is
  bounded by these two subjects — a question for other gates, not this one.
- **This review's authority.** `novelty_authority = false`. No venue-worthiness,
  submission, or freeze decision follows from this document; those belong to the
  programme's governance, per the receipt contract in
  `papers/orion-06-recursive-recovery/manuscript/sections/02-methods.tex` (Methods,
  "Typed failure and authority").
