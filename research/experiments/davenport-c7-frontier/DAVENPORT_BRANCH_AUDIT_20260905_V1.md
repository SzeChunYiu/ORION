# Davenport remote branch audit — 2026-09-05 V1

Comparison base: `86f089ab63ba90f7df292cd44d5a46c7527014ce`. All 23 remote branch heads were freshly resolved before mathematical work and rechecked after the first six proof commits; the two remote listings were identical. The private continuation is `shadow/davenport-boundary-20260905`.

## Complete discovered branch census

Counts below are commit ancestry, not theorem-strength scores. “Base-only” and “branch-only” mean the two sides of `base...branch`.

| Branch | Head | Base-only | Branch-only |
|---|---|---|---|
| `shadow/c7-davenport-frontier-20260903-sol` | `0b38852dddd3bf567064bf4e4bf9def646995cee` | 223 | 10 |
| `shadow/davenport-a1-c2-elimination-20260904` | `2fd9bd97628b97fca5d443343d9a8689025f80d0` | 129 | 5 |
| `shadow/davenport-a1-c2-hostile-audit-20260904` | `f70f6033793480bba6f128e3ec8fe72f56a9b7cb` | 128 | 3 |
| `shadow/davenport-a1-c4-orion-20260904` | `35961d63808827377771032ba5ee0f3110058716` | 106 | 3 |
| `shadow/davenport-a2-light-c12-elimination-20260904` | `59f1246e71f2727776f44774126183afdd62c0ae` | 117 | 0 |
| `shadow/davenport-c7-frontier-20260903` | `86f089ab63ba90f7df292cd44d5a46c7527014ce` | 0 | 0 |
| `shadow/davenport-paper2-a2-radial-20260904` | `e4d92bd6b6b18fc5db8d46f744930a80cc31bb49` | 56 | 0 |
| `shadow/davenport-paper2-a3-shared-donor-20260904` | `86f089ab63ba90f7df292cd44d5a46c7527014ce` | 0 | 0 |
| `shadow/davenport-paper2-breakthrough-a2-20260904` | `6be5e754005317f9389d677065572a0ce26743e9` | 4 | 0 |
| `shadow/davenport-paper2-circular-gap-20260904` | `6e5648314fcb74dddf3da019b1bab707578743c5` | 1 | 0 |
| `shadow/davenport-paper2-integration-20260904` | `86f089ab63ba90f7df292cd44d5a46c7527014ce` | 0 | 0 |
| `shadow/davenport-paper2-integration-20260904-leftsafe` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-integration-20260904-leftsafe-final` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-integration-20260904-leftsafe2` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-integration-20260904-leftsafe3` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-integration-20260904-leftsafe4` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-integration-20260904-leftsafe5` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-integration-20260904-leftsafe6` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-left-a3-final-20260904` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-left-a3-final2-20260904` | `5929b4578be54cd399adb65119a7105eb8cc01a9` | 61 | 0 |
| `shadow/davenport-paper2-left-a3-final3-20260904` | `a884877ca181bfbd66c31c0baef75039392c270d` | 58 | 0 |
| `shadow/davenport-paper2-rank3-plane-20260904` | `d1348de8d7a0612d08644944c8d9556b09e39e45` | 58 | 2 |
| `shadow/davenport-paper2-shared-donor-20260904` | `c036ce05619206ef0d7d4ec9b9452d2f3bbe399e` | 3 | 0 |

## Reconciliation of nonancestral histories

- The live frontier, main Paper-2 integration, and a3-shared-donor branches all pointed to the starting commit. The later circular-gap, shared-donor, radial, and left-a3 results were already ancestors of that commit.
- The rank3-plane branch has two nonancestral commit identities but no patch-unique commits under a cherry comparison; its exact overlap-plane theorem and checker are byte-identical at the live baseline.
- The a1-c4 branch has nonancestral merge history, but the theorem differs only in an older status sentence: it reports a2 layers c<=3 while the live baseline correctly includes c=4. No stronger new proof was present there.
- The a1-c2 and hostile-audit branches retain alternative earlier proof/checker histories. Their theorem subject is the c=2 slice already settled in the live branch; the live baseline carries the later theorem and audit refinements. Their files and commit differences were inspected, and none of their history was overwritten.
- The c7-davenport-frontier-sol branch contains separate bounded B7/B43 neighborhood results and harness/CI registration. These are preserved as a separate computational lane and do not supply or supersede the prime-uniform exceptional boundary proofs developed here. No bounded-neighborhood claim is promoted to a full Davenport value.

## Isolation and claim boundaries

The existing shared checkout was inspected read-only. A separate checkout was created for this session, and branch identity was checked before each commit. The baseline mathematical files were not rewritten; all theorem advances, failed routes, and this checkpoint are additive.

The connected-source search and direct ref census found no newer Davenport head beyond the supplied live commit. This is an audit of the accessible remote branches, not a claim to see unpushed work on another machine. Any future continuation must refresh the remote census again before integrating.
