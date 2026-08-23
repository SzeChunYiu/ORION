# Measured-transfer test: ORION-QG probe depth  <->  Freeze-Schmid zero-sum ladder
Date 2026-08-22.  **VERDICT: COSTUME.**
Files: qg_check.py, qg_sens.py (numerics).  Source: arXiv:0905.4248v2 (Freeze-Schmid),
QG34_ADAPTIVE_PROBE_TREE_RESULTS.json.

## 0. Citation correction
The bound `D_{k+1}(G) <= D_k(G) + M` is **Proposition 3.1(2)**, not 3.2(2).
`D_{k+1}(G) <= max{D_k(G) + l, s_{<=l}(G) - 1}` is **Proposition 3.1(3)**.
Proposition 3.2 is a different, s_{<=l}-based counting statement. Fix before citing.
Also: the ladder's second slot is s_{<=l}(G), which specialises to eta(G) only at
l = exp(G) ("we denote s_{<=exp(G)}(G) by eta(G)"), so writing `eta_l` is loose.

## (a) FS Prop 3.1(2) -> probe depth.  RESULT: NO NONVACUOUS READING EXISTS.

FS proof (verbatim structure): pick U minimal zero-sum, |U| = M, U | B, |B| = D_{k+1}.
Then max L(U^{-1}B) <= k, so |U^{-1}B| <= D_k, hence
    |B| = |U^{-1}B| + |U| <= D_k + M.
The load-bearing step is `|B| = |U^{-1}B| + |U|` -- the measure decomposes **additively
and exactly** across the peel, because peeling removes elements from a multiset, and the
cost of the peel is its SIZE, a variable quantity.

What is M in the identification lane? M must be "the cost of one peel". In QG a peel is
one probe and **every probe costs exactly 1**, irrespective of its arity or how much it
splits. So:
  M = 1        -> D(S) <= D(S_v) + 1.  TRUE, and it is literally the definition
                  `D(S) = 1 + min_p max_v D(S_v)`. VACUOUS.
  M = arity a  -> D(S) <= D(S_v) + a.  TRUE but strictly weaker than the definition
                  for a >= 1. VACUOUS.
  any M >= 1   -> same, weaker than the definition. VACUOUS.
There is no assignment of M that both respects QG's cost model and says anything the
definition does not already say. **Every reading is vacuous**; the transfer produces no
content. The reason is precisely the mismatch that kills the delta organ below: FS's
per-rung cost |U| is variable, QG's is the constant 1, so FS's `+M` has nothing to bind to.

(I considered and discarded a stronger reading -- carrying across the additive
decomposition itself, giving |S| = a*|S_v| for the optimal probe. That is a strawman I
constructed, not something the correspondence proposes, and it dies on inspection since
it needs every class size to be a power of a while the histogram contains 3, 6, 12, 24, 48.
Recording it as discarded rather than as a refutation.)

## (b) Arity lower bound -> zero-sum.  RESULT: the corresponding quantity does not exist.

QG's `ceil(log_a |S|)` is a **counting/entropy** bound: d probes of arity a distinguish at
most a^d objects. It needs a branching parameter.
FS has no branching parameter. Its lower bounds are **constructions/packings**:
(4.2) D_k(G) >= k exp(G); and D_k(G) >= D(G^-) - 1 + k exp(G) (line 556) -- built by
appending k copies of a maximal-order element to an extremal zero-sum-free sequence.
Counting bound vs construction bound are different kinds of object.
Forcing the transfer predicts D_k logarithmic in k. The paper proves the opposite:
"for each finite abelian group G we have D_k(G) = D_0(G) + k exp(G)" for all large k
(lines 52, 635) -- **eventually an exact arithmetic progression, slope exp(G)**.
=> transfer gives a statement the source paper itself disproves.

## (c) Where the dictionary breaks.  The chosen-vs-forced asymmetry is REAL, and there
##     are three further breaks, one of them numerically decisive.

**(c1) FS's `max` is not over branches.** In `max{D_k + l, s_{<=l}(G) - 1}` the second
argument contains **no recursive call at all** -- it is an absolute cap from the
definition of s_{<=l}. The shape is `T(k+1) <= max{T(k) + c, C}`: a monotone recurrence
with a ceiling. In QG, *every* argument of the max is a recursive call and every branch
must be resolved. FS has no tree, no branching, no adversary. Both are spelled "max";
they quantify different things (proof cases vs adversarial replies).

