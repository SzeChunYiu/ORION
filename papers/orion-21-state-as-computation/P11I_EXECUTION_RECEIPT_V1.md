# P11I Execution Receipt V1

**Protocol freeze commit:** `4c769ae7`
**Protocol:** `P11I_WIDE_HIGH_WIDTH_REPLICATION_PROTOCOL_V1.md`
**Result:** `P11I_WIDE_HIGH_WIDTH_REPLICATION_RESULT_V1.json`
**Terminal:** `P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL`

## Order and environment

The protocol, seeds, complete factorial, unit of analysis, thresholds, arms and
non-compensatory rule were committed before any P11I scientific execution.
An initial project-venv launch stopped while importing NumPy and accessed no
outcome. The unchanged committed runner then executed with Python 3.12.13,
NumPy 2.3.5 and scikit-learn 1.8.0.

## Panel

- three fresh frozen seeds;
- three complete parity-bank geometries: 91, 364 and 969 columns;
- matched state widths `r=3` and `r=7` in every seed/geometry pair;
- nine independent high-width units and nine matched low-width controls;
- five repeated protected queries inside each cell;
- the same L1, L2 and ExtraTrees best-of-arms universal attack as P11H.

All nine high-width units passed every gate without averaging across units:

| statistic across nine units | observed range | frozen gate |
|---|---:|---:|
| compiled accuracy at `n=64` | 0.9690–0.9981 | `>=0.95` |
| pooled best accuracy below `n=256` | 0.8489–0.9421 | `<0.95` |
| compiled minus pooled at `n=64` | +0.2463–+0.3543 | `>=+0.20` |

The pooled attack scored 1.0000 in every matched `r=3` control, so the positive
high-width result does not come from a dead attack. Answer-laundering checks were
zero throughout.

## Replay and binding

Two fresh Python subprocesses produced byte-identical canonical scientific
payloads with SHA-256
`b50ace30aec14a2885444989a1f33c02a1be7fdc2f798697728bd46e2b8ee0ce`.
The authoritative result file SHA-256 is
`adb473201618c6ab9bf15d9f8ee134fade1e49bb2ff3acfbbd56f2fb37f03aff`.

## Claim boundary

P11I supports replication of the pooled-attack survival claim only in the
registered `r=7` controlled regime. It does not relabel P11D or P11H, and it
does not support an unconditional or real-system superiority claim.
