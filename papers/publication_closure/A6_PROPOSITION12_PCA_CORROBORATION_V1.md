# Corroboration: Proposition 12 is donor-owned by proof-carrying authorization

**Status:** `CORROBORATION_OF_AN_ALREADY_MADE_DOWNGRADE`
**Scientific authority delta:** `NONE`.

`A6_DONOR_MATRIX_V2.md` covers all six donor fields #49 requires, including proof-carrying
action, and `A6_REMAINING_CANDIDATES_ADVERSARIAL_V1.md` had already downgraded Proposition
12. This document is **not news**; it is a second, independent route to the same place, and
it is recorded because two routes are worth more than one when a paper's novelty rests on
the outcome.

I had drafted this as a fresh finding before reading the matrix. Publishing it as a
discovery would have been a duplicate. What follows is the part that is not.

## The verification

Appel & Felten, *Proof-Carrying Authentication*, 6th ACM Conference on Computer and
Communications Security, 1999, read from the authors' own PDF rather than cited from memory:

- access is granted only when the requesting client supplies a proof, in the framework's
  logic, that the request follows from the server's published policy;
- the server's role is purely verification of the supplied derivation, and the authors
  deliberately move the burden of finding one onto the requester because the logic is
  undecidable;
- **the framework contains no notion of confidence, probability or expected utility anywhere
  in the access decision.** Its "trust" is a qualitative logical abbreviation, not a degree
  of belief; soundness is model-theoretic, not statistical.

Proposition 12 states there is no well-defined map `f` with `Perm(e) = f(Conf, EU)`. Its
proof constructs two effects with equal `(Conf, EU)` differing only in whether a support set
exists. In PCA that is not a countermodel to anything — it is the design, and has been since
1999.

## Why it is `SPECIALIZATION` rather than `DONOR`

PCA never had to prove this, because it never introduced `Conf` or `EU`. ORION-18 does
introduce them (Definition 20), so within its signature the separation is a real thing to
establish. That is exactly what `SPECIALIZATION` means here, and it is the disposition the
matrix already records.

## Corollary 12.1, which is a separate point and does matter

Corollary 12.1 follows syntactically from Definition 10 and adds nothing to Proposition 12,
its own parent. A results list that counts 12, 12.1 and 12.2 as three results triples the
apparent weight of one. See `A6_DONOR_SUBTRACTION_COMPLETION_V1.md`.
