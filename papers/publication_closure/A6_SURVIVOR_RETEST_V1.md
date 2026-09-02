# The two deferred re-tests, performed: Rushby channel control and input/output permission

**Status:** `BOTH_RETESTS_PERFORMED__TALLY_UNCHANGED__RESIDUE_DECOMPOSED`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. This document performs re-tests that earlier
matrices deferred. Re-tests can only narrow or confirm; they promote nothing.

## What this is answering

Two documents explicitly deferred work that this one performs.

`A6_DONOR_MATRIX_V3.md`, Rushby row:

> the survivor must be re-tested against it before it is defended. That re-test is not
> performed here.

`A6_DONOR_MATRIX_V4.md`, input/output row:

> the survivor should be re-read against it alongside the Rushby re-test V3 called for.
> Neither re-test is performed here.

Since those matrices were written, `A6_PROPOSITION14_DONOR_CHECK_V1.md` downgraded the
last `SURVIVING_NEW_CONSEQUENCE` (Proposition 14 clause 2) to `SPECIALIZATION`, the #49
Phase 1 stop rule fired at **6 donor / 6 specialization / 0 surviving**, and the position
became: every individual theorem is inherited; the composition is the only candidate
object. The re-tests below therefore run against the *residue as it now stands*, not
against a surviving theorem.

All three primary sources were located and checked in session, not recalled: the full
Rushby 1992 report (SRI CSL-92-02 long version), the Springer published records of
Makinson–van der Torre 2000 and 2003, and the OASIS XACML 3.0 core specification.

## Re-test 1 — Rushby 1992, against the primary text

### What the report actually supplies (confirmed donor)

- Channel control is posed as an **intransitive** policy: "directed graphs, where nodes
  represent security domains and edges indicate the direct information flows that are
  allowed", with the paradigm "the only channels for information flow from Red to Black
  must be those through the Crypto and the Bypass".
- Rushby shows the transitive (Goguen–Meseguer) formulation cannot express this — it is
  simultaneously too strong and too weak — and adopts Haigh–Young's intransitive purge:
  `v ∈ sources(α,u)` iff `v = u` or a subsequence of actions by domains
  `w₁,…,wₙ` exists with `w₁ ↣ w₂ ↣ … ↣ wₙ`, `v = w₁`, `u = wₙ`.
- **Theorem 8** gives the access-control reading verbatim in ORION-18's shape: A→B→C is
  permitted through B while "A may not have alter access to any locations to which C has
  observe access; in this way, direct flow of information from A to C is prevented".

Mapped to ORION-18: the registered coercion is the declared channel (the Crypto/Bypass
role); oracle rule 4 — foreign source domain without registered coercion →
`UNAUTHORIZED` — is Red ↛ Black. **V3's judgement that the mediation shape is donor is
confirmed from the primary text, not from the secondary summary.**

### The residue against the primary text

V3 granted A6 only one thing beyond Rushby: "the declared channel must itself carry a
fresh authority-bearing premise." Checked against the report, that residue is real but
not Rushby-shaped, and not new:

- The 1992 policy is a **static** reflexive relation on domains; the model "admits no
  'rules'". Modification of access-control tables is explicitly out of scope: in models
  that permit it, "the 'rules' should be individually verified by direct reference to the
  appropriate unwinding theorem". No per-use channel evaluation, no freshness, no
  revocation, no epochs, no third decision value appear anywhere in the report.
- The freshness/continuous-evaluation half is donor elsewhere and **already dispositioned
  in the repo's own corpus**: `ORION18_FINAL_V4_PROPOSED.md` records that "the
  continuous-control reading of permission is usage control (Park and Sandhu 2002,
  2004)" — UCON's ongoing obligations and condition-mutable attributes are per-use,
  premise-conditioned permission evaluation.
- The cannot-evaluate third value is donor in a deployed standard (XACML 3.0 `Indeterminate`
  plus fail-closed obligations — next section).

**Verdict: the V3 residue decomposes into three donor-owned mechanisms — intransitive
channel control (Rushby/Haigh–Young) × per-use premise-conditioned evaluation
(Park–Sandhu UCON) × a distinguished cannot-evaluate terminal (Chow's reject option;
XACML).** Stating their composition as a constraint inside a typed three-valued calculus
is positioning, not a theorem. This is consistent with the fired stop rule: the
composition is the bounded-synthesis paper's object, and each part is inherited.

## Re-test 2 — input/output logic, re-read at the published record

### What the 2000 paper supplies (donor, as V4 granted)

The Springer record of *Input/Output Logics* (JPL 29:383–408, 2000) characterizes the
framework as operations "resembling inference, but where input propositions are not in
general included among outputs" and where "the operation is not in any way reversible",
with four named output operations (simple-minded, basic, simple-minded reusable, basic
reusable; the reusable ones recycle outputs as inputs). Treating an obligation as
something produced from a state by a non-reversible transformation — ORION-18's emission
framing — is donor here, exactly as V4 recorded.

### The 2003 permission paper narrows further (new finding)

*Permission from an Input/Output Perspective* (JPL 32(4):391–416, 2003) separates
negative from positive permission, and then **splits positive permission in two**:

