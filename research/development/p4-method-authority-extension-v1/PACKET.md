# P4 method-transfer authority extension — development packet

Parent issues: #410, #412. Coordinator: #403. Publication parent: #101.

## Pre-existing design authority

Issues #410/#412 were frozen before this implementation session and supplied the method receipt, coordinate separation, hostile cases, benchmark families, claim ceiling and allowed terminals. This packet records implementation mapping; it does not retroactively invent a successful protocol.

## Subject / branch

- implementation base: `main@451ed1da903d9b5eda67c60dadb280e4cea20a17`
- final integration base after P2 extension merge: `main@741de5bb3f990271f3b2e128b7603e5b1c7df230`
- lane: `shadow/p4-method-authority-extension-2026-08-18`
- additive only: current citation-saturated protected-V2 P4 manuscript/result package remains unchanged.

## Scientific object

`MethodTransferReceipt.v1` is a content-bound method-evidence receipt. It keeps donor ID↔digest pairs aligned, binds target/signature/assumption/adaptation/reconstruction/protected-evaluator/novelty state, and grants no authority itself.

`P4_METHOD_AUTHORITY_RECORD_V1` derives separate `VALIDITY`, `APPLICABILITY`, `TRANSFER`, `NOVELTY`, `UTILITY`, and `ADOPTION` coordinates. `ADOPTION` is mechanically `CANNOT_CHECK` under P4 because P5/host governance owns that transition.

## RED / hostile families

- donor assumption erased -> applicability/transfer blocked;
- invalid reconstruction -> validity/transfer blocked;
- visible success + protected failure -> validity/utility blocked;
- generator accessed evaluator -> validity/utility blocked;
- known prior art -> novelty blocked without erasing useful validity/transfer;
- known composition claimed as new primitive -> novelty blocked;
- novelty route absent -> `CANNOT_CHECK`;
- wrong source lineage -> transfer blocked;
- receipt/authority bytes changed -> digest failure;
- independent donor-ID/digest sorting -> forbidden; multi-donor pairing test retained;
- all-deny policy -> no false promotion but fails clean coverage;
- clean fully evidenced method -> science coordinates pass while adoption remains external.

## Protected discriminator

`METHOD_AUTHORITY_BENCH_V1.json` is a closed synthetic ten-case world with explicit gold for bounded method-claim promotion. Its purpose is to falsify anti-laundering semantics and security-by-total-refusal, not to establish real-world method novelty or frontier scientific value.

The frozen summary terminal is `P4_METHOD_AUTHORITY_SUPPORTED` for this closed discriminator: P4 coordinate product has zero false promotions and full clean promotion coverage; visible-success/provenance-only fail open; all-deny is broken shut.

## Authority / nonclaims

- P4 verifies bounded method claim coordinates; it does not invent methods.
- P8 owns broader cross-capability typed authority.
- P5/host owns adoption.
- real novelty still needs the current novelty route; synthetic closed-world novelty does not authorize external novelty.
- current P4 protected-V2 publication result remains unchanged.

## Verification target

Run at minimum:

```bash
pytest -q tests/test_p4_method_authority_extension.py tests/test_p4_method_authority_lineage.py tests/test_p4_method_authority_bench.py tests/test_p4_method_authority_claim_boundary.py
python papers/paper-04-verified-scientific-discovery/scripts/run_method_authority_bench.py --check
```

Then run repository CI on the PR head against the final integration base. No issue closes from prose or a local green alone.
