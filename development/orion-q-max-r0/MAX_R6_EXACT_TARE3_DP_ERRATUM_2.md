# MAX-R6 exact TARE-3 joint DP erratum 2

Date: 2026-08-20
Applies before any exact-joint-DP outcome.
Authority: pre-outcome comparator clarification only; no R6 or novelty authority.

## E3 — strongest deterministic frame-only comparator

The original `B_FRAME_ONLY` text left the result dependent on which auxiliary frame was retained when multiple target-agnostic frames achieved the same minimum Uanti support. Gate 4 requires a strict win over this comparator, so that ambiguity is not acceptable.

The comparator is therefore frozen as the stronger two-stage object `B_FRAME_ONLY_STRONG`:

1. enumerate every valid ordered pairwise-anticommuting auxiliary triple `R=(R0,R1,R2)` admitted by the same exact-joint grammar and every central axis `c`;
2. compute `C_Uanti_parity(R,c)` without consulting target Pauli strings beyond their qubit count;
3. retain the entire set of `(R,c)` pairs attaining the global minimum Uanti support;
4. only after that target-agnostic minimum set is frozen, optimize exactly over target permutation, all admissible distinct control labels, exact minimum-weight Tag generators, and Restore strings for every retained `(R,c)`;
5. define `B_FRAME_ONLY_STRONG` as the minimum complete `C_joint` over that retained set;
6. if multiple witnesses attain the same comparator cost, tie-break only for serialization by ascending `(R0,R1,R2,c,target_permutation,labels,S0,S1)` under the implementation's canonical integer encoding.

Thus the comparator gives generic frame-weight optimization the **best possible downstream benefit among every globally Uanti-minimal frame**. The joint candidate cannot obtain a development positive merely because an arbitrary frame-only tie was resolved unfavorably.

## Gate binding

Development gate 4 in `MAX_R6_EXACT_TARE3_JOINT_FRAME_DP_PROTOCOL.md` is read as:

> for at least one open subject, an exact joint optimum is strictly lower in `C_joint` than `B_FRAME_ONLY_STRONG`.

No other search variable, objective coefficient, subject, evidence budget, threshold, donor credit, or fresh-subject rule changes. Erratum 1 remains controlling for the deterministic witness rule and the top-four expensive-verifier panel.

If the candidate does not strictly beat this stronger comparator, the method-language development gate fails and the negative must be retained.
