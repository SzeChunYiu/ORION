# Freeze-governance adjudication: the three descriptor-only families and the successor-frame rebind

Decision id: `A3_DESCRIPTOR_ONLY_ADJUDICATION_V1`. Frozen 2026-09-03 by the A3
freeze-governance adjudication lane, acting as governance over the frozen
artifacts of PR #2195 (`WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3`). This
record adjudicates the three families the v3 harvest failed closed on, and
decides the successor-frame rebind question that decision reserved to
governance. Nothing in this record promotes itself: it grants no scientific
authority, amends no frozen executable, rebinds no frame, and takes effect as
a governance act only through the external, non-self sign-off recorded in §6.

## 1. What was observed (the boundary this decision answers)

The governed v3 harvest (sbatch 3570688, `workflowhub-member-manifest-freeze-v3/RESULT_V3.json`)
verified 128/128 families byte-reproducible under v3 across 3 fetches per
version — the request-generated volatility mechanism is fully captured by the
exclusion rule — but failed closed on the pre-registered descriptor-only gate:
families **106, 360, 384** have equal before/after v3 aggregates
(`v3_content_only_before_after_equal_workflow_ids`), so their frozen v2
before/after aggregate difference is confined entirely to the excluded
request-generated members. The v3 decision §7 required exactly this lane:
"the family is inadmissible under v3, and the frame-rebind lane must adjudicate
it explicitly." No chunks were emitted, no substrate was materialized, and the
pool builder records the boundary as recorded-not-bound.

The question per family: do the version **descriptors** (the ro-crate
metadata content describing the change) show a genuine content transition, or
an artifact of the request-generation mechanism?

## 2. Adjudication method (pre-registered, zero free parameters)

`adjudicate_descriptor_only_families_v1.py` (frozen here, sha256
`c89521d1…`) reads the frozen 128-family successor frame through the frozen
digest-checked loader, then fetches both versions of each of the three
families three times through the frozen v3 transport (same URL form, UA,
retry tuple, read limit as `harvest_member_manifests_v3.fetch_once`). Per
fetch it records raw and canonical-JSON digests of `ro-crate-metadata.json`,
the preview digest, the v3 retained/excluded split and the v2 cross-check.
Executed as LUNARC sbatch **3571474** on cn050 (account lu2026-2-51,
partition lu48), staged entirely under
`/projects/hep/fs9/users/scyiu/orion-a3-v3/adjudication-20260903`
(raw per-fetch descriptor bytes retained there; never committed — they are
per-request bytes; only their digests and the derived pinned-path values are
bound into the committed evidence,
`workflowhub-descriptor-only-adjudication-v1/EVIDENCE_V1.json`, sha256
`be8626b5…`).

Discriminator: within one version, across its 3 fetches, the **volatile**
canonical paths are those differing between any two fetches. Across versions,
over all 9 before/after fetch pairs, the **version-pinned** paths are those
differing in every pair yet never within a version. The same construction is
applied order-free to `@graph` nodes keyed by `@id`. Pinned ≠ ∅ ⇒ a
version-pinned descriptor transition; pinned = ∅ with all cross differences
coinciding with within-version volatility ⇒ request-generation artifact;
anything else ⇒ CANNOT_DISTINGUISH. The rule was fixed before execution and
is applied verbatim by the frozen executable.

## 3. Per-family verdicts

