# Mirrored CI evidence

The external-probe evidence for this paper was produced by GitHub Actions, whose
artifacts expire after their short retention windows (the older probe set on
2026-09-15 and the matched OpenAIRE/Crossref set on 2026-09-17). After those
dates the upstream copies are gone and only what is here can be checked, so the
archives are mirrored into the repository rather than merely referenced.

The three `p2-wide-openaire-matched-*` archives retain the full candidate
capture, the failed first evaluator handoff, and the successful evaluator-only
repair. Their terminal is `P2_WIDE_EXTERNAL_CANNOT_CHECK`: every structured DOI
crosswalk request returned HTTP 400, so transport validity failed and all three
candidate projections collapsed to the same bytes. These archives preserve a
failed campaign; they do not support external superiority.

Verify with:

    python3 scripts/mirror_ci_evidence.py --check

`MANIFEST.json` records, per archive and per file inside it, the byte count, the
raw SHA-256, and — for anything that parses as JSON — a canonical-JSON digest.

## Why two digests

The mirrored MetaSyn false-negative ledger is 23,902 bytes; the copy committed
under `evidence/external_results/` is 18,656 bytes. They are **JSON-identical**:
CI pretty-prints, the repository stores compactly. So a raw byte digest of a
CI-produced JSON file does not match a raw byte digest of the committed one, and
a reader who recomputes the wrong one concludes the evidence was altered.

Nothing in the paper currently binds either digest of that file, so no claim is
affected today. The canonical-JSON digest is the one to bind: it is stable across
serialisations and is what makes "the same evidence" a checkable statement rather
than an accident of formatting.

## Not mirrored

`p2-manuscript-audit` is excluded: the compiled PDF and its log rebuild from
source, so archiving them would spend repository space on something a reader can
regenerate.
