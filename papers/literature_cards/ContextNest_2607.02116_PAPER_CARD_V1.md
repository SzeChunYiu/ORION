# Paper Card — ContextNest / Verifiable Context Governance

**Source mode:** primary arXiv record/abstract.  
**Context mode:** targeted current-donor check.  
**Checked:** 2026-08-21.

## 01. Bibliographic position
Misha Sulpovar, Benn R. Konsynski, Qaish Kanchwala, Gabe Goodhart. **ContextNest: Verifiable Context Governance for Autonomous AI Agent.** arXiv:2607.02116 (2026).

The primary abstract alternates `ContextNest`/`ContextNext` naming in the retrieved record; final citation/title should follow current arXiv metadata and the paper itself at submission.

## 02. Research question
How can an agent's external context store provide provenance, version identity, integrity, traceability and point-in-time reconstruction rather than relevance alone?

## 03. Background route
The work positions context governance beneath RAG/retrieval: retrieval decides relevance, while a governance layer decides which artifacts are approved/current/attributable/integrity-verified.

## 04. Prior-work / field context
RAG, knowledge stores, provenance/versioning and MCP-based context infrastructures are parent areas.

## 05. Pain point
A relevant retrieved document may be stale, unapproved, untraceable or impossible to reconstruct as the exact version consumed by an agent.

## 06. Core insight
Use typed documents/metadata, deterministic selectors, URI references, SHA-256 hash-chained version histories, graph checkpoints, live source nodes and context-consumption audit traces to govern what an agent is allowed to consume.

## 07. Method / module logic
The abstract reports an open specification/reference implementation and two controlled experiments: a stale-version attack and retrieval-determinism comparison.

## 08. Essential formulas
Not assessable/needed from source-limited record.

## 09. Experiment-to-claim evidence
The abstract reports governed selection with 97% answer-quality pass rate versus 93–90% BM25 variants at lower token cost in one stale-version experiment, and stable document-set selection for deterministic selectors/BM25 versus non-deterministic dense+HNSW retrieval in a 1,060-document experiment.

## 10. Main conclusions
Provenance/version/integrity governance is a distinct layer from retrieval quality; deterministic governed context can prevent some stale/version failures and support reconstruction/audit.

## 11. Conclusion boundaries
ContextNest directly owns broad claims about governed/versioned/provenanced agent context and hash-chained audit history. Q4 cannot claim novelty for such infrastructure generally.

## 12. Author-stated limitations
Not fully assessable from abstract record. Full paper required before detailed claims about security strength, adversary model or generality.

## 13. Critical analysis
Q4 must separate **container/context governance** from **decision sufficiency**. Its residual is not “store provenance and versions,” but whether typed/scoped knowledge changes rational downstream actions under identical visible facts—for example, which failure receipt to reopen, which interval to verify, or whether a transported certificate can be accepted.

## 14. Learned knowledge
A provenance-rich context layer can still leave the next decision unresolved. Q4 should state that governance supplies trustworthy state; its experiments test how type/scope information should be consumed by specific decisions.

## 15. Knowledge connections
Database provenance; P13 responsibility-carrying state; STALE; Q4 transport/remint; context retrieval governance.

## 16. Testable research ideas
- Run Q4 decision policies over a ContextNest-like governed store to isolate storage governance from decision semantics.
- Test whether responsibility-scoped support certificates can be encoded as governed context metadata.

## ORION claim effect
**Removed from Q4 novelty:** generic provenance/version/context governance, deterministic retrieval governance, hash-chained context history.  
**Q4 retained residual:** bounded matched-information evidence about how type/scope changes downstream decisions after state is available.
