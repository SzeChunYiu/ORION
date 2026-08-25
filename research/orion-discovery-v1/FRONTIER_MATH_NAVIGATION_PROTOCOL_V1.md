# Frontier Mathematics Structural Navigation Protocol V1

## Status

This is the complete theory/protocol handoff for using ORION’s discovery harness on frontier mathematics. It specifies what computation must execute; it does not claim that ORION has solved a new frontier problem.

```text
protocol = FROZEN_THEORY_READY_FOR_EXECUTION
frontier_result = NONE
proof_authority = EXTERNAL_OR_NATIVE_CHECKER_REQUIRED
novelty_authority = CANNOT_CHECK
```

The protocol operationalizes three research lanes:

```text
ASSEMBLE known donor fragments
TRANSFER a useful structure from another field
COMPLETE the remaining obstruction with a generated residual
```

A strong campaign may use all three.

---

# 1. Mathematical frontier state

For a problem `P`, freeze

\[
\mathcal M_P=(S,T,K,D,L,V,B,H,A),
\]

where:

- `S` — exact theorem/conjecture/problem statement and scope;
- `T` — target terminal: proof, disproof, construction, bound, classification, algorithm, or impossibility;
- `K` — accepted mathematical knowledge available to the candidate;
- `D` — donor fragments and their source identities;
- `L` — allowed proof, construction, computation, and transformation language;
- `V` — native verifier: proof assistant, exact checker, symbolic algebra, or expert proof review;
- `B` — vector resource budget;
- `H` — negative history: failed lemmas, counterexamples, search ceilings, donor absorption, and open hard strata;
- `A` — authority and chronology boundary.

A mathematical statement is not a usable frontier target until its quantifiers, definitions, parameter domain, equivalence notion, and acceptable proof object are frozen.

## 1.1 Target kinds

```text
EXISTENCE
NONEXISTENCE
EXACT_VALUE
UPPER_BOUND
LOWER_BOUND
CLASSIFICATION
NORMAL_FORM
STRUCTURAL_CHARACTERIZATION
ALGORITHM
COMPLEXITY_SEPARATION
EQUIVALENCE_OR_REDUCTION
CONJECTURE_GENERATION
COUNTEREXAMPLE
```

Different targets require different donor and validation semantics.

---

# 2. Structural address for mathematical knowledge

Every problem, theorem, counterexample, and donor fragment receives a `MathStructuralAddress`.

## 2.1 Address coordinates

```text
object kinds and algebraic signatures
quantifier pattern
target kind
parameter and asymptotic regime
symmetry/group action
equivalence and quotient relation
invariants and conserved quantities
local/global structure
decomposition or recurrence pattern
extremal/optimization structure
obstruction and counterexample signature
proof operators used
construction operators used
validation/checker semantics
resource profile
```

The address must be based on mathematically meaningful roles. A bag of terms or citation embedding may be used for retrieval but cannot authorize structural transfer.

## 2.2 Obstruction address

A failed programme is encoded as

\[
\omega(P)=
(
failed\ obligations,
minimal\ counterexamples,
trapped\ invariants,
missing\ state,
method\ closure,
resource\ boundary,
validation\ boundary
).
\]

Searching by obstruction often reaches more useful distant fields than searching by the theorem’s surface statement.

Examples of structural obstruction motifs include:

```text
local move trapped by global invariant
finite-state quotient missing one coordinate
induction loses a boundary term
compactness absent
exchange axiom fails
submodularity absent
noncommuting diagram
rank obstruction
parity/congruence obstruction
extremal examples form a hard stratum
relaxation gap
no common optimum under a coarsened state
```

---

# 3. Donor accumulation

## 3.1 Search routes

The donor accumulator runs all routes before claiming saturation:

1. exact theorem/problem terminology;
2. synonyms and function-only description;
3. decomposition into subproblems;
4. proof-method and counterexample search;
5. parent discipline/history;
6. structurally analogous theorem schemas;
7. obstruction-only search;
8. implementation/proof-library search;
9. cited-by/related-work expansion;
10. hostile “assume this is solved elsewhere” search.

Each donor is decomposed into fragments, not stored only as a citation.

## 3.2 Donor fragment schema

