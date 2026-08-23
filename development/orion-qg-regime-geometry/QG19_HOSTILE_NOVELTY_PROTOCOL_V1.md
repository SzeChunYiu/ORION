# QG-19 — the hostile external-novelty lane: which of our headline claims does the literature already own?

Date: 2026-08-22
Lane: ORION-QG / regime geometry, wave 3
Branch: `claude/orion-harness-verification-b17qdj`
Base revision: `c2b2b1ae`
Status: **FROZEN BEFORE ANY OUTCOME-DETERMINING SEARCH.**

Authority ceiling: **NOT_R6**. `novelty_authority: false` — and note the direction: this
lane can only ever *remove* novelty, never grant it. `physical_quantum_advantage_claim:
false`. No chemistry data is read. The protected stretched-N₂ discriminator
`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt` is never read.

**Network access: REQUIRED and EXPECTED.** This is the one lane in the programme that
must reach outside. Every retrieved item is recorded with its identifier, its retrieval
query, and the verbatim passage relied on. An item that cannot be quoted cannot be used.

Runtime cap: **< 60 minutes**. Search-call cap: **90 queries**, disclosed with the count
actually spent.

---

## 0. Why this lane exists, and why it is adversarial by construction

Every novelty freeze in this programme was authored **without literature access**. The
reopen adjudication classified that as `DONOR_SUBSUMPTION` **risk** — negative N6 — and
predicted the correcting move: a lane whose success condition is *finding that we were
scooped*. The external donor register (`QG_EXTERNAL_DONOR_REGISTER_V1.md`) was a first
pass and found a nearest miss (D1, complete equational theories) but was not run
hostilely: it searched for context, not for subsumption.

This lane inverts the incentive. **A subsumed claim is a successful outcome.** The lane is
scored on how much novelty it removes, and a run that removes none must state, per claim,
exactly which searches were run and came back empty — an empty result is only credible
if the search that produced it is inspectable.

## 1. The claims under attack, frozen

Each is stated here in the form a literature search must attack, with its receipt. No
claim may be added, softened, or withdrawn after the first search runs.

**C-A (QG-22 Q3, the structural criterion).** *Let F have a configuration space that
factorizes over n positions with fixed local alphabet size A, a feasibility predicate that
is a fixed-dimension conserved syndrome (homomorphism into a fixed finite abelian group of
order 2^D, D independent of n), and an objective that is a sum of per-position local
terms. Then the exact optimum is computable in time O(C_ext·2^{2D}·n + n·A^L) — linear in
n — by min-plus DP over the syndrome, deciding optimality costs the same order, and naive
enumeration costs Θ(A^{Ln}).* Receipt: `QG22_COMPLEXITY_SEPARATION_RESULTS.json` q3.
**Prior expectation: HIGH subsumption risk.** This has the shape of standard algebraic
dynamic programming / bounded-treewidth / fixed-parameter tractability, and the lane that
produced it labelled it `CONJECTURE` and "standard donor mathematics" itself.

**C-B (intrinsic support number κ).** *A two-sided family invariant: a support budget B
such that the family's optimum is realized at support ≤ B and provably not at B−1.
Measured κ_R6I = 1, κ_TARE = 2, both exactly and all-n.* Receipts: QG-9 V6 ladder, QG-18.
**Attack vector**: is "smallest budget at which an optimum is realizable, with matching
lower bound" a named invariant elsewhere — circuit complexity's support/locality measures,
matroid rank, sparse-recovery sparsity, tensor border rank, Boolean sensitivity?

**C-C (regime geometry as a five-component template).** *Donor-optimal region + elementary
trades with minimal witnesses + sufficiency bounds + decidable membership predicates +
prospective forecasts, as a reusable specification for characterizing where a compilation
family's optimum lives.* **Attack vector**: superoptimization surveys, equality saturation
(D2), cost-model taxonomies, the "optimization landscape" literature.

**C-D (κ ≠ syndrome rank; the rewrite-alignment failure).** *QG-20's finding that a
certified syndrome rank and a measured margin agree only under a rewrite mismatch, and
that rank − κ = μ fails on the rewrite the margins are actually measured under.*
**Attack vector**: is the rank/invariant-mismatch-under-rewrite phenomenon named in
rewriting theory, or in the ZX-calculus / stabilizer-simplification literature?

**C-E (the negative-history typology).** *`orion.kernel.negative`'s eight categories —
FAILED_DEFINITION, FAILED_DECOMPOSITION, NULL_ABLATION, HARMFUL_OVERUSE,
DONOR_SUBSUMPTION, FALSE_POSITIVE, INACTIVE_NO_ATOM_CONDITION,
UNRESOLVED_OR_NON_IDENTIFIABLE — as a first-class typed record of what failed and why.*
**Attack vector**: negative-results venues, provenance/experiment-tracking schemas
(PROV-O, ML metadata standards), the reproducibility literature, registered reports.

