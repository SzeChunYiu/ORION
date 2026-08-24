# Paper B / B1 — exact rank-only proof-gap report

Date: 2026-08-24  
Base: `8ed6d54c66af4bf0404f833dc872a6db6d07a849`  
Primary owner: `PAPER_B`  
Decision: **accepted inside the defined proof-system and R6I unit-objective ceiling**.

## Result

The rank-only zero-sum deletion proof system has exact uniform certificate ceiling `d` whenever its `F_2^d` production alphabet spans the quotient and contains a basis. Linear dependence gives the upper bound; the basis word has nonzero total and no legal zero-sum deletion, giving the matching proof-system lower bound.

Both frozen R6I block alphabets satisfy the hypotheses at `d=5`. Their QG6 analytic bases occur in the enumerated production change alphabets and are exact zero-sum-free length-five words. Therefore the QG6-style proof abstraction has certificate complexity exactly 5. The independently protected V6 theorem gives intrinsic support exactly 1. The single-copy compiler proof-gap is exactly `5 versus 1`.

For `t` independent R6I components with the explicitly defined summed support budget, direct-sum amplification gives exact certificate budget `5t` and exact intrinsic budget `t`. The additive gap `4t` is unbounded; certified exhaustive-search polynomial degrees separate as `5t` versus `t` within the product component.

## What this closes

This replaces an informal “local proof systems fail” narrative with a theorem for a precisely defined, production-instantiated class. The class contains the QG6 rank proof and excludes the whole-system Tag relocation used by V6.

It does not prove a lower bound for every local proof system, every syndrome-preserving system, or a future system that uses additional acceptance semantics. The product theorem is amplification of the same mechanism, not a second independent compiler mechanism.

## Verification

- both production blocks: rank 5, basis contained in change alphabet, basis total nonzero, zero nonempty zero-XOR subsets;
- abstract standard-basis theorem exhausted for `d=1,...,12`;
- exact product rows for `t=1,2,3,10,100`, ending at certificate/intrinsic budgets `500/100` and gap `400`;
- source, independent generic, and native decisions agree;
- four fresh-workspace runs produced the identical receipt and dual-file hash;
- focused tests: `5 passed in 1.92s`.

Positive terminal:

`PAPER_B_B1_R6I_RANK_ONLY_CERTIFICATE_COMPLEXITY_5_VS_INTRINSIC_1__DIRECT_PRODUCT_GAP_4T_MACHINE_CORROBORATED`

## Receipts

- protocol SHA-256: `30d18a0ec53027634fb48a460da4e20fede9092264515dc5d5b1af7153afa59c`;
- source result digest: `1d230beebcbbf3caa1dfa966331c93c227907fe08babbedaae068a4d5df96840`;
- source result file SHA-256: `c3d963e266482b4af7ce01373a5fdf4f882f5752be60c34c6f8bba7c484ae628`;
- generic verification digest: `77370fa02b6c4bdd0ae0e8481aa79b020d7655f675e2407c61c46e4713a7214d`;
- generic file SHA-256: `4de1c2021e39de14c1700355412ca7805efe4a0964c656152de3141dbd7034d6`;
- native manifest digest: `7c7fa1a1c03b8c101946ba0ff6600cc880b95506303c7aec286393651115666c`;
- dual receipt digest: `44ff44c83e0c923d8fbcb1e7a93650e65511c7e838dd35edef9fd333b367808c`;
- dual file SHA-256: `a1ade3b3c9c6e87897d11232c00a4703b8c1b9c087ab42ec8290d9a540559bbb`;
- QG6 result file SHA-256: `51d5ffcdd682384cc2259146d0c7e9a835c4644d1cffa36c6d9fca0d1c06f884`;
- QG6 protected receipt SHA-256: `3e32e25656cc0d78d96a9325cf344fcca24f04c4acd8eeb5932eb6e790466b0d`;
- V6 result file SHA-256: `f8df10d5604267e43701adb032f33baf1dfaa5a6572e5bdeaeda7707c4100b66`;
- V6 protected receipt SHA-256: `4e3a3596b3bfbbad584252861efb75a396a815b193bf71c2b0b39a487db023b5`.

The native run used two cycles with statuses `ADVANCED`, `TERMINAL`.

## Donor subtraction and remaining boundary

The generic zero-sum-free/Davenport boundary for `C_2^d`, linear dependence, direct sums, and support sparsification are donor mathematics. The residual is the exact R6I production-alphabet instantiation, formal identification of the proof abstraction, its exact `5 versus 1` compiler gap, and the bounded direct-product consequence.

Primary-source donor review remains mandatory before novelty authority. There is no physical T-count/runtime/qubit advantage, objective transfer, grammar transfer, complexity-class lower bound, second-mechanism claim, or venue guarantee. CI was skipped and provides no authority. No manuscript or claim-ledger file was changed.

