# P8 local replay V3

This route reproduces the 17-case reference-policy preflight and the five
registered laundering-attack opportunities. It is local replay: labels are not
protected from this repository, the evaluator is not independent, and no
deployed agent is measured.

Environment lock:

- `uv.lock`
- SHA-256 `4e0f595c568cf7cfdf15bb88518ad2fc5951a1cf9f03bb3c4b307471f852dade`
- install: `uv sync --frozen --extra dev --extra proofs`

From the repository root:

```bash
make -C papers/paper-08-epistemic-authority-autonomous-science reproduce-v3
```

The attack receipt must report five registered, five evaluated, and five
blocked opportunities. Zero opportunities can never be called a pass. A
successful command licenses only `LOCAL_REFERENCE_REPLAY_MATCH`; protected
label custody, independently authored attacks, and deployed-agent authority
remain unresolved.
