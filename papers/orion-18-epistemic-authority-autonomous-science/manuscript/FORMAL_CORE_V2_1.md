# ORION-18 formal core V2.1 — primitive closure

**Supersedes:** `FORMAL_CORE_V2.md` where the two differ.
**Theory terminal:** `CLOSED_V2_1`
**Novelty / separate-paper terminal:** `CANNOT_CHECK` (unchanged by V2.1)
**Date:** 2026-08-18

V2 closed the derivation-typing, coercion-composition and revocation gaps but left four
elements of its own authorization rule implicit. Definition 10 clause 2 and all three
terminals of Definition 11 are stated in terms of a *blocker* that V2 never defines;
Definition 10 is silent about confidence and expected utility even though its intended
reading is that neither can move a terminal; the revocation machinery of Definitions
12–13 and Theorem 4 is never lifted to a statement about how authority behaves as the
premise stream grows; and Definition 15 relativizes protection to a candidate effect
without saying that protected custody is therefore one root class among several.

V2.1 closes exactly those four. It adds no new mechanism. Every V2 definition and result
not restated below remains in force, and §5 records the one place where V2.1 *corrects*
rather than extends V2.

## 1. Blockers

### Definition 18 — blocker

A blocker for effect request `e` is a valid available judgment

\[
b:\tau_b,\qquad \tau_b=(d,k,s,c,t),
\]

whose scope `s` covers `e` and whose content establishes that `e` is impermissible rather
than merely unsupported. `B(e)` denotes the set of blockers active for `e` in context
`\Gamma`.

A blocker is an *establishing* judgment, not the absence of a discharging one. This is the
distinction Definition 11 already relies on: an undischarged obligation whose evidence is
unavailable yields `CANNOT_CHECK`, whereas a present judgment establishing impermissibility
yields `DENIED`.

Blockers are premises like any other, so a blocker is cleared only by Definition 13. By
Theorem 4, `b` ceases to be active exactly when every support set `S_i\in\mathcal S(b)`
contains a revoked or invalid premise.

### Definition 19 — blocker determination

For effect `e` and blocker type `\tau_b`, the determination of `\tau_b` at epoch `t` is

- `ESTABLISHED` when some `b:\tau_b\in B(e)` is currently derivable;
- `REFUTED` when the available evidence entails that no `b:\tau_b` can be derived under
  the current premises;
- `UNDETERMINED` otherwise.

### Proposition 10 — blocker absence is not blocker refutation

Definition 10 clause 2 is satisfied only when every blocker type in scope for `e` is
`REFUTED`. If any is `UNDETERMINED`, the terminal is `CANNOT_CHECK`.

#### Proof

Suppose `UNDETERMINED` were read as satisfying clause 2. Then two contexts differing only
in whether the evidence needed to determine `\tau_b` has been consulted yield the same
`AUTHORIZED` terminal, one of which contains a derivable blocker. That assigns `AUTHORIZED`
to an effect Definition 11 classes `DENIED`, contradicting soundness. Hence clause 2
requires `REFUTED`, and `UNDETERMINED` falls to the `CANNOT_CHECK` clause of Definition 11,
whose premise — a mandatory premise that can be neither established nor refuted — is exactly
this case. `\square`

This is the fail-closed reading. "No blocker has been seen" is not "no blocker applies".

### Proposition 11 — blockers are monotone under evidence accumulation

Let `E\subseteq E'` be premise sets with no revocation between them. If `\tau_b` is
`ESTABLISHED` under `E`, it is `ESTABLISHED` under `E'`.

#### Proof

`ESTABLISHED` means some support set `S_i\in\mathcal S(b)` has every member valid under
`E`. Enlarging the premise set does not invalidate a member, since invalidation is
Definition 13 revocation, excluded by hypothesis. So `S_i` remains complete and `b`
remains derivable. `\square`

Proposition 11 is the semantic content Proposition 2 needs: an absolute blocker cannot be
outweighed by further positive evidence because further positive evidence cannot remove it.
Only revocation can.

## 2. Confidence, utility, support and permission

### Definition 20 — four separated quantities

For judgment `j` and effect request `e`:

