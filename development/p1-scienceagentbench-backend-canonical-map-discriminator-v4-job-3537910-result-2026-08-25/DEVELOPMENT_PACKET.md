# Paper 1 V4 body-free job 3537910 result and GPU residual packet

## Status and immutable outcome

This packet preserves the one authorized body-free discriminator job executed
from merged commit `8e84ae99af5122ce6f8e641955e196c27aed07c8`.
Job `3537910` is `FAILED`, exit `1:0`, elapsed 86 seconds on `cg14`, with one
allocated A40 GRES. The exact terminal is:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK failure_code=GPU_IDENTITY_INVALID detail_sha256=a31dfb1a2c932320ecf692f380dfd8aca87a7afb107026347fed63e2c4a490c4
```

The live receipt is a truthful `CANNOT_CHECK`, not a discriminator PASS. It
opens no protected body and invokes no tokenize, completion, generation,
evaluator, or outcome operation. Its cleanup proves the owned server process
and process group absent.

## Positive first-attestation witness

The receipt completed these live stages:

```text
CONTRACT_BOUND
RUNTIME_FILES_BOUND
SERVER_STARTED
SERVER_READY_BODY_FREE
CANONICAL_MAP_ATTESTATION_1
SERVER_CLEANUP_PASS
```

Under the merged code semantics, `CANONICAL_MAP_ATTESTATION_1` is a fresh,
body-free witness that the exact live server executable, argv, allowlisted
environment, loopback listener, and the frozen server/backend/model map
identities passed their first attestation. Each mapping used only its frozen
logical/canonical path set with matching device/inode identity. The receipt
does not retain the attestation object or observed segments, so this is a
code-semantic stage witness, not a field-level reconstruction and not a causal
repair or promotion of failed predecessor job `3537893`.

## Atomic development questions

1. Does the retained outer failure-detail hash match any static
   `GPU_IDENTITY_INVALID` detail in the executed core?
2. If not, which dynamic branches remain possible, and what can be concluded
   without guessing an unretained diagnostic body?
3. What semantic delta separates the V4 GPU capture from the prior direct-route
   capture that passed before job `3537893` reached its later backend gate?
4. What is the smallest successor that retains enough body-free evidence to
   discriminate the residual without weakening singular-A40 checks?
5. Which positive mapping claim survives the later GPU CANNOT_CHECK, and which
   second-attestation/final-rebind claims remain forbidden?

## Failure classification

`classify_gpu_identity_failure_v1.py` binds the executed V4 core by SHA-256,
enumerates every static `GPU_IDENTITY_INVALID` detail from its AST, and checks
their exact outer hashes. None matches the retained `a31df...` hash. It also
checks the nonzero-return branch with an empty stderr hash; that candidate does
not match. The executed branch therefore necessarily incorporated a nonempty
`nvidia-smi` stderr hash. The retained double hash cannot distinguish:

- nonzero `nvidia-smi` return with nonempty stderr; or
- zero return with nonempty stderr. In this branch V4 failed before decoding or
  parsing stdout, so stdout content and validity remain `CANNOT_CHECK`.

The prior direct-route capture used the same query and filtered environment and
failed on nonzero return, but did not reject a successful command solely for
nonempty stderr. Job `3537893` on the same node passed that earlier GPU stage
before its later backend-map gate. That history makes the zero-return branch a
useful successor test fixture, but it does not rank the two live alternatives:
return-code class remains `CANNOT_CHECK`.

## Saturation, challenge, and false-flat risks

The offline control-flow classification is saturated over the exact executed
core and retained outer hash: all static details are enumerated, and the two
dynamic stderr-dependent templates are explicit. It is not saturated over the
unretained `nvidia-smi` return code or stream bodies.

The strongest challenge is a transient NVML/driver failure with nonzero return,
not benign stderr. That alternative remains live. Treating the prior job's GPU
success as proof for job `3537910` would be a context substitution and is
forbidden. Treating the first map attestation as the full V4 result would omit
the uncompleted GPU, second-attestation, final hash/custody, and listener gates.

Reopen if the executed core hash, receipt hash, terminal bytes, or AST branch
set differs; if retained return-code or stream evidence refines the branch; or
if a full successor fails before reproducing the first mapping witness.

## Frozen successor hypothesis

The smallest V5 GPU-capture correction must keep the exact absolute
`nvidia-smi` argv, filtered environment, timeout, singular row/UUID/name gates,
and all zero protected/generative boundaries. It must additionally retain:

- return code;
- stdout `{bytes, sha256}`;
- stderr `{bytes, sha256}`;
- a typed outcome subcode for nonzero return and zero-return/nonempty-stderr.

The smallest truth-preserving V5 keeps both dynamic cases fail-closed: nonzero
return is a typed CANNOT_CHECK, and zero-return/nonempty-stderr is a distinct
typed CANNOT_CHECK. Only zero return with empty stderr proceeds to the same
exact one-row `NVIDIA A40` parser. Synthetic tests must also show that malformed
stdout is never described as parseable merely because stderr is nonempty.

Treating a valid zero-return one-A40 result with nonempty stderr as PASS is a
separate policy change, not a conclusion from job `3537910`. If later justified,
that policy must retain the nonempty stderr byte/hash binding in the PASS
receipt and must not claim stderr cleanliness.

A future full body-free V5 run still needs fresh roots and separate owner
authorization to reproduce both mapping attestations and the final rebind. No
in-place retry and no protected execution are authorized by this result packet.

## Accounting

- Prior protected scheduler cost: 90 GPU-seconds.
- Job `3537910` body-free scheduler cost: 86 GPU-seconds.
- Combined scheduler cost if reported: 176 GPU-seconds, explicitly separated
  as `90 protected + 86 body-free`.
- Protected infrastructure submissions remain three.
- Protected generation attempts remain zero.
- Job `3537910` is one body-free discriminator submission, not protected
  infrastructure ordinal four, not generation ordinal one, and not a hidden
  sample.
