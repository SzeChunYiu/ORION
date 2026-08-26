# Mathematical Extensions R7 — Antichain Compilation of Typed Authority

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, `MATHEMATICAL_EXTENSIONS_R5.md`, and `MATHEMATICAL_EXTENSIONS_R6.md`.

Status: theorem addendum. Generic positive-Datalog provenance, support hypergraphs, resilience, and hitting-set hardness are donor mathematics. The results below exploit the typed license caps and their global signature order.

## 1. Signature poset

Quotient licenses by the R5 syntactic signature

`sig(lambda)=(seed-membership vector, rule-cap-membership vector)`.

Order the resulting classes by componentwise inclusion: `lambda <= mu` when every `lambda` seed is also a `mu` seed and every rule enabled for `lambda` is enabled for `mu`.

For every seed claim `q`, let `U_q` be the set of license classes that seed `q`. For every rule `r`, let `K_r` be the classes that enable `r`. Both are upsets of the signature poset.

## 2. One simultaneous fixed point

For a claim `q`, let `A(q)` be the set of licenses authorizing it. Directly refuted claims are assigned the empty set. Otherwise define

`F(A)(q)=U_q union`

`union_{r:head(r)=q} [K_r intersection intersection_{b in body(r)} A(b)]`.

**Theorem D10 (upset fixed-point semantics).** The least fixed point of `F` gives, simultaneously for every license, exactly the ordinary positive-Horn closure of that license projection.

**Proof.** Membership of one license `lambda` in the displayed recurrence is precisely the Boolean immediate-consequence operator for the `lambda` seeds and `lambda`-enabled rules. Least fixed points commute with coordinate projection because the operator is positive and coordinatewise. ∎

Every iterate and every final authority set is an upset. Typed nonpromotion is therefore a structural invariant, not a post-processing convention.

## 3. Antichain representation

Every upset in a finite poset is uniquely determined by its minimal elements.

**Theorem D11 (exact antichain compilation).** Replacing every authority upset by its minimal antichain preserves the full typed least-fixed-point semantics. No license coordinate is lost.

If the signature poset has width `w`, every stored label has at most `w` generators. The number of licenses may be much larger because aliases and dominated policy levels do not enlarge the antichain.

The R6 minimal/maximal-license reductions are immediate consequences: presence of all licenses is controlled by minimal signatures, while absence of all licenses is controlled by maximal signatures.

## 4. Chain threshold theorem

Suppose the signature classes form a chain `1<...<m`. Every nonempty upset is a suffix and can be represented by one threshold. Let `s(q)` be the first level seeding `q`, or infinity; `k(r)` the first level enabling rule `r`, or infinity; and `tau(q)` the first level authorizing `q`.

**Theorem D12 (min-max authority recurrence).** For an unrefuted claim,

`tau(q)=min( s(q),`

`min_{r:head(r)=q} max(k(r), max_{b in body(r)} tau(b)) )`.

For a finite acyclic rule graph, all thresholds are computed in one topological pass.

**Proof.** Union of suffixes takes the smaller threshold. Intersection of suffixes takes the larger threshold. Substitute these identities into Theorem D10. Acyclicity makes every body threshold available before its head. ∎

Thus `m` separate Horn evaluations collapse to one bottleneck-style computation. The threshold records the weakest policy level at which a complete derivation becomes valid.

## 5. Recursive programs

For positive recursive rules, iterate the min-max recurrence from infinity, decreasing thresholds whenever a seed or derivation improves them. Finiteness of the chain guarantees termination at the least fixed point. Standard work-list acceleration applies. The theorem concerns semantics; implementation complexity depends on the chosen poset and antichain data structure.

## 6. ORION authority application

The frozen QG5 record contains one erroneous original exactness label among 9,546 benchmark entries. The stratified authority calculus retracts exactly the original closed-form exactness and regime label while retaining the independently supported upper bound, repaired label, support theorem, and exact `F2` statement.

The antichain formulation explains this behavior without flattening evidence classes. `PROSPECTIVE`, `POST_OUTCOME`, `THEOREM`, and bounded-computation authority are propagated by their own caps. A post-outcome repair can restore a conclusion at one policy coordinate while remaining unable to recreate prospective authority.

Potential applications include regulatory provenance, data-use licenses, evidence retraction, incident-response claims, and multi-agent scientific systems in which reachability alone is too coarse.

## 7. Prior-art recalibration

Generic minimal supports, blocker hypergraphs, robustness, responsibility, and deletion hardness overlap current Datalog causality and database-resilience work and receive no novelty credit here.

The residual contribution is powerset-valued evidence labels with cap-preserving rules, exact coordinatewise retraction, nonpromotion and dominance from a global signature order, exact antichain compilation of all license projections, and the chain min-max evaluator.

## 8. Atomic status

- Per-license Horn equivalence: inherited `VERIFIED`.
- Upset fixed-point theorem: `VERIFIED`.
- Antichain compilation: `VERIFIED`.
- Chain min-max recurrence: `VERIFIED`.
- QG5 minimal retraction: `VERIFIED` by frozen source/generic/native records.
- Generic provenance novelty: `WITHDRAWN`.
- Real-world legal correctness of any example policy: `NOT_CLAIMED`.
