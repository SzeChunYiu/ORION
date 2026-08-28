# ORION-16 — real-system minimal revalidation: result

**Paper:** ORION-16 — Formal Epistemic Structures and Mechanics
**Successor id:** `ORION16.REAL_SYSTEM_DISCRIMINATOR.v1`
**Protocol:** `PROTOCOL_AND_PREDICTIONS.md`, committed before any clone (`ab09991f5`)
**Status:** `DISCRIMINATOR_EXECUTED__ALL_FIVE_STAMPED_PREDICTIONS_HOLD`
**Scientific terminal:** `READY_TO_SUBMIT_SECOND_TIER` (evidence)
**Filing terminal:** `BLOCKED__NO_VENUE_FORMAT_MANUSCRIPT` (see final section)
**Scientific authority delta:** `NONE` — this adds an empirical result; it retracts nothing

---

## 1. What #1649 asked for and what was run

The discriminator asked for 2-3 independently sourced systems with real
dependency and change graphs, compared against full revalidation,
changed-set-only, direct-neighbour, dependency-closure, and graph-quality
mutations. `ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1` recorded honestly that
this had not been run.

It has now been run on all three systems blueprint §4.5 names, using declared
dependency edges so that no toolchain is executed:

| system | domain | nodes | edges | resolution fidelity | change sets |
|---|---|---|---|---|---|
| Mathlib4 | Lean 4 | 8,409 | 26,305 | **99.99%** | 191 real commits |
| nf-core/rnaseq | Nextflow DSL2 | 138 | 135 | **95.79%** | 41 real commits |
| Gene Ontology | OBO | 39,907 | 68,311 | n/a (asserted relations) | 4 inter-release diffs |

## 2. Costs and stranding

Cost is obligations revalidated; stranding is obligations in the true affected
closure that an arm fails to revalidate, summed over change sets.

| system | arm | median cost | % of full | stranded |
|---|---|---|---|---|
| Mathlib4 | full | 8,409 | 100% | 0 |
| | changed-set-only | 1 | 0.0% | **609,006** |
| | direct-neighbours | 7 | 0.1% | **605,463** |
| | affected-closure | **345** | **4.1%** | 0 |
| nf-core/rnaseq | full | 138 | 100% | 0 |
| | changed-set-only | 1 | 0.7% | **16** |
| | direct-neighbours | 2 | 1.5% | **0** |
| | affected-closure | 2 | 1.5% | 0 |
| Gene Ontology | full | 39,907 | 100% | 0 |
| | changed-set-only | 957.5 | 2.4% | **45,272** |
| | direct-neighbours | 2,633.5 | 6.6% | **36,697** |
| | affected-closure | **12,171.5** | **30.5%** | 0 |

## 3. The stamped predictions

| | prediction | outcome |
|---|---|---|
| P1 | affected-closure strands nothing | holds 3/3 — **but see §5: definitional here** |
| P2 | cheap arms strand on >= 2 systems | **holds** — changed-set-only on 3/3, direct-neighbours on 2/3 |
| P3 | conservative cost monotone in added edges and >= exact | **holds 3/3** |
| P4 | incomplete risk monotone and positive at 10% | **holds 3/3** |
| P5 | median closure <= 50% of full on >= 2 systems | **holds 3/3** (4.1%, 1.5%, 30.5%) |

**P5 was registered as the prediction that could sink the method**, on the
explicit worry that Mathlib4's deep import graph might make the reverse closure
cover most of the library. It does not: the median change reaches 345 of 8,409
modules. The threshold was fixed before measurement and was not moved.

## 4. The sharpest finding: 1% graph error erases the entire benefit

On Mathlib4 the exact affected closure costs 667 obligations on the mutation
subset. Adding just **1% conservative edges** raises it to **8,372 — 99.6% of the
whole library.** At 5% and 10% it is 8,381 and 8,382.

Theorem 2 says the surplus is exactly the weight of the extra reachable set; on a
deep graph that surplus is almost everything. So on real deep dependency
structures, near-exact extraction is not a refinement of the method — it is the
whole of it. A 1% extraction error converts a 4.1%-cost method into full
revalidation.

Incompleteness is correspondingly graded: deleting 1 / 5 / 10% of Mathlib4's true
edges strands 8,801 / 46,098 / 56,005 obligations, and by Theorem 3's corollary
the only sound response to suspected incompleteness is abstention.

## 5. What is not evidence, stated plainly

**P1 is definitional in this harness.** The affected-closure arm *is* the true
closure set, so it strands nothing by construction. Its value is a consistency
check on the harness, not empirical support, and it is reported as such rather
than counted as a fourth confirmation.

