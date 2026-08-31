# ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Governing issue:** #1649 Tier A — **ORION-16's one promotion attempt, now spent**
**Terminal:** `THEOREM_PROVED__TAXONOMY_MATCHES_FROZEN_REAL_GOLD`
**Scientific authority delta:** `NONE`

---

## 1. What was missing, and what this supplies

PR #1638 proved `A(Delta)` is the unique minimal sound revalidation set **for a
given correct graph**. That assumption is the whole gap between a formal result
and a real system, because real dependency graphs are *extracted*, and extraction
is imperfect.

This packet drops it. Theorems 1–4 give the two-sided exact accounting #1649 asks
for:

```
over-approximate    sound, extra work  =  w(A_G \ A_{G*})        Theorems 1-2
under-approximate   unsound, risk      =  w(A_{G*} \ A_G)        Theorem 3
exact               neither surplus nor risk, uniquely optimal   Theorem 4
```

**Corollary that matters:** a method that knows its graph may be incomplete
cannot certify — the stranded obligations are precisely the ones it cannot see —
so the only safe terminal is `CANNOT_CHECK`.

## 2. The frozen real gold matches the taxonomy 4/4

| regime | case | predicted | gold |
|---|---|---|---|
| exact graph | `RC-ALIAS-COMPLETE` | `ADMISSIBLE` | `ADMISSIBLE` |
| empty closure | `RC-UNCHANGED` | `ADMISSIBLE` | `ADMISSIBLE` |
| **missing edges** | `RC-ALIAS-MISSING` | **`CANNOT_CHECK`** | **`CANNOT_CHECK`** |
| wrong edges | `RC-ALIAS-WRONG` | `REOPEN` | `REOPEN` |

The `RC-ALIAS-MISSING` row is load-bearing. An incomplete alias graph does **not**
produce a confident wrong answer in this system — it produces `CANNOT_CHECK`,
exactly what the corollary prescribes. The frozen system already behaves the way
the theorem says a sound one must.

## 3. What this does not establish — stated, not omitted

#1649's empirical discriminator wants **2–3 independently sourced systems** with
real dependency/change graphs, compared against full revalidation,
direct-neighbour, changed-set-only, dependency-closure and a strongest
incremental-verification baseline.

**That comparison has not been run, and is not manufactured.** The frozen audit is
a *terminal-correctness* audit over 16 cases on **one** system, not a *cost*
comparison. The cost bounds of Theorems 2 and 3 are **proved, not measured**.

**Correction.** An earlier draft said no such comparison *exists in the
repository*. That was a repo-scoped absence claim made from a paper-scoped
search, and it is wrong: ORION-17's `P7_CLOSURE_RETENTION_V1.json` is an executed
campaign over three independently sourced real Python packages with real import
graphs and an exhaustive baseline. It does not substitute — it measures closure
retention, not revalidation-set cost — but a reviewer assessing this claim should
see it.

So this earns the **theory objective** and explicitly not the empirical one. Per
the stop rule, the general theorem and bounded paper stand and no deployed-system
claim is made.

## 4. Prospectivity — not claimed

The 16 gold terminals were readable before the theorems were written. §2 is
**explanatory agreement on pre-existing frozen evidence**, not prediction.

Four of the sixteen cases instantiate the taxonomy and are the four reported; the
other twelve concern P9/P10 subject matter outside this theorem's scope and are
neither used nor suppressed. The full gold file is SHA-256 bound, so the selection
is auditable.

## 5. Adverse and `CANNOT_CHECK` evidence

All preserved. The scope ceiling stands verbatim — universal minimality of the
five lift coordinates, deployed-agent performance and donor novelty remain **not
established**. `external_independent_validation` remains `CANNOT_CHECK`; this is
same-programme work and does not discharge it. No gold terminal is rewritten and
**no `CANNOT_CHECK` is converted** — one of them is the packet's central
confirmation.

## 6. Donor boundary

**No novelty claimed.** Reachability closure, monotone dependency semantics and
the sound-over-approximation tradeoff are donor-owned; incremental verification,
build systems and regression test selection own the generic machinery.

The ORION residual is the exact two-sided accounting stated over the *affected
closure* object — surplus cost and stranded risk as complementary weights of the
same set difference — plus the demonstration that the frozen gold's
`CANNOT_CHECK` on incompleteness is the theorem's prescribed terminal rather than
an implementation choice.

## 7. Stop rule and budget

**#1649, verbatim:** *"If real dependency extraction cannot be made
authoritative, keep the general theorem and bounded paper; do not manufacture
deployed-system claims."*

It has not been made authoritative. The general theorem is kept, the bounded paper
stands, no deployed-system claim is made. **ORION-16's promotion budget is spent;
no further rescue cycle is authorized.**
