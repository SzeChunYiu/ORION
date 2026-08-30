# The independent all-matchings optimum: why it is still open

## The requirement, and why it is live now

`COMPUTE_PLAN_V2` defers one obligation conditionally:

> For any row used in a universal-basis claim the protocol requires a **second
> implementation** to establish the all-matchings optimum; reusing
> `solve_six_targets` is explicitly not independent. That checker is not written
> yet and is **not needed unless Stage 1 yields positives**.

Stage 1 yielded positives. The requirement now attaches to the three rows it
certified — indices 152, 156 and 162. This note records an attempt to satisfy it,
why the attempt failed, and what would actually discharge it, so the gap is
stated rather than left implicit in a passing suite.

## Two routes, both closed

**A second enumeration is not available.** At n=2 the sparse pair universe is 120
ordered anticommuting pairs, which is already the complete dense universe, and
`solve_six_targets` walks the full Cartesian cube of it across all 15 matchings.
A second enumeration would be the same enumeration under another name, and would
establish nothing the first did not.

**A re-derived cost model would transliterate its own subject.** The cost
arithmetic — frame, tag and restore, the four ordered variants per matching, the
pairing of a tag weight with the orientation that produced it — lives in the
solver. `manuscript/sections/02-methods.tex` describes the instance structure but
does not state the arithmetic. Any reimplementation would therefore be read off
the code it is supposed to check independently.

## The attempt, and the bug that ended it

A third route looked promising and was tried: rescore every candidate through
`restore_cost_full_scan`, which the module's own docstring calls an "independent
O(n) recomputation" and which today is applied only to the winning witness, never
to the search. Substituting it across the whole cube would falsify a real and
specific failure — that the incremental `restore_cost_sparse`, with its
precomputed baseline and its delta restricted to `active_union(pairs)`,
understates some candidate's cost and hides a cheaper witness.

The attempt reported C1 = 4 against the solver's 6 on all three controls. That
was not a solver defect. It was a defect in the attempt: the solver selects
`(tag_weight, orientation, tag)` as one unit and holds that orientation for the
rest of the candidate, and it evaluates four ordered variants per matching. The
attempt took `min(tags)` across orientations while computing frame and restore
costs separately, so it combined a tag from one orientation with costs from
another and priced combinations that do not exist.

The discrepancy is recorded because it is the useful part. A checker that
disagrees with a solver which has just produced a clean 33,755-instance census is
far likelier to be wrong than the solver, and it was. The broken checker is not
committed; a wrong independent confirmation is worse than a missing one.

Repairing it means reproducing the variant and orientation handling faithfully --
which lands back in the transliteration the protocol rules out.

## What would discharge the requirement

A formal statement of the cost model in the manuscript — frame, tag, restore, the
variant set and the orientation binding, written as mathematics rather than as
code — from which a second implementation could be built without reading the
solver. That is a manuscript task, not a compute task, and it is the honest
blocker.

Until then the three certified rows carry Stage 1's terminal, which does not
depend on this, and **no universal-basis claim should be made on them**, which is
exactly the condition the compute plan attached the requirement to.
