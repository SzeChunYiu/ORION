# ORION-QG QG-36 — at instance level, existence is not free either

QG-35 showed that for a single TARE column type, the cheap bulk+spectrum summary
decides every *existence* question and no *selection* question. QG-36 asks the
compiler-relevant version: what happens for a whole instance?

The answer strictly strengthens QG-35: **under the shared-frame model, the
aggregate summary fails to determine even the achievable cost.**

## The model, stated as an assumption rather than derived

QG-28 establishes that exact all-`n` TARE cost depends only on the 715-vector
`M = (M_o)` of column-type multiplicities. This atom adds one hypothesis:

> **Shared-frame model.** A single frame serves the whole instance, so the
> achievable cost is `min_p sum_o M_o * K_p(o)`.

That is a **modelling assumption, not a consequence of the frozen grammar**, and
the result below is conditional on it. Under the contrasting per-column
independent model, cost is `sum_o M_o * min_p K_p(o)`, every term is
spectrum-determined, and **the result does not apply**. Which model the
production compiler realises is a question for the QG-26/28 lane, not settled
here.

## Result

Two instances with **identical aggregate bulk+spectrum summaries** and
**identical per-column optima** have **different achievable cost**:

| instance | shared-frame optimum |
|---|---|
| `{ IXIYXZ , IIIIIX }` | **3** |
| `{ IXIYYZ , IIIIIX }` | **4** |

`IXIYXZ` and `IXIYYZ` lie in the same joint class — identical bulk, identical
spectrum — and each has per-column optimum `0`; `IIIIIX` has per-column optimum
`3`. So every *part* is summary-determined and the *whole* is not.

Re-derived independently (`qg36_witness_independent_verify.py`), recomputing
bulk, spectrum and all 384 responses from the primitives rather than reading any
cache.

**Not a rarity.** Over a systematic sample of size-2 instances,
**60,674 of 117,900** pairs sharing an aggregate summary have different
shared-frame cost.

## Why this is the stronger statement

| level | existence | selection |
|---|---|---|
| single column (QG-35) | **free** — proved, 0 of 92 classes split | impossible — 85 of 92 split |
| instance, shared frame (QG-36) | **not free** — explicit witness | impossible a fortiori |

QG-35's part (a) was a genuine theorem *about columns*, and it does not lift. The
reason is compositional: a shared frame must be good for the columns
**jointly**, and jointness is exactly the indexed information that C1 shows the
spectrum discards by construction. Summing per-column optima is an upper bound
that the aggregate summary cannot correct.

Stated plainly for the compilation setting: **knowing the cheap summary of every
column of a circuit tells you the best each column could do in isolation, and
does not tell you what the circuit can do.**

## Boundaries

- Conditional on the shared-frame hypothesis above.
- Size-2 instances only. Whether the gap grows, saturates or shrinks with
  instance size is **not computed** and is recorded as open, not as "checked and
  fine".
- The 60,674/117,900 figure is a systematic sample (`x` strided over the 715
  types), not an exhaustive census.
- No claim about which model the production compiler realises.

## Provenance

Found by exploration; the committed scripts are replay instruments and **no
pre-outcome freeze is claimed for this atom**, as for QG-35 and unlike QG-34.

## Authority

`mathematical_proposal: true`, `NOT_R6`, no compiled-resource claim,
`novelty_claim: false`.
