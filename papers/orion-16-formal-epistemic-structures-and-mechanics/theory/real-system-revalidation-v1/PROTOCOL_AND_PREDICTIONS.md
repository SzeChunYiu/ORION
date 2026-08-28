# ORION-16 — real-system minimal revalidation: frozen protocol and stamped predictions

**Paper:** ORION-16 — Formal Epistemic Structures and Mechanics
**Successor id:** `ORION16.REAL_SYSTEM_DISCRIMINATOR.v1`
**Governing issue:** #1649 ORION-16 empirical discriminator / blueprint §4.5
**Status:** `PROTOCOL_FROZEN__NO_SYSTEM_CLONED_NO_OUTCOME_OPENED`
**Scientific authority delta:** `NONE`

This document is written and committed **before** any repository is cloned and
before any measurement is taken. Its predictions are stamped here so they cannot
be adjusted to the outcome.

---

## 1. What was missing and what makes it obtainable

`ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1` proves the graph-quality theorems
but records honestly that #1649's empirical discriminator — *2-3 independently
sourced systems with real dependency/change graphs* — was not run. Blueprint §4.5
names three systems and adds a stop rule: stop if native graph extraction cannot
be made authoritative.

The route that makes it authoritative without executing a toolchain is that all
three systems **declare** their dependency edges rather than implying them:

| system | ecosystem | declared edge | authority |
|---|---|---|---|
| `leanprover-community/mathlib4` | Lean 4 | `import Mathlib.A.B` header | Lean imports are explicit and complete; there is no wildcard import |
| `nf-core/rnaseq` | Nextflow DSL2 | `include { X } from './modules/...'` | DSL2 module resolution is exactly this statement |
| Gene Ontology | OBO | `is_a:` / `part_of:` stanza | the ontology's own asserted relations |

No build, no reasoner and no test execution is required to obtain `G*`, so the
§4.5 stop rule is not triggered by toolchain availability. Any system whose
extraction is incomplete or ambiguous is reported `CANNOT_CHECK` for that system
and contributes no result.

## 2. Objects

- Obligations: one per module/term, unit weight.
- `G*`: the declared edge set above, taken as the authoritative graph.
- Change sets `Delta`: the modules touched by each of the most recent 200
  commits, taken from the real history; for GO, the terms obsoleted between
  consecutive releases.
- Affected closure `A_G(Delta)`: reverse reachability from `Delta` — everything
  that transitively depends on something changed.

## 3. Registered arms

1. `full` — revalidate every obligation.
2. `changed-set-only` — revalidate `Delta`.
3. `direct-neighbours` — `Delta` plus immediate dependents.
4. `affected-closure` — exact reverse reachability under `G*` (**the method**).
5. `conservative` — `G*` plus a fixed fraction of added edges, then closure.
6. `incomplete` — `G*` minus a fixed fraction of true edges, then closure.

Edge mutation fractions are fixed at `{0.01, 0.05, 0.10}` before any run, with
seed `20260828`, and the same change sets and obligations are used for every arm.

## 4. Cost and risk

- cost(arm) = number of obligations revalidated.
- risk(arm) = obligations in `A_{G*}(Delta)` the arm does not revalidate — the
  stranded set, which is exactly Theorem 3's exposure.

## 5. Stamped predictions

Theorems 1-4 are identities over the closure operator, so confirming them is not
by itself informative. The predictions that can actually fail are about
**magnitude on real graphs**, and they are stamped here:

- **P1** `affected-closure` strands zero obligations on `G*`, on every system.
- **P2** `changed-set-only` and `direct-neighbours` strand a non-zero number of
  obligations on at least two of the three systems.
- **P3** cost(`conservative`) is non-decreasing in the added-edge fraction, and
  cost(`conservative`) >= cost(`affected-closure`) at every fraction.
- **P4** risk(`incomplete`) is non-decreasing in the deleted-edge fraction and is
  strictly positive at the `0.10` fraction on at least two systems.
- **P5 — the falsifiable magnitude claim.** On at least two of the three systems,
  the **median** `affected-closure` cost over the change sets is at most **50%**
  of `full` revalidation.

**P5 is the one that can sink the method, and it is registered as such.** Deep,
densely imported libraries can have reverse closures covering most of the system;
Mathlib4 is a live candidate for exactly that. If the closure of a typical change
is most of the library, exact affected-closure revalidation buys little over full
revalidation on real code, and the honest reading is that the theorems are sound
but the practical gain is absent. No threshold in P5 will be moved after the
measurement, and a failure will be reported as a failure.

## 6. Stop rule (§4.5, binding)

> *"Stop if native graph extraction or semantic obligation outcomes cannot be made
> authoritative. In that case retain the general theorem and bounded paper."*

Extraction authority is asserted per system in §1 and is checked mechanically at
run time; a system failing that check yields `CANNOT_CHECK` and no result.

## 7. Authority

`scientific_authority_delta = NONE` for this document. It freezes a protocol and
stamps predictions; it contains no measurement. `V4.4`, `V4.6`, the ledger scope
ceiling and `external_independent_validation = CANNOT_CHECK` are untouched.
