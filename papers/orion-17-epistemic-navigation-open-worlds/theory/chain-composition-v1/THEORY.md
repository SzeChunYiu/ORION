# ORION17.CLOSURE_CHAIN_COMPOSITION.v1 — THEORY

**Paper:** ORION-17 — Epistemic Navigation in Open Worlds
**Successor id:** `ORION17.CLOSURE_CHAIN_COMPOSITION.v1`
**Governing issue:** #1649 Tier A (execution order 6)
**Authorized by:** `WAVE1_TOP_TIER_PROMOTION_TRIAGE_2026-08-28.md` — ORION-17's **one** promotion attempt
**Authored:** 2026-08-28
**Status:** `RE_VERIFICATION_PLUS_ONE_LEMMA__TIER_A_EVIDENCE_NOT_EARNED`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 1. Correction: the arbitrary-chain theorem already exists

**An earlier draft of this packet framed Theorems 1–2 as a new arbitrary-chain
result. That framing was wrong and is retracted here.**

`CLAIM_LEDGER_V4.md` row `ORION-17.V4.5` already states, as a **mechanized
theorem** (Z3 over uninterpreted sorts,
`formal/mechanized/P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json`):

> *"Heterogeneous closure-carrying transforms compose scientifically only under
> exact intermediate closure-contract binding or a registered equivalence bridge —
> **for chains of any length**, over any number of transformations, contracts,
> closure coordinates and obligations, and for every donor-native validity
> predicate."*

That subsumes both directions I had written up as new: the sufficiency of bridge
entailment and, via *"only under"*, its necessity. The Wave-1 closure blueprint
(2026-08-28, §4.10) flags exactly this, and it is right.

**What this packet actually contributes**, restated honestly:

1. an **independent, methodologically different re-verification** of V4.5 — the
   ledger's proof is Z3 over uninterpreted sorts; this one is explicit finite
   enumeration over concrete chains, so a shared solver-encoding error could not
   produce both;
2. a **classification of the frozen three-domain campaign** by that theorem,
   including the flask density observation (§4);
3. one **scoped lemma the ledger does not contain** (§3.4), framed as a
   revalidation lemma rather than a headline.

None of these is a new arbitrary-chain theorem.

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

### Theorem 1 (chain composition — sufficiency) — *re-verification of V4.5, not new*

If every step preserves closure and every consecutive pair bridges, then final
closure holds, **for chains of arbitrary finite length**.

**Proof.** Induction on `k`. The base case is the pairwise theorem. For the step,
the bridge guarantees the input contract of `T_{k+1}` is entailed by what the
first `k` steps established, and preservation carries it across `T_{k+1}`. ∎

### Theorem 2 (necessity) — *re-verification of V4.5's "only under", not new*

Bridging is not decorative. **If one bridge link is broken, there is a chain in
which every pairwise step succeeds in isolation and global closure nonetheless
fails.**

The checker exhibits such a chain at length `2` rather than asserting it. The
mechanism: a property that step `1` does not establish is *required* by step `2`'s
input contract; each step is individually satisfiable, but nothing in the chain
ever establishes the property, so it is absent at the end.

This is the **bridge-separation witness** #1649 asks for. It is a concrete
witness for a necessity direction V4.5 already asserts — useful as independent
corroboration, **not** as a new result.

### Theorem 3 (order sensitivity)

Reordering the same transforms can break a bridge that held. An exhibited witness
shows a contract sequence that bridges in one order and fails in another, so
**epoch/order is a real assumption** and not bookkeeping.

### 3.4 Lemma (affected-obligation slice) — the one part the ledger lacks

Searching `CLAIM_LEDGER_V4.md` for `affected`, `revalidat`, `slice` and
`ancestral` returns **zero** matches, so this is not a restatement.

**Lemma.** For a chain represented by an obligation-dependency DAG with final
closure root `r`, and a changed leg/interface set `Delta`, the obligations that
are both **reachable from `Delta`** and **ancestral to `r`** form the unique
minimal sound revalidation set under separation witnesses.

**Proof.** Soundness: anything not reachable from `Delta` has unchanged premises;
anything not ancestral to `r` cannot affect the final closure, so neither needs
revalidation. Minimality: for any obligation in the slice there is, by the
separation witness, an instance in which omitting it leaves `r` wrongly closed —
this is `ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1`'s necessity argument
restricted to the ancestor cone of `r`. ∎

**This is deliberately a lemma, not a headline.** It is structurally shared with
ORION-16 and adds an ancestry restriction to the closure that ORION-16 does not
need, because ORION-16 has no distinguished root. Per the blueprint's §4.11 it
should be recorded as a revalidation lemma and nothing more.

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

**The stop rule fires, on the corrected reading.** V4.5 already owns the
arbitrary-chain theorem, so this packet adds no new arbitrary-chain consequence.
What it adds is an independent re-verification by a different method, a
classification of the frozen campaign, and one scoped revalidation lemma.

Per the Wave-1 closure blueprint §4.12, ORION-17's actual Tier-A blocker is a
**decisive naturalistic multi-hop study** — a real chain of three distinct
operations (representation migration, responsibility relabel, objective change)
with externally sourced facts, predictions stamped before global closure labels
are opened, and five registered baselines.

**That study is not done here, so the Tier-A evidence breakthrough is NOT
earned.** ORION-17 returns to its bounded submission lane. The bounded paper is
unaffected and is not inflated.

**ORION-17's promotion budget is spent.** No further rescue cycle is authorized.