```text
fragment identity and source revision
source domain and target kind
premises
conclusion/guarantee
input/output types
proof/construction operators
invariants preserved
known failure boundary
counterexamples
resource assumptions
native validation
license/access
ADOPT / ADAPT / COMPOSE / DEFER / REJECT
```

## 3.3 Donor saturation terminal

Stop only after two materially different rounds yield no fragment or correspondence that changes:

- the obstruction diagnosis;
- the product closure;
- the transfer candidate set;
- the residual completion target;
- the strongest comparator;
- the claim ceiling.

The terminal is

```text
DONOR_SEARCH_STABLE_AT_CUTOFF
```

not proof of universal literature completeness.

---

# 4. Lane A — donor composition search

## 4.1 Typed donor hypergraph

Construct a hypergraph whose nodes are mathematical contracts and whose hyperedges are donor fragments or legal compositions.

A partial route records:

```text
reached contracts
outstanding premises
open interface/typing obligations
invariants preserved/lost
resource vector
proof-object lineage
```

## 4.2 Product search

Enumerate or search typed products under the frozen grammar. Candidate priorities must remain Pareto rather than an arbitrary score unless a price vector is supplied.

Relevant coordinates include:

```text
number of outstanding obligations
new target reach
proof depth/size
checker cost
resource vector
transfer debt
authority debt
counterexample survival
```

## 4.3 Minimal composition certificate

For a successful route, compute every inclusion-minimal donor subset where tractable. Record the interaction order.

Example:

```text
a1 alone: no target
b2 alone: no target
c3 alone: no target
all pairs: no target
a1 × b2 × c3: target proved
```

The registered interaction order is three.

## 4.4 Composition result interpretation

- If the exact product lies in the frozen donor-product closure, report `DONOR_COMPOSITION_ONLY`.
- If known fragments require a generated bridge outside the product closure, isolate the bridge as a residual completion.
- If a different field supplies one fragment through a map, also open the transfer lane.
- If multiple minimal products exist, preserve all of them.

---

# 5. Lane B — structural transfer search

## 5.1 Retrieval policy

Search candidates with:

```text
high surface/domain diversity
low structural distortion
matching obstruction signature
compatible validation semantics
manageable transfer debt
```

Surface distance is an exploration coordinate, not scientific authority.

## 5.2 Correspondence forms

Use either:

- relational structure maps;
- axiom/theory interpretations;
- functorial or simulation relations;
- reduction/equivalence maps;
- invariant-preserving encodings;
- mechanism role maps.

## 5.3 Transfer-debt audit

Before applying a source theorem or method, discharge:

```text
premise mapping
relation/axiom preservation
boundary conditions
parameter correspondence
validation correspondence
resource correspondence
failure-mode correspondence
```

A partially mapped analogy may still guide completion, but it cannot authorize a theorem.

## 5.4 Negative twins

For each high-value transfer, create or find a case with similar surface cues but a changed load-bearing structure. A structurally grounded transfer should distinguish them.

## 5.5 Transfer result interpretation

```text
STRUCTURAL_HINT_ONLY
PARTIAL_ANALOGY_WITH_DEBT
EXACT_INTERPRETATION
TARGET_VALIDATED_TRANSFER
CROSS_DOMAIN_REUSABLE_METHOD
```

Distant origin does not automatically make the result novel.

---

# 6. Lane C — residual completion

## 6.1 Residual obligations

After local composition and transfer first refusal, compute

\[
O_{res}=O(target)\setminus Discharged(best\ partials).
\]

The residual generator receives:

- the exact residual obligations;
- minimal counterexamples;
- candidate hard strata;
- conserved invariants;
- donor-product closure;
- forbidden target-oracle fields;
- allowable edit layers.

It does **not** receive the protected answer.

## 6.2 Completion edit families

Search edits to:

```text
new definition/object/state coordinate
new invariant or conserved quantity
new lemma or intermediate theorem
new decomposition or normal form
new proof rule/operator
new representation/quotient/lift/duality
new conjecture/question
new counterexample construction
new exact referee or validation interface
```

## 6.3 Reducibility referee

Every generated edit is tested against:

