# Minimum Hybrid Splicing in Typed Authority Graphs — R10

Date: 2026-08-26

Status: analytic extension. Generic SET COVER complexity and approximation are donor-owned. The paper-specific object is the minimum number of independently valid evidence origins whose coordinate erasure can manufacture an authorization proof that no selected origin supports by itself.

## 1. Fine-origin and erased-origin semantics

Fix one declared authority/license coordinate and a finite positive Horn program `G` on claims `Q`. Let `O={1,...,r}` be evidence origins. Origin `i` independently seeds a set `S_i subseteq Q`.

With origins preserved, origin `i` is evaluated independently:

`C_i = Cl_G(S_i)`.

There is no authorized bridge between distinct origins in this base model. A target `q` therefore has fine-origin authority from a selected origin set `J subseteq O` exactly when

`q in union_{i in J} C_i`.

After **coordinate erasure**, the same selected records are pooled before inference:

`C_erase(J)=Cl_G(union_{i in J} S_i)`.

A selected origin set `J` is a **hybrid-splicing witness** for target `q` when

`q in C_erase(J)`

but

`q notin union_{i in J} C_i`.

Thus the erased system authorizes `q` only by combining premises across independently evaluated records.

Define the **splicing width**

`sw_G(q)=min{|J| : J is a hybrid-splicing witness for q}`,

with value `infinity` if no witness exists.

This definition measures proof-origin concentration. It is distinct from cryptographic validity of any individual artifact: every selected origin may be internally authentic and valid.

## 2. Pairwise checking is easy

For a fixed selected set `J`, compute all `C_i` and let

`C = union_{i in J} C_i`.

By the existing merge-safety theorem, coordinate erasure introduces no new authority beyond the independent closures exactly when `C` is closed under every rule of `G`. Equivalently,

`Cl_G(union_i S_i)=C`.

This is checked in linear worklist time in the explicit Horn incidence size after the component closures are available.

The new question is different: **how few origins suffice to create the first unsafe merge?**

## 3. Decision problem

### MINIMUM HYBRID SPLICING

**Input:** finite positive Horn program `G`, origins `O` with seed sets `S_i`, target claim `q`, integer `k`.

**Question:** is there a hybrid-splicing witness `J subseteq O` with `|J|<=k`?

### Theorem D-R10.1 — NP-completeness

MINIMUM HYBRID SPLICING is NP-complete. Hardness holds even when:

- there are no refutations;
- there is one license coordinate;
- `G` is acyclic and depth one;
- `G` contains a single rule;
- the target is not derivable from any individual origin.

### Proof

Membership in NP is immediate. Guess `J`, compute each component Horn closure and the pooled closure in polynomial time, and check the two conditions in the witness definition.

For hardness, reduce SET COVER while ensuring that no one origin already authorizes the target.

Start from a SET COVER instance with universe `U`, sets `A_1,...,A_r`, and budget `k`. Add one fresh element `z` and one fresh set `{z}`. Let

`U' = U union {z}`,

`A'_i=A_i` for `i<=r`, and `A'_{r+1}={z}`.

Set the new budget to `k+1`. The transformed instance has a cover of size at most `k+1` exactly when the original instance has a cover of size at most `k`. No single transformed set equals `U'`.

Create one claim `e_u` for every `u in U'` and one target claim `q`. Origin `i` seeds exactly

`S_i={e_u : u in A'_i}`.

The Horn program consists of the single rule

`{e_u : u in U'} -> q`.

Because no individual transformed set covers `U'`, no single origin derives `q`; in fact every fine-origin closure is just its seed set. Under coordinate erasure, a selected origin set `J` derives `q` exactly when the corresponding transformed sets cover `U'`. Hence a hybrid-splicing witness of size at most `k+1` exists exactly when the original SET COVER instance has a cover of size at most `k`.

The construction is polynomial and satisfies all listed restrictions. ∎

## 4. Complexity dichotomy

Theorems 14 and D-R10.1 give a useful security/verification dichotomy:

- **verify one proposed merge:** linear-time positive-Horn replay;
- **find the smallest collection of records that can create an unsafe hybrid proof:** NP-complete.

This mirrors a common operational split: checking a submitted evidence bundle can be cheap even when proactively finding the smallest dangerous cross-record combination is combinatorially hard.

## 5. Exact and parameterized algorithms

Let `r=|O|` and let `M` be the explicit Horn incidence size.

A direct exact algorithm enumerates all origin subsets in nondecreasing cardinality and evaluates the pooled and fine closures, giving

`O(2^r * r * M)`

in a straightforward implementation. Therefore the problem is fixed-parameter tractable in the number of origins.

For the single-conjunctive-rule reduction family above, the problem is exactly SET COVER. Standard exact subset DP and standard SET COVER approximation guarantees apply to that restricted family; these algorithms/guarantees are donor-owned and must be cited as such.

No generic logarithmic approximation claim is made here for arbitrary recursive Horn programs.

## 6. Weighted splicing cost

Assign each origin a nonnegative acquisition or trust cost `w_i`. Define

`sw_w(q)=min{sum_{i in J} w_i : J is a hybrid-splicing witness}`.

The weighted decision version is NP-hard already for the same depth-one reduction, by WEIGHTED SET COVER. This permits an operational interpretation in which difficult-to-combine records carry higher cost than readily co-located records.

## 7. Authorized bridges

If an explicit bridge policy permits certain cross-origin combinations, the baseline fine semantics must first compute the authorized bridge closure. A splicing witness is then defined relative to that intended closure rather than raw per-origin independence.

This is essential for real systems: legitimate same-request fragmentation, delegated identity chains, or an approved evidence-chain object must not be counted as attacks merely because several artifacts participate.

The minimum-splicing problem is therefore parameterized by the **declared bridge policy**. Erasing origin coordinates beyond those bridges is the tested failure.

## 8. Application boundary after August 2026 standards developments

Current authorization work now explicitly addresses heterogeneous evidence composition. In particular, the August 2026 IETF Internet-Draft `draft-schrock-ep-authorization-evidence-chain-05` defines Authorization Evidence Chains that preserve native verification, material-action matching, and relying-party evidence requirements; the related Action Evidence Boundary draft specifies executor-side evidence consumption and reconciliation.

Those systems are nearest work and must be treated as donor/context rather than as a problem ORION uniquely discovered.

The residual D contribution is therefore narrower and more formal:

1. typed least-fixed-point nonpromotion and retraction;
2. an exact linear-time merge-safety criterion for a submitted positive-rule evidence graph;
3. origin-sensitive prevention of undeclared cross-record proof construction;
4. the NP-complete minimum-hybrid-splicing problem above;
5. exact hostile corpora and independent replay; and
6. use of these theorems as a **static analyzer or preflight checker** for evidence-chain / gateway integration policies.

A strong application experiment should feed standards-valid evidence artifacts into a deliberately separate integration graph and ask whether the graph can manufacture a permission from mismatched origins. It must not claim that OAuth, MCP, Cedar, AIP, EP-AEC, or a compliant gateway is itself vulnerable unless a real implementation demonstrates that fact.

## 9. Paper-ready consequence

If the theorem survives nearest-work review, the D manuscript can state:

> In positive typed authority graphs, checking whether one proposed merge creates new authority is linear, while finding the smallest collection of independently valid origins whose coordinate erasure can manufacture a new authorization is NP-complete even for a single acyclic conjunctive rule.

That sentence is mathematically stronger and more durable than a generic claim that authorization evidence should retain provenance.
