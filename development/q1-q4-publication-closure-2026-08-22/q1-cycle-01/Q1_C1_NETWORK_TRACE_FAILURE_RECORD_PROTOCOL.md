# Q1-C1 network-trace failure-record protocol

- Frozen: 2026-08-23
- Parent workflow run: `32610489210`
- Parent job: `97122617045`
- Parent artifact head: `48f2f7f71807b752a11ee1b1cf355e50182ab199`
- Parent outcome: `INVALID__NETWORK_TRACE_COUNT_COULD_NOT_BE_SERIALIZED`
- Authority: none

## 1. Preserved parent result

The dedicated environment gate passed exactly with Python `3.12.13`, NumPy
`2.3.5`, cryptography `50.0.0`, cffi `2.1.1`, and pycparser `3.0`. `strace`
preflight also passed. The separated lane step then executed for approximately
four minutes forty-two seconds before Lane B rejected its own result:

```text
result schema validation failed:
$/network_control/network_syscall_count: const mismatch
```

The immutable comparison job was correctly skipped. No lane result commit,
coordinator comparison, scientific PASS, or publication authority was created.

## 2. Typed defect

The result schema requires `network_syscall_count == 0`. The Lane B parent
correctly chooses `INVALID` when traced network-class syscalls exist, but the
same nonzero count makes an `INVALID` result impossible to serialize. The
schema therefore admits only the success-side observation and discards the
evidence needed to diagnose a failure. In addition, `strace -e trace=network`
includes local-domain socket operations and negative-control activity; its raw
line count is not, by itself, an outbound-IP count.

This is an evidence-custody defect, not a scientific counterexample and not a
reason to weaken the no-egress gate.

## 3. Prospective child contract

A strict descendant implementation may make only the following changes before
the next execution:

1. `network_syscall_count` becomes a nonnegative observed integer rather than a
   success-only constant.
2. Every lane result records the raw trace digest and preserves the complete raw
   trace whether the terminal is `PASS`, `INVALID`, `BLOCKED`, or
   `COUNTEREXAMPLE`.
3. The coordinator continues to forbid release when the observed count is
   nonzero. This child is diagnostic: it does not pre-authorize any syscall or
   endpoint.
4. Lane bytes are committed before comparison even when a lane terminal is not
   `PASS`.
5. A coordinator terminal, if produced, and the complete result tree are
   committed/uploaded under `always()` semantics even when the release
   assertions fail.
6. The next run is not a rerun of the parent. It is a new diagnostic child whose
   purpose is to expose and preserve the exact trace lines. Any later allowance
   or classification rule requires another protocol frozen after those trace
   lines are observed.

## 4. Precedence and release

- A scientifically valid counterexample remains `COUNTEREXAMPLE`.
- A nonzero traced network-class syscall count remains `INVALID` in this child.
- Schema validation must accept and preserve that `INVALID` record.
- Only zero traced network-class syscalls, exact dependencies, repeat equality,
  and all other frozen checks may reach `PASS`.
- No result grants novelty, manuscript-quality, submission, merge, or
  publication authority.

The parent failure is retained as a useful structure: it identifies that a
fail-closed trace gate must also be failure-recording.
