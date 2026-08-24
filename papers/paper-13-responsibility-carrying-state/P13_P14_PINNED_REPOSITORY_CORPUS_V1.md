# P13+P14 pinned repository corpus (V1)

Companion protocol doc for `P13_P14_PINNED_REPOSITORY_CORPUS_V1.json`
(schema `ORION.P13P14.PinnedRepositoryCorpus.v1`). The JSON is the corpus of
record.

Status: **FROZEN_CORPUS_PINNING**. This pins the external repository corpus
required by issue #1086 (consolidated P13+P14): *use 30-50 pinned repositories
from >=5 unrelated organizations; never use ORION as external subject.* It
contains no derived gold and no campaign results, and must never be cited as
evidence that any campaign ran or passed.

## Contents

- **45 repositories** across **22 distinct organization logins** (python,
  numpy, pandas-dev, scipy, matplotlib, rust-lang, golang, git, jquery, vuejs,
  redis, erlang, curl, pallets, psf, pydata, networkx, lodash, emberjs,
  nodejs, microsoft, apache), each pinned to the exact commit SHA of its
  default-branch head at retrieval time, with repository URL, retrieval UTC
  timestamp, owning-entity note and license verification evidence.
- **31 entries are gold-eligible** (license `VERIFIED_WITH_URL_AND_DATE` with
  recorded SPDX id) across **14 organizations** — both the full corpus and the
  eligible-only subset satisfy the 30-50 repository and >=5 unrelated
  organization minimums.
- **14 entries are license-unclear** (`CANNOT_CHECK__LICENSE_UNCLEAR`: GitHub
  reported no SPDX id on either the repository or the license endpoint —
  platform detection recognizes only standard SPDX texts, so custom or dual
  licences such as CPython's PSF licence or Redis' dual RSALv2/SSPLv1 fail
  closed rather than being manually asserted). They are pinned for record
  only and yield no gold under the frozen derivation contract.
- Dropped before freezing: `rust-lang/clippy` and `git/git-gui` (HTTP 404 at
  retrieval time).
- Excluded by rule: every SzeChunYiu-owned repository. ORION is never a
  subject of its own lifecycle-contract campaign.

## How each entry was built

GitHub REST API via the `gh` CLI, per repository:

1. `repos/{owner}/{repo}` — default branch and reported license SPDX id;
2. `repos/{owner}/{repo}/commits/{branch}` — head commit SHA recorded as
   `pinned_sha`;
3. `repos/{owner}/{repo}/license` — raw response bytes hashed
   (`evidence_fetch_sha256`) as the license verification receipt, with
   `evidence_api`, `evidence_field` and `evidence_url` recorded.

An entry is gold-eligible only when a real SPDX id (not `NOASSERTION`) was
confirmed; anything unclear fails closed to `CANNOT_CHECK__LICENSE_UNCLEAR`.

## Binding

The corpus JSON binds, by SHA-256:

- `P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md` — the rule of record
  governing what may count as gold for this campaign family;
- `P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json` — the frozen
  five-fact-class derivation contract; gold may be derived from these
  repositories only under that contract.

## Owner entities

Organization logins are GitHub accounts, not legal entities; each entry
records the owning entity as best the platform reports it (e.g. NumFOCUS
fiscal sponsorship for pandas, the Rust Foundation for rust-lang, Redis Ltd
for redis, the OpenJS Foundation for jquery, Ericsson for erlang/otp).
Organization count for the box minimum is by distinct GitHub organization
login; the unrelated-organizations requirement is satisfied by governance
unrelatedness to ORION and to each other's owning entities, not merely by
distinct login strings.

## Limits

- License status is the platform-reported SPDX id cross-checked against the
  license endpoint, not legal review.
- Pins are branch-head pins at retrieval time, not tag pins; tag/signature
  facts were not audited in this freeze.
- No ancestry, tag/signature, test-exit or timestamp-order facts have been
  derived for any entry; deriving them is the campaign's open remainder, along
  with the lifecycle/RCS-vs-baselines comparison.
- Pinning a corpus does not execute a campaign and creates no results
  (`scientific_authority_delta: NONE`).

## Checker

`check_p13_p14_pinned_corpus_v1.py` re-verifies, from the JSON alone: schema,
box minimums (30-50 repos, >=5 orgs, on both full and eligible-only counts),
no ORION/SzeChunYiu subject, binding hashes recomputed live against the rule
and contract artifacts, per-entry field completeness, license fail-closed
consistency, and tamper-evidence of the frozen corpus (mutating any pinned
sha, license verdict or count must flip the verdict).