> One of them, which we call static positive permission, guides the citizen and law
> enforcement authorities in the assessment of specific actions under current norms, and
> it behaves like a weakened obligation. Another, which we call dynamic positive
> permission, guides the legislator. It describes the limits on the prohibitions that may
> be introduced into a code, and under suitable conditions behaves like a strengthened
> negative permission.

This maps onto both halves of ORION-18 at once:

| i/o 2003 | ORION-18 |
|---|---|
| static positive permission: per-action assessment under current norms, "behaves like a weakened obligation" | the per-effect authorization rule (Definition 10/11): each effect judged against the currently valid premises |
| dynamic positive permission: "limits on the prohibitions that may be introduced into a code" — constrains the *legislator*, not the citizen | the policy/self-modification scope restriction (Propositions 7/15/16): an unprotected root cannot ground self-admission; custody is relative to effects that can reach the deciding policy |

ORION-18's separation of **effect authorization** from **authorization-to-change-the-
authorization-rules** therefore parallels the static/dynamic permission split of the i/o
tradition. Both manuscripts must cite this line; the separation is inherited design
stance, not a discovery. Permission in i/o logic is qualitative, which aligns with
Proposition 12 (permission is not a function of `Conf`/`EU`) while donor-owning the
stance that permission is a distinct logical category from graded belief.

### What i/o logic does not threaten

Nothing in the published records consulted here (titles, abstracts, keyword sets,
reference lists of 2000/2001/2003) introduces time, epochs, freshness, revocation, or
withdrawal of previously derived obligation; the 2001 *Constraints for input/output
logics* addresses consistency of output with standing constraints, not premise
revocation. The revocation mechanics of Proposition 14 remain dispositioned by RFC 3161
and bitemporal databases (`A6_PROPOSITION14_DONOR_CHECK_V1.md`), which are closer
parents. This absence claim is scoped to the published records listed; a full-text study
of the constrained variant could only narrow further, never widen.

## Supplementary donor found by the who-else-solved-this attack: XACML 3.0

Running the re-test's own method ("who else had to solve this exact problem" rather than
"which fields does my matrix list") surfaced a standards-track donor absent from the A6
corpus: **OASIS XACML 3.0**. Verified against the core specification in session:

- The decision set has a distinguished cannot-evaluate value: "A policy can return
  'Permit', 'Deny', 'NotApplicable' or 'Indeterminate'", where "if an error occurs when
  evaluating the rule, then the rule returns a result of 'Indeterminate'".
- Obligations are **fail-closed**: the policy enforcement point is "required to deny
  access unless they understand and can discharge all of the" Obligations attached to the
  decision; only Advice (never obligations) may be safely ignored.

Consequences: "authorization decision with a distinguished cannot-evaluate value" is
donor; "an undischargeable obligation forces the refusal" is donor, in a deployed
standard, as a *non-compensatory obligation semantics*. What remains for ORION-18 is
thin and must be stated as such: XACML collapses cannot-discharge into `Deny` at
enforcement, whereas ORION-18 preserves `CANNOT_CHECK` as its own terminal in the typed
calculus and makes abstention mandatory rather than denial — one sentence of distinction,
plus V3's already-narrowed residue (non-compensatory *abstention* which the
risk-coverage framing does not express). Absence of an XACML row in V2–V5 is a matrix
gap, now recorded here.

## The tally

| verdict | before this document | after |
|---|---|---|
| `DONOR` | 6 | 6 |
| `SPECIALIZATION` | 6 | 6 |
| `SURVIVING_NEW_CONSEQUENCE` | 0 | 0 |

Both re-tests confirm; neither re-opens a survivor; each narrows. The stop-rule position
is unchanged: all individual theorems inherited; the composition is the only candidate
object, and its parts are each donor-owned (Rushby channel shape, UCON per-use
evaluation, XACML/i-o permission categories, PKI/bitemporal revocation semantics).

## Boundary — what this document does not establish

1. It does not execute the laundering attacks inside Rushby's formalism (no unwinding
   check of ORION-18's five domains). That would be a construction, not a donor test;
   the A6 method is donor subtraction only.
2. It does not claim i/o logic lacks revocation as a theorem of the literature — the
   absence statement is scoped to the published records consulted, as stated above.
3. The i/o static/dynamic mapping is a shape correspondence read off the 2003 abstract's
   own definitions, not a formal translation; no embedding is defined or checked.
4. XACML is added as a supplementary donor row; V2–V5's existing verdicts are not
   re-derived against it.

## Honesty about this document

The Rushby findings rest on the full primary text. The i/o findings rest on the Springer
published records (abstracts, keywords, reference lists, citation metadata) — the full
texts are paywalled and were not consulted; every load-bearing sentence above quotes or
paraphrases only what those records state. The XACML findings rest on the OASIS core
specification text. The UCON disposition is quoted from the repo's own
`ORION18_FINAL_V4_PROPOSED.md`, which performed that check. I also wrote the matrices
that deferred these re-tests; performing one's own deferred tests is the minimum
obligation, and the XACML gap shows the matrix list was again incomplete until attacked
by problem, not by field.
