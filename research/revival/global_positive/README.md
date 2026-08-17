# Global-positive certificate (issue #285)

This directory freezes `GlobalPositiveCertificate.v1` **before candidate outcomes**.

It is not a claim that ORION is globally positive. A single mean “global score” is not authority. Phase-4 programme operation is not authorized (`#210` depends on `#209`).

## Frozen artifacts

| File | Role |
| --- | --- |
| `CERTIFICATE_SCHEMA_V1.json` | Heterogeneous dimensions, non-compensatory admission rule, terminals |
| `PORTFOLIO_FREEZE_V1.json` | Four required family slots + optional fifth, frozen split names, UNBOUND task payloads |
| `PROTOCOL_V1.json` | Hypotheses, statistics, baselines, ablations, `outcome_accessed: false` |
| `LITERATURE_MATRIX_V1.md` | Nearest-work dispositions (`ADOPT` / `ADAPT` / `COMPOSE` / `DEFER` / `REJECT`) |
| `DEVELOPMENT_PACKET.md` | High-impact implementation packet for this fibre |

Executable admission lives in `src/orion/study/global_positive/`. It can admit a **synthetic complete** outcome bundle in tests. Against the published freeze, missing task bindings remain `CANNOT_CHECK` and block admission.

Pinned V1 content hashes (SHA-256 of canonical JSON):

- schema `b5dbcdea86814fcb7925d5003d9a8d76536839ba3683baa1ea30b32cf33bdc62`
- portfolio `8f00cf1b8d0b88df9b050243d531c20a7ca7470db135211552cb460b9f0fd5a4`
- protocol `dce1d11753b0a7da786c21e157716c9ff6815e16400de8d847089c9d9563b7cb`
- freeze fingerprint `d61712e7dfb739652b59f66e84317b6e38d008a30096d84943bc10d180ee97fc`

## Scientific terminals (issue close)

Close #285 only as one of:

- `GLOBAL_POSITIVE_SUPPORTED` — multiple prospective rounds, matched baselines beaten, `#283` receipt
- `LOCAL_ONLY`
- `OVERCONSERVATIVE`
- `REFUTED`
- `CANNOT_CHECK`

This landing does **not** close the issue as `GLOBAL_POSITIVE_SUPPORTED`.

## Remaining CANNOT_CHECK

- Real task payloads for all five family slots
- Multi-round prospective candidate outcomes
- Official continual-optimizer baseline execution
- `#283` verification of any global-positive claim
- Phase-3/Phase-4 operating authority