- `Conf(j)\in[0,1]` — the agent's confidence in judgment `j`. For an effect request `e`,
  write `Conf(e)` for the profile of confidences over the judgments available to `e`;
- `EU(e)\in\mathbb R` — the expected utility of committing `e`;
- `Sup(o)` — factual support: the support family (Definition 12) witnessing discharge of
  obligation `o`;
- `Perm(e)\in\{AUTHORIZED,DENIED,CANNOT\_CHECK\}` — permission (Definition 11).

These are four distinct types. `Conf` and `EU` are agent-internal quantities, `Sup` is a
structure over premises, and `Perm` is a terminal.

### Proposition 12 — permission is not a function of confidence and expected utility

There is no well-defined map `f` with `Perm(e)=f(Conf,EU)`.

#### Proof

Definition 10 reads only obligations, blockers, grants, freshness and binding. Construct
`e_1,e_2` with `Conf(e_1)=Conf(e_2)` and `EU(e_1)=EU(e_2)`, differing only in that some
`o\in O_h` is discharged for `e_1` and undischarged for `e_2` because the evidence its
required judgment type names is unavailable. Unavailable evidence removes a support set,
not a confidence value, so the confidence profiles remain equal by construction. By
Definition 10 clause 1, `Perm(e_1)=AUTHORIZED` and `Perm(e_2)=CANNOT\_CHECK`. Both lie in
the same fibre of `(Conf,EU)`, so `f` is not well defined. `\square`

### Corollary 12.1 — no amount of confidence or utility promotes a terminal

Raising `Conf` or `EU` cannot convert `CANNOT_CHECK` or `DENIED` into `AUTHORIZED`, since
neither appears in any clause of Definition 10.

### Corollary 12.2 — soft preferences rank, they do not discharge

V2's remark that soft preferences may rank already authorized effects is exactly the claim
that `EU` is a total preorder on the `AUTHORIZED` fibre and has no action on the terminal
itself.

## 3. Monotonicity of authority

### Proposition 13 — authority is non-monotone

`Perm` is non-monotone in the premise stream in both directions:

1. adding a premise can move `AUTHORIZED\to DENIED`, by establishing a blocker
   (Definition 18);
2. revoking a premise can move `AUTHORIZED\to CANNOT\_CHECK` or `AUTHORIZED\to DENIED`, by
   breaking every support set of a discharge (Theorem 4).

#### Proof

For (1) take `e` authorized under `E` and let `E'=E\cup\{x\}` where `x` completes a support
set of a blocker in scope; Definition 10 clause 2 then fails. For (2) take `e` authorized
with a single support set `S` for a hard obligation `o`, and revoke any `x\in S`; by
Theorem 4 no complete support set remains, so `o` is undischarged and clause 1 fails,
landing in `CANNOT_CHECK` if the evidence is merely unavailable and `DENIED` if the
revocation itself establishes a blocker. `\square`

Propositions 11 and 13 together fix the direction of the asymmetry: authority is non-monotone,
blockers are monotone. Evidence can only ever take authority away or leave it, never restore
it, without a corresponding revocation.

### Proposition 14 — demotion is mandatory and forward-only

Let `\kappa` authorize `e` at epoch `t` and let premises be revoked at `t'>t` such that no
complete support set of `\kappa` survives.

1. If `e` has not been committed, `e` is not authorized at `t'`; the prior certificate does
   not transport (Definition 14).
2. If `e` was committed at `t`, the epoch-`t` authorization judgment stands as a historical
   fact: it was correctly issued on the epoch-`t` premises, and `t'` does not rewrite it.
   This is **not** a claim that the commit remains authorized. `\kappa` is invalid at `t'`,
   so `e` carries no forward authorization and any dependent effect must be re-derived.
   Symmetrically, a blocker discovered at `t'` does not make the commit pre-effect
   authorized (Proposition 5).

#### Proof

(1) is Theorem 4 plus Definition 14: the certificate is not valid at `t'` and freshness is
required at the commit epoch. (2) is Proposition 5 in both directions: an epoch-`t'`
judgment is not an epoch-`t` premise. `\square`