Theorems 1-4 are identities over the closure operator. What is empirical here is
**magnitude on real graphs** — P2 through P5 — not the theorems themselves.

**An honest negative.** On nf-core/rnaseq, `direct-neighbours` strands **zero**
obligations: on a shallow pipeline graph the cheap heuristic is already sound, and
the exact method buys nothing over it (both cost 2). The method's advantage
appears only where dependency structure is deep. This is the same boundary
ORION-17 found on flask, reached independently, and it bounds the claim: exact
affected-closure revalidation matters for deep graphs, not for all systems.

**Gene Ontology rests on 4 change sets**, because only five archived releases in
the probed window resolve. That is enough to compute the arms but too few for a
stable median, and the GO row should be read as corroborating, not load-bearing.

**Nextflow fidelity is 95.79%**, so roughly 6 declared includes of ~141 do not
resolve to a file on disk. They are excluded from `G*` rather than guessed.

## 6. Two extraction refusals, recorded

The guard refused results twice before producing this one, and both refusals are
part of the record rather than a tidied-away detail:

1. A first run reported Mathlib4 with 720 nodes and 588 edges. The checkout was
   complete (8,975 files); the parser was wrong. Mathlib4 uses Lean's module
   system, so imports read `public import Mathlib.X.Y`, and matching only a bare
   `import` captured 345 of 8,410 files — **8% of the graph**. Had the run been
   believed, every number above would have been computed on a fragment.
2. A second run refused nf-core/rnaseq at 24.3% because the guard then measured
   *fraction of files carrying an edge*. That guard was itself wrong: a leaf
   Nextflow process module legitimately includes nothing. Authority is now
   measured as **resolution fidelity** — declared statements that resolve — which
   is the property that actually matters.

`CANNOT_CHECK` is a distinct exit and is never reported as a pass.

## 7. Independent verification

`independent_checker/check_discriminator.py` re-derives every verdict from
`RESULT.json`, imports no ORION-16 module, and re-runs no measurement. It carries
five negative controls, including a direct test that the 0.95 fidelity threshold
rejects 0.94 and 0.243 and accepts 0.96.

## 8. Terminal, and why it is second tier

`READY_TO_SUBMIT_SECOND_TIER`.

The discriminator #1649 asked for has been delivered in full: three
independently sourced systems, authoritative declared graphs, registered arms and
mutations, and a risky prediction (P5) that could have failed and did not.

That is not the same as clearing the bar the paper's own ledger still holds open.
Three things keep this below top tier, and each is visible in the sections above
rather than argued around:

1. `external_independent_validation` remains `CANNOT_CHECK`. This is
   same-programme work and does not discharge it.
2. Of the three systems, Gene Ontology rests on four change sets and is
   corroborating rather than load-bearing, which leaves two systems carrying the
   result.
3. Of those two, nf-core/rnaseq produced a **null for the method** — the cheap
   direct-neighbour policy is already sound there. So one load-bearing system
   supports the cost claim and one bounds it.

A single deep system plus a null and a thin corroboration is a strong, honest
empirical package. It is not the multi-system external confirmation a top-tier
methodology venue would expect, and claiming otherwise would be the kind of
overreach this lane already retracted once on ORION-17.

## 9. What this earns, and what it does not

It earns #1649's ORION-16 **empirical discriminator** on three independently
sourced real systems with authoritative declared graphs.

It does not establish universal minimality of the five lift coordinates, does not
convert `external_independent_validation` (still `CANNOT_CHECK`, since this is
same-programme work), and makes no deployed-agent performance claim. The
`CLAIM_LEDGER_V4.md` scope ceiling stands verbatim, and no frozen byte, gold
value or terminal is modified.

## 9. Packaging status — no venue-format manuscript exists

The scientific package described above is complete and independently verified.
**The submission package is not**, and the terminal above should be read as a
statement about the evidence, not about readiness to file.

The only manuscript artifact is `manuscript/main.pdf`, which renders as
*"Working framework draft"* over historical base documents. It is an internal
versioned working document: it carries no venue template, no author block, no
abstract/introduction/related-work structure in submission form, and no
anonymisation. `JOURNAL_READINESS_V2.md` records the same gap from the other
side — its *"convert Markdown manuscript to venue template and perform
copyedit/reference-format pass"* item is unchecked.

Accordingly the operative terminal for filing is:

**`BLOCKED__NO_VENUE_FORMAT_MANUSCRIPT`**

This is a manuscript-preparation blocker, not a scientific one. Nothing in the
evidence is missing or undetermined because of it, and no experiment is required
to clear it. What is required is writing: converting the working framework into a
venue manuscript under the `nature-*` skills protocol, then a copyedit and
reference-format pass.
