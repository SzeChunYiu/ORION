# Receipt V3 strict-deadline P1 development packet

## Frozen question

Can the prospectively frozen 120-test strict absolute-deadline protocol be
migrated into Process Receipt V3 while preserving the byte-identical legacy
dialect and the already-green current hostile frontier?

This packet implements `V1-RECEIPT-V3-DEADLINE-P1-01` from source commit
`ed6aa96485e583fdf47fc483d92702e8928c6a2c` and source tree
`1fc4b2bc647c60f21ef8def2ed6647fa9d8fb081`. The oracle is the immutable Git
blob `55b3399b3c732a4b8303799be28ffef2439f0e5b`, SHA-256
`103c3678e34ea33b7657bec911c8d604b97196bdbf56df40df3f4d2ab8cc051d`.

## Atomic obligations

1. Keep the first three `ChildIdentityBound` positional fields and legacy
   payload bytes unchanged; add an all-or-none strict child occurrence binding.
2. Derive strict versus legacy operation from closed subject, invocation, and
   trace coordinates. Reject cross-dialect relabeling and unbound strict
   results.
3. Make `DeadlineBinding` the process-start PRE observation and
   `ProcessStartCompletion` mandatory POST knowledge for both success and
   failure.
4. Bind every strict external MAIN effect into a contiguous admission,
   attempt/result, completion transaction with global ordinals and exact event
   chain coordinates.
5. Recompute selector timeout float64 bits from remaining integer nanoseconds;
   reject one-ULP, original-timeout, non-finite, negative, and visible-EINTR
   substitutions.
6. Make deadline crossing irreversible while retaining the completed attempt,
   its charged observations, primary failure ordering, and independent FINALIZE
   reserve.
7. Preserve the legacy reducer/replay identities, event hashes, receipt hashes,
   work denominators, failures, and adverse evidence.

## Incumbent and donor reconstruction

- The incumbent module already supplied checked deadline binding/refusal types,
  strict invocation coordinates, effect admission/completion types, and the
  frozen P0 reducer. It did not yet connect these values into a strict
  transaction reducer.
- The archived oracle is treated as a prospective specification, not as an
  editable test donor. No assertion, cap, timeout, retry rule, or denominator is
  changed.
- The current 113-node Linux hostile receipt is the compatibility donor. The
  Darwin capture environment exposes one additional platform option node and
  different `EINPROGRESS` parameter IDs; those are retained and reported rather
  than hidden.

## Negative history and initial RED

The exact oracle initially produced `42 passed, 78 failed`. Visible roots were:

- 68 child-occurrence and effect-binding failures;
- 8 strict/legacy dialect-separation failures;
- 1 strict-to-legacy relink diagnostic failure;
- 1 failed-spawn deadline-crossing knowledge failure.

After strict coordinates and factories were added, the RED reduced to
`61 passed, 59 failed`; after transaction validation it reduced to
`119 passed, 1 failed`. The last failure established that bytes returned before
a crossing POST observation remain acquired and retained, while canonical EOF
authority is censored. The implementation preserves that distinction.

## Frozen implementation hypothesis

A dual-dialect value algebra plus a pure strict-trace validation pass is
sufficient. Context-free dataclass construction validates intrinsic fields;
the reducer rederives contextual chain, invocation, child, deadline, ordinal,
and effect coordinates. The incumbent reducer then retains its legacy state
machine and work accounting, with narrow strict transaction adaptations.

No host clock is read during reduction, build, or verification. Capture-time
factories only consume supplied observations. No paper, LUNARC, custody,
finalizer, or immutable-OID surface is in scope.

## Saturation assessment and reopen triggers

The implementation is saturated only against the immutable 120-node oracle and
the frozen current hostile frontier. Reopen immediately if any of the following
occurs:

- a legacy hash or serialization byte changes;
- Linux collects other than 73 + 17 + 23 + 120 unique nodes;
- a constructor or reducer consults an ambient clock;
- a strict effect can omit, reuse, relink, or reorder PRE/attempt/result/POST;
- a crossed completion authorizes later MAIN work or suppresses prior adverse
  knowledge;
- a fresh independent reproduction disagrees.

## Authority ceiling

This is local process-receipt conformance engineering. It grants no scientific
authority, paper authority, novelty, independent reproduction, full dual-lane
execution, ORION V1 freeze, or publication readiness. Those remain `OPEN` or
`CANNOT_CHECK` as applicable; `paper_authority_delta=NONE`.