Point 2 is why demotion is an obligation on the *pending* queue rather than a rewrite of
history: history is immutable `H`, and the recorded fact is that the commit occurred under
premises later revoked. Reading it as "the commit was authorized, so it stands" is the
fail-open error — the historical judgment is preserved precisely so that the loss of support
is visible, not so that it can be cited as continuing authority.

## 4. Root classes

### Definition 21 — root class

A root `g\in G` belongs to exactly one class:

- `PROTECTED_CUSTODY` — a root satisfying Definition 15 relative to the candidate effect;
- `DELEGATED_GRANT` — a root derived from a higher authority context by an explicit,
  in-scope delegation;
- `STANDING_POLICY` — a root fixed by policy independently of any candidate effect;
- `OBLIGATION_FREE` — a domain-level root for a domain with `O_h=\emptyset`.

### Proposition 15 — protected custody is one root class, not the only one

Protection is a predicate on roots relative to an effect, not the definition of a root.

#### Proof

Definition 15 quantifies over a candidate effect `e`: the same root may be protected
relative to `e` and unprotected relative to `e'` that can rewrite the deciding policy.
A predicate that varies with `e` cannot be the identity of the root. Concretely, a
`DELEGATED_GRANT` can authorize an effect whose domain carries no self-modification
capability at all, with no custody claim made or needed. `\square`

### Proposition 16 — Proposition 7 is a scope restriction, not a custody requirement

Proposition 7 states that an unprotected root cannot ground *self-admission*. It does not
state that every authorization requires protected custody. The restriction bites exactly
when the candidate effect can reach the deciding policy or its evidence, which is the
hypothesis of Definition 15 and is false for the majority of `DELEGATED_GRANT` and
`OBLIGATION_FREE` cases.

## 5. Correction to V2

V2's Definition 10 clause 2 and Definition 11 read "no blocker applies" and "no active
blocker applies". Under Definition 19 that phrasing is ambiguous between `REFUTED` and
`UNDETERMINED`. Proposition 10 resolves it in favour of `REFUTED`. Any implementation that
reads clause 2 as "no blocker has been observed" is unsound by Proposition 10 and is a
fail-open defect of exactly the kind Definition 11's third terminal exists to prevent.

This is the only place V2.1 changes a V2 reading rather than adding to it.

## 6. Executable support

`formal/check_theory_closure_v2_1.py` deterministically checks, with finite countermodels
and the standard library only:

- fail-closed blocker determination, including the fail-open countermodel;
- blocker monotonicity under evidence accumulation;
- a witness pair proving permission is not a function of confidence and expected utility;
- authority non-monotonicity in both directions of Proposition 13;
- forward-only demotion, including the non-retroactivity of a later blocker;
- protected custody as one root class, with an authorized non-custody root and a refused
  unprotected self-admission;
- that the V2 results relied on above still hold.

## 7. Final theory terminal

- `P8_THEORY = CLOSED_V2_1`
- `P8_NOVELTY = CANNOT_CHECK_UNTIL_LITERATURE_CLOSURE`
- `P8_SEPARATE_PAPER = CANNOT_CHECK_UNTIL_STRONG_BASELINE_DISCRIMINATOR`

V2.1 closes primitives internal to the theory. It moves neither of the two `CANNOT_CHECK`
terminals, which depend on literature closure and on a strong baseline discriminator
respectively, and it does not weaken §10's product-decomposition result.

## Addendum (2026-08-24): native cross-system execution protocol

The ORION-18 native-execution box is frozen as contract
`ORION-18.NATIVE.CROSS_SYSTEM_PROTOCOL.V1` (protocol document plus machine-readable
twin plus binding checker under `formal/`): twelve ordered cross-system pairs
over OPA/Rego, Cedar, in-toto/SLSA and Sigstore, clean and hostile cases for
every pair, ideal typed-product baseline. The protocol **is not executed**:
the required binaries are absent from the producing environment, the status is
`CANNOT_CHECK` with the tooling gap recorded, and simulation-as-execution is a
prohibited inference. Nothing in V2.1's closure or in the §10 product
decomposition is changed by this addendum.
