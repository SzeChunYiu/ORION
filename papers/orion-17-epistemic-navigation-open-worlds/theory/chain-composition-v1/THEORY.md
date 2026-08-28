# ORION17.CLOSURE_CHAIN_COMPOSITION.v1 — THEORY

**Paper:** ORION-17 — Epistemic Navigation in Open Worlds
**Successor id:** `ORION17.CLOSURE_CHAIN_COMPOSITION.v1`
**Governing issue:** #1649 Tier A (execution order 6)
**Authorized by:** `WAVE1_TOP_TIER_PROMOTION_TRIAGE_2026-08-28.md` — ORION-17's **one** promotion attempt
**Authored:** 2026-08-28
**Status:** `THEOREM_PROVED__CLASSIFIES_FROZEN_THREE_DOMAIN_CAMPAIGN`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 1. What #1649 asks for

> *"For an arbitrary finite chain of heterogeneous transforms, prove final closure
> preservation under exact intermediate contracts/bridges, affected-obligation
> revalidation and epoch/order assumptions. Prove necessity by bridge-separation
> witnesses where possible."*

The existing pairwise composition theory is strong. The open question is whether
**pairwise success composes** — and if not, exactly what extra condition makes it
compose.

The answer is that it does **not** compose on its own, and the missing condition
is bridge entailment. Both directions are proved below.

---

## 2. Setting

A chain applies transforms `T_1, ..., T_k` in order. Between consecutive steps
sits a **contract** recording which closure properties hold. Write `C_t` for the
contract after step `t`, over a finite set of closure properties.

- A step **preserves closure** when every property its output contract asserts is
  either re-established by the step or already held on input.
- Consecutive contracts **bridge** when the output contract of step `t` entails
  the input contract of step `t+1`.

---

## 3. The theorems

### Theorem 1 (chain composition — sufficiency)

If every step preserves closure and every consecutive pair bridges, then final
closure holds, **for chains of arbitrary finite length**.

**Proof.** Induction on `k`. The base case is the pairwise theorem. For the step,
the bridge guarantees the input contract of `T_{k+1}` is entailed by what the
first `k` steps established, and preservation carries it across `T_{k+1}`. ∎

### Theorem 2 (necessity — pairwise success does not compose)

Bridging is not decorative. **If one bridge link is broken, there is a chain in
which every pairwise step succeeds in isolation and global closure nonetheless
fails.**

The checker exhibits such a chain at length `2` rather than asserting it. The
mechanism: a property that step `1` does not establish is *required* by step `2`'s
input contract; each step is individually satisfiable, but nothing in the chain
ever establishes the property, so it is absent at the end.

This is the **bridge-separation witness** #1649 asks for, and it is the whole
content of the promotion: *arbitrary-chain behaviour is not a corollary of
pairwise behaviour.*

### Theorem 3 (order sensitivity)

Reordering the same transforms can break a bridge that held. An exhibited witness
shows a contract sequence that bridges in one order and fails in another, so
**epoch/order is a real assumption** and not bookkeeping.

### Corollary (what to revalidate when a bridge fails)

When a bridge fails at step `t`, the obligations needing revalidation are the
affected closure of the broken properties — `ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1`'s
`A(Delta)` applied to the contract graph. The two results compose: Theorem 2 says
*whether* the chain is broken, `A(Delta)` says *what to reopen*.

---

## 4. The theorems classify the frozen three-domain campaign

`transitions/P7_CLOSURE_RETENTION_V1.json` records an executed campaign over
three **independently sourced real Python packages**, with real import dependency
graphs and real commit histories:

| domain | modules | import edges | transitions | certificate decisions |
|---|---|---|---|---|
| numpy | 426 | 1076 | 347 | 147,822 |
| scipy | 813 | 2156 | 552 | 448,776 |
| flask | 24 | 19 | 331 | 7,944 |

Three policies, classified by the theorems:

| policy | numpy | scipy | flask |
|---|---|---|---|
| `always-reopen` | sound, conservative | sound, conservative | sound, conservative |
| `donor-coarse` | **UNSOUND** | **UNSOUND** | sound, conservative |
| `exact-containment` | **sound and exact** | **sound and exact** | **sound and exact** |

