# Graph Atlas R9 Execution Protocol

## Frozen inputs

- branch parent: `codex/five-paper-top-tier-r8-20260826@16f12a2635abe82b649821b2a3c3e563fdf339e0`;
- Python: 3.11 or 3.12;
- NetworkX: exactly 3.6.1;
- domain: Graph Atlas indices 209--1252;
- target: chromatic number;
- base representation: sorted degree sequence plus triangle count.

## Command

```bash
python -m pip install 'networkx==3.6.1'
python papers/five-paper-top-tier-r8/C/artifact/fiberguard_graph_atlas_r9.py
```

The command must reproduce `FIBERGUARD_GRAPH_ATLAS_R9_RESULTS.json` byte-for-byte. The canonical content digest is computed before the `content_sha256` field is inserted.

## Fail-closed controls

1. Atlas length must be 1,253.
2. The seven-vertex slice must contain 1,044 graphs at indices 209--1252.
3. Two exact chromatic-number engines must agree on every graph.
4. Every four-graphlet profile must sum to 35 induced subgraphs.
5. The empty and complete graphs must have chromatic numbers 1 and 7.
6. `C4` count must leave at least one ambiguous base fibre.
7. The graphlet-4 profile and the `C4+clique+one-WL` bundle must each have zero target diameter.
8. One-WL plus graphlet-4 must yield 1,044 refined fibres.

Any failed control terminates nonzero. No partial run can be promoted to an absence result.

## Authority boundary

This protocol proves finite exactness on the declared complete unlabeled atlas only. It does not establish distributional frequency, large-instance scaling, production utility, or independent replication.
