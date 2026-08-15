# Candidate answer — DIAGNOSE.ATTRIBUTION.v0

**Target dimensions:** TRANSITION_MODEL, INVARIANTS, OUTPUTS, PROVENANCE.
**Incumbent evidence:** RAKL `publication/papers/paper-03-method-evolution-mechanics/sections/04_experience_to_method_architecture.tex` @ `bd4ce50f` (§Failure learning is an evidence ladder).

## Proposed step-specific contract

**Transition model — the failure evidence ladder (deliberately slower than success learning).**

```text
TaskEpisode(non-success)
  -> observed failure
  -> competing diagnoses          (a failed attempt may mean: claim false | weak
                                   representation | incomplete source | missing tool |
                                   wrong context packet | infrastructure failure)
  -> discriminating test
  -> supported diagnosis
  -> boundary lesson candidate
  -> cross-context validation
```

Attribution advances only by discriminating evidence; recurrence alone never becomes a causal explanation (this cell is where the shadow substrate's mode/effect/cause separation gets its promotion semantics).

**Invariants.**
- The first plausible narrative is inadmissible as attribution: at least two competing diagnoses must be registered before a discriminator is selected, or the outcome is `ATTRIBUTION_OPEN`.
- Diagnosis revisions are **append-only versions**: a later diagnosis supersedes without erasing the original observation or the earlier diagnosis.
- A raw failure cannot mint a globally blocking impossibility; only an independently verified impossibility blocks reuse, and only inside its registered scope.
- Infrastructure/instrument causes must be explicitly excluded before any mechanism-level attribution (the Paper IV v1 packet is the canonical exemplar of an instrument negative that is not a mechanism negative).

**Outputs.** `SUPPORTED_DIAGNOSIS(scope)`, `ATTRIBUTION_OPEN(competing set)`, `DISCRIMINATOR_UNAVAILABLE → CANNOT_CHECK`, `INSTRUMENT_ATTRIBUTED` (failure belongs to the instrument, target question reopens).

**Provenance.** Every supported diagnosis binds: episode ids, the competing set it defeated, the discriminating observation, and its scope boundary — so a future contradicting episode can reopen exactly this attribution.

## Known-answer / hostile test candidates

1. Same failure signature across two variations, no discriminator run → question generation may fire (mechanical layer already does), but attribution must remain `ATTRIBUTION_OPEN`.
2. Discriminator separates "missing source detail" from "representation weak" → only the supported branch may seed a boundary lesson.
3. Hostile: submit an attribution whose only evidence is recurrence count → rejected fail-closed.

## Not licensed

Live attribution accuracy (how often the supported diagnosis survives fresh episodes) is an empirical open coordinate.
