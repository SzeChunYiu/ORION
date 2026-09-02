# A6 Phase 1 — donor matrix V4

**Status:** `TWO_REMAINING_FIELDS_CLOSED__DONOR_SUBTRACTION_ONLY`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. Like V2 and V3, this matrix can only
narrow novelty.

V2 covered five fields, V3 six more. Auditing ORION-18's `JOURNAL_READINESS.md`
§2 against the whole A6 corpus by **reading match context rather than counting
hits** leaves two genuine remainders, closed here.

## What the audit found

Seven of §2's ten family items were already discharged, and two more turned out
to be discharged in documents the earlier keyword sweep had not attributed to
them:

- **deontic / action logic** is dispositioned across `A6_COMPOSITION_ROUTE_V1`,
  `A6_DONOR_SUBTRACTION_COMPLETION_V1`, `A6_PROPOSITION12_ADVERSARIAL_V1`,
  `A6_PROPOSITION14_DONOR_CHECK_V1` and `A6_REMAINING_CANDIDATES_ADVERSARIAL_V1`
  — with a real donor search through it, not a mention ("Deontic logic supplies
  the same separation independently"; "I found no formulation in which loss of
  support *obliges* demotion").
- **ETAS / effect systems** is dispositioned in `A6_DONOR_SUBTRACTION_V1` and
  `A6_DONOR_SUBTRACTION_COMPLETION_V1` with named prior art (Bernstein 1966;
  Lucassen & Gifford 1988).

Two were not:

- **trust management** — **partially** covered, and the first version of this
  document overstated the gap. `A6_DONOR_SUBTRACTION_COMPLETION_V1` does
  disposition the **RT framework** of Li, Mitchell & Winsborough, as
  `SPECIALIZATION`, for the plurality of trust roots. What is absent is the
  other strand of the lineage: PolicyMaker, KeyNote and SPKI/SDSI appear
  nowhere, so decentralised *compliance checking* and *chain discovery* were
  never dispositioned. V2's "authorization / delegation logics" row cites
  Abadi–Burrows–Lampson–Plotkin and Appel & Felten, which are authorization
  *logics*, and does not close that strand either.

  The correction matters to how this document should be read: the claim below is
  that one strand of trust management was missing, not that the field was
  untouched. It was found by re-running the scan with `RT framework` restored to
  the pattern — an earlier verification pass had silently dropped that
  alternative and read the empty result as absence.
- **input/output logic** — §2 says "deontic / input-output / action logic". The
  deontic and action-logic halves are covered; input/output logic proper is
  named nowhere.

## Fields dispositioned in V4

| Required donor field | Primary donor objects checked | What the donor already supplies | A6 consequence |
|---|---|---|---|
| trust management — compliance-checking strand (the RT-framework strand is already `SPECIALIZATION` in `A6_DONOR_SUBTRACTION_COMPLETION_V1`) | Blaze, Feigenbaum & Lacy, *Decentralized Trust Management*, IEEE Symposium on Security and Privacy (1996) — PolicyMaker; Blaze, Feigenbaum, Ioannidis & Keromytis, *The KeyNote Trust-Management System, Version 2*, RFC 2704 (1999), DOI 10.17487/rfc2704; Ellison, Frantz, Lampson, Rivest, Thomas & Ylonen, *SPKI Certificate Theory*, RFC 2693 (1999), DOI 10.17487/rfc2693; Rivest & Lampson, *SDSI — A Simple Distributed Security Infrastructure* (1996); Clarke, Elien, Ellison, Fredette, Morcos & Rivest, *Certificate Chain Discovery in SPKI/SDSI*, Journal of Computer Security 9(4) (2001) | a compliance checker that answers "does this request, supported by these credentials, comply with this policy?" without a central authority; delegation chains discovered rather than pre-registered; and — the load-bearing part for ORION-18 — SDSI's deliberate **separation of naming from authorization**, kept apart precisely because conflating them was recognised as a design fault in the PolicyMaker lineage | Decentralised compliance checking over delegation chains is **donor**, and so is the naming/authorization separation. ORION-18 must not present "authority is checked against credentials rather than granted by a centre" as new, and — more sharply — must not claim the naming/authorization split as its own insight: SPKI/SDSI made it a deliberate architectural choice in 1996. What A6 may still own is the constraint on **repair-generated** credentials, which no chain-discovery formulation addresses because chains there are discovered, never manufactured. |
| input/output logic | Makinson & van der Torre, *Input/Output Logics*, Journal of Philosophical Logic, DOI 10.1023/A:1004748624537; *Constraints for Input/Output Logics*, DOI 10.1023/A:1017599526096; *Permission from an Input/Output Perspective*, DOI 10.1023/A:1024806529939 | norms as a transformation from inputs to obligated outputs rather than as truth-valued propositions, with the detachment question — which obligations actually follow from a given state — made explicit and the logic of the normative code kept separate from the logic of facts; a constrained variant for inconsistent output; and a treatment of **permission** in the same transformational setting | Treating an obligation as something *produced from* a state rather than asserted of it is **donor**, and it is the closest formalism to A6's "the transformation emits obligations". Naming it removes a defence A6 could otherwise have leaned on — that deontic logic's proposition-valued obligations are a poor fit — because input/output logic already is the better fit and is not ours. The permission paper is the sharper threat of the three: A6's permission semantics must be read against it, not only against classical deontic permission. |

## Effect on the tally

None. V4 adds no result-level rows, so `DONOR` 6 / `SPECIALIZATION` 5 /
`SURVIVING_NEW_CONSEQUENCE` 1 stands as adversarially revised. As with V3, the
change is to the **risk** carried by the survivor: input/output logic is a
closer formalism for obligation emission than anything V2 or V3 checked, and the
survivor should be re-read against it alongside the Rushby re-test V3 called
for. Neither re-test is performed here.

## What remains open in ORION-18 §2

Hostile exact-composition search, two no-material-change rounds, and a current
`#287` novelty certificate. Three passes over the field list cannot satisfy a
stability criterion; that is what the remaining items are for.

## Method note, recorded because it produced a wrong claim first

Both fields here were identified by scanning the A6 corpus. The first scan of
the trust-management family used the pattern
`trust management|SPKI|SDSI|KeyNote|RT framework|Blaze` and reported a hit; a
later "verification" scan used
`trust management|SPKI|SDSI|KeyNote|Blaze|Li, Grosof|Becker` — **`RT framework`
had been dropped** — returned nothing, and the nothing was read as absence. The
resulting claim, that the field had zero coverage, was false.

Two rules that would have caught it, and are applied above: an absence claim
needs a search whose scope is justified rather than merely one that returned
nothing, and any scan asserting absence must be run alongside a control term
that *must* match. The corrected scan reports 1 trust-management match outside
this document against 126 control matches for `donor` across the same 18 files,
so the scan demonstrably reads them.

## Citation provenance

Every citation in this V4 was located and checked against published records for
this document — the trust-management lineage including both RFC numbers and
their DOIs, and the three input/output logic DOIs. Nothing here is asserted from
recollection.

## Boundary

A donor matrix, not a priority certificate. Every entry can only subtract from
what ORION-18 may claim. If a source not listed here states the composed
repair/non-amplification result directly, this matrix must be amended rather
than the claim defended by terminology.
