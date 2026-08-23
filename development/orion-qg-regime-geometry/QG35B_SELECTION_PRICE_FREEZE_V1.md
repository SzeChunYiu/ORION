# QG-35b FREEZE — exact price of SELECTION (committed before any solver run)
Date 2026-08-22. Author: descriptor-audit lane. Status: FROZEN.
Primitives regenerated from main via qg34_build_primitives.py (715 reps / 384 probes /
45 bulk / 54 spectrum / 92 joint, size histogram {1:7,2:22,3:6,4:6,6:25,8:2,12:14,24:8,48:2}).

## Definitional pins (fixed now so no value can be steered later)
P1. best(o)   = min over ALL 384 probes of K_p(o).
P2. argmin(o) = frozenset{ p in [0,384) : K_p(o) == best(o) }.   (full set, all 384)
P3. SELECTION terminal test is **frozenset EQUALITY** of argmin(o) across the state.
    NOT overlap, NOT lex-min agreement, NOT |argmin| agreement.
P4. Branching alphabet = the same integer K_p values as QG-34 (11 values in [-3,7];
    per-class max arity <= 6). A probe splits S into {o in S : K_p(o) = v} over v.
P5. The terminal predicate is evaluated on the CURRENT state S, never inherited from
    the initial joint class.
P6. D_sel* = max over the **92 initial joint classes**. (Not over all reachable states.)
P7. State space stays "sets of orbit types" throughout. The recursion is NOT quotiented
    to argmin-block ids: two types in one argmin block may have different K_p responses,
    so probes do not factor through the argmin partition. Only the STOPPING RULE moves.

## Recursions
  PRIMARY   D_sel(S) = 0 if |{argmin(o) : o in S}| == 1
            D_sel(S) = 1 + min_p max_v D_sel({o in S : K_p(o) = v})   otherwise
  SECONDARY D_act(S) = 0 if  INTERSECTION_{o in S} argmin(o) != empty
            D_act(S) = 1 + min_p max_v D_act(...)                     otherwise
  D_act is the ACTIONABLE price: a compiler needs one frame that is optimal for every
  candidate still in play, not the full optimal set. NOTE: "common frame exists" is
  **not transitive** (o1~o2 and o2~o3 does not give o1~o3), so D_act is NOT a partition
  target and cannot be phrased as a lattice node. Reported as a separate quantity.
  Both stopping predicates are downward-closed under subsets, so both recursions and
  both infeasibility certificates are well-posed.

## Admissible outcome branches (frozen; no others may be reported)
  B1. D_sel* = 3  -> selection costs exactly what full identification costs; the
                     coarsening 715 -> 646 buys nothing. QG-35(c) as committed STANDS.
  B2. D_sel* = 2  -> price of selection strictly below price of identification.
                     QG-35(c) as committed OVERSTATES and MUST BE CORRECTED.
  B3. D_sel* = 1  -> surprising; requires the depth-0 infeasibility certificate on every
                     class with non-constant argmin before it may be reported.
  B4. CANNOT_CHECK_RESOURCE_BOUND -> solver did not close within budget; report as such.
  D_sel* = 0 is EXCLUDED A PRIORI: 85 of 92 joint classes have non-constant argmin
  (recomputed from main this session), so D_sel* >= 1.
  Upper bound D_sel* <= 3 is FORCED: every QG-34 tree reaches singletons and singletons
  are argmin-monochromatic, so any QG-34 tree is a valid selection tree.
  => admissible set is exactly {1, 2, 3} + CANNOT_CHECK_RESOURCE_BOUND.
  Same four branches for D_act*, with D_act* >= 1 (76 of 92 classes have NO common
  optimal frame) and D_act* <= D_sel*.

## Deliverables required before any value may be reported (QG-34 parity)
  D1. Bellman value over the reachable state set (exact, not sampled).
  D2. Matching infeasibility certificate at D*-1 on EVERY class attaining D*, not a
      sample. (i.e. prove no tree of depth D*-1 resolves any worst class.)
  D3. Per-state arity information lower bound ceil(log_a m(S)) with m(S) = number of
      DISTINCT ARGMIN BLOCKS spanned by S (not |S|), reported per class with tightness.
  D4. Independent re-derivation with a DIFFERENT state encoding AND an independently
      written terminal predicate. Solver B must not share is_terminal with solver A;
      otherwise per-class agreement says nothing about the only thing that changed.

## Explicitly NOT claimed by this atom
  - No claim about the true fixed-probe minimum for selection (QG-32 territory).
  - No claim that argmin-set equality is the right compiler contract; D_act is offered
    as the alternative reading and both are reported.
  - No novelty claim. No proof authority. Machine-checked proposal only.

## Pre-registered note on the "weakest sufficient summary" sub-question
Half of it is definitionally true and will be reported as such, not as a finding: once
D_sel* is computed, "the argmin partition is reachable from bulk+spectrum plus D_sel*
probes" is exactly what that number means. Only the intermediate-summary half is
substantive, and it will be answered against what qg35 already tested
(selection_lexfirst_split_classes; per-frame "is frame p optimal?" splits; the existence
list already establishing optimal VALUE and |argmin| are spectrum-determined).
