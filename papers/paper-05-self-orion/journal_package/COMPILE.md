# ORION-P5 compile instructions

From `papers/paper-05-self-orion/`, render the tracked SVG figure first:

```bash
rsvg-convert -f pdf -o figures/p5_1_governed_development_loop.pdf figures/p5_1_governed_development_loop.svg
```

Then build from `papers/paper-05-self-orion/manuscript/`:

```bash
mkdir -p /tmp/orion-p5-build
tectonic main.tex --outdir /tmp/orion-p5-build --keep-logs --keep-intermediates
```

Acceptance for this snapshot requires:

- exit status 0;
- no fatal error, emergency stop, undefined reference/citation or overfull box;
- exactly 37 rendered pages for source subject
  `c6c71c6c758aa605fa414ff8eaeb87f1ef4b0672`;
- all-page PNG inspection with no clipping, overlap or duplicate figure;
- byte-identical copies at `manuscript/main.pdf` and
  `journal_package/manuscript.pdf`; and
- clean verification of `journal_package/SHA256SUMS` from the paper root.

The build does not rerun the live provider or protected campaigns. It preserves
the immutable 21/24 diagnostic, the bounded post-outcome 24/24 instrument
diagnosis and the frozen 96-case `NO_TERMINAL_UNDER_FROZEN_RULES` receipt. No
build or checksum result grants H1, general superiority, peer-review readiness
or self-promotion authority.