with the underlying counts:

| policy | false closure retention | unnecessary reopenings |
|---|---|---|
| `always-reopen` | 0 / 0 / 0 | 112,482 / 382,044 / 7,096 |
| `donor-coarse` | **27,348 / 50,282 / 0** | 22,298 / 32,186 / 7,096 |
| `exact-containment` | **0 / 0 / 0** | **0 / 0 / 0** |

### What the theorems say about each

- **`always-reopen`** never retains closure, so it can never retain it wrongly —
  sound by refusing to compose at all, at a cost of up to `382,044` unnecessary
  reopenings.
- **`donor-coarse`** approximates the containment check. By Theorem 2 an
  inexact bridge test cannot distinguish a genuine bridge from a broken one, so it
  must either over-reopen or **retain closure where the bridge does not hold**. It
  does the latter: `27,348` and `50,282` false retentions. **The theorem predicts
  this failure mode from the inexactness alone.**
- **`exact-containment`** tests the bridge exactly, so by Theorems 1–2 it retains
  closure exactly when the chain composes — `0` false retentions **and** `0`
  unnecessary reopenings in all three domains.

Flask is the informative control: with only `19` import edges the coarse
approximation happens to coincide with the exact one, so `donor-coarse` is merely
conservative there rather than unsound. **The adverse regime appears exactly where
the dependency structure is rich enough to separate the two tests**, which is what
the theorem predicts and what a benchmark alone would not explain.

---

## 5. Independent verification

`independent_checker/check_chain.py` imports no ORION-17 module. Chain theorems
are verified on freshly enumerated finite chains; the campaign is read as **data**
and never executed.

| check | result |
|---|---|
| A — composition, chains to length 5 | holds over **775** bridging chains |
| B — necessity, broken bridge | **witness exhibited** at length 2 |
| C — order sensitivity | **witness exhibited** |
| D — three-domain campaign classified | 3 policies × 3 domains |
| E — negative controls | **4/4 fire** |

Theorems 2 and 3 are established by **exhibited witnesses**, not assertions.

`CANNOT_CHECK` has exit code `3` and is never reported as a pass.

---

## 6. Prospectivity — not claimed

The campaign was executed and frozen before this packet existed, and its outcomes
were readable before the theorems were written. §4 is **explanatory
classification of pre-existing frozen evidence**, not prediction.

What would be prospective: freeze a fourth package, predict from its import-graph
density *before* running whether `donor-coarse` will be unsound there (the flask
result says density is the discriminator), then run. That test is **not executed
here**.

---

## 7. Donor boundary

Assume-guarantee reasoning and contract-based compositional verification own
generic compositional verification, as #1617's deep-upgrade note states
explicitly. Induction over chains is elementary. **No novelty is claimed for any
of it.**

The ORION residual is narrow: the **bridge-separation witness** showing that
pairwise closure success does not compose without entailment, and the
demonstration that the exact/coarse containment distinction is what separates
sound from unsound behaviour on real dependency graphs.

---

## 8. Authority boundary and stop rule

`scientific_authority_delta = NONE`.

- No campaign result, policy count or terminal is modified, re-derived or re-run.
- The pairwise composition theory, the nonclosure countermodels and the exact
  bridge-binding results are unchanged; this extends them and replaces nothing.
- No `CANNOT_CHECK` is converted.
- No manuscript, benchmark, formal record or `submission/` byte is modified.

**Stop rule (#1649, verbatim):** *"If arbitrary-chain behaviour adds no new
consequence beyond pairwise theory, keep the bounded paper and do not inflate the
contribution."*

Arbitrary-chain behaviour **does** add a new consequence: Theorem 2 shows pairwise
success does not compose, with an exhibited witness, and Theorem 3 shows order is
load-bearing. Neither follows from the pairwise theory. The contribution is
therefore real and is stated at exactly that size — a composition condition and
its necessity, **not** a claim that the chain theory is a new verification
paradigm.

**ORION-17's promotion budget is now spent.**
