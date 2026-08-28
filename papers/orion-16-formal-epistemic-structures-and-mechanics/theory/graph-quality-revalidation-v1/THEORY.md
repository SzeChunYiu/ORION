# ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1 — THEORY

**Paper:** ORION-16 — Formal Epistemic Structures and Mechanics
**Successor id:** `ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1`
**Governing issue:** #1649 Tier A (execution order 3)
**Authorized by:** `WAVE1_TOP_TIER_PROMOTION_TRIAGE_2026-08-28.md` — ORION-16's **one** promotion attempt
**Extends:** `ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1` (PR #1638)
**Authored:** 2026-08-28
**Status:** `THEOREM_PROVED__TAXONOMY_MATCHES_FROZEN_REAL_GOLD`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 1. What was missing

PR #1638 proved that for a **given correct** dependency graph, the affected
closure `A(Delta)` is the unique minimal sound revalidation set. That assumption —
*given correct* — is the whole gap between a formal result and a real system,
because real dependency graphs are extracted, and extraction is imperfect.

#1649 asks precisely for this: a theorem distinguishing **sound over-approximate**,
**exact**, and **learned/incomplete** graphs, with *"an explicit bound on extra
work induced by conservative edges and failure risk induced by missing edges."*

This packet drops the correctness assumption.

---

## 2. Setting

Let `G*` be the true dependency graph over obligations and `G` the graph a method
actually uses. Write `A_G(Delta)` for the affected closure of `Delta` under `G`,
and let `w` be a non-negative weight (cost) on obligations.

Three regimes, exactly as #1649 names them:

```
G  ⊇ G*      over-approximate / conservative
G  =  G*      exact
G  ⊉ G*      incomplete / learned, some true edge missing
```

---

## 3. The theorems

### Theorem 1 (over-approximation is sound)

If `G ⊇ G*` then `A_{G*}(Delta) ⊆ A_G(Delta)` for every `Delta`. Revalidating
`A_G(Delta)` is therefore sound.

**Proof.** Every `G*`-path from `Delta` is a `G`-path, so every node reachable in
`G*` is reachable in `G`. Soundness follows from #1638's sufficiency direction
applied to the larger set. ∎

### Theorem 2 (the cost of conservatism, exactly)

The extra work a conservative graph induces is exactly the weight of the surplus:

```
cost(G) - cost(G*)  =  w( A_G(Delta) \ A_{G*}(Delta) ).
```

Nothing is wasted anywhere else, and the surplus is entirely attributable to
edges in `G \ G*` that create reachability. ∎

### Theorem 3 (the risk of incompleteness, exactly)

If `G ⊉ G*` then there is a `Delta` and an obligation
`j ∈ A_{G*}(Delta) \ A_G(Delta)`. Revalidating `A_G(Delta)` leaves `j`
unchecked while its premises may have changed, so the method is **unsound** on
that update. The exposed risk is exactly

```
risk(G)  =  w( A_{G*}(Delta) \ A_G(Delta) ).
```

**Corollary (the only safe response to detected incompleteness is abstention).**
A method that knows its graph may be incomplete cannot certify: by Theorem 3 the
stranded obligations are precisely the ones it cannot see. Accepting is unsound;
the correct terminal is `CANNOT_CHECK`. ∎

### Theorem 4 (exactness is the unique cost-optimal sound choice)

Among all sound graphs — i.e. all `G ⊇ G*` — the exact graph `G*` minimises
`w(A_G(Delta))` for every `Delta`, and it is the only one attaining that minimum
whenever some surplus edge is reachable. ∎

### The duality this exposes

```
over-approximate    buys safety with work        cost surplus w(A_G \ A_{G*})
under-approximate   buys work with risk          risk w(A_{G*} \ A_G)
exact               neither surplus nor risk
```

Graph quality is therefore not a soft engineering preference but a **two-sided
exact accounting**: every edge you add over the truth costs work you can name,
and every edge you omit costs safety you can name. This is the statement that
turns #1638's formal result into one about real extraction.

---

## 4. The taxonomy matches the frozen real-transition gold

`top_tier/p6_real_transition_gold_v1.json` carries 16 real transition cases with
terminals in `{ADMISSIBLE, CANNOT_CHECK, REOPEN}`. Four of them instantiate the
taxonomy directly, and the theorems predict all four **before** consulting them:

| regime | case | theorem predicts | gold |
|---|---|---|---|
| exact graph | `RC-ALIAS-COMPLETE` | `ADMISSIBLE` | **`ADMISSIBLE`** |
| empty affected closure | `RC-UNCHANGED` | `ADMISSIBLE` | **`ADMISSIBLE`** |
| **missing edges** | `RC-ALIAS-MISSING` | **`CANNOT_CHECK`** | **`CANNOT_CHECK`** |
| **wrong edges** | `RC-ALIAS-WRONG` | `REOPEN` | **`REOPEN`** |

The `RC-ALIAS-MISSING` row is the load-bearing one. An incomplete alias graph does
**not** produce a confident wrong answer in this system — it produces
`CANNOT_CHECK`, which is exactly what Theorem 3's corollary prescribes. The
frozen system already behaves the way the theorem says a sound one must.

`RC-ALIAS-WRONG` is distinct from missing: wrong edges mean `G` is not a superset
of `G*`, so Theorem 1's soundness guarantee is void and reopening is forced.

---

## 5. Independent verification

`independent_checker/check_graph_quality.py` imports no ORION-16 module. Theorems
are verified on freshly enumerated DAG **pairs** `(G*, G)`; the gold is read as
data and never executed.

| check | result |
|---|---|
| A — over-approximation is sound | holds over **11,892** `(G*, G, Delta)` triples |
| B — extra work equals the surplus closure | holds |
| C — missing edges strand an obligation | **54,172** pairs checked, explicit witness recorded |
| D — exactness is cost-optimal among sound graphs | **0** violations |
| E — taxonomy vs frozen real gold | **4/4 match** |
| F — negative controls | **4/4 fire** |

The Theorem-3 witness is recorded concretely (`n=2`, `Delta={0}`, stranded
obligation `1`) rather than asserted, so the unsoundness is exhibited rather than
argued.

`CANNOT_CHECK` has exit code `3` and is never reported as a pass.

---

## 6. What this does **not** establish

#1649's empirical discriminator asks for *"2–3 independently sourced systems with
real dependency/change graphs"* compared against full revalidation,
direct-neighbour, changed-set-only, dependency-closure and a strongest incremental
verification/build/test-selection baseline.

**That comparison is not made here and is not manufactured.** The frozen
real-transition audit is a *terminal-correctness* audit over 16 transition cases,
not a *cost* comparison against build-system baselines, and it covers one system,
not two or three.

**Correction, and a pointer a reviewer should have.** An earlier draft of this
section asserted that no such comparison exists *in the repository*. That was a
repository-scoped absence claim made from a search of this paper's directory
only — the same scope error twice over. It is wrong.

`papers/orion-17-epistemic-navigation-open-worlds/transitions/P7_CLOSURE_RETENTION_V1.json`
records an executed campaign over **three independently sourced real Python
packages** — numpy (426 modules, 1076 import edges), scipy (813, 2156), flask
(24, 19) — with real commit histories and a three-policy comparison including an
`always-reopen` baseline.

That is the closest thing in the repository to #1649's ORION-16 discriminator, and
it is genuinely close: real dependency graphs, real changes, an exhaustive
baseline. It still does **not** substitute, because it measures *closure retention
under transforms*, not *revalidation-set cost*, and its baselines are containment
policies rather than build-system or test-selection tools. But the honest statement
is "the ORION-16 discriminator has not been run", **not** "no such data exists" —
and anyone assessing this claim should look at that campaign first.

So this packet earns the **theory objective** of #1649's ORION-16 entry and
explicitly does not earn the empirical discriminator. Per the stop rule, the
general theorem and the bounded paper stand; no deployed-system claim is made.

The honest reading of §4 is **taxonomy agreement on a frozen real audit**, not a
cost benchmark. The cost bounds of Theorems 2 and 3 are proved, not measured.

---

## 7. Donor boundary

Reachability closure, monotone dependency semantics, and the observation that
conservative static analyses trade precision for soundness are **donor-owned** —
incremental verification, build systems and regression test selection own the
generic machinery, and the sound-over-approximation idea is standard static
analysis. **No novelty is claimed for any of it.**

The ORION residual is the exact two-sided accounting of §3 stated over the
*affected closure* object — surplus cost and stranded risk as complementary
weights of the same set difference — and the demonstration that the frozen
transition gold's `CANNOT_CHECK` on incompleteness is the theorem's prescribed
terminal rather than an implementation choice.

---

## 8. Authority boundary and stop rule

`scientific_authority_delta = NONE`.

- `V4.4`, `V4.6` and their counts are unchanged; #1638's result is extended, not
  altered.
- The `CLAIM_LEDGER_V4.md` scope ceiling stands verbatim: universal minimality of
  the five lift coordinates, deployed-agent performance and donor novelty remain
  **not established**.
- `external_independent_validation` remains `CANNOT_CHECK`; this is same-programme
  work and does not discharge it.
- The 16 frozen transition terminals are read, never rewritten. No gold value is
  modified and no `CANNOT_CHECK` is converted — indeed one of them is the
  packet's central confirmation.
- No manuscript, ledger, formal record or `submission/` byte is modified.

**Stop rule (#1649, verbatim):** *"If real dependency extraction cannot be made
authoritative, keep the general theorem and bounded paper; do not manufacture
deployed-system claims."*

Real dependency extraction across 2–3 independently sourced systems **has not been
made authoritative here**. The general theorem is kept, the bounded paper stands,
and no deployed-system claim is made. **ORION-16's promotion budget is now spent.**
