# Q1 TARE full-text donor-boundary audit V3

Date checked: 2026-08-21
Primary source: Schillo, Sturm, Quay, arXiv:2601.05740v4, **TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation**.
Source mode: full-text primary PDF, figure-aware inspection + text anchors.

Purpose: replace abstract-level donor subtraction with the exact freedoms/optimizations stated by the TARE authors. This file is publication positioning only and grants no novelty authority.

## Direct donor facts verified from the full text

### 1. TARE itself is unambiguously donor-owned

Section 4 introduces Tag-And-Restore Encoding as the authors' block-encoding construction for a Pauli-string linear combination. The method pairs target strings `P_k` with a pairwise anticommuting family `R_k`, uses `Tag` to correlate the `R_k` terms with orthogonal control states, and uses `Restore` to transform each `R_k` into its corresponding `P_k` with phase.

Q1 therefore gives zero novelty credit to:
- the TARE construction;
- `Uanti` as a linear combination of pairwise anticommuting `R_k`;
- Tag/Restore architecture;
- the `T_k R_k = P_k` transformation relation;
- construction of Tagging operations from symplectic linear systems.

### 2. The freedom in `R_k` is explicitly donor-stated

The TARE paper does **not** fix the auxiliary anticommuting family as part of the theorem. Its Remark 1 states that `R_0,...,R_{m-1}`, the ancilla number `a`, and the control states `c_k` can be chosen freely by the user so the block encoding can be tailored to hardware gates, width or depth.

Therefore Q1 must not say or imply:
- "we discovered that the anticommuting frame can be chosen";
- "TARE assumes one fixed frame family" as a theorem-level donor restriction;
- "free frame choice" is an ORION novelty.

### 3. Tagging operations are explicitly optimizable in the donor method

Theorem 2 constructs the Tag Pauli strings `S_i` from a linear system. The paper notes that the solution is generally non-unique and can be exploited to optimize:
- individual `S_i` weight;
- row-wise maximum / depth proxy;
- total Tag weight / gate-count proxy.

The numerical comparison obtains the `S_i` by independently optimizing each for minimum weight.

Therefore Q1/QG must not claim novelty for:
- observing non-uniqueness of the Tag solution;
- minimizing Tag weight in general;
- recognizing a width/depth/gate-count tradeoff from Tag choices.

### 4. The donor numerical study does **not** jointly optimize the entire `R_k`/Tag/Restore design space

In the numerical comparison the authors choose specific control-label schemes and **fix a canonical anticommuting family** (`R_{2j}`, `R_{2j+1}` given explicitly in their Eq. 31), while independently optimizing the Tag strings for minimum weight. The transformation strings are then computed from the TARE relation.

This is the crucial residual boundary for Q1:

> The donor theorem exposes substantial freedom, but its reported numerical comparison does not constitute an exact global classification of all joint frame/Tag/Restore choices under ORION's frozen structural objective.

Q1 is therefore allowed to study the exact expressivity consequences of those freedoms, provided it does not restate the freedoms themselves as new.

### 5. The donor paper already frames optimization as constraint-dependent

The TARE authors explicitly motivate tailoring choices to native hardware gates, width, depth and gate count. Q1's raw support-count objective is therefore **one analysis objective**, not a universal donor cost model.

This strengthens Q1's scope rule:
- all-n support-two authority is indexed to the frozen R6M/raw-support objective;
- alternative hardware-aware objectives require independent analysis;
- QG objective-phase work is naturally complementary rather than a contradiction of TARE.

### 6. The donor also leaves larger-operator splitting open

TARE is constructed for `m <= 2n+1`; the authors note that larger operators can be split into groups and combined by an LCU step, but do not further explore that direction in this paper. Q1's R4B/R4D split-related work must still distinguish any donor/open question from its own coefficient/implementation findings and must not imply the donor never mentions splitting.

## Q1 candidate residual after full-text subtraction

The strongest defensible Q1 contribution is now:

1. **Exact joint family question.** For a fixed shared-Tag TARE batch grammar and fixed structural objective, determine which restricted families attain the unrestricted exact optimum.
2. **Exact counterexamples.** Give minimal verified witnesses showing why natural restricted joint families fail (split-anchor Tag coupling; frame-for-Tag borrow).
3. **All-n expressivity theorem.** Prove that the complete support-<=2 frame family `D++` contains an exact optimum for every n/target instance in the frozen R6M/raw-support grammar.
4. **Boundary mechanism.** Explain why support 2 is a genuine proof boundary while support >=3 can be exchanged away.
5. **Bounded structural regime evidence.** Evaluate compact named subfamilies/predicates prospectively, while retaining later QG refutations that show those named closed forms are not universal.

The novelty sentence must **not** start from "TARE leaves freedom". It should start from:

> TARE explicitly leaves auxiliary frame, control-label and Tag choices open to user optimization. We characterize the exact joint expressivity of a frozen shared-Tag compilation family built from those donor-exposed freedoms under a stated structural objective.

## Required Q1 manuscript edits

### Abstract/Introduction
- credit donor-exposed frame/Tag/control freedom explicitly;
- remove any wording suggesting donor TARE treats the joint design space only heuristically unless a full-text source directly supports that exact statement;
- replace with the narrower statement that the donor numerical study fixes one canonical `R_k` family and optimizes Tag strings independently for its reported comparisons.

### Related work
Add a donor-boundary paragraph:
- donor theorem: free `R_k`, ancilla count, controls; Tag solutions non-unique and optimizable;
- donor numerics: canonical `R_k` family, independent minimum-weight Tags;
- Q1 residual: exact global family/closure/counterexample theory for the frozen ORION grammar/objective.

### Methods
State explicitly that the R6M support-count objective and D/D+/D++ families are **analysis objects defined for this expressivity study**, not the donor paper's universal implementation objective.

### Discussion
Use the donor's constraint-dependent optimization motivation to justify QG objective-indexed follow-up instead of presenting objective dependence as a surprise about TARE itself.

## Claims now forbidden after full-text review

- "TARE fixes the anticommuting frame."
- "TARE does not consider optimizing the Tag."
- "ORION introduces the idea of choosing `R_k` for hardware/depth/width."
- "The donor literature treats the full design space as merely heuristic" unless narrower source-grounded wording is used.
- "Q1 optimizes all physically relevant TARE costs."

## Reviewer-risk resolution

A skeptical TARE author should be able to agree with the following positioning:

- their primitive and explicit design freedoms are fully credited;
- Q1 studies a new exact *analysis problem over those freedoms*, under a clearly declared frozen objective;
- later QG papers explore how that exact analysis changes with other objectives/families;
- no donor circuit/resource claim is reassigned to ORION.

## Source anchors used in this audit

Primary PDF, arXiv:2601.05740v4:
- Section 4 high-level construction: relation between `P_k`, `R_k` and stated freedom deferred to Section 4.1;
- Theorem 1 / Remark 1: `R_k`, `a`, `c_k` user-selectable; `S_i` optimizable;
- Theorem 2 / Remark 2: non-unique Tag linear-system solutions and weight/depth/gate-count optimization possibilities;
- Section 5: numerical comparisons use fixed canonical `R_k` family and independently minimum-weight Tag strings.

Final submission should cite the current paper version and recheck title/version metadata within 14 days.
