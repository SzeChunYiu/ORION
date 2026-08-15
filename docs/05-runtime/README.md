# Runtime and LLM integration

ORION's minimum runtime is now provider-neutral.

```text
external LLM SDK/client ----> LLMProvider ----┐
external search/index ------> RetrievalProvider|--> OrionRuntime --> OrionSolver
protected verifier ---------> VerificationProvider┘
```

`OrionRuntime.from_providers(...)` converts the LLM port into `LLMResearchReasoner` and injects all providers into the modular solver.

## Integration rule

A provider is an implementation detail. Replacing a model vendor, web search service, vector database, or verification backend must not change:

- K/W/M state semantics;
- the recursive operator order;
- authority rules;
- residual diagnosis/reframe governance;
- saturation requirements;
- negative history.

## LLM response contract

The current `LLMResearchReasoner` requests typed JSON for search planning, source interpretation, reconstruction, diagnosis, reframing and answer composition. Model text is proposal data. `ABSORB` may increase claim authority only when the separate `VerificationProvider` returns certificate IDs.

## Minimum external integration

An application supplies:

```python
runtime = OrionRuntime.from_providers(
    llm=my_llm_provider,
    retrieval=my_retriever,
    verification=my_verifier,
)
result = runtime.solve(Problem("id", "question"))
```

The callable adapters can wrap existing SDK functions without importing vendor packages into ORION core.

## Current boundary

This is **integration-ready**, not evidence that arbitrary live providers are reliable. Before a live adapter is promoted, run adapter contract tests plus the known-world solver benchmark, then a frozen external task packet. Tool/code-execution ports are a later capability layer and must not be smuggled through the LLM interface.
