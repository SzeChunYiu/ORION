# Mirrored CI evidence

The external-probe evidence for this paper was produced by GitHub Actions, whose
artifacts **expire on 2026-09-15**. After that date the upstream copies are gone
and only what is here can be checked, so the archives are mirrored into the
repository rather than referenced.

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