**(c2) FS's `min` is decoupled from the successor -- so there is no fixed point.**
Prop 3.1(3) holds "for each l", so you may minimise over l afterwards. But l does not
change D_k: the successor is the same object whatever l you pick. In QG, choosing p
*determines* the family {S_v}; choices are coupled across levels. That coupling is what
makes QG a Bellman/game recursion with a fixed point to solve. FS has a family of
independent bounds to evaluate and take the best of.
Algebraically: FS's recursion is one-directional along a TOTAL order (k -> k+1 on N), so
it **unrolls to a closed form** -- which is exactly how the paper proves
D_k(G) = D_0(G) + k exp(G). QG's recursion is over a PARTIAL order with branching, so it
**cannot be unrolled** and requires fixed-point iteration over 4441 states. Unrollable
vs. not is the same distinction as (c4)'s linear vs. logarithmic, seen from the algebra
rather than the growth rate. This is exactly the team lead's
chosen-vs-forced intuition, and it is correct: M in 3.1(2) is min over which U *exist*
inside an extremal B -- extremal bookkeeping determined by G and k, optimised by nobody.

**(c3) The two D's are not the same type of function.**
  FS:  D_k : N -> N            (a sequence indexed by an integer)
  QG:  D   : 2^X -> N          (a value on the lattice of states)
A "ladder" needs a common index. There isn't one; nothing in FS plays the role of S.

**(c4) DECISIVE, and numerically checkable: the growth laws disagree.**
  FS:  D_k(G) = D_0(G) + k exp(G) eventually -- LINEAR in the ladder index.
  QG:  D(S) >= ceil(log_a|S|), and 3 = ceil(log_4 48) -- LOGARITHMIC in state size.
Linear vs logarithmic is precisely the signature of no-branching vs branching. A shared
composition law would have to produce the same growth law. It does not.

And QG's depth is not even a function of (state size, branching factor): recomputing the
per-class arity bound from source, ceil(log_a|S|) is beaten strictly on **12 of 92**
classes -- classes where counting says 2 probes suffice but 3 are required. So QG's value
carries genuine combinatorial obstruction that no additive/counting ladder can express,
whereas FS's D_k is pinned exactly by a linear formula for all large k.

## THE POINT THAT KILLS THE DELTA ORGAN
The proposed enveloping object is "a refinement lattice whose nodes carry a resolution
COST". The cost annotation is the whole delta. But:
  - In QG every probe costs **1**. The lattice is depth-annotated, not cost-weighted;
    there is no nontrivial per-node weight anywhere in the instance.
  - In FS the per-rung cost M = |U| **is** genuinely variable -- but FS has no lattice,
    only N.
So the lane with variable costs has no lattice, and the lane with a lattice has no
variable costs. **Neither instance exhibits the object being proposed.** The two
recursions agree only in the regime where the cost annotation is trivial, which is
fatal for a proposal whose entire content is the cost annotation.
(The team lead is right that Pacini's lattice nodes are unweighted. But QG-34 does not
supply the missing weights either -- it supplies a single global depth, D_* = 3.)

## Why "both lanes produced a min-max" was weak evidence (confirming the stated suspicion)
Correct, and worse than suspected: the two are not both min-max in the same sense.
QG is min-max over a game tree. FS is a monotone recurrence with a ceiling, whose "min"
ranges over a free parameter of a bound and whose "max" ranges over two proof cases.
Stripping the notation, FS's recursion is one-dimensional and QG's is a tree. There is
no shared mechanism to transfer.

## RETRACTED: a side finding I raised and then falsified myself
I initially flagged `arity_lower_bound_tight_on: 80` of 92 as arithmetically impossible,
on the assumption that probes are Pauli-valued so max arity a <= 4 (under which the
not-tight count provably lies in [6,10], never 12). **That assumption was wrong and the
flag is withdrawn.** `qg34_build_primitives.py` builds K as an integer cost difference
(`config_cost(...) - baseline`), not a Pauli letter: K takes **11** distinct values
overall (-3..7) and the per-class max arity runs to **6**
(arity histogram {1:7, 2:25, 3:8, 4:30, 5:18, 6:4}).

Recomputing the bound from source with the true per-class arity gives
LB histogram {0:7, 1:30, 2:51, 3:4} against depth {0:7, 1:30, 2:39, 3:16}. The margins
then force the transport exactly: 7 + 30 + 39 tight, LB-2 leftover 51-39 = 12 pushed to
depth 3, plus 4 tight at LB 3. **Not tight on exactly 12; tight on exactly 80 of 92.**
The committed figure is correct and is now independently reproduced from main by a third
implementation. No defect. (Artifacts: class_arity.json, qg_check.py, qg_sens.py.)

## Verdict
**COSTUME.** The resemblance is notational. (a) transfers vacuously or falsely,
(b) has no counterpart quantity and predicts a growth law the source paper disproves,
(c) breaks at four places including a numerically decisive growth-law mismatch. The
cost annotation -- the proposed delta -- is the single feature the two lanes do not
share. Do not promote to MechanicCandidate; record as a tested negative.

## What is NOT killed
QG-34's own result stands on its own: D_* = 3, minimality certified at depth 2, an
independent re-derivation agreeing per class. It does not need the zero-sum analogy, and
nothing here bears on it. Likewise the C1 completeness result is untouched.
