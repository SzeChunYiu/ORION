# ORION-15 compile instructions

From `papers/orion-15-self-orion/`, render the tracked SVG figure first:

```bash
rsvg-convert -f pdf -o figures/p5_1_governed_development_loop.pdf figures/p5_1_governed_development_loop.svg
```

Then build from `papers/orion-15-self-orion/manuscript/`:

```bash
mkdir -p /tmp/orion-p5-build
tectonic main.tex --outdir /tmp/orion-p5-build --keep-logs --keep-intermediates
```

Acceptance for a future current package requires:

- an exact immutable source revision and toolchain binding;
- no fatal error, emergency stop, undefined reference/citation, or overfull box;
- all-page PNG inspection with no clipping, overlap, or duplicate figure;
- a new render-input closure and page-level visual and claim audit; and
- clean verification of the successor package's `SHA256SUMS`.

The current `journal_package/manuscript.pdf` is the retained historical Tectonic
artifact. Do not overwrite it or relabel the newer pdfTeX working PDF as its
successor without completing those gates.

A build reruns no live provider or protected campaign. It preserves the 21/24
diagnostic, bounded post-outcome 24/24 diagnosis, and frozen 96-case
`NO_TERMINAL_UNDER_FROZEN_RULES` receipt. Compilation and checksums grant no H1,
general superiority, peer-review readiness, or self-promotion authority.
