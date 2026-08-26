# P6 local replay V3

This route reproduces the bounded local formal instrument. It is **local
replay**, not independent replication, empirical lifting, or external custody.

Environment lock:

- `uv.lock`
- SHA-256 `4e0f595c568cf7cfdf15bb88518ad2fc5951a1cf9f03bb3c4b307471f852dade`
- install: `uv sync --frozen --extra dev --extra proofs`

From the repository root:

```bash
make -C papers/paper-06-formal-epistemic-structures-and-mechanics reproduce-v3
```

The command validates the versioned schema and generator, binds the append-only
negative/null registry, and runs the V2/V2.1 assumption, theorem and refutation
checks, including the bounded SMT certificate-lifting obligation. A successful
command licenses only `LOCAL_REPLAY_MATCH`. It does not
satisfy `independent_replay_attestation`.
