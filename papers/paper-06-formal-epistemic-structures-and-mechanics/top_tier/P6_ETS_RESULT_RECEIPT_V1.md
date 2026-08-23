# P6 ETS bounded executable result receipt V1

**Protocol:** `P6_ETS_PROTOCOL_V1.md`  
**Frozen cases:** `ets_cases_v1.jsonl`  
**Frozen gold:** `ets_gold_v1.json`  
**Post-freeze checker:** `check_ets_top_tier_v1.py`  
**GitHub Actions run:** `32644815733`  
**Artifact:** `p6-ets-v1-receipt`, artifact ID `9494570298`  
**Terminal:** `P6_ETS_BOUNDED_EXECUTABLE_POSITIVE`

## Prospective chronology

The protocol was committed first, then the 18 case facts, then the independent gold dispositions. The checker and workflow were added only afterward. No historical P6 result was relabeled.

## Exact content binding

- case SHA-256: `8868875a7d7e9db376543fe466409adf3b2f02bd03885c9fe3803d9c6b5d2ae2`
- gold SHA-256: `57cc7707cc24a243bf0c40f2908fc316e4d2f24272f6b30554ffabceacbdec16`
- canonical receipt SHA-256: `a5d56cbae63d550b2d1a773605e41d3a614113ba87c479e810ce4d3c66e60fe7`
- uploaded artifact ZIP SHA-256: `b45df33c73eb78e941b53d3ef0b0c4ca95970974ee56387b565ee358e23d0a08`
- two fresh executions were byte-identical: `P6_ETS_V1_BYTE_REPLAY_GREEN`.

## Results

Across 18 frozen cases / three six-case families:

| System | exact accuracy | unsafe false-admissible | laundering false-admissible | unnecessary reopen on independent-support controls |
|---|---:|---:|---:|---:|
| strong declared donor product | 0.50 | 9 | 3 | 0 |
| ETS checker | 1.00 | 0 | 0 | 0 |

Per-family ETS accuracy was 1.00 in formal/software, agent-memory/tool-state and scientific-evidence-state. Donor accuracy was 0.50 in each family.

## Executable theorem checks

- **T6.1 finite factorization/non-implication:** exactly one of the 16 assignments of `(computational support, evidence transport, scientific obligation, scientific authority)` was admissible when all four were required. Flipping each single factor produced a registered non-admissible terminal.
- **T6.2 composition:** matching epoch/scope transport composed; explicit epoch mismatch, scope mismatch and open-obligation counterexamples blocked composition.
- **T6.3 erasure:** 47 pairs shared the declared donor decision signature while requiring different scientific dispositions. The first frozen witness is `FS-CLEAN` (`ADMISSIBLE`) versus `FS-EVIDENCE` (`REOPEN`).

## Scientific disposition

This result supports a **bounded executable ETS separation** over the frozen interface. It does not establish universal P6 superiority over arbitrary donor systems. In particular, if a donor product is extended with responsibility-scoped evidence/obligation/authority semantics until it is extensionally equivalent, the result becomes an equivalence/assimilation result.

The top-tier P6 terminal remains pending broad external real-system transition evidence, cross-paper overlap review, immediate pre-submission literature saturation and final package binding.
