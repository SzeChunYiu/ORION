# P10 OCME formal non-vacuity protocol V1

**Programme:** #977  
**State:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** establish that Obstruction-Certified Method Expansion is a non-vacuous executable object in two exact formal settings before attempting autonomous/native-prover discovery.

This protocol does **not** claim autonomous method invention or broad problem-solving superiority. The candidate edits are frozen explicitly; they are not credited as discovered by ORION.

## Setting A — Boolean affine closure over GF(2)

### Old method language

Inputs `x=(x0,x1,x2,x3) in {0,1}^4`.

The registered old closure is every affine Boolean function

`f(x)=a0 XOR (a1*x0) XOR ... XOR (a4*x3)`

with coefficients in GF(2). This exactly models the closure of projections/constants under XOR/affine composition for one-output functions.

### Obstruction family

Targets are pairwise conjunctions `AND(x_i,x_j)`.

The checker must exhaust all `2^5=32` old affine functions and prove that each frozen conjunction target is outside the old closure.

### Candidate edit

Add one semantic primitive `AND2(u,v)=u AND v` while leaving inputs, target truth table and verifier unchanged.

The checker must verify:

- the primitive is not equivalent to any old affine function;
- it solves the originating conjunction family;
- the same primitive transfers to held-out variable pairs frozen before execution.

### Known-method controls

Affine parity/projection/constant targets must be recognized as already in old closure; declaring expansion for them is a false expansion.

## Setting B — integer affine-composition closure

### Old method language

Input domain for verification: `D={-3,-2,-1,0,1,2,3}`.

The old language contains rational affine maps `f(x)=a*x+b`; composition remains affine.

### Obstruction family

Targets are shifted squares `(x-k)^2` for frozen integer shifts.

The checker must certify non-membership without an arbitrary coefficient search bound: two/three points determine any affine candidate, and another frozen point must contradict it. It must also verify nonzero second finite difference on consecutive points.

### Candidate edit

Add one semantic primitive `SQUARE(u)=u*u`. Together with old affine pre/post maps it must realize the originating and held-out shifted-square targets without changing the verifier.

### Known-method controls

Frozen affine targets such as `2*x+3` and `-x+1` must remain classified `KNOWN_COMPOSITION`.

## Frozen task table

`ocme_formal_cases_v1.json` defines originating, held-out and known-method controls for both settings. No task may be added or removed after results.

## Required certificates

For each promoted target emit:

- exact old-language closure identifier;
- exhaustive/algebraic non-membership certificate;
- candidate-edit outside-closure certificate;
- exact verifier success before/after edit;
- held-out/originating status;
- known-method false-expansion result.

## Frozen positive terminal

`P10_OCME_FORMAL_NONVACUITY_V1_GREEN` requires:

1. both settings have at least one exact obstruction;
2. `AND2` and `SQUARE` are independently verified outside their old closures;
3. every frozen obstruction target is unreachable in the old language and reachable after its single registered edit;
4. every held-out target is solved by the same edit family without changing verifier semantics;
5. every known-method control is recognized as old-closure reachable;
6. two executions are byte-identical.

Failure of either setting remains a negative result. No search timeout is accepted as an obstruction certificate.

## Authority boundary

A GREEN result earns **formal OCME non-vacuity**, not the broad P10 paper terminal. Still pending are strong native solving baselines, at least one generated/non-hand-coded edit, real verifier-backed discovery, matched search/synthesis/evolutionary comparators and independent implementation beyond this checker.
