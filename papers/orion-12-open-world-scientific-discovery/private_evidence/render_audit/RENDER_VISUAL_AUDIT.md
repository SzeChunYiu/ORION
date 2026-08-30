# Exact render and every-page visual audit — 2026-08-28

- target adapter: Elsevier CAS single-column
- canonical review PDF: `manuscript.pdf`
- PDF SHA-256: `e23e853d4a4b39417f4b420ec51d071b2ed7595a6cc1284bdac6d8374dc70217`
- PDF bytes: `94747`
- pages: 11
- contact sheet SHA-256: `bff1604a8fc78f7e5b35d46261338dfec8ac6e7138beb73e7dfd21efbe7c3999`
- two clean builds with `SOURCE_DATE_EPOCH=1787918400`: byte-identical
- metadata: exact title; author `Anonymous authors`; no JavaScript, forms or encryption

## Page inspection

1. Title, 232-word abstract and seven keywords fit; anonymous surface; no clipping.
2. Introduction, authority layer and formal-model opening are readable; equations fit.
3. Formal model and Methods fit; no margin collision.
4. Pipeline diagram is legible; crossed forbidden transition and obligation flow are visible; no clipped nodes.
5. Exact-contract and TREC methods plus controlled-results opening fit.
6. Table 1 and recall figure are sharp; reader-facing curve labels have white backgrounds and do not collide with trajectories.
7. Stopping-failure figure and Tables 2–3 are readable; the information-equivalent tie and adverse gate remain visible.
8. Table 4, external boundaries and Related Work fit.
9. Discussion and availability transition cleanly; no sparse spill.
10. Ethics, Conclusion, AI declaration and first reference block fit.
11. Reference continuation is readable; final page ends normally with no orphan heading or clipped line.

## Rendered-surface residue

Normalized PDF text has zero unresolved hits for `ORION`, `P2`, `P2-X`, `TIER_`, author identity, private paths, repository issue/PR/branch/commit/CI tokens, machine terminals, source filenames or release placeholders. The generic phrase “committed tier” denotes a reader-facing planned precision tier and is not an internal code. Scientific uses of “workflow” and “issue” were inspected in context and are ordinary domain language.

No undefined reference/citation, overfull box, broken glyph, unreadable table, clipped figure, black square or sparse final-page defect remains. Tectonic emits a repeat-pass internal-consistency notice around the stable bibliography and CAS/PDF destination-object notices; the `.blg` contains no bibliographic error and the rendered reference list converges.
