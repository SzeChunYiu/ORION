# Engineering substrate bound (#286)

The following tests reproduce the #136 verified-structural-transfer substrate. They are **LOCAL_ENGINEERING_ONLY**. Passing them does not establish scientific cross-domain mechanic transfer.

| File | Authority |
|---|---|
| `tests/test_verified_structural_transfer.py` | LOCAL_ENGINEERING_ONLY |
| `tests/test_transfer_v2.py` | LOCAL_ENGINEERING_ONLY |
| `tests/test_transfer_v2_assets.py` | LOCAL_ENGINEERING_ONLY |

Runtime packages `src/orion/transfer/` and `src/orion/transfer/v2/` remain engineering infrastructure / V2 future-study hooks.

`src/orion/transfer/scientific/` is the #286 freeze layer. Its toy selector/ablation tests are also LOCAL_ENGINEERING_ONLY and are not held-out scientific outcomes.
