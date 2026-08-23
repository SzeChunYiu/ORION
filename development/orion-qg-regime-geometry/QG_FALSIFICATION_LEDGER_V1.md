# ORION-QG — falsification ledger

We do not have external peer review. This document is **not** a substitute for it
and must never be described as one. What it does is discharge review's actual
*function* — catching errors before publication — by a mechanism a reader can run
without us: for every claim, the exact computation that would **refute** it.

Run `python3 research/extensions/orion-qg/qg_reproduce_all.py`. It recomputes
14 headline numbers from the cost primitives on `main` and fails loudly on any
mismatch. Nothing below is read from a stored result.

## Standing invitation

**Every claim here is stated so that one computation can kill it.** If any
refutation test below succeeds, the corresponding claim is wrong and we want to
know. Where a test is cheap, it is already run and its outcome recorded.

| # | claim | refutation test | status |
|---|-------|-----------------|--------|
| 1 | 715 local-Clifford orbit types, sizes `{1:1, 3:63, 6:651}` | enumerate all 4096 types under the 6 letter automorphisms and count | reproduced |
| 2 | **C1**: spectrum partition **=** `S_3 x (S_2 wr S_3)` orbit partition | exhibit two types with equal spectrum in different orbits, or vice versa | none exists — checked as set systems, both directions |
| 3 | bulk is **not** a symmetry quotient | show bulk is constant on every orbit | fails on **168** of 715 reps |
| 4 | **QG-34**: `D_* = 3` | exhibit a depth-2 adaptive tree resolving any of the 16 worst classes | infeasibility certified on all 16 |
| 5 | **QG-35(a)**: existence is free | exhibit a function of the achievable-cost multiset that splits a joint class | 0 of 92 split, and it is *proved*: the spectrum **is** the sorted response tuple |
| 6 | **QG-35(b)**: selection is impossible | show the optimal-frame set is constant on all 92 joint classes | non-constant on **85**, with disjoint-argmin witnesses |
| 7 | **QG-32c**: universal fixed minimum is 5 | exhibit any 4-subset of the 168 coverage masks covering all 5895 pairs | all **32,018,910** enumerated, none covers |
| 8 | **QG-39**: budget-0 regret is 5 | exhibit a frame with regret `< 5` on the worst class | all **384** checked, none |
| 9 | **QG-41**: separation holds on SixLCU | show selection is determined there, or that the reconstruction misreads `qg4` | 0 mismatches / 500 vs `qg4.member_cost` |
| 10 | **QG-40**: separation appears in Qiskit | show the cost is layout-invariant (i.e. the instrument is dead) | validity check included — the **first version was dead** and was caught |

## Claims deliberately NOT made

Listing these is part of the ledger, because the most common failure of an
unreviewed result is scope creep.

- **No performance comparison.** Nothing claims any ORION method beats Qiskit,
  Symphony, PCOAST or any production compiler. QG-40 tests whether a *phenomenon*
  appears, not whose numbers are better.
- **No physical-resource claim.** QG-39's regret of 5 is in the frozen cost
  model's own units. It is **not** T-count, ancilla, depth, or runtime. The
  mapping to a hardware resource is **not done**, and that is the single largest
  open gap in this lane.
- **No novelty claim** over Burnside/Pólya counting, local-Clifford symmetry,
  decision-tree minimisation, set cover, or the QG-26/27/28/31/32 chain.
- **QG-36 is conditional** on a shared-frame model that is an assumption, not a
  consequence of the grammar. Under per-column independent choice it does not
  apply.

## What has already been killed here

Recorded because a ledger that only lists survivors is advertising.

1. The **eta-ladder** was presented as a new lemma. It is Freeze–Schmid 2010
   **Prop. 3.1(3)**, in a *stronger* form. Killed by literature check.
2. The **descriptor-completeness trichotomy** was proposed as a method. It is
   Lehmann's maximal-invariant classification (1959), Defs 8–9 and Thm 4. Killed.
3. The **cost-annotated ladder** unifying the zero-sum and probe lanes was tiered
   `MechanicCandidate`, tested by measured transfer, and found to be a **COSTUME**
   — four structural breaks, growth laws linear vs logarithmic.
4. A **citation error** (Prop 3.2 vs 3.1) reached `main` and was corrected.
5. The **first Qiskit experiment** reported a clean negative that was **vacuous**
   — cost counted only `cx` while routing inserts `swap`.

Five self-inflicted kills, four of them after the claim was already written up.
That is the rate a reader should assume still applies to what survives.

## Where an actual referee is still needed

Mechanised falsification cannot supply: whether the object is *interesting* to a
quantum-compilation audience; whether the framing overstates; whether a
relevant literature was missed entirely. Those need a human in the field, and
this ledger does not pretend otherwise.
