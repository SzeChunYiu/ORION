# P7 local replay V3

This route reproduces the eight-case **reference-policy preflight** and bounded
formal checks. It does not execute a navigation agent and is not independent
replication.

Environment lock:

- `uv.lock`
- SHA-256 `4e0f595c568cf7cfdf15bb88518ad2fc5951a1cf9f03bb3c4b307471f852dade`
- install: `uv sync --frozen --extra dev --extra proofs`

From the repository root:

```bash
make -C papers/paper-07-epistemic-navigation-open-worlds reproduce-v3
```

The generated trace binds eight authored cases and eight evaluated decision
opportunities. Repeated traces or policy reruns do not increase the independent
unit count. A successful command licenses only `LOCAL_REFERENCE_REPLAY_MATCH`;
naturalistic evaluation and independent custody remain separate gates.
