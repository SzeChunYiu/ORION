# Paper A claim ledger

| ID | Claim | Evidence | Status / boundary |
|---|---|---|---|
| A-C1 | For every `b>=2`, one local change in the `b`-way Restore functional increases cost by at most `b-1`. | Analytic Lemma 1 + bounded exhaustive checker for `b=2..7`. | PROVEN-ALL-B; finite rows corroborate. |
| A-C2 | In MultiTag-TARE with `s>=0`, throughout `mu >= (b-1)t_R`, an optimum exists with `support(R)<=rank(V_R)<=s+1` for every frame. | Theorem 2 zero-signature deletion proof + A1 parent bindings. | PROVEN-ALL-SIZES for the explicitly defined grammar/objective. |
| A-C3 | Arbitrary nonnegative Tag support weights do not change C2 when Tags are fixed by the exchange. | Objective accounting in Theorem 2. | PROVEN within the stated objective form. |
| A-C4 | R6M has intrinsic support number `kappa=2`. | Protected all-size upper theorem + exact lower witness bound by Paper A A1. | PROVEN-EXACT, one-Tag R6M only. |
| A-C5 | `s+1` is intrinsically sharp for every `s`. | none | OPEN; explicitly not claimed. |
| A-C6 | Larger support is necessary outside `mu >= (b-1)t_R`. | none | OPEN; outside-cone means certificate unavailable only. |
| A-C7 | Structural support savings imply physical T-count/runtime/qubit savings. | none | OUT OF SCOPE / forbidden promotion. |
| A-C8 | TARE, Tag/Restore, binary symplectic algebra, sparse normal forms, or exact synthesis are ORION inventions. | donor literature | DONOR-OWNED / forbidden novelty claim. |

## Headline decision proof

**Question:** when can dependent symplectic coordinates be deleted without losing exact optimality?  
**Answer:** when the frame refund dominates the exact worst-case `b-1` Restore increase; support then descends to realized signature rank.  
**Strongest alternative:** the rank ceiling is merely an artifact of a proof language and not intrinsic.  
**Resolution:** the manuscript labels it a normal-form certificate; only R6M receives a matching intrinsic lower witness.  
**Boundary:** explicit MultiTag-TARE grammar and objective cone only.
