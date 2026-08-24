# P5 V2 terminal-preserving six-arm adapter protocol

**Frozen:** 2026-08-23T15:42:15Z, before any native output example or outcome  
**Authority:** source-interface and synthetic conformance only

For arm a, let g_a map a hidden task world to the complete information the
adapter may observe: the typed native terminal, complete mutation/write set,
and any frozen input-native certificate. Let r be the minimal P5 revision
class. A singleton adapter output c is lawful only when every admissible
world in the fibre g_a^-1(z) has r=c, and c belongs to the arm's frozen
support set. If two worlds in one fibre require different classes, the fibre
is mixed and the adapter must emit UNRESOLVED.

Native success strings, patch existence, archive rank, profile status,
CLEAN, DRAWBACK, ABSTAIN, open needs, drafts, scores, timeouts and errors
do not by themselves determine a P5 class. Error, timeout, abstention, empty,
partial, invalid, unsupported and mixed fibres are preserved as UNRESOLVED;
they are never converted into success.

Conditional support is conservative:

- SWE-agent: any of the seven proper classes only with one host-validated
  input-native certificate and a complete single-class write set.
- MOSS, DGM and ADIAS: only within-class model, model-class expansion,
  representation-regime or execution repair under the same uniqueness rule.
- Double Ratchet metric-only: only EVALUATOR_REPAIR, and only with a
  pre-outcome evaluator-defect certificate, byte-frozen solver, evaluator-only
  mutation and passed development validity gate.
- ScienceClaw: no native singleton class. Its artifacts and statuses may be
  scored externally but may not be relabelled as a revision decision.

These are adapter-conformance statements, not correct-repair or performance
claims. Correctness, minimality, preservation, fresh transfer and H1--H4
remain external and CANNOT_CHECK.