All three families: descriptor bytes are regenerated per request (3 distinct
raw digests per version; the only within-version volatile path is
`$.@graph[2].sdDatePublished` — the registry's serve-date dressing), all three
sit in the volatile-95 (per-fetch v2 aggregates do not reproduce the frozen
frame), and the v3 collapse was re-verified inside the adjudication run
(before == after v3 aggregate, both stable across fetches).

- **Family 106 (v2→v3): `DESCRIPTOR_SHOWS_VERSION_PINNED_TRANSITION`** — 34
  pinned paths, 2 pinned `@graph` nodes. The main-entity/workflow node
  (`nextflow.nf`) moves version 2→3, gains DOI
  `doi.org/10.48546/workflowhub.workflow.106.3`, gains `datePublished`
  2021-12-16, gains an image reference (`rd_connect-initial_cwl.jpg`, an
  `ImageObject` node present only in the v3 descriptor and **not** a crate
  member — retained member count stays 2+2 excluded = 4 on both sides);
  `dateCreated` moves 08:43:08Z→08:45:49Z (2021-05-21, the after-version
  minted ~3 min after the before-version). A genuine re-publication
  transition with byte-identical workflow content.
- **Family 360 (v1→v2): `DESCRIPTOR_SHOWS_VERSION_PINNED_TRANSITION`** — 8
  pinned paths, 1 pinned node. The workflow node
  (`workflows/assembly-wf--v.5-cond.cwl`) moves version 1→2 and its
  `description` text genuinely differs (+2 chars in the MGnify description);
  `dateCreated` 07:41:18Z→08:03:35Z (2022-06-07). A genuine metadata-edit
  re-publication with byte-identical workflow content (500 retained members
  on both sides).
- **Family 384 (v2→v3): `DESCRIPTOR_SHOWS_VERSION_PINNED_TRANSITION`** — 10
  pinned paths, 1 pinned node. The workflow node (`run_wf.sh`) moves version
  2→3 and its `license` changes **GPL-3.0 → Apache-2.0** — the exact
  licensing-change-recorded-only-in-the-descriptor case v3 §5 named as a
  surrendered signal, and independently corroborated by the frozen frame-row
  licence receipts; the node also gains the DOI
  `doi.org/10.48546/workflowhub.workflow.384.3` and `datePublished`. A
  genuine licence/re-publication transition with byte-identical workflow
  content (326 retained members on both sides).

Common evidence note: the after-side `dateModified` values (2026-05-13
13:00:33Z / 13:05:02Z / 13:05:29Z) share one five-minute window, consistent
with a registry-side metadata event touching the three latest versions; the
version-pinned differences themselves are stable across every fetch. The
verdicts are "genuine version-pinned descriptor transition"; they make no
claim about who or what performed the re-publication.

## 4. What this does and does not license

Licenses: (a) the per-family scientific record that all three version-pair
changes are real, descriptor-level transitions — not request-generation
artifacts — so the v2 frame's admission of them captured real changes, albeit
through a channel (per-request crate bytes) that cannot distinguish real from
noise; (b) the falsification of the "artifact" reading of the v3 collapse;
(c) continuation of the programme on the frozen v2-bound frame with the v3
boundary recorded, exactly as the pool builder already records it.

Does NOT license: any change of stratum, REUSE/REOPEN target, or eligibility
for the three families (external-curator custody, untouched); any amendment
to `A3_CANDIDATE_POLICY_FREEZE_V1.json` (its `normalization_source`
supersession stays conditional on a substrate that was never materialized);
any modification of a frozen executable, validator, frame, or pool artifact;
any inference that descriptor bytes are reproducible (they are regenerated
per request; only their canonical path structure carries pinned signal).

## 5. Successor-frame rebind decision: NO REBIND, with evidence

The eligible-pool substrate does **not** rebind from v2 to v3 aggregates.
`successor_frame_rebound` stays false everywhere. Rationale:

1. **There is no v3 substrate to bind.** The governed harvest failed closed
   before emitting any chunk (`fail_closed_before_emitting_any_chunk`,
   `member_manifests_committed: false`; no `SNAPSHOT_V3.json` exists —
   cross-checked by directory enumeration). Binding the pool to v3 aggregates
   now would mean binding to artifacts that do not exist; forcing it would
   require tuning a failed gate toward green, which the frozen execution
   contract forbids ("a failed gate is a result; it is never tuned toward
   green").
2. **The frozen admission rule is inexpressible for exactly these three
   families under v3** — and all three carry genuine transitions (§3). A
   v3-bound frame admits at most 125 of the 128 frozen families while
   discarding real change signal (360's description edit, 384's licence
   change). The frozen allocator requires exactly 96 primary + 32 replication
   = 128 eligible clusters (24+8 × 4 strata); a 125-family v3 frame fails
   closed with `CANNOT_CHECK_A3_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL`.
   This is mechanically re-proven inside this record's validator self-test.
3. **The recorded-not-bound pool state is correct, not deficient.** It keeps
   the v2-bound frame as admission authority, carries the v3 boundary and the
   three family ids verbatim on the pool, and still allocates under the
   frozen frame. Rebinding would trade a working, honestly-bounded pipeline
   for a strictly weaker one.

What a future rebind would require (recorded, NOT performed, NOT licensed
here): a separately frozen successor-frame re-admission campaign mirroring
`WORKFLOWHUB_TWO_REPLACEMENT_SUCCESSOR_V1` — a frozen candidate-universe rule
admitting replacements under the v3 differ rule, restoring the frame to 128
with a new `successor_frame_sha256` — followed by its own governed v3 harvest
and freeze delta, and external sign-off. That campaign loses the three
genuine descriptor-only transitions from the frame; whether that trade is
worth making is a governance question for that freeze, answered there.

## 6. Authority chain and sign-off

Authored by the A3 freeze-governance adjudication lane acting as governance
over the executing lane's frozen artifacts; every artifact it adjudicated is
bound by digest in `A3_DESCRIPTOR_ONLY_ADJUDICATION_V1.json` and is modified
by this change not at all. Following the RSHEA discipline enforced across
this programme: **sign-off is an external, non-self act of continuation,
never promotion.** The external acts that give this record effect are (a) the
orchestrator's central merge of this PR after CI green on the new head —
which this lane does not perform and cannot perform for itself — and (b) for
any successor campaign, the further external sign-off of that campaign's own
freeze. Until (a) lands, this record is a pending governance proposal;
nothing downstream may cite it as authority. No artifact in this programme
self-promotes, self-signs, or treats its own output as gold.

## 7. What would falsify or reopen this decision

- A future governed refetch of any of the three families whose descriptors
  show no version-pinned difference across all cross-version pairs (e.g. the
  registry normalizing away the pinned fields) would reopen that family's
  verdict toward artifact or cannot-distinguish.
- Evidence that a field here counted volatile (`sdDatePublished`) can be
  version-pinned for some family, or that a field here counted pinned can
  vary within a version under a different fetch regime: the
  volatile/pinned partition would need a governed amendment.
- The descriptor of a future version encoding a workflow-content change
  while the content members stay byte-identical (descriptor-only false
  negative for v3): reopens the v3 gives-up ledger, not this adjudication.
- A separately frozen successor-frame re-admission campaign landing on main
  supersedes this record's no-rebind state by construction, with a new frame
  digest and its own authority chain.