**C-F (the digest-custody-is-not-correctness finding).** *Matching a declared result digest
and replaying deterministically establishes integrity, never correctness, because a
deterministic bug replays exactly and a buggy analyzer emits a digest-valid receipt; so
corroboration strength must be a typed property that fails closed on overclaim.*
Receipt: `RECEIPT_CHURN_HAZARD_2026-08-21.md`, `orion_research_harness.corroboration`.
**Attack vector**: software supply-chain (SLSA, in-toto, reproducible builds), scientific
workflow provenance, proof-carrying code, verified compilation (CompCert).

## 2. Search protocol, frozen

For each claim C-A … C-F, in that order:

1. **Three query families, all three mandatory**: (i) the claim's own vocabulary; (ii) the
   claim's vocabulary translated into the *donor field's* terms, named in §1's attack
   vector; (iii) an inverted query searching for the claim's *negation* or for surveys of
   the area, which surfaces prior art that the direct query's phrasing hides.
2. Record every query verbatim with its result count, including queries returning nothing.
3. For each retrieved candidate, record: identifier (arXiv/DOI/venue+year), title, and the
   **verbatim passage** relied on. No passage, no verdict.
4. Assign exactly one verdict per candidate, from the frozen set in §3.
5. Assign exactly one **claim-level** verdict, which is the strongest candidate verdict
   found for that claim.

## 3. Verdict set, frozen

* `SUBSUMED` — a prior source states the claim, or a strictly more general one, in a form
  that covers our stated domain. The claim loses all novelty.
* `SUBSUMED_IN_SPECIAL_CASE` — a prior source covers a proper sub-domain of our claim.
  Novelty survives only outside that sub-domain, which must be named.
* `INSTANCE_OF_KNOWN_GENERAL` — the claim is a specialization of an established general
  result. Novelty is at most the specialization, and the general result must be cited.
* `NEAREST_MISS` — a prior source is close and must be cited and distinguished, with the
  distinguishing property named. Novelty survives, narrowed.
* `NO_PRIOR_ART_FOUND` — the three query families returned nothing that bears. This is
  **not** a novelty grant; it is a statement about the searches run, and it is only usable
  alongside the full query log.
* `CANNOT_ASSESS` — the source could not be retrieved or read. Recorded, never inferred.

## 4. Gates

* **G1 — no self-serving verdicts.** For every claim assigned `NO_PRIOR_ART_FOUND`, all
  three query families must be present in the log with their verbatim queries and result
  counts. A missing family fails the gate.
* **G2 — no verdict without a quote.** Every non-`NO_PRIOR_ART_FOUND` verdict binds a
  verbatim passage. Paraphrase fails the gate.
* **G3 — no novelty granted.** The RESULTS file must not contain any statement that a
  claim *is* novel. The only permitted directions are subsumed, narrowed, or unresolved.
* **G4 — prior expectation recorded before the search.** §1's HIGH-risk annotation on C-A
  is frozen here; the results must state whether each prior expectation was borne out. A
  lane that finds exactly what it expected everywhere is reporting its priors, not the
  literature, and must say so.
* **G5 — hostile-source admission.** A source that *contradicts* one of our results, as
  opposed to anticipating it, is recorded under `contradicting_sources` and never
  discarded as off-topic.
* **G6 — no retrieval laundering.** Nothing may be cited that was not retrieved in this
  run and logged in §2. Prior knowledge of a reference is not retrieval, and a citation
  recalled rather than fetched is `CANNOT_ASSESS`.
* **G7 — cap disclosure.** Queries spent, sources retrieved, sources unreachable, and
  every claim left at `CANNOT_ASSESS`, all reported with counts.
* **G8 — authority ceiling.** NOT_R6; `novelty_authority: false`.

## 5. Terminals, frozen

* `QG19_SUBSUMPTION_FOUND__NOVELTY_REDUCED` — at least one claim is `SUBSUMED` or
  `INSTANCE_OF_KNOWN_GENERAL`. **The success branch.**
* `QG19_NARROWED__NEAREST_MISSES_ONLY` — no outright subsumption, but nearest misses
  narrow one or more claims and are now bound as required citations.
* `QG19_NO_SUBSUMPTION_FOUND__SEARCHES_LOGGED` — the searches ran and returned nothing
  bearing. Credible only with the complete G1 log, and grants nothing.
* `QG19_BLOCKED__NO_NETWORK` — retrieval unavailable. The lane produces a query plan and
  no verdicts, and every claim stays `CANNOT_ASSESS`.

## 6. Files this lane may create

1. `development/orion-qg-regime-geometry/QG19_HOSTILE_NOVELTY_RESULTS.json`
2. `development/orion-qg-regime-geometry/QG19_QUERY_LOG.md`
3. `development/orion-qg-regime-geometry/QG_EXTERNAL_DONOR_REGISTER_V2.md` — the register
   updated with everything this lane retrieved, superseding V1 without deleting it.

No other repository file is created or modified.

## 7. What this lane cannot do

It cannot establish that anything is novel. It cannot raise any authority. It cannot
change a prior claim's receipt — a subsumed claim is recorded as subsumed in this lane's
results and in the wave record, and the original receipt stands as issued with the
subsumption scored against it. It cannot read the protected subject.
