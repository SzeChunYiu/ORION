# Native-output fibre factorisation theorem

## Theorem

Let W be the set of task worlds allowed by a frozen protocol, let g map each
world to the complete information visible to an adapter, and let r map each
world to its correct minimal revision class. A deterministic exact adapter A
with r = A composed with g exists if and only if r is constant on every fibre
of g.

## Proof

Necessity: if g(w1)=g(w2), then A(g(w1))=A(g(w2)). If r=A composed with g,
then r(w1)=r(w2), so r is constant on the fibre.

Sufficiency: if r is constant on every fibre, define A(z) as that common value
for any world with g(w)=z. The definition is independent of which world is
chosen, and A(g(w))=r(w). On observations outside the image of g, define A
arbitrarily or fail closed.

Therefore a single same-visible-symptom pair with two different minimal
revision classes proves that no singleton adapter is lawful on that symptom.
The terminal-preserving output is UNRESOLVED.

## Frozen six-arm counterexamples

The prospectively frozen synthetic fixture set supplies one mixed fibre per
arm, without using any native output example or public/protected outcome:

| Arm | Same visible symptom | Compatible minimal classes |
|---|---|---|
| SWE-agent | patch produced and exit zero | EXECUTION_REPAIR; EVALUATOR_REPAIR |
| MOSS | successor replay improved | WITHIN_CLASS_MODEL_REPAIR; REPRESENTATION_REGIME_REPAIR |
| DGM | child selected as archive best | MODEL_CLASS_EXPANSION; EXECUTION_REPAIR |
| ADIAS | profile issue open and patch compiles | WITHIN_CLASS_MODEL_REPAIR; EXECUTION_REPAIR |
| Double Ratchet metric-only | DRAWBACK | EVIDENCE_REPAIR; EVALUATOR_REPAIR |
| ScienceClaw | open need with valid typed artifact | EVIDENCE_REPAIR; MEASUREMENT_REPAIR |

Every raw symptom fibre is mixed. Patch success, replay improvement, archive
rank, compile success, DRAWBACK and open-need status therefore license zero
singleton P5 classes.

## Certified refinement

A wrapper may refine the observation to include a host-validated input-native
class certificate and the complete mutation/write surface. A singleton is
conformance-lawful only when:

1. native status is complete success;
2. exactly one certificate class exists;
3. the complete write set belongs to exactly one class;
4. certificate and write class agree;
5. the class is in the arm's frozen support set; and
6. arm-specific custody conditions hold.

This refined adapter labels the proposed action type. It does not establish
that the action is correct, minimal, preserving, transferable, or superior.
Those remain external outcomes.

## Arm-specific support result

- SWE-agent has seven conditionally supportable classes under certified
  single-surface mutation.
- MOSS, DGM and ADIAS each conditionally support four agent/scaffold classes:
  within-class model, model-class expansion, representation-regime and
  execution repair.
- Double Ratchet metric-only conditionally supports only EVALUATOR_REPAIR,
  with solver-byte preservation and a development validity gate.
- ScienceClaw's native interface supports no singleton revision class.

The 90-case bounded synthetic conformance run passed 90/90. Seventy cases
correctly remained UNRESOLVED; the twenty singleton cases were certificate and
write-surface contract checks, not comparator observations.

## Wider claim

The theorem applies to any adapter that translates a coarse native interface
into a richer scientific decision taxonomy. Interface coverage cannot be
created by relabelling: a target decision is identifiable exactly when it
factors through the information exposed by the native interface. Unsupported
fibres are a scientific interface limit, not missing performance data.

