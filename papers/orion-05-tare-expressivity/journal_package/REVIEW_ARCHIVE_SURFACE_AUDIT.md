# Anonymous review-archive surface audit

Date: 2026-08-28

## Bound archive

| Field | Value |
|---|---|
| Filename | `support_two_normal_form_review_2026-08-28.zip` |
| SHA-256 | `8ff07f17b23f9ba96736ac67a88308c809e9837122c662e97bccf4679e5dc09c` |
| Bytes | 48,386 |
| Files | 23 |
| ZIP integrity | pass |
| Deterministic rebuild | byte-identical across two clean builds |
| Fixed member timestamp | 2026-08-28 12:00:00 |

## Exact public contents

- neutral README and two licences;
- standalone local-lemma checker;
- direct support-bounded solver and displayed-instance sharpness check;
- dated literature-boundary and nearest-object crosswalk;
- pre-measurement runtime specification;
- all 120 sanitized attempt rows;
- recorded environment fields;
- deterministic schedule validator and runtime aggregator;
- generated adverse summary;
- complete anonymous manuscript source and bibliography.

The archive deliberately omits the earlier static exact-comparison summary, the unavailable separate exact referee, public checksum lists, author metadata, protected data, source-control history, and the original unrestricted measurement stack. Its README states that the runtime files support deterministic audit of the retained observations, not a new timing campaign.

## Executable verification

| Check | Result |
|---|---|
| `proof_sanity.py` | pass; 192 local cases; maximum increase 2; no subset-lemma failure above support two through support eight |
| `verify_sharpness.py` | pass; support-two minimum 5; support-one minimum 6; all witness checks true |
| `aggregate_runtime.py --check runtime_summary.json` | pass; 120 total; 108 completed; 12 timed out; 0 errors |
| Three-qubit support-two timeouts | 6 |
| Full-subject support-two timeouts | 6 |
| Positive-performance rule | false |
| Isolated source compile | pass; 8 US-letter pages; exact metadata and extracted text |

## Recursive strict scan

Archive member names and every byte payload were scanned case-insensitively. The forbidden classes were:

- author identity and email;
- project and paper-series codes;
- local paths and repository URLs;
- commits, branches, pull requests, issue numbers, workflows, continuous-integration and build-history terms;
- hashes, digest labels and 40-to-64-character hexadecimal objects;
- machine terminal labels and filing-readiness states;
- private lineage phrases involving internal checks, production conventions/raw costs, frozen grammar/system history, donor ownership, or authorized interpretations;
- standalone internal short codes matching paper, result-round, hypothesis or baseline identifiers.

Result: **23 files scanned; zero forbidden hits**.

Generic scientific uses of “source” and Python's `dataclass(frozen=True)` semantics are not private lineage and were not prohibited. The licence texts were included in the same scan.

## Scientific and anonymity boundary

The audit establishes only reader-surface cleanliness and deterministic behavior of the included checks. It does not establish external replication, novelty, significance, target fit, author declarations, or real journal acceptance. The archive remains anonymous and must not be supplemented with human metadata during blind review.
