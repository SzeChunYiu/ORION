# Davenport generalized-form publication manifest — 2026-09-05

This records the reviewed proof packet based on `eea6aeafd767773ddf095e34417b8da5345bbe21`. The full mathematical statement and remaining scope are in `GENERALIZED_SATURATED_DONOR_FORMS_20260905_V1.md`.

## 1. Commit and tree identities

Each row is one genuine proof advance or its assembly checkpoint. The local commit was reviewed first. The published Git object was then created on the corresponding published parent. In every row, the returned remote tree SHA was checked against the exact local tree SHA before creating the published commit. All sixteen tree comparisons passed.

Commit SHAs differ because publication through the authorized Git object API uses its own commit metadata. Tree identity is exact; no proof content was changed in this translation. The local history and this mapping preserve the original review identities.

| Order | Reviewed local commit | Published commit | Identical tree | Change |
|---:|---|---|---|---|
| 1 | `bd61d79bf7520d27928012a2844510f2e98037c2` | `523d1230ccd3fb600d848be92df64b86c33a5365` | `2577dd591d8dd99ffad9567133da0151b190293f` | Prove positive-even rank-two selector and complete growing overlap layers |
| 2 | `2c1f961e045be488029aba16e23bdd03ea5f894a` | `f8a03cd8c3a683a9f38343292c08e63ea1464f2c` | `551a555ee3401ac9d5b8f72a7fcbc73f195353dc` | Eliminate arbitrary-value type-two extreme rank-three rows structurally |
| 3 | `c01ffb8c57eb94bc2ed25617c4cdfb3c6196a7cf` | `e0960eaf970add3f6353a0c3db828efc594f5fc9` | `26275fe89d355dba29938f56dd9019ee816384a7` | Prove exact type-two saturated-donor inverse form for all primes at least seven |
| 4 | `8a370dd792bd5c4991567e218dcfcb3496cfafe7` | `0a5fc6b8b3cdf23b32df5db73e3de9ae3c82f2b5` | `1f74214533d2337eb422a86c908cf0c849d6a5a8` | Prove and preserve a two-parameter obstruction to all radial relation scalars |
| 5 | `7e0fc92d43059b8823f6c43a41f8083f6fb0acdb` | `f5b7ee87e19943d7239e5484011926005b3203e4` | `b23156231305ce9b63f8487be50031685a8bc73f` | Eliminate the type-two singleton endpoint by saturated maximal-atom quotient |
| 6 | `a64182e42dd4a76578b8b516077b0e17c2305e51` | `96222f7dbc02a7f0093fdd729d70e0ac4c89a6b1` | `70ba6e95b06b6f406e3a2bfef75e3ae340d7d978` | Eliminate the full type-two two-occurrence endpoint with quotient multiplicity rigidity |
| 7 | `e99984ed7d1c49353fadbf814604d17f43b6fbcd` | `53c042e8941f607eac653eb311373cd0589a8c5e` | `f942e4b4289ff8332226e0030b24b286ceb4e414` | Force saturated type-two extensions into three affine planes |
| 8 | `905b0e0ad81b8ca3c1e74afef899ea6db514872d` | `697b710d609193f177e1c02bd861f6f20e330e39` | `26492d46f9ec3df66ef8dbed966b3c4ecf2f39fc` | Reduce the general line to seven levels for large primes and all their powers |
| 9 | `b96ade3666b07bfea4e8f43ff9ed55d690b2d3a1` | `1d9818ef3cbe9a8b976ab685e5355ce2a2c8c611` | `0a74514d9b32b329625c62fe6c56abaac390e7d5` | Classify all type-one saturated extensions with the exact donor threshold |
| 10 | `68ded4ef54f3335110810569f08cbedafaee118a` | `563f0aca87abcaa89ddeaab42bfc5c79b354f415` | `14453b520bf10e4278feb9bae01816e9ee41c61f` | Prove constant-donor type-two inverse forms and both exact exceptions |
| 11 | `a3410da3fa3881210ca2296a1e3333b393ac3667` | `4bc04a8070bc725360e2c3b247ead88b5641e8ca` | `3573710836d64ecbc46121430a826e6fba72f5da` | Eliminate saturated type-two boundary overlaps by adaptive circular gaps |
| 12 | `839ac61b6fc85e64a1136c08bc64db4cf2728de8` | `b9efceacef7dafc92da17cb7ccdcf99682618a26` | `454da5faa7c48802ec852dfb377df5279bbc6dbc` | Close all saturated rank-three overlaps at least seven with a generalized remainder selector |
| 13 | `7242f68a2eb52e5dfda1fdfc0b21af7e7f1d03f2` | `f0fd113c1746a7178726c5e6a8b7d9080c6d81dc` | `36254c93aae4efc99ee5f36b51135c7bac7d04d3` | Close every saturated rank-three overlap at least four by structural remainder cases |
| 14 | `66b013518219df10135e18774f782aace5ffbb4f` | `88c04cc9d871b771e3496135e51ef7c5e67378f9` | `840990d82e8c9ebf586d6efa8de6fb5790f3bed7` | Eliminate both one-share saturated rank-three inverse families for every prime |
| 15 | `c566332d4338877b5d7c338a0d3d4051669ca65d` | `9db0636462f63e865cf81b045e450678d81b82b5` | `21b96b72a880f8ec22b024757ab56d8f9fecd227` | Close the two- and three-share saturated rank-three layers including exact exceptions |
| 16 | `d9e3f4beb727c8e2dc64ce182c670bed2804b8be` | `4793d9f42891de31ad0690de24b348b334948940` | `cdabec6b067bdfccd0566e7a2006e4a394f77911` | Assemble generalized inverse forms and complete saturated type-two boundary closure |

The proof-packet tip before this manifest is `4793d9f42891de31ad0690de24b348b334948940`. Following documentation commits add and normalize this manifest; the final branch tip includes them and is not falsely identified with the proof-packet tip.

## 2. Branch preconditions

The first and renewed all-Davenport branch audits found the same 24 heads, with live branch `shadow/davenport-c7-frontier-20260903` still at the stated base. No newer external result required absorption. A separate exact-name lookup confirmed that `shadow/davenport-general-form-20260905` did not exist before this session created it.

The session-owned continuation branch and the user-authorized live branch are to receive this additive history through non-forced updates, each preceded by a fresh remote-ref check. Main and other sessions' branches are not part of these updates. The proof packet preserves all earlier work, including the completed exceptional type-three boundary and the old failed-route records.

## 3. Verification and claims

The published content has independent internal mathematical review of all generalized classifications, both converses, exact exceptions, residue selectors, complete saturated-boundary assembly, occurrence counts, and external donor hypotheses. The final finite endpoint tables are explicit equations following symbolic reductions. No companion or prime sweep supplied theorem authority. The published rank-two donor's own bounded computer-assisted inputs are explicitly attributed in its proof note.

The Git formatting check passed for the entire additive proof packet against its base. Mathematical review is not an external referee report or a priority claim.

The new complete result is the all-prime type-two rank-three **saturated-new-value boundary**, together with the exact type-one and type-two donor inverse forms and the additional rank-two results. The full first-corridor theorem, the unsaturated rank-three boundary, and the generalized Davenport equality, including `D_3(C_7^3)`, remain unproved by this packet.
