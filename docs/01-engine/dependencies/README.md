# Mechanic dependencies

ORION treats dependencies as explicit contracts rather than invisible runtime assumptions.

A dependency requirement records:

- dependency identity/kind;
- whether it is mandatory;
- exact identity/version binding semantics;
- precondition for safe use;
- failure propagation;
- fallback behavior;
- integrity/provenance requirements.

The universal V0 layer recovers structural mechanic dependencies from the recursive workflow graph. A required dependency that fails, blocks, or cannot be checked propagates a typed prerequisite residual unless a separately verified fallback exists. An alternative implementation/provider/path is never an implicit fallback: it is a versioned variation whose applicability must be evidenced.

The structural plan does not guess every provider, evaluator, data source, tool, schema, evidence root or resource dependency. Those remain step-specific open coordinates and should be discovered/reopened as real mechanic designs and live tasks expose them.
