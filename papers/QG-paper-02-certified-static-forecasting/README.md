# QG2 — Theorem-backed static forecasting

**Stable ID:** ORION-QG-P2  
**Canonical manuscript:** `manuscript/main.tex`  
**Status:** `INTERNAL_REVIEW_PASS__LAYERED_CERTIFICATE_CLAIM / SUBMISSION_GATES_OPEN`

## One job

QG2 studies how to forecast an exact TARE structural cost without invoking the unrestricted dynamic-programming referee, while keeping separate certificates for **cost exactness**, **regime explanation**, and **empirical validation**.

The V1 manuscript stopped at a valuable QG-5 refutation: the original three-family formula missed one fresh `n=3` instance. Current main contains the repair and its own later stress test. QG-5b defines `F2(t)=C_Dxx(t)`, the exact minimum over the full support-`<=2` family. R6S already proves `C_DP=C_Dxx` for all `n` under the frozen unit objective, so F2 is theorem-backed exact; it also has zero error on 9,547 compared instances. An enlarged closed-form borrow explanation `B'` repairs the QG-5 miss on those panels, but QG-7 later refutes `B'` as an all-`n` explanation with 64 exact hybrid witnesses. The **cost certificate survives the explanation refutation** because those witnesses still lie inside support two.

That separation is the paper's central result: an exact forecast can have stronger authority than the compact human-readable regime story attached to it.

## Boundary

F2's exactness is only for the frozen R6M grammar and unit support-count objective. QG-2/QG-8 show objective indexing is mandatory. Chemistry rows obtained by containment pinch are labeled as such. No full-circuit, hardware, runtime-superiority, or physical quantum-advantage claim is made.

See `JOURNAL_READINESS.md`, `REPRODUCE.md`, and `CLAIM_LEDGER_V2.md`.