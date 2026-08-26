# Preserved small-world build (NOT part of the frozen offline_gold suite)

`tasks.json` and `world.json` here are the preserved branch-side small-world
corpus build (20 tasks / 100 documents, seed 20260816) recovered by the
branch-forest preservation sweep (#1002, commit `1f545b8d`) from an un-PR'd
`paper-02` branch. They are a different, earlier build than the frozen
390-task / 1210-document sharded corpus recorded in
`../offline_gold/MANIFEST.json` and must not be placed inside that frozen
directory: the offline-gold frozen-suite verification fails on any file
present but not recorded in the manifest.

Moved here (originally restored to their branch-side paths inside
`offline_gold/`) to keep both the preserved bytes and the frozen archive
exact. No scientific content changed.
