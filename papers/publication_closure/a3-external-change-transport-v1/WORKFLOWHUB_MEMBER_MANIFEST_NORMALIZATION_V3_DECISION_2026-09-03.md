# Freeze-governance decision: member-manifest normalization v3 (request-generated member exclusion)

Decision id: `WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3`. Frozen 2026-09-03,
before the v3 harvest ran, by the A3 freeze-governance lane. The frozen v2
normalization, the frozen successor frame, the frozen validators and the frozen
candidate policy are untouched by this decision and remain the authorities
until a separately governed successor-frame rebind says otherwise.

## 1. What was observed (the boundary this decision answers)

The member-manifest harvest of 2026-09-03 (sbatch 3569824 on cn004; volatility
diagnostic sbatch 3569845; both logged under
`workflowhub-member-manifest-freeze-v1/RESULT_V1.json`) attempted to
materialize member-level normalized manifests for all 128 families of the
frozen successor frame, bound to the frame's frozen per-family before/after v2
aggregates. It failed closed on 95 of 128 families:

- For those 95 families the WorkflowHub `ro_crate` endpoint regenerates
  `ro-crate-metadata.json` and `ro-crate-preview.html` at request time. Three
  consecutive fetches of the SAME version of workflow 29 returned three
  distinct v2 aggregates while the member set was identical and every
  workflow-content member was byte-identical; the only differing members were
  the two generated files.
- The other 33 families reproduce their frozen v2 aggregates exactly, on
  every fetch.
- Consequence recorded by the boundary result: the v2 aggregates for the 95
  volatile families bind single-request bytes that are irretrievable from the
  live registry, so member-level candidate-visible manifests bound to the
  frozen v2 aggregates are unobtainable for 95/128 families by any fetch
  strategy.

## 2. The decision

v3 excludes the two request-generated crate files from the frozen
member-manifest aggregates and from the candidate-visible member manifests,
uniformly for every crate of every family:

- **Rule (exact).** The v3 normalized member manifest is the frozen v2
  `normalized_content_manifest` (bind_workflowhub_rocrate_content_v1.py,
  imported verbatim) minus every entry whose canonical path is exactly
  `ro-crate-metadata.json` or `ro-crate-preview.html` at the crate root. The
  v3 aggregate is the frozen v2 `canonical_json_sha` over the retained
  entries. Nothing else changes: same canonical path validation, same
  duplicate-path rejection, same directory skipping, same per-member Unix
  semantics (kind, executable bit), same path sort, same canonicalization.
- **Structural validity is retained, not weakened.** A crate must still
  contain exactly one root `ro-crate-metadata.json` to be accepted at all;
  v3 merely stops hashing that member's bytes into the aggregate. A missing
  or duplicated root metadata member remains a hard error.
- **Root-only exclusion.** `nested/ro-crate-metadata.json` or any other
  member that merely shares a basename is ordinary workflow content and is
  retained.
- **Uniform, not per-family.** The rule is applied identically to the stable
  33 and the volatile 95. No family list, no conditional exclusion, no
  observed-outcome-dependent membership: a per-family rule would re-derive
  the partition from fetch noise and bake a registry artifact into the
  substrate.
- **Zero free parameters, nothing resolved at run time.** The exclusion set
  is fixed by this document, not tunable.

## 3. Motivation

The v2 aggregate mixes two populations with different ontologies:

1. **Versioned workflow content** — the workflow documents and payload files
   a workflow author uploaded under a version id. These were byte-stable
   across fetches for all 128 families in the diagnostic, including the
   volatile ones. They are the substrate the A3 candidate policy's premise
   universe is meant to range over (the certificate's issuance state).
2. **Request-generated crate dressing** — registry-rendered metadata and an
   HTML preview produced by the endpoint at fetch time. For 95 families
   these differ on every request; they carry no version-pinned identity at
   all.

Binding frozen aggregates to population 2 was never the scientific intent of
the v2 preflight: it bound whatever bytes one request happened to return. The
diagnosis showed that binding to be unreproducible for 95/128 families, which
makes member-level substrate materialization under v2 impossible without
giving the registry's renderer a vote in what counts as changed content. v3
restores the original intent — frozen digests over version-pinned workflow
content only — at the cost of the explicit reductions in §5.

This is exclusion, not canonicalization: the generated files have no stable
canonical form to normalize to (three fetches of the same version differ with
no rule relating the variants), so any canonicalizer would be a
pseudo-deterministic fiction. Recording their *presence* (the excluded-path
set, which the diagnostic showed to be fetch-stable) without hashing their
bytes is the strongest honest treatment available.

## 4. Scope

- Applies to: the normalized member manifests and their aggregates used for
  member-level substrate materialization of the frozen 128-family successor
  frame (`workflowhub-member-manifest-freeze-v3/`, harvested by
  `harvest_member_manifests_v3.py` under `normalize_member_manifests_v3.py`).
- Does **not** modify: `bind_workflowhub_rocrate_content_v1.py` (the frozen
  v2 normalization module, still imported verbatim), the v2 durable snapshot
  (`workflowhub-normalized-content-binding-v2/`), the frozen successor frame
  (`WORKFLOWHUB_TWO_REPLACEMENT_SUCCESSOR_V1.json` +
  `workflowhub-two-replacement-successor-v1/RESULT_V1.json`,
  `successor_frame_sha256` a47d9255… unchanged), the frozen validators, or
  the frozen candidate policy executable and its decision rule.
- Re-verification requirement carried by this decision: the v3 harvest must
  perform at least three independent fetches per family per version and gate
  on byte-identical v3 aggregates across all of them for all 128 families;
  any failing family fails the whole harvest closed with the exact partition
  recorded. A failed gate is a result; it is never tuned toward green.
- Downstream effect on the candidate policy: the premise universe of
  `A3_TRANSPORT_THREE_VALUED_V1` ("every normalized member-manifest entry of
  the BEFORE RO-Crate") now ranges over v3 manifests, so the two
  request-generated members are no longer premises. This changes no decision
  rule, no executable and no free parameter — under v2 the excluded members
  would have been CONTRADICTED premises on 95/128 families by fetch noise
  alone, which is precisely the artifact being removed. The
  `normalization_source` line of `A3_CANDIDATE_POLICY_FREEZE_V1.json` (which
  names the v2 preflight verbatim) is superseded for substrate
  materialization by this decision; amending that freeze document is reserved
  to freeze governance and is explicitly NOT performed by this lane.

## 5. What v3 gives up, stated now

- **Descriptor-only change blindness.** A version pair whose only real
  difference lives in the excluded files (a pure metadata/description edit
  re-uploaded as a new version with identical workflow files) is
  indistinguishable, under v3, from no content change: before and after v3
  aggregates are equal. The v3 harvest must record any such family
  explicitly (`v3_content_only_before_after_equal_workflow_ids`) and fails
  closed rather than materializing a vacuous change cluster, because the
  frozen frame's admission rule (normalized content must differ) cannot be
  expressed for it under v3. Under v2 such pairs were detectable; that
  sensitivity is surrendered.
- **The frozen v2 aggregates stop being the live binding.** v3 aggregates
  are not comparable to the frozen v2 values (they cover fewer members for
  every family, stable ones included), so nothing downstream may silently
  keep using v2 receipts as if the substrate were intact. Until a separately
  governed successor-frame rebind binds the frame to v3 aggregates, the v3
  artifacts are substrate materialization only and the v2-bound frame
  remains the authority for frame admission. This decision grants no rebind.
- **Crate-descriptor drift becomes invisible.** If the registry later
  changes how it renders metadata or the preview for an unchanged version,
  or if the RO-Crate metadata document of a future version encodes a
  scientifically meaningful change (licensing change recorded only in the
  descriptor, authorship change, external identifier remint), v3 cannot see
  it. Licence and provenance continue to enter the programme only through
  the separately frozen frame-row licence receipts, not through crate
  bytes.
- **`ro-crate-preview.html` is not bound at all.** v2 hashed it; v3 records
  only its presence. It was already a derived rendering of the metadata, so
  this loses no independent signal, but the record is stated rather than
  implied.
- **One fetch-noise channel is accepted as unknowable.** The generated
  members' per-request bytes are transport dressing; v3 declares them out of
  scope for content identity rather than pinning them, so no artifact of
  this programme claims to reproduce them.

## 6. Non-goals

- No successor-frame rebind, no stratum adjudication, no candidate
  prediction, no gold access, no protected-outcome access (flags in the
  freeze document and in every result artifact state this and fail closed if
  violated).
- No rescue of the 95 volatile families' v2 aggregates: those single-request
  bytes are gone, and this decision does not pretend otherwise.
- No change to the candidate policy's decision rule or to any baseline.

## 7. What would falsify or reopen this decision

- The v3 harvest finding any family whose v3 aggregate is not byte-identical
  across at least three independent fetches: the volatility mechanism would
  then reach workflow-content members, and the exclusion rule would be
  insufficient (recorded honestly, terminal stays fail-closed).
- Any family collapsing to equal before/after v3 aggregates: the
  version-pair change is then descriptor-only, the family is inadmissible
  under v3, and the frame-rebind lane must adjudicate it explicitly.
- Evidence that a root-named member is author-uploaded versioned content for
  some family (rather than registry-generated): the uniform rule would be
  over-broad for that family and the decision would need a governed
  amendment, not a silent per-family patch.
