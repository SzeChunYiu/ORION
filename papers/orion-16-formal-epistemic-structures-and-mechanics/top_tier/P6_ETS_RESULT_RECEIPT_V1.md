# P6 ETS bounded executable result receipt V1

**Protocol:** `P6_ETS_PROTOCOL_V1.md`  
**Frozen cases:** `ets_cases_v1.jsonl`  
**Frozen gold:** `ets_gold_v1.json`  
**Primary post-freeze checker:** `check_ets_top_tier_v1.py`  
**Second independent checker:** `check_ets_independent_v1.py`  
**Primary GitHub Actions run:** `32644815733`  
**Two-checker GitHub Actions run:** `32653576016`  
**Latest artifact:** `p6-ets-v1-receipt`, artifact ID `9496839720`  
**Latest artifact ZIP SHA-256:** `fa6ec2504978d374e9a1573f92b27933820d8a484bb625375cb1d1dc2b2650d9`  
**Scientific terminal:** `P6_ETS_BOUNDED_EXECUTABLE_POSITIVE`  
**Independent verification terminal:** `P6_ETS_SECOND_INDEPENDENT_CHECKER_GREEN`

## Prospective chronology

The protocol was committed first, then the 18 case facts, then the independent gold dispositions. The primary checker and original workflow were added only afterward. No historical P6 result was relabeled.

The second checker was added only after the bounded primary result existed. It does not import or execute the primary checker: it evaluates the same frozen case facts and gold through a distinct prioritized defect-set formulation, then independently reconstructs T6.1–T6.3 summary invariants. CI requires the two implementations to agree on every protected classification.

## Exact content binding

- case SHA-256: `8868875a7d7e9db376543fe466409adf3b2f02bd03885c9fe3803d9c6b5d2ae2`
- gold SHA-256: `57cc7707cc24a243bf0c40f2908fc316e4d2f24272f6b30554ffabceacbdec16`
- original canonical primary receipt SHA-256: `a5d56cbae63d550b2d1a773605e41d3a614113ba87c479e810ce4d3c66e60fe7`
- original uploaded artifact ZIP SHA-256: `b45df33c73eb78e941b53d3ef0b0c4ca95970974ee56387b565ee358e23d0a08`
- latest two-checker artifact ZIP SHA-256: `fa6ec2504978d374e9a1573f92b27933820d8a484bb625375cb1d1dc2b2650d9`
- primary replay: `P6_ETS_V1_BYTE_REPLAY_GREEN`;
- independent replay: `P6_ETS_INDEPENDENT_V1_BYTE_REPLAY_GREEN`;
- cross-implementation agreement: `P6_ETS_TWO_IMPLEMENTATIONS_AGREE`.

## Results

Across 18 frozen cases / three six-case families:

| System | exact accuracy | unsafe false-admissible | laundering false-admissible | unnecessary reopen on independent-support controls |
|---|---:|---:|---:|---:|
| strong declared donor product | 0.50 | 9 | 3 | 0 |
| ETS checker | 1.00 | 0 | 0 | 0 |

Per-family ETS accuracy was 1.00 in formal/software, agent-memory/tool-state and scientific-evidence-state. Donor accuracy was 0.50 in each family.

The second verifier reproduces all 18 frozen gold dispositions exactly and matches the primary checker case-for-case. Its label-independence attack remints `id`, `family` and `case_type` and verifies that the scientific terminal is unchanged.

## Executable theorem checks

- **T6.1 finite factorization/non-implication:** exactly one of the 16 assignments of `(computational support, evidence transport, scientific obligation, scientific authority)` is admissible when all four are required. Flipping each single factor produces a registered non-admissible terminal. The second checker reconstructs this result from an independent bit-pattern enumeration.
- **T6.2 composition:** matching epoch/scope transport composes; explicit epoch mismatch, scope mismatch and open-obligation counterexamples block composition. The second checker reconstructs these boundary conditions independently.
- **T6.3 erasure:** 47 pairs share the declared donor decision signature while requiring different scientific dispositions. The first frozen witness is `FS-CLEAN` (`ADMISSIBLE`) versus `FS-EVIDENCE` (`REOPEN`). CI requires the independent checker to reproduce the primary `47`-witness count.

## Scientific disposition

This result supports a **bounded executable ETS separation with two-implementation verification** over the frozen interface. It does not establish universal P6 superiority over arbitrary donor systems or a theorem beyond the frozen finite semantics. In particular, if a donor product is extended with responsibility-scoped evidence/obligation/authority semantics until it is extensionally equivalent, the result becomes an equivalence/assimilation result.

The top-tier P6 terminal remains pending broad external real-system transition evidence, any theorem generalization needed for the final headline, cross-paper overlap review, immediate pre-submission literature saturation and final package binding.
