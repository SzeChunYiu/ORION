# ORION-20 generated OCME result receipt V1

**Run:** GitHub Actions `32655587097`  
**Artifact:** `p10-generated-ocme-v1`, artifact ID `9497413065`  
**Artifact ZIP SHA-256:** `197cbdd9dd0e6d38e45243fe0a339a49b958c4443676cd7c65e22a78eaabd799`  
**Primary terminal:** `P10_GENERATED_OCME_V1_SUPPORTED`  
**Independent terminal:** `P10_GENERATED_OCME_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** `P10_GENERATED_OCME_TWO_IMPLEMENTATIONS_AGREE`

## Exact binding

- protocol SHA-256: `2cedd908c312661f1cbc930e89890f0537753b41a495cffad64dd96a619b0a99`
- cases/grammar SHA-256: `b9f2e8a1d28715584c5b08f2a01261b213a8da14509780bc5d882acc231c306b`
- primary receipt SHA-256: `cb949e5883d2864c2b9bc863a840fa66a023ebdaa9b780771ccc1bf39a936575`
- independent receipt SHA-256: `a85d7a7cd04fe36f8835e2c82129e10d5cd1e029b5ef4baca587db25828ecd66`
- deterministic primary replay: GREEN
- deterministic independent replay: GREEN
- selection contract: `ORIGIN_ONLY__HELD_OUT_OPENED_AFTER_SELECTION`

## Generated setting A — Boolean majority

Old method language is the complete 32-function affine family over four Boolean inputs. The originating three-input majority target is exactly outside that closure.

The generator receives all `16` anonymous binary Boolean truth tables, not an `AND` label. Under the prospectively frozen composition template

`g(a,b) XOR g(a,c) XOR g(b,c)`,

and fixed selection rule (exact originating solve, outside affine closure, minimum truth-table Hamming weight, integer-code tie break), it selects code `8`, truth table `[0,0,0,1]`.

Only after selection are the three held-out variable triples opened. The selected primitive solves all `3/3`. Frozen XOR/projection/constant controls all remain `KNOWN_COMPOSITION`; false expansion count is `0`.

Because the old affine closure is enumerated exactly, arbitrary search/synthesis/evolution restricted to that old language is semantically unable to reach the majority target; this is not a finite-search timeout argument.

## Generated setting B — integer cubic

Old method language is rational affine functions on the exact verifier domain `{-4,-3,-2,-1,0,1,2,3,4}`. The originating cubic-plus-affine target is outside that closure.

The generator receives five anonymous unary candidates with prospectively fixed complexity ranks. Under exact origin fitting with wrapper `primitive(x)+a*x+b`, it selects candidate `U3`; post-selection semantic reveal identifies it as `CUBE`, with originating wrapper `(a,b)=(2,1)`.

Only after selection are the three held-out cubic-plus-affine targets opened. The selected primitive solves all `3/3`, with exact wrappers `(-1,2)`, `(0,3)`, and `(-3,-2)`. Both affine controls remain `KNOWN_COMPOSITION`; false expansion count is `0`.

The independent verifier rederives affine exclusion by a separate exact collinearity test and agrees on `U3` and all transfers.

## Aggregate

- generated outside-closure edit selections: `2`;
- held-out transfers: `6/6`;
- false expansions on known-method controls: `0`;
- exact old-language exhaustive search/synthesis/evolution closure: GREEN in both registered finite settings;
- two structurally independent implementations: exact agreement;
- byte replay: GREEN.

## Scientific disposition

ORION-20 now has a prospectively frozen **generated finite OCME positive**, not merely hand-declared non-vacuity. The successful primitive semantics were selected from frozen anonymous grammars using originating tasks only; held-out targets did not participate in selection.

This is still not unrestricted autonomous method invention. The candidate grammars and composition/wrapper templates were supplied prospectively by the experiment. The result establishes that obstruction-certified method-space expansion can be generated and transfer under two exact finite method-language models, while broad native Lean/problem-solving superiority and competition with open-ended theorem-proving/program-synthesis/evolution systems remain separate gates.
