# Apply and integration

This directory is designed to be committed as one additive top-level tree whose parent is
`b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8`.

The companion delivery contains:

- a thin Git object pack with the exact packet blobs, trees and commit;
- an installation script that verifies the target repository already has the parent;
- a unified add-file patch; and
- commit metadata.

The intended branch is `shadow/issue1701-descending-closure-20260829`. Integration is by pull request, never by writing
directly to `main`.

Before opening a pull request, run:

```bash
python ISSUE_1701_DESCENDING_25_20_V1/check_descending_closure.py
python -m unittest -v ISSUE_1701_DESCENDING_25_20_V1/test_check_descending_closure.py
git status --short
```
