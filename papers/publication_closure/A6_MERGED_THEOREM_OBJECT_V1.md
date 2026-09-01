# A6 Phase 1 — merged theorem object before any merged manuscript

**Status:** `MERGED_FORMAL_OBJECT_V1__NO_OUTCOME_OR_EXTERNAL_AUTHORITY`
**Date:** 2026-09-01
**Scientific authority delta:** `NONE`.

This file is the controlling composed theorem object for the ORION-16 + ORION-18
Tier-A Phase-1 programme.  It deliberately states the object in ordinary formal
language first.  Paper-specific names appear only in the source-mapping section.
No merged manuscript claim may be stronger than this object.

## 1. Primitive signature

Let:

- `D=(V,E)` be a finite directed dependency graph;
- `C subseteq V` be the currently certified claims;
- `X subseteq V` be the declared changed set;
- `Desc_D(X)` be the strict descendants of `X`;
- `A_D(C,X) = (X intersect C) union (Desc_D(X) intersect C)` be the affected set;
- a certificate be a tuple `k=(q,h,t,S,p)`, where `q` is its subject, `h` its
  authority domain, `t` its epoch, `S` its support/root record, and
  `p in {AUTHORIZED,DENIED,CANNOT_CHECK}` its permission terminal;
- `R` be a set of accepted exact-change preservation/revalidation proofs, each
  binding its subject, the exact changed set, the domain, the epoch, and an
  issuer that is outside the candidate transition's own authority;
- `fresh(k,h,t)` mean that `k` is valid for exactly domain `h` and epoch `t`;
- `new_authority(r)` mean that a repair step `r` actually supplies a fresh grant,
  root or discharged support that was not already available to the pre-change
  certificate.

Define the authorization bit

`auth(AUTHORIZED)=1`, `auth(DENIED)=auth(CANNOT_CHECK)=0`.

This bit is deliberately only a privilege order.  `DENIED` and `CANNOT_CHECK`
remain incomparable epistemic terminals; nothing below collapses one into the
other.

## 2. Selective revalidation object

A member `q in A_D(C,X)` is **preservable** only when `q notin X` and an accepted
proof in `R` establishes that the old certification is invariant under exactly
`X` while binding the same domain and epoch.  Directly changed certified roots
are never preservable by continuity; they require a new revalidation.

The selective reopen set is

`Reopen(D,C,X,R) = A_D(C,X) minus Preservable(D,C,X,R)`.

### Theorem S — selective revalidation safety

Assume the dependency graph is support-sound and every accepted preservation
proof is sound for the exact declared change.  Reopening/revalidating every
member of `Reopen(D,C,X,R)`, while preserving only `Preservable(D,C,X,R)`, leaves
no certification that may have become stale solely because of `X`.

The theorem is a safety statement.  Minimality additionally needs the usual
realizability/completeness premise for every affected member not protected by an
accepted exact-change proof.

## 3. Domain/epoch confinement object

An old certificate `k=(q,h,t,S,p)` may be transported as the *same authority*
only within its bound domain and epoch.  A transition to `(h',t') != (h,t)`
must either:

1. produce a new certificate from fresh, explicitly bound support/root evidence;
   or
2. remain non-authorizing (`DENIED` or `CANNOT_CHECK`).

A historical authorization at epoch `t` remains a fact about epoch `t`; it is
not forward authority at a later epoch after its support has been revoked.

### Theorem C — confinement implies non-amplification under repair

For a repair step that supplies no `new_authority`, if domain/epoch confinement
holds then

`auth(p_after) <= auth(p_before)`.

In particular a repair cannot turn `CANNOT_CHECK` or `DENIED` into `AUTHORIZED`
merely by changing domain, epoch, derivation path, or by exploiting a vacuously
empty obligation set.  A promotion is admissible only when the step records the
fresh support/root/grant that licenses it.

This theorem does **not** say authority can never increase.  It says an increase
must be attributable to a new authority-bearing premise rather than to the
repair mechanism itself.

## 4. Information-equivalent ideal donor

For the control comparison, both candidate and ideal typed product receive the
same tuple

`I=(obligations_discharged, blockers_refuted, grant_valid,
    epoch_current, domain_bound)`.

The ideal product returns:

- `AUTHORIZED` iff all five components are true;
- `DENIED` iff a blocker is established (represented by `blockers_refuted=false`
  with determination complete);
- otherwise `CANNOT_CHECK`.

The candidate may implement the decision in a different control structure, but
under information equivalence it may read no additional field and may hide no
missing premise.

### Control theorem I — information-equivalent tie

If candidate and ideal product implement the same typed authorization relation
on the same information tuple, their terminals are equal for every tuple.  Any
observed advantage over this donor therefore requires extra information,
different authority assumptions, or an implementation defect; it is not a
scientific-performance gain under information equivalence.

This is intentionally a donor/control theorem, not a novelty claim.

## 5. Required hostile countermodels

Any checker claiming this object must reject at least:

1. **root omission:** remove a directly changed certified root from the affected
   set;
2. **descendant omission:** remove a reachable certified descendant;
3. **self-preservation:** allow a directly changed root to retain its old
   certificate without revalidation;
4. **epoch laundering:** reuse an epoch-`t` authorization at `t+1` after support
   loss without fresh authority;
5. **domain laundering:** re-ground an unresolved certificate into an
   obligation-free domain and call it authorized without a new authority-bearing
   premise;
6. **ideal-donor asymmetry:** give the candidate an extra readable bit while
   still labelling the comparison information-equivalent.

## 6. Source mapping, after the theorem object

- The dependency/affected-set and exact-change preservation/revalidation pieces
  correspond to the ORION-16 V2.1 formal core, especially its support-sound
  affected set and preservation boundary.
- The three-valued permission, epoch demotion, root classes and non-amplification
  constraint correspond to the ORION-18 V2.1 formal core.
- `A6_COMPOSITION_ROUTE_V1.md` identified the seam between those two objects;
  `a6-amplification-real-classifier-v1/` demonstrates that the seam is not
  vacuous on the shipped transition classifier.

The merged object does not import either paper's transition function.  Its
independent finite formalization is in
`a6-independent-formalization-v1/check_merged_formalization_v1.py`.

## 7. Claim boundary

A green finite formalization establishes internal consistency of the composed
object over its exhaustive finite model.  It does not establish novelty,
external scientific validity, or the Phase-2 externally adjudicated study.
Those remain separate gates.
