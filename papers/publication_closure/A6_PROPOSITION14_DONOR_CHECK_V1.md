# The last survivor, checked against two fields the donor search missed

**Status:** `LAST_SURVIVOR_DOWNGRADED__SUBTRACTION_TALLY_REACHES_ZERO`
**Scientific authority delta:** `NONE`. This document can only narrow what the papers may
claim, and it narrows it to nothing.

## What this is answering

`A6_REMAINING_CANDIDATES_ADVERSARIAL_V1.md` — my own earlier document — left exactly one
`SURVIVING_NEW_CONSEQUENCE`: ORION-18 Proposition 14 clause 2. `A6_DONOR_MATRIX_V2.md`
covers all six donor fields #49 requires and keeps that same disposition.

The survivor rests on one sentence in that adversarial document's donor search:

> Non-monotonic logic gives retraction; AGM gives contraction; neither makes demotion
> *obligatory*. Deontic logic distinguishes permission from obligation but I found no
> formulation in which the loss of support *obliges* a demotion while leaving the historical
> judgment standing.

The search looked in logic. The claim is about **records of past decisions under later
revocation**, and two mature fields formalise exactly that. Both were checked against
primary or standards sources in session, not recalled.

## The claim, stated at its true size

Proposition 14 clause 2: if an authorization held at epoch `t` and its premises are revoked
at `t' > t`, then for a **committed** effect the epoch-`t` judgment stands as a historical
fact — correctly issued on epoch-`t` premises — while carrying **no forward authorization**,
so dependent effects must be re-derived. The paper names the failure it prevents: reading
"the commit was authorized, so it stands" as continuing authority.

Two things must be donor-owned together for this to fall: the historical judgment standing,
**and** the demotion being obligatory rather than merely available.

## Donor 1 — PKI long-term validation. Both halves, in one standard.

RFC 3161, *Internet X.509 Public Key Infrastructure Time-Stamp Protocol*. A timestamp
authority provides proof-of-existence for a datum at an instant, and the standard states the
consequence directly: a timestamp

> can be used to verify that a digital signature was applied to a message before the
> corresponding certificate was revoked, thus allowing a revoked public key certificate to
> be used for verifying signatures created prior to the time of revocation.

That is clause 2's first half exactly. The epoch-`t` judgment stands; revocation at `t'`
does not rewrite it.

The second half is the other side of the same standard's model. A relying party is required
to check revocation status before accepting a certificate for a **new** operation; a revoked
certificate confers no forward authority, and the requirement is normative, not optional.
Long-term validation and archive timestamping exist precisely to keep the historical
judgment verifiable *while* the certificate is dead going forward.

So PKI supplies the pair the donor search could not find: the past judgment preserved, the
forward authority withdrawn, and the withdrawal obligatory on anyone relying on it.

## Donor 2 — bitemporal databases. The same separation, as a data-model invariant.

Valid time versus transaction time, in the Jensen and Snodgrass sense, standard since the
1980s. Transaction time records when the system believed a fact; valid time records when the
fact holds. Transaction time is append-only, and the field's own justification for that is
the sentence Proposition 14 clause 2 is trying to state:

> the record of the system's own past beliefs is a historical fact that cannot be falsified;
> corrections are expressed as new assertions at different valid times, layered atop an
> immutable transaction-time log.

"The epoch-`t` judgment stands and the correction at `t'` is a new assertion rather than a
rewrite" is the bitemporal invariant with the nouns changed.

## The fairest reading, and it still is not a survivor

There is a real residue, and it should be stated rather than dismissed. PKI's obligation is
a conformance requirement on relying parties; bitemporal append-only is a data-model
invariant. Neither is expressed as a **deontic obligation inside a formal calculus with
three-valued terminals**. ORION-18 does express it that way.

That is what `SPECIALIZATION` means in this scheme: a donor-owned fact instantiated in a
new setting. It is not `SURVIVING_NEW_CONSEQUENCE`, because the consequence — historical
validity separated from continuing authority, with withdrawal obligatory — is not new. It
is the operating assumption of every long-term signature format and every bitemporal store
in production.

**Verdict: `SPECIALIZATION`, downgraded from `SURVIVING_NEW_CONSEQUENCE`.**

## The tally

| verdict | before | after |
|---|---|---|
| `DONOR` | 6 | 6 |
| `SPECIALIZATION` | 5 | **6** |
| `SURVIVING_NEW_CONSEQUENCE` | 1 | **0** |

#49's Phase 1 stop rule, in its own words:

> **Theory stop rule:** if no nontrivial theorem/consequence survives donor substitution,
> stop the broad top-tier theory claim and submit a bounded synthesis/specialist formal
> paper instead.

**The antecedent is now satisfied.** No individual result in either V2.1 core survives.

## What is left, and it is not nothing

The stop rule is about theorems and it fires. It is silent about the composition, and the
composition is a different object. Neither PKI nor bitemporal databases has a
**dependency-driven selective revalidation** mechanism: PKI re-checks a certificate,
bitemporal stores re-query a timeline, and neither computes an affected set and re-derives
only what a change touched. That is ORION-16's half, and ORION-18 has no repair vocabulary
to constrain it with.

So the position after A6 Phase 1 is narrow, defensible, and finally settled:

1. **Every individual theorem is inherited.** Six donor, six specialization, zero surviving.
   Both manuscripts must present them as inherited and claim nothing on them.
2. **The composition is not inherited**, and `a6-amplification-real-classifier-v1/` gives it
   a machine-checked attack — four amplifying edges, five realized in ORION-16's own case
   set — and a guard that closes them under a controlled metric.
3. The top-tier case, if there is one, rests **entirely** on the composition. A bounded
   specialist formal paper built on it is what the stop rule points to.

## Honesty about this document

I wrote the adversarial document whose survivor this removes, and its donor search was mine.
It looked in logic for a claim about records under revocation, and the two fields that own
that claim are not logics. That is the kind of miss a donor matrix organised by field is
supposed to catch, and `A6_DONOR_MATRIX_V2.md` did list assurance cases and proof-carrying
action — but not archival signature validation or temporal databases, which #49 does not
name either.

The correct conclusion is not that the matrix was wrong. It is that a donor search bounded
by a list of fields is only as good as the list, and a claim should be attacked by asking
*who else has had to solve this exact problem* rather than *which of my six fields covers
it*.
