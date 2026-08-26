# ORION Paper IV — Protected V2 Citation-Saturated Peer-Review-Ready Archive

This release is an additive, immutable successor to `orion-p4-v2-peer-review-ready`. It preserves the same publication-authorizing protected V2 experiment and headline results while archiving the 2026-08-17 submission-literature saturation refresh and its newly audited TMLR PDF.

## Headline result
- ORION: **0/360** false scientific-authority promotions.
- Strongest frozen comparator mechanism (ProvenAI-style): **180/360**.
- Both: **60/60** clean promotions, zero clean false negatives.
- H1: PASS, effect `-0.50`, paired 95% CI `[-0.553,-0.447]`.
- H2: PASS, clean-coverage effect `0`, CI `[0,0]`.
- H3: **NOT SUPPORTED**, correct-CANNOT_CHECK effect `0`, CI `[0,0]`.

## Citation-saturation refresh
The manuscript bibliography was expanded from 13 to 19 targeted references after a functional saturation sweep across scientific verification, provenance/research integrity, abstention/refusal, benchmark/evaluator auditing, protected evaluation/assurance, and contamination-resistant evaluation. Added manuscript-facing parent-domain work includes SciIntegrity-Bench, AgentAbstain, Automated Benchmark Auditing, Holistic Agent Leaderboard, INSPECT-AI/RIPE-KG, and Behavioral Integrity Verification. SRE-Bench was screened and explicitly deferred rather than added as padding.

The refresh does not change the frozen protected V2 protocol, campaign, comparator mechanisms, ablations, or numerical claims.

## Exact evidence identities
- citation-saturated publication source merge: `46a3a4f893ac936cb1f1215494c9662ed1a5c66e`
- repaired subject: `f6e51b5c8f905382b8e2f5568d9035fc14241aa1`
- protected campaign: `31976589735`
- hidden split SHA-256: `3fe91b669643fa158f2f64c1e6ab70837afbb9b0582e297f1da6e1c3c696fcd9`
- executable harness SHA-256: `094f43cb320f8e8e3196049269b20ac22e7e94fa9890b80f27f38ef49f7c82ea`
- protected safe-bundle artifact ZIP SHA-256: `51ac14bc3a6b4b570aaca6d4a41c91f53d9bf2887e66f0620c412f78566a3b44`
- exact-main CI: `32005097845`
- exact-main TMLR audit: `32005097963`
- audited 12-page PDF SHA-256: `f2ede371e254e37cf57c309565a5ede09ab3d61f9feba75b67eccca2a4893ccf`

## Assets
The release workflow attaches:
1. the independently audited citation-saturated anonymous TMLR PDF;
2. the unchanged safe publication bundle from protected V2; and
3. a source supplement archived from the exact citation-saturated publication commit.

Protected per-case gold and raw scored-process traces remain intentionally unreleased. Comparator arms remain protocol-matched mechanism reimplementations rather than executions of external authors' original software. The earlier 39-case live-model arm remains exploratory and non-authorizing.
