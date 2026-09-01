# Provenance — vendored `nature-*` paper-writing skills package

## Local positive-feedback extension

`nature-publication-closure/` is an ORION-local extension added on 2026-08-31
after six-paper closure review exposed recurring authority-precedence,
denominator, venue-identity and exact-mirror gaps. It does not claim upstream
provenance and must remain labelled local when the upstream bundle is refreshed.

- **Source repo:** `/Users/billy/nature-skills` (local git checkout)
- **Pinned revision:** `93bb0f9` (2026-07-03, "Merge pull request #90 …")
- **Vendored on:** 2026-08-26 by the V1 takeover session, at operator directive:
  *"when you write the papers, you must use this package skills … make it explicit
  somewhere in the repo that ai sessions must use this package to write their
  papers — including rewriting existing papers and new papers."*
- **What is vendored:** every skill directory (`nature-*` + `_shared`) in full text —
  all `SKILL.md`, `README.md`, `manifest.yaml`, `references/`, `agents/`, `scripts`,
  and text examples.
- **What is deliberately excluded:** binary example assets (`*.png *.jpg *.jpeg *.gif
  *.tif *.tiff *.pdf *.pptx`) and the source repo's `.git`. The excluded material is
  a figure-style gallery, not protocol; nothing normative was dropped. (~27 MB of
  example figures live in the source checkout if ever needed.)

## Refresh procedure

When the source package advances:

```bash
git -C /Users/billy/nature-skills pull --ff-only
rsync -a --delete --exclude='.git' --exclude='*.png' --exclude='*.jpg' \
  --exclude='*.jpeg' --exclude='*.gif' --exclude='*.tif' --exclude='*.tiff' \
  --exclude='*.pdf' --exclude='*.pptx' \
  /Users/billy/nature-skills/skills/ papers/skills/nature/
# then update the pinned revision above and commit.
```

On machines without the source checkout, treat the vendored copy as canonical —
it is self-contained (skills reference only `_shared` and their own `references/`).
