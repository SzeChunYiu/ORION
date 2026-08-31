# ORION-14 publication-freeze addendum V1

**Freeze date:** 2026-08-31  
**Status:** `SCIENCE_FROZEN__SMALL_CORPUS_SCOPE__HUMAN_FILING_AND_PACKAGE_OPEN`

This addendum is part of the frozen ORION-14 paper-content packet. It freezes the
science and states plainly what the science was computed over, which is smaller than
the artifact request that prompted it.

## Earned scientific ceiling

The minimal promotion reduct successor `ORION14.MINIMAL_PROMOTION_REDUCT.v1` returns
`status: PASS` under an independent checker whose independence is stated in the
artifact: *no ORION-14 module imported; bench read as data; reduct recomputed*.

**The load-bearing finding is that three-valued encoding is not decorative.** Under
the ternary encoding a minimal sufficient set exists at `k* = 3`. Under a binary
encoding **no sufficient set exists at all** — `k*_binary` is null, because
`closed_world_new_method` and `novelty_unknown` collide once `CANNOT_CHECK` is
binarised away. The artifact says how to read that, and this freeze repeats it:
*the absence of a binary `k*` is the finding, not a failure to compute.*

Two reducts of size 3 exist — `{claims_new_primitive, known_composition,
prior_art_found}` and `{known_composition, prior_art_found, req:NOVELTY}` — with a
core present in **every** reduct of `{known_composition, prior_art_found}`. Several
features appear in no reduct at all, including `assumptions_dropped`,
`assumptions_preserved` and `evaluator_independent`.

Three negative controls all pass: binarising `CANNOT_CHECK` destroys the reduct; the
full feature set is sufficient under ternary; and the empty set is not sufficient.
The controls matter here — without them, "a small reduct exists" would be
uninterpretable.

The anonymous-review artifact is deterministic and verified. The tracked filing
object `journal_package/orion14_anonymous_review_2026-08-28.zip` has SHA-256
`ec842a56dc49b7363de847e7c015fa2730c810a04652c5e440d9a72af4b665a3`, **two clean
builds were byte-identical with the same digest**, all members passed `unzip -t`, and
the headline verifier terminal is `ANONYMOUS_REVIEW_HEADLINES_VERIFIED`. The
protected V3 panel result stands as a distinct 30/30 against 0/30 and 15/30
terminal/interface-attainability result.

## Frozen boundary

**The corpus actually analysed is small, and smaller than what was asked for.** The
reduct was computed over `method_authority_extension/METHOD_AUTHORITY_BENCH_V1.json`:
**10 cases, 3 promotable, 17 features.** Issue #1617 requested a minimal promotion
reduct over a frozen 400-case table. That table does not exist: the scope gate
records a whole-repository search, excluding `.git`, which turned up 385-row
candidates rather than a 400-case file.

So the reduct result is real and independently checked, but it is a result about a
ten-case bench, not about four hundred cases. No reader should scale it. The board
records the corresponding decision — filing is not blocked on the missing 400-row
table — and this freeze respects that decision without letting it blur the scope.

`prior_art_found` is retained as a genuine three-valued feature rather than being
collapsed, which is precisely why it survives into the core of every reduct.

## Human filing and package: open

This freeze covers science, not submission. The Wave-1 closeout leaves human filing
actions unchecked — confirming or creating an OpenReview profile; entering complete
author names, affiliations and ORCIDs; and entering funding, conflicts and
ethics/IRB declarations as applicable.

Separately, the paper's `journal_package/SHA256SUMS` and `manuscript/main.pdf` are
currently being repaired in another lane, because the packaged PDF is bound by
`journal_package/CLAIM_EVIDENCE_MATRIX.json` and a refresh there is package
regeneration rather than a digest swap. This addendum deliberately touches neither.

## Frozen content surface

The content packet consists of the manuscript and its submission directory,
`submission/ANONYMOUS_REVIEW_ARTIFACT_MANIFEST_V1.md` with the deterministic review
ZIP it names, `submission/WAVE1_CLOSEOUT_2026-08-28.md`, the promotion-reduct
successor at `theory/promotion-reduct-v1/` with its `RESULT.json` and independent
checker, `method_authority_extension/METHOD_AUTHORITY_BENCH_V1.json` as the analysed
corpus, and this addendum. ORION-14's claim is about when verification axes can
support scientific claims; it does not own the benches it is measured over.
