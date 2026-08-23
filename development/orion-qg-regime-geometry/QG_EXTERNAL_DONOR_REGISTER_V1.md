# ORION-QG external donor register V1 — first literature check with actual search access

Date: 2026-08-21. Branch: `claude/orion-harness-verification-b17qdj`.
Authority: development record only. This register **lowers** claims; it grants nothing.

## Why this document exists

Every QG lane froze a "novelty threat" file asserting that a hostile search found no close
parent for the combined regime-geometry object. Those assertions were made by lane agents
with **no literature-search access** — they were reasoned self-assessments over the team's
own prior knowledge, not searches. This is the first check run against an actual paper
corpus (arXiv ~2.5M via alphaXiv; ~200M via Consensus). It is still **not peer review**,
and `novelty_authority` remains **false** everywhere.

## Donors found that the lane freezes did NOT name

### D1 — Complete equational theories for quantum circuit fragments (NEAREST MISS)

An active 2025–2026 literature proves **finite complete rewrite bases** for circuit
fragments:

- *A Complete Equational Theory for Real-Clifford+CH Quantum Circuits* (arXiv 2602.06644,
  CNRS / Paris-Saclay / Inria / ENS Paris-Saclay, 2026-02-06)
- *Simpler Presentations for Many Fragments of Quantum Circuits* (arXiv 2602.09874, Inria,
  2026-02-10)
- *Polycontrolled PROPs for Qudit Circuits: A Uniform Complete Equational Theory for
  Arbitrary Finite Dimension* (arXiv 2602.09873, 2026-02-10)
- *Completeness for Prime-Dimensional Phase-Affine Circuits* (arXiv 2603.06466, 2026-03-06)
- *Completeness for flow-preserving rewrite rules* (arXiv 2608.13035, 2026-08-13)
- *A complete set of transformation rules for reversible circuits* (arXiv 2508.17273,
  Sun Yat-Sen University, 2025-08-24)

**Why it is the nearest miss.** QG's headline phrasing — "a complete finite basis of
elementary trades" — reads as a completeness claim about a rewrite system, which is
exactly this literature's object.

**The distinction that survives, stated precisely.** Equational completeness means the
rule set derives every semantic **equality** between circuits. QG's trade basis is a claim
about **cost extrema**: that a finite set of structural configurations attains the
**optimum** of a frozen objective. Neither implies the other — a complete equational
theory says nothing about which member of an equivalence class is cheapest, and a complete
trade basis need not generate all equalities. **Required correction going forward:** QG
prose must say "complete *trade* basis (optimum-attaining), not an equational-completeness
result", and cite this literature when the word "complete" appears near "basis".

### D2 — Exact synthesis with unconditional optimality

*High-Performance Exact Synthesis of Two-Qubit Quantum Circuits* (arXiv 2601.19166,
2026-01-27) — "exact synthesis provides unconditional optimality and canonical structure,
but is often limited to small, carefully scoped regimes."

**Distinction.** Exact synthesis *achieves* an optimum. QG *characterizes the region where
a cheaper canonical construction already attains it*, without running the optimizer. The
QG exact referees (DP, brute) are instances of this donor and receive **zero** novelty
credit — which the freezes did already state for the referees, but not by naming this line.

### D3 — Undecidability of phase ordering (context that strengthens, not threatens)

*On the decidability of phase ordering problem in optimizing compilation* (Touati et al.,
2006, ~50 citations) proves optimal phase-ordering is **undecidable** in general, with
restricted decidable instances.

**Reading.** QG's decidable exact membership predicates (P0, P1, the cones) are interesting
*because* of this backdrop: they are decidable optimality characterizations inside a
restricted family. QG must not claim decidability results in general compilation, and
should cite this as the reason the restriction is doing real work.

### D4 — Exhaustive optimal-vs-heuristic characterization in classical compilers

*Understanding and exploiting optimal function inlining* (Theodoridis et al., ASPLOS 2022,
~37 citations) — exhaustively finds optimal inlining decisions (search space reduced
2³⁴⁹ → 2²⁵) and measures the gap to LLVM's strategy.

**Closest methodological parent overall.** They exhaustively characterize optimal vs
heuristic on real workloads. **Distinction:** they respond to the gap with *autotuning*;
they do not produce a structural predicate saying when the heuristic is already optimal.
QG's contribution relative to D4 is the predicate/regime map, not the exhaustive study.

### D5 — Global binary symplectic simplification (already absorbed)

*Efficient Compilation for Hamiltonian Simulation via Global Binary Symplectic Form
Simplification* (arXiv 2608.11579, 2026-08-12) — the Symphony/PHOENIX++ line the QG
freezes already name as zero-credit donor territory. Confirmed present and correctly
absorbed.

## What survived the check

No paper surfaced that produces, for a compilation family, the **bundle**: donor-optimal
region + minimally-witnessed elementary trade basis + all-n sufficiency bound + decidable
structure-only membership predicate + prospectively-confirmed cost forecast. The candidate
contribution stated in `PROGRAMME_CHARTER_V1.md` therefore stands as a **candidate** after
a real search, which is strictly more than it could claim before today.

The **intrinsic support number** framing (QG-paper-03) — κ as a two-sided family invariant,
with κ_R6I = 1 machine-checked — also found no parent. It is closest to D1's "normal form"
results, which bound *representations*, not *optima*.

## What this register does NOT establish

- It is a search by the same team that produced the claims; not peer review, not adversarial.
- Two search backends, ~10 queries. Absence of a hit is weak evidence of absence.
- Nothing here touches the deeper limitation recorded in the wave-2 record and the papers:
  every QG grammar (R6M, R6I, TARE, SixLCU, StabPrep) is **defined by this programme**, and
  on real DUCC chemistry every scanned batch is donor-exact — the machinery has not yet
  found a real-world instance where it beats the simple construction.
- `novelty_authority: false` and `physical_quantum_advantage_claim: false` remain correct
  in every receipt and must not be flipped on the strength of this document.

## Required actions

1. QG-paper-01 and QG-paper-03: cite D1 where "complete basis" appears and state the
   optimum-attaining vs equational-completeness distinction explicitly. Cite D3 beside every
   decidable-predicate claim, D4 as the closest methodological parent.
2. Future lane novelty freezes must name D1–D5 explicitly as absorbed prior art.
3. Registered successor **QG-19**: a hostile external-novelty lane run *against* the
   corpus rather than from memory — adversarial queries designed to find a parent, with the
   query set frozen before searching, and any close parent reported as a first-class
   donor-absorption terminal.
