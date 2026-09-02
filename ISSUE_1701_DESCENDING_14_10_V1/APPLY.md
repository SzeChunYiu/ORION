# Apply and integration instructions

Use the delivery installer against a clone that contains live-main commit
`b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8`. The installer updates only
`refs/heads/shadow/issue1701-descending-closure-20260829` after verifying the
three exact commit parents and trees.

After installing this audit commit:

1. replay the native checkers on the exact ORION-14/13/10 branch heads;
2. recover only the listed additive directories path-by-path;
3. re-run repository tests and paper-local checksum/freeze checks;
4. rebuild ORION-14 and ORION-12 packages from the resulting live source tree;
5. keep ORION-11 untouched unless a concrete live-main defect is found.

Do not cherry-pick the diverged closeout branches wholesale. Do not use their old
PDF/archive hashes as live-main filing identities.
