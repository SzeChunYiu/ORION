# Paper C / C3 — arbitrary-order value separation report

Date: 2026-08-24  
Base: `cfce47d8c4edb9c3df83efd35c699cb9a25a8a07`  
Primary owner: `PAPER_C`  
Decision: **accepted inside the frozen structural grammar authority ceiling**.

## Result

For every `m>=5` and `L>=1`, the frozen construction gives two equal-length `X/I` compiler instances with identical ordered weights and identical exact common-factor counts for every labeled term subset of size at most `m-2`. Both instances strictly improve over unary and have the unique all-term one-block optimum, yet their exact improvements differ by

`[m(ceil(log2(m))+1)-1]L`.

Thus, for every fixed `m>=5`, complete labeled interaction data through order `m-2` leaves an exact-value ambiguity that grows linearly without bound in `L`.

The C1 theorem still supplies the exact low-order improvement decision. C2 separately supplies pair-information value and optimizer-witness separation. C3 strengthens only the value-information side: it does not claim a new optimizer separation because both C3 instances intentionally have the same unique optimizer shape.

## Exact corroboration

The source and independently written generic implementations both enumerated every set partition for `m=5,6,7,8,9` at `L=1`.

| `m` | qubits | partitions | factor entries through `m-2` | `Delta(A)` | `Delta(B)` | gap |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 180 | 52 | 25 | 1,520 | 1,501 | 19 |
| 6 | 415 | 203 | 56 | 4,301 | 4,278 | 23 |
| 7 | 946 | 877 | 119 | 11,654 | 11,627 | 27 |
| 8 | 2,133 | 4,140 | 246 | 30,491 | 30,460 | 31 |
| 9 | 5,914 | 21,147 | 501 | 96,485 | 96,441 | 44 |

Every row matched the interaction tensor, unique optimizer, strict-decision, and closed-form gap gates. The all-`m,L` authority comes from the parity count and dominance proof, not extrapolation from these finite rows.

## Receipts

- protocol SHA-256: `434ebd31db54775d05b5fc53dd6b13f2647cfe8b7a73b282586600937d2dce1c`;
- source result digest: `d35d50524a7c1734c86493b9db2f5eff8b9fdb8ec94a639cba9cd5e4dad0c815`;
- source result file SHA-256: `3cdfd845652f243741635c6ad11fe3c0531262c6667023c91fac29a8f459a802`;
- generic verification digest: `8076c38a64e5045b9d2c4701b2bbaa8255a09aeec4386f3fec659e87489a8bcc`;
- generic file SHA-256: `073a329fb5e1dae94f18c5c60178ca49185a72d69724ddf07ff7427248f340d6`;
- native manifest digest: `63f9706ece3982173287f374e21a8e0b750a37948aa1fbc97f06212f5d864ca6`;
- dual receipt digest: `2f51550e062f7ee40cb2680040d63f475d90bbd22cf32fbc8ad094874bd88b3b`;
- dual file SHA-256: `fbab12a5d91676e6be0919536b3cfd0dbdbc727d63c6f4b804936fe25d6678cf`;
- C1 parent file SHA-256: `3ffdd36ab1c73680930f3e5471ec095a5dd2ea33438765d3ccca0584bc9afeff`;
- C2 parent file SHA-256: `3a5e8eeee12d246ccf2a1d7422bdf4e0c0027c066934870272cdee9e7a6055f1`.

Positive terminal:

`PAPER_C_C3_ARBITRARY_FIXED_ORDER_INTERACTION_DATA_VALUE_INSUFFICIENT__LINEAR_GAP_MACHINE_CORROBORATED`

The native run used two cycles with statuses `ADVANCED`, `TERMINAL`. Four fresh-workspace replays produced the identical receipt and file hash. Focused tests: `5 passed`.

## Adverse history

The first independent implementation exceeded the execution window because it rescanned all columns inside every partition and exited with status `143` before a decision. The exact adverse terminal and repair are preserved in `PAPER_C_C3_ENGINEERING_AMENDMENT_1_2026-08-24.md`. No scientific gate was weakened and no failed lane was counted as acceptance.

## Donor subtraction

Parity trades and low-order-marginal equality are donor mathematics. C3 claims only their exact realization in this compiler grammar, the unique one-block dominance proof, and the exact value-gap formula. A primary-source donor review is still required before assigning novelty authority.

## Remaining authority boundary

The construction uses a deliberately conservative, nonminimal number of common columns and grows exponentially with `m`; no efficiency or minimality claim is made. The result is structural `SELECT+PREP+WIDTH` cost only. It gives no physical T-count/runtime/qubit advantage, multiplicative approximation lower bound, cross-objective result, cross-grammar result, novelty certificate, or top-tier venue guarantee. CI was skipped and supplies no authority.

