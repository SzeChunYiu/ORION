# ORION-QG QG-35 — existence is free, selection is not

An unconditional impossibility result for feature-determined compiler boundaries,
with the exact price of the missing information.

Relates to `#911`, `#924`, `#904`, programme `#740`. All primitives recomputed
from `main`; no unmerged PR is required.

## The criterion, and why it settles the question

A predicate `B` on column types is decidable from a summary `A` **iff `B` is a
union of blocks of `A`'s partition**. That is immediate. What makes it decisive
here is that we now hold `A`'s partition exactly: bulk × spectrum has **92
blocks** over the 715 local-Clifford orbit types.

So "is this compiler boundary feature-determined?" stops being a search over a
predicate language and becomes an inspection of 92 sets.

## Theorem (existence–selection separation)

**(a) Existence is free.** Every function of the achievable-cost multiset is
determined by bulk + spectrum.

*Proof.* The spectrum **is** the sorted 384-response tuple. Any symmetric
function of the responses therefore factors through it. ∎

Verified instances, all splitting **0** of the 92 classes: "is the donor
optimal?", "is an improvement of `>= k` available?" for `k = -3..3`, the optimal
cost value itself, the number of optimal frames, and the full multiset of
achievable costs.

**(b) Selection is impossible from that summary.** The optimal-frame set is
**not** determined by bulk + spectrum:

| quantity | classes split (of 92) |
|---|---|
| identity of the optimal-frame set | **85** |
| lexicographically first optimal frame | 77 |
| worst single frame's optimality predicate | 48 |

**352 of the 384** individual "is frame `p` optimal?" predicates are
undetermined, and **708 of the 715** column types live in a joint class on which
the optimal-frame set is non-constant.

**(c) The price is exactly 3.** Cost is letter-`S_3` invariant, so the 715 orbit
types resolve selection completely — 646 distinct optimal-frame sets occur across
them. QG-34 gives the residual cost: `D_* = 3` adaptive indexed probes, with a
matching depth-2 infeasibility certificate on all 16 worst classes, so 3 is
minimal.

## The witnesses

85 explicit pairs share a joint class — hence **identical bulk and identical
spectrum** — and share the same **optimal value**, while having **different
optimal frames**. In several, the optimal-frame sets are **disjoint**:

| pair | joint class | optimal value | optimal frames | shared |
|---|---|---|---|---|
| `IXIYXZ` / `IXIYYZ` | 48 | 0 | `{86,163,177,194,201,302}` / `{87,114,117,243,247,303}` | **0** |
| `IXXYYZ` / `IXXYZY` | 48 | −2 | `{114,243}` / `{162,195}` | **0** |
| `IXIXIY` / `IXIXYI` | 24 | 0 | `{37,349}` / `{85,301}` | **0** |

A compiler reading bulk + spectrum sees two inputs it cannot tell apart, knows
correctly that an optimal frame exists and what it costs, and **cannot name a
single frame that is optimal for both**.

All three were re-derived independently
(`qg35_witness_independent_verify.py`), recomputing bulk, spectrum and the full
384-response from the primitives rather than reading any cache.

## What this sharpens

QG-2 reported a negative: under a frozen coefficient-weighted objective, **no
predicate in the frozen literal family** is exact. That is a statement about a
search.

This is a statement about **existence**: no predicate computable from bulk +
spectrum decides frame selection, at **any** expressiveness — arbitrary
functions, learned models, unbounded formulas — because the information is not
present in the summary. A negative from searching becomes a negative from
information content.

## Why it matters for the regime-geometry programme

It separates two questions the compilation literature routinely conflates:

- **"Is there a better compilation?"** — a symmetric, cheap question, answered
  in full by the coarse summary.
- **"Which compilation is it?"** — provably not answerable from the same data,
  and the gap is not a modelling artefact but exactly the position-asymmetric
  information that C1 shows the spectrum discards by construction.

The regime geometry template asks for *decidable membership predicates computable
from input structure with no optimizer call*. This says precisely which such
predicates can exist for TARE frame choice, and prices the rest at three probes.

## Provenance and honesty

The separation was found by exploration **before** this protocol was written.
The committed scripts are replay instruments, not prospective discovery
instruments — the same convention already used in this programme for
confirmatory work. No pre-outcome freeze is claimed for this atom.

## Authority

`mathematical_proposal: true`, `NOT_R6`, no compiled-resource claim,
`novelty_claim: false`. No credit taken over the QG-26/27/28/31/32 chain, whose
constructions this analyses.