- old proof/method closure;
- donor-product closure;
- equivalent macros and library abstractions;
- stronger search under matched resources;
- target-oracle leakage;
- trivial restatement of the target.

## 6.4 Minimum completion

Search strict subedits or weaker semantic effects. A candidate is class-relative minimal only when no weaker registered edit closes the target.

## 6.5 Hidden consequences

A proposed lemma or representation must prove or predict consequences not used to generate/select it:

- held-out parameter values;
- unseen examples;
- an independent corollary;
- a new bound;
- a counterexample excluded by the theory;
- reduced proof search under a new revision;
- another problem in the same structural family.

---

# 7. Proof–counterexample dual laboratory

## 7.1 Isolated packets

Before synthesis, freeze:

### Proof packet

- strongest donor-based proof routes;
- exact missing premises;
- failed inference steps;
- candidate invariant requirements;
- proof-assistant goals.

### Counterexample packet

- strongest search for worlds satisfying current premises and falsifying the target;
- minimal counterexamples;
- hard-stratum signatures;
- constructions defeating candidate lemmas.

The two packets must not share hidden outcomes during generation.

## 7.2 Separator synthesis

Given verified positive/supporting instances `P`, counterexamples `N`, and predicate library `F`, find a minimum predicate family that separates every positive-negative pair.

This is exact set cover over `P × N`.

The resulting separator is a **missing-lemma candidate**, not a proof.

## 7.3 Synthesis packet

Open only after proof and counterexample packets are sealed. Ask:

```text
Which premise/invariant does the proof require
that the counterexample family cannot satisfy?
```

Candidate outputs:

- new lemma;
- missing state coordinate;
- corrected theorem premise;
- stronger counterexample;
- impossibility theorem;
- decomposition of the hard stratum.

---

# 8. Hard-stratum management

When a theorem handles only part of an exact or generated universe, define

\[
H=X\setminus Solved.
\]

Record:

```text
hard-stratum identity
defining invariant boundary
size/orbit count where known
why the current proof fails
minimal counterexamples
smallest extra coordinate that could distinguish it
candidate reductions to donor-owned objects
```

Never repeatedly spend compute on the solved region unless independently reproducing the proof.

## 8.1 Hard-stratum split

A useful successor either:

- proves the same mechanism on `H`;
- partitions `H` into structurally simpler strata;
- finds a new regime/counterexample;
- proves a lower bound showing the method family cannot close `H`;
- returns `CANNOT_CHECK` with an exact resource or authority boundary.

---

# 9. Symbolic lift

Every finite theorem or census at structural level B2/B3 is lifted before publication framing freezes.

Replace load-bearing constants by parameters and record:

```text
constant-specific proof steps
parameter-only proof steps
predicted second parameter point
predicted first failure boundary
known donor theorem that may absorb the lift
new proof obligations
```

A finite pattern is not promoted to an infinite theorem by curve fitting or repeated agreement.

---

# 10. Navigation algorithm

## 10.1 Pseudocode

```text
INPUT:
  frozen frontier state M_P
  target contract t
  donor cutoff and resource vector B

1. RECONSTRUCT
   normalize definitions, responsibilities, verifier, and known negative history

2. SATURATE DONORS
   exact-term -> function -> decomposition -> structure -> obstruction -> history

3. CERTIFY FIRST OBSTRUCTION
   information / formulation / method / instrument / resource / validation

4. FIXED-REGIME FIRST REFUSAL
   run strongest exact/search/prover methods in old language
   if t reached: NO_JUMP_SEARCH

5. COMPOSITION LANE
   enumerate typed donor products
   retain Pareto frontier and all minimal successful subsets

6. TRANSFER LANE
   retrieve low-distortion structural addresses across domains
   construct relational/axiomatic maps
   discharge transfer debt and run negative twins

7. RESIDUALIZE
   compute obligations not discharged by best composition/transfer partials

8. COMPLETE
   generate minimal edits only at the first unsupported layer
   attach ProposalOrigin and old-closure reducibility receipts

9. DUAL ATTACK
   seal proof packet and counterexample packet
   synthesize missing-lemma separators

10. VALIDATE
    native proof/checker, hidden consequences, held-out family/parameter transfer

11. SUBTRACT DONORS
    rerun hostile prior-art and strongest donor-product comparison

12. ADJUDICATE
    separate validity, novelty, and adoption authority

OUTPUT:
  proof / disproof / construction / boundary / donor tie / CANNOT_CHECK
  plus immutable negative history and next hard stratum
```

