# P2 SYNERGY V2 implementation-only amendment

## Preserved V1 failure

V1 reached the frozen public files and parsed the first review world, but it
failed before writing any result.  The static-centroid expression returned an
`n x 1` SciPy sparse matrix.  Applying `numpy.asarray(...).ravel()` preserved
that matrix as one object rather than materialising its `n` values, so indexing
the candidate set raised `IndexError: index 1 is out of bounds for axis 0 with
size 1`.

No arm metric, aggregate, gate, or scientific terminal was observed in V1.

## Sole V2 change

`run_synergy_successor_v2.py` changes only the extraction of the already
declared cosine similarity:

```python
(x @ x[positive].T).toarray().ravel()
```

The source files and checksums, four worlds, identity joins, outcome-blind seed
rule, vectorizer, random seeds, arms, active-model hyperparameters, budgets,
metrics, gates, terminals, and forbidden claims are unchanged.  The V2 protocol
records the implementation-only successor identity and the pre-outcome V1
failure.
