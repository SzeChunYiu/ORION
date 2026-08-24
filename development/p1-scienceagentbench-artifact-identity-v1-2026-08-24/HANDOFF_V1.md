# P1 ScienceAgentBench PF-01 artifact identity handoff V1

## Terminal

`P1_SAB_PF01_ARTIFACT_IDENTITY_CLOSED__FULL_ARCHIVE_SHA256_BOUND__1769478786_BYTES__ZERO_PAYLOAD_RETAINED__ZERO_ENTRIES_OPENED__ZERO_OUTCOMES_OPENED__ZERO_TASKS_RUN`

This packet closes only preflight blocker PF-01. It is an outcome-blind transport
and artifact-identity receipt, not permission to extract the archive, a benchmark
run, a protocol freeze, evaluator validation, independent custody, or scientific
promotion.

## Exact identity

| Field | Bound value |
|---|---|
| Official landing URL | `https://buckeyemailosu-my.sharepoint.com/:u:/g/personal/chen_8336_osu_edu/IQB870QrmuqwS5Ck33cHpJfkAVt3LsMeariREIwP3AT7byA?e=3ckueC` |
| Final URL | `https://buckeyemailosu-my.sharepoint.com/personal/chen_8336_osu_edu/Documents/Research/benchmark_verified.zip?ga=1` |
| Filename | `benchmark_verified.zip` |
| Retrieval interval | `2026-08-24T10:04:57.191895Z` to `2026-08-24T10:06:19.168343Z` |
| Full GET | HTTP/2 `200`, one redirect, no Range header, no automatic retry |
| Byte count | `1,769,478,786` |
| SHA-256 | `46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610` |
| ETag | `"{2B44EF7C-EA9A-4BB0-90A4-DF7707A497E4},3"` |
| Last-Modified | `Wed, 29 Apr 2026 23:39:44 GMT` |
| Content-Type | `application/x-zip-compressed` |

The response body was streamed through an 8 MiB in-memory buffer to SHA-256 and
an integer counter. It was never written to disk, retained, extracted, parsed as
a ZIP, or added to ORION. No file-entry payload, gold program, evaluator program,
rubric, gold result, or task outcome was opened or interpreted.

## Transport and preflight cross-checks

Immediately before the full stream, a body-free `HEAD` request with
`Range: bytes=0-0` returned HTTP/2 `206`, `Content-Range:
bytes 0-0/1769478786`, `Content-Length: 1`, and `Accept-Ranges: bytes`. The full
GET returned `Content-Length: 1769478786`. Both responses preserved the same
final URL, ETag and Last-Modified value. Against the pinned preflight receipt,
the byte total agrees exactly and the ETag agrees after normalizing HTTP quotes.
The preflight metadata value `2026-04-29T23:39:42Z` is two seconds earlier than
the transport `Last-Modified` value. That field-level difference is retained
without interpretation; the preflight receipt records the landing URL rather
than the transport final URL.

The preflight central-directory receipt is not promoted into the full-archive
hash. It remains separately bound as SHA-256
`2bd7f1a85ce55654f50af5cb7461ef17a2c913596f1def28b205f0325539567e`,
offset `1,769,361,388`, length `117,376`, with 955 entries. Its recorded extent
plus the 22-byte end record equals the streamed archive length exactly:

`1,769,361,388 + 117,376 + 22 = 1,769,478,786`.

The central directory was not reopened during this task. This is an identity
cross-check against the pinned preflight receipt, not a second content
inspection.

## Source pin and remaining blockers

- Official code: `OSU-NLP-Group/ScienceAgentBench` at
  `c26e151ed601ba109dc4d35e057ff8e73fec469d`.
- Verified annotations: `osunlp/ScienceAgentBench` at
  `9c6e96c9e74572e979b0930ee735041cef528cb7`, split `verified`.
- Preflight receipt SHA-256:
  `95033900763e22c67b95104f35f18fc75d6d678d4c12e5851b848bb186b55bbf`.
- ORION audit-start base: `d4cf8c09c128c0b0331b96b45385c35a96b9427e`;
  integration base: `e4026dc81a8ccc44841cd2d44115bb05873a03da`.

PF-02 through PF-06 remain open. Correct verified-split execution, runtime,
official evaluator reproducibility, matched-arm bindings, and the construct and
authority boundary are unchanged. Scientific authority delta: `NONE`.