## 10.2 Fairness and completeness

On a finite registered donor/map/edit universe, a fair exhaustive navigator with a complete verifier is complete relative to that universe. On an open mathematical research space it is not complete, and no failure to find a proof establishes impossibility.

## 10.3 Vector navigation frontier

Do not select by one opaque creativity score. Retain non-dominated routes over:

```text
target reach
structural distortion
open obligations
proof/checker cost
memory/search cost
authority debt
transfer scope
false-invention risk
```

A scalar is permitted only when an explicit downstream decision supplies prices prospectively.

---

# 11. Execution schemas

## `MATH_FRONTIER_STATE.v1`

```text
problem and target IDs
formal statement/definitions
parameter and equivalence scope
known theorem/donor manifest
method-language identity
native verifier identity
resource vector
negative-history tip
hidden consequence IDs
external custody state
```

## `MATH_DONOR_FRAGMENT.v1`

```text
source revision
premises/conclusion
structural address
proof/construction operators
invariants
failure boundary
native replay
resource assumptions
```

## `MATH_NAVIGATION_RECEIPT.v1`

```text
obstruction address
composition frontier
structural-transfer frontier
residual obligations
Pareto routes
selected next experiment and why
all alternatives defeated/retained
```

## `MATH_COMPLETION_CERTIFICATE.v1`

```text
generated edit and origin
old-closure non-reducibility
minimum-subedit results
preservation/reopening
proof object or exact counterexample
hidden consequences
held-out transfer
external novelty state
```

---

# 12. First frontier campaign selection criteria

Choose a problem with:

- exact or machine-checkable local objects;
- a meaningful unresolved target;
- rich donor literature and known failed routes;
- finite or bounded subproblems for counterexample generation;
- a proof assistant or independent exact referee;
- no need for private experimental custody in the first tranche;
- enough structural depth that simple brute force is not the whole result.

Priority classes:

1. finite/extremal combinatorics with parametric lift;
2. algebraic or graph normal-form problems;
3. proof-assistant theorem families;
4. exact algorithm or compiler invariants;
5. state-quotient/minimal-representation problems;
6. symbolic physical-law worlds only after the math lane is identifying.

The ORION-Q/ORION-RG exact mathematics lanes are appropriate candidates because they already preserve counterexamples, hard strata, exact checkers, and donor boundaries.

---

# 13. Non-compensatory success gate

A strongest frontier-math discovery requires:

```text
proposal origin clean
old closure obstruction real
candidate non-reducible
native proof/counterexample valid
hidden consequence passes
held-out parameter/family transfer passes
strong donor product receives first refusal
independent proof reconstruction
external novelty review
```

Missing any factor narrows the terminal.

## Allowed terminals

```text
FIXED_REGIME_SOLUTION
DONOR_COMPOSITION_SOLUTION
STRUCTURAL_TRANSFER_SOLUTION
MINIMAL_RESIDUAL_COMPLETION_FINITE_CLASS
HYBRID_DISCOVERY_CANDIDATE
NEW_COUNTEREXAMPLE
LOWER_BOUND_OR_IMPOSSIBILITY
DONOR_EQUIVALENT
HARD_STRATUM_IDENTIFIED
PROOF_VALID_NOVELTY_CANNOT_CHECK
CANNOT_CHECK
```

A rigorous refutation or donor equivalence is a successful scientific outcome.

---

# 14. What computation must do

The theory work is complete. The execution lane must now:

1. build a content-bound donor hypergraph;
2. run product-closure and minimal-subset search;
3. build structural addresses and cross-domain candidate maps;
4. enumerate/learn residual completions without protected-answer access;
5. execute proof and counterexample packets;
6. run exact native verification;
7. generate hidden consequences and held-out parameter tests;
8. preserve all failed candidates and donor ties;
9. obtain independent proof and novelty authority.

The executor may refute or narrow the theory instantiation. It may not weaken the gates after seeing outcomes.
