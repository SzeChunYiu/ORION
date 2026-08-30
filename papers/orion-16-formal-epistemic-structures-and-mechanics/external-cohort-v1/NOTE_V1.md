# ORION-16 external sourcing custody v1

**Terminal: `SOURCING_INPUT_ONLY__DEFERRED_TO_ACTIVE_LANE_1695`.**
This directory defines no protocol, no arms, no gate, and no terminal for any
ORION-16 claim. It contains custody and availability data only.

## Why there is no protocol here

Issue #1701 forbids creating a competing ORION-16 protocol while issue #1695 —
campaign `ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1`, the real authoritative
graph campaign over E4 RTPTorrent / E5 Bazel / E6 Cargo — is active.

I checked rather than assumed: `gh issue view 1695` reports **state `OPEN`**, and
`gh pr list` shows PR #1695 open on branch `science/o16-real-system-design-v1`.
The lane's `CANDIDATES.md` and `PROTOCOL_SKETCH.md` exist on that branch and on
no other branch I searched (they are absent from `main`).

Writing a selection protocol here would have been exactly the forbidden act.
So the deliverable for ORION-16 is: *blocked by an active lane, with the evidence*,
plus the one non-competing contribution that lane can actually use.

## What was missing, and what this adds

`CANDIDATES.md` names its candidate repositories but **pins none of them**. A
search for 40-hex commit identifiers over that file returns zero matches, and its
extraction recipes are written against moving refs (`git rev-list --first-parent
-n 300 origin/main`). Without pinned commits the S1/S3 graph extraction is not
reproducible.

This record pins each named repository at an observed HEAD, obtained with
`git ls-remote` — no clone, no checkout, no build, zero bytes of repository
content fetched to this machine. The repositories were chosen by `CANDIDATES.md`,
not by me; pinning is not selection.

All 8 named repositories were reachable:

| tier | repository | pinned HEAD |
|---|---|---|
| C1 Bazel | envoyproxy/envoy | `a02111b95305cd3b6ea08bcd90bf867744c0a268` |
| C1 Bazel | abseil/abseil-cpp | `2c004366e983c5be8334ac1ea3d4420e8fbcbea7` |
| C1 Bazel | grpc/grpc | `85b660f942194349dedabb5659256f40c84e671a` |
| C3 Cargo | paritytech/polkadot-sdk | `90c177d163860c7836bdd118306f0459de9e7f28` |
| C3 Cargo | rust-lang/cargo | `e7167a4bac50fd878ce18530e901624d83be218e` |
| C3 Cargo | servo/servo | `cb42ac01c8afcf84d918ee138bcf3f35d9e3209d` |
| C4 Defects4J | rjust/defects4j | `8c16da8230843cdc918eaf4ddb449637f02b83c6` |
| C4 Defects4J | TestingResearchIllinois/starts | `a01412c4aae5dd472101fd00cf7aad2fc584f4ed` |

## RTPTorrent: verified, deliberately not downloaded here

Issue #1695 records the 5.0 GB RTPTorrent zip as **already downloading on
billy-old with md5 verification**. Downloading it again on this Mac would
duplicate in-flight work, and this machine has a prior ENOSPC incident that
halted a session outright.

What is useful instead is the authoritative integrity metadata that the in-flight
download can be checked against, which I fetched from Zenodo without touching the
payload:

- record `4046180`, DOI `10.5281/zenodo.4046180`
- "RTPTorrent: An Open-source Dataset for Evaluating Regression Test Prioritization"
- licence `cc-by-4.0` (`metadata.license.id`)
- `rtp-torrent-v11.zip`, **5,016,963,482 bytes**, MD5 `1f7fa822b0cf155bd007a94d1a24a336`

The size cross-checks against the "5.0 GB" stated in #1695. The record publishes
MD5 only, so whoever completes the download must compute a SHA-256 locally and
record it before any arm output is read — the same rule ORION-13's OAEI licence
manifest applies to bench23. MD5 is transport sanity, not tamper evidence.

## Blindness

Nothing here is a selection, so there is no selection to keep blind. Repository
choice came from `CANDIDATES.md`; the only decisions I made were mechanical
(resolve HEAD, read published metadata). No graph was extracted, no build run, no
test executed, no arm scored.

## What I could not get

- `CANNOT_CHECK` — **whether any pinned historical commit is buildable.**
  `CANDIDATES.md` records historical-commit bit-rot as a kill risk (old WORKSPACE
  external deps 404, old Bazel versions). Testing that needs a build environment
  and CI, which must not run on this Mac. Reachability at pin time is not
  buildability, and I do not report it as such.
- `CANNOT_CHECK` — **T1/T2/T3 authoritativeness adjudication.** That judgement is
  defined in `CANDIDATES.md` and belongs to lane #1695.
- Not attempted — the RTPTorrent payload, for the reasons above.
