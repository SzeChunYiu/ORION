# First-principles Davenport publication receipt — 2026-09-05

Base: `a7ab107f76b99ceb7fda0c6a8285527d36be87ca`. The live target is `shadow/davenport-c7-frontier-20260903`; the isolated continuation is `shadow/davenport-first-principles-20260905`.

The six reviewed commits below were reproduced as GitHub Git objects. Each returned remote tree was required to equal the reviewed local tree before its commit object was created. Commit metadata differs, so commit SHAs differ. This table preserves the exact mapping.

| Advance | Reviewed local commit | Publication commit | Identical tree |
|---|---|---|---|
| Prove minimal defect contraction and joint compatibility laws | `7a47e5d53230fdeddd9fcb57b31abf0bb7684ae5` | `444db5d9e2868b8874bae36b74c3468e5dbb940b` | `3589b5f43a2e2fa4a9bdd5395463c343b546b239` |
| Prove block insertion and simultaneous atomic excess budgets | `a862e81e45f0a8ebc58beccdff98440ca30d8559` | `e9e0f1297986c55380c529d9f00b6e1ac92bd9ed` | `f3f53d548caad6c2187125c60977a7b5dcab4abc` |
| Derive exact quotient atomization and kernel carry formula | `4aa61ec523cc958319c61181950df2ee4d2fd5fc` | `33f355713bc26fbff3bb79f3ab06e1c78a7390c8` | `7f175cd7de1b7d59a8c2e66b0217de7799ea4f06` |
| Reduce the global affine bound to splitting exact boundary blocks | `bab4736ba141be6abb3682f3a17bb51a32b00d2b` | `6500c94ac476dec823d5f8e8cf56addcf7f0e11e` | `5e423e894c629916bde06db26ff5710a570a0b29` |
| Eliminate the entire type-two rank-two penultimate overlap by quotient atomization | `2a68482cc58ba9a9939036208d901444fa340c35` | `01504589499d87644aa5d08837839c2f4dc291c0` | `3f435014ab82cfb29cc6d3341fa39f26c535e3e1` |
| Record first-principles checkpoint and remaining global proof gates | `93c745c3f0987701a860a7f0c5062d000ac890d4` | `17765ed0ba4a1eb9e6c89ffc946dd509ec90c7f3` | `a015598c06b4d3965af246f094a370f951c154ba` |

The publication head before this receipt is `17765ed0ba4a1eb9e6c89ffc946dd509ec90c7f3`, tree `a015598c06b4d3965af246f094a370f951c154ba`. This receipt is a subsequent documentation commit; it does not modify any theorem.

Five entries are proof advances; the sixth is the scientific checkpoint. The penultimate-overlap theorem closes the whole rank-two type-two `c=H-1` layer. The other proofs give general contraction, insertion, quotient and splitting reductions. None claims the full first corridor or a value of `D_3(C_7^3)`.

Before publication, all 25 remote Davenport branch heads were checked again and remained unchanged. Live-ref advancement is permitted only from the expected base and only as a non-forced fast-forward. The original-metadata local history is retained on the continuation/review branch; the published history is fetched and compared by both commit and tree identity.

Validation: mathematical proof review and primary donor checks are recorded in the theorem notes; `git diff --check` passed on all six reviewed commits. No brute-force realization search was used.
