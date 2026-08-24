# Q0_RAW rights quarantine and hash-only redaction

Exact terminal:
`P2_Q0_RAW_DECRYPTED_TEXT_QUARANTINED_HASH_ONLY_PROVENANCE`.

The two redistributed V1 trace copies had SHA-256
`10ffd34a8b3de5e3b9e45b0e309bf451ff201c2dd0c5d1837e70504959d684cd`
before redaction. Each contained 24 `Q0_RAW` query strings derived from the
decrypted benchmark. The original bytes are now held outside the redistributed
worktree in a mode-`0600` quarantine under a mode-`0700` directory. They must
not be circulated.

Both redistributed traces now omit every `Q0_RAW.query` value and retain only
the per-task SHA-256 provenance and an explicit redaction terminal. Their new
SHA-256 is
`3eaee226dfb323ad812b67b533be70041345b734e54a447fddedf9f1c2881797`.
The machine-readable mapping is
`Q0_RAW_QUARANTINE_RECEIPT_V1.json`, SHA-256
`c4a71e39d19b2f934fdb6556993fd238756f322898069be4ff87853b64b88631`.

This archival transform does not rerun or alter provider responses, candidates,
scores, gates, or the retained V1 `CANNOT_CHECK` terminal. Historical result
receipts continue to name the quarantined original trace hash; the public
redaction receives its own archival identity. Authoritative upstream permission
for plaintext redistribution remains `CANNOT_CHECK`; no plaintext
redistribution is authorized. This is a rights-conservative provenance action,
not a legal opinion.
