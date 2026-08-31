# ORION-22 — package audit

**Authority:** audit only · `scientific_authority_delta = NONE`

Closes the `EXACT_CURRENT_PDF_VISUAL_AUDIT` item of the Wave-2 disposition with
evidence, and records `FINAL_ARCHIVE_LICENSE_AND_HANDOFF` as genuinely open.

## 1. PDF currency — VERIFIED

The committed `manuscript/main.pdf` was last written at `6d2d1699b` (2026-08-27).
**Zero** commits touch `papers/orion-22-adaptive-state-reasoning/manuscript/` after
that commit, so the PDF is current with respect to its own source.

This is additionally enforced in CI rather than resting on the observation above.
`manuscript-clipping-audit.yml` runs:

```bash
git diff --exit-code -- ':(glob)papers/orion-??-*/manuscript/main.pdf'
```

so a checked-in PDF that does not match the clean pinned rebuild fails the job.

## 2. Visual / clipping audit — VERIFIED, and the gate is fail-closed

`scripts/audit_manuscript_clipping.py --discover-current` discovers PDFs by

```python
current = set(papers.glob("orion-??-*/manuscript/main.pdf"))
```

which matches `papers/orion-22-adaptive-state-reasoning/manuscript/main.pdf`. This
paper is therefore in scope, not merely unmentioned.

Three properties make the pass meaningful rather than vacuous:

1. `papers/MANUSCRIPT_CLIPPING_BASELINE.json` is an **empty list**. With no baselined
   exceptions, *any* clipping found is new and exits 2. An empty baseline is the
   strictest setting here, not an absent one.
2. **Exit 3 = "could not check" is failed, not reported as clean.** The workflow says
   so in-band. "Could not check" and "checked and fine" do not share an exit path.
3. The job passes on current `main`.

So the current PDF is audited and clean, and would fail loudly if it were not.

## 3. Archive / licence / handoff — OPEN

A search of the paper directory for `*licen*`, `*archive*` and `*handoff*` returns
**nothing**. There is no licence statement, no permanent-archive artifact and no
external handoff record.

This is recorded as **OPEN**, not as satisfied. It is a filing-time input and does
not block the scientific closure recorded in the Wave-2 disposition, but the paper
is not package-complete until it exists. No licence is invented here.

## Box status

| Wave-2 item | status |
|---|---|
| Execute frozen robustness suite under altered prices / task shifts / hidden parameters | DONE (bound on `main` by #1611) |
| Independent replay | DONE (independent replay + second checker, #1611) |
| Update manuscript with favourable and adverse regimes | DONE (#1611) |
| `EXACT_CURRENT_PDF_VISUAL_AUDIT` | **DONE** — this document |
| `FINAL_ARCHIVE_LICENSE_AND_HANDOFF` | **OPEN** — nothing exists |
