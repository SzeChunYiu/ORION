# P6-X2 science terminal V1

Date: 2026-08-19
Parent: #533

## Terminal
`P6_CERTIFICATE_LIFTING_SEMANTICS_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`

## What changed from P6 V3
V3 established a scientific-admissibility erasure/separation theorem over donor semantic embeddings. X2 widens constructively: it absorbs strong modern proof/certificate machinery as first-class donor certificates and defines when those certificates can be lifted into preservation of scientific standing after change.

## Donor-first result
The strong donor stack retains its native strengths:
- runtime authorization/path/history/replay certificates;
- certified-trace permissibility and proposal/certification/execution separation;
- portable action identity/approval/runtime/outcome receipts;
- workflow provenance/reproducibility execution signatures;
- executor-purity/attestation certificates;
- existing dependency/effect/authorization semantics.

P6 does not replace or reclaim those mechanisms.

## Added P6-X2 semantics
A valid donor certificate or donor-certificate product lifts to preserved scientific standing only through explicit claim-specific continuity coordinates. The frozen bounded instance uses claim/content binding, measurement semantics, evidence semantics, inferential obligation and scientific epoch.

The improvement over the donor stack is:
1. explicit scientific lift witnesses;
2. no laundering from accumulation of lower-level certificates;
3. exact selective revalidation of affected scientific coordinates while retaining unaffected donor certificates;
4. extensional equivalence to an ideal donor product enriched with the same scientific fields/rules.

## Exhaustive support
Primary checker: `check_p6_x2_certificate_lifting.py`.
Independent checker: `independent_check_p6_x2_certificate_lifting.py`.

Exact bounded enumeration:
- 320 donor-certificate/scientific-extension states;
- 0 donor-conservativity violations;
- 25 minimal single-coordinate certificate-lifting separation witnesses;
- 31 countermodels where all donor-native certificates may be treated as valid yet an absent scientific coordinate prevents lifting;
- 155 exact full-revalidation successes;
- 1,055 proper-subset revalidation failures;
- 0 ideal enriched-product mismatches;
- canonical row SHA-256 `e1e3c48bcefea3750d952c6b0ff37ac660a2e21f9823fdfdeb50bb62e819ff93`.

## Wider allowed claim
> Strong execution, action, workflow and attestation certificates can be composed and preserved as lower-level objects in dynamic scientific computation, but preservation of scientific standing requires an explicit lift across claim-specific semantic obligations; material changes trigger exact revalidation of affected scientific coordinates without discarding unrelated valid donor certificates.

This is a general formal architecture claim only over the registered certificate interface and donor embeddings. It is wider than the prior erasure result because it specifies positive composition/reuse and selective preservation.

## Forbidden upgrades
- universal minimality of the five scientific coordinates;
- deployed-agent superiority;
- claim that PoE/PCE/PCAA/workflow signatures/purity certificates are insufficient for their native goals;
- inherent expressivity or centralization advantage;
- claim that no future donor can directly encode the same scientific lifting information.

## Reopen rule
Reopen if a primary formal system supplies an equivalent scientific lift/preservation/revalidation calculus over equally rich donor certificates, or if a countermodel breaks selective revalidation under the registered interface assumptions.

## Addendum 2026-08-22 — what those zeros were, and what they are now

Two of the eight quantities listed under *Exhaustive support* were not
measurements when this terminal was written, and the artifact did not say so.

`0 donor-conservativity violations` was computed as `projected_native =
native_valid` followed by `if projected_native != native_valid`: one variable
compared with itself, 0 under every theory of lifting. `0 ideal
enriched-product mismatches` compared `liftable(...)` against an inline copy of
`liftable`'s own body, so under a consistently applied theory it was `x == x`.
Neither could have come out any other way, which is the failure class recorded
at `research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/`.

Both are measurements now, and neither number moved. What changed is what the
checker is able to say:

- **T1 gained the projection.** `check_p6_x2_certificate_lifting.py` now carries
  `project_to_donor`, and states conservativity about the *image of `liftable`
  along it*: a donor certificate is certified by the lifted semantics exactly
  when it is certified by the donor theory. The comparison reads the lifting
  rule, and the fibre quantification visits the 32 `native_valid = False` states
  that no assertion in the file previously reached — so
  `assertion_coverage_status` moved from `PARTIAL` to `COMPLETE` without a
  bolt-on "nothing lifts without a donor" assertion.
- **T5 gained a constructed ideal product.** The ideal enriched donor product is
  now the donor theory's own validator run over a requirement set enlarged by
  the five scientific coordinates, rather than the lifting predicate written
  twice. It never mentions `liftable`, so a wrong theory of lifting cannot
  co-mutate it.

Measured against a register of nine wrong theories of lifting
(`python -m orion.study.p6.refutation_audit`), all five published quantities now
reject at least one, and every wrong theory in the register is rejected by at
least one quantity. Before the repair, T1 and T5 rejected none of the eight then
registered, and `science_lifts_without_donor` — scientific standing preserved
with no valid donor certificate underneath it, the direct denial of P6.V4.1 —
was rejected by no check at all.

The ninth entry is new and is this document's own third falsifier made
executable: `unbridged_donor_discharges_coordinate`, under which one donor family
discharges `evidence_semantics` with no bridge rule binding it. It is the only
registered theory in which the donor coordinate and the scientific coordinates
interact, and it is rejected by the separation witnesses, the revalidation block
and the reconstructed ideal product.

### Multiplicity of the reported counts

`liftable` does not take the donor family as an argument, so donor-independence
holds by construction and the five-family loop repeats every quantity enumerated
inside it. The published counts and their distinct content:

| published | distinct | multiplicity |
| --- | --- | --- |
| 320 state evaluations | 64 | ×5 |
| 25 separation witnesses | 5 | ×5 |
| 155 full revalidation successes | 31 | ×5 |
| 1,055 proper-subset failures | 211 | ×5 |
| 31 product countermodels | 31 | ×1 |

This is not a defect in the rule — donor-independence is a claim P6 makes, and a
theory under which the issuing family decides the verdict is registered as false
— but reporting 320 without reporting 64 overstates the enumeration. The result
JSON now carries a `donor_axis` block with both. Giving the five families
distinct native validators, as the finite-model checker's three embeddings have,
would change the enumerated space and therefore `canonical_rows_sha256`; that is
a new theorem instance, not an edit to this one.
