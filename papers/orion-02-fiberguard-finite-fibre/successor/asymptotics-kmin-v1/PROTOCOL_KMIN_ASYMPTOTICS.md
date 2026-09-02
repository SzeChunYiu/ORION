# PROTOCOL — profile-Kmin asymptotics V1 (asymptotics-kmin-v1)

## Aim

Replace two hard limits of the frozen C2–C10 certification harness
(`../verify_c2c10_profile.py`, 10/10 certified) — float precision
(`G > 2^53` for `m ≳ 51`) and partition-enumeration cost (`m = 66` exceeded a
10-minute timeout) — with an exact integer DP, and settle the asymptotic law
of the profile-Kmin `Kmin(m, 1)` across dyadic bands of `m`.

## Disclosure (pre-registration honesty)

The DP design and the validation gate were fixed against the frozen harness
(match at `m = 5..16`, plus exact agreement with the frozen harness's own
ad-hoc outputs at `m ∈ {41,42,44,48,63,64,65}` recorded in the parent study)
BEFORE any `m ≥ 66` value existed. A pilot sweep `m = 66..140` was launched
before this protocol file was committed; the discriminating prediction P2 was
authored in `DERIVATION_KMIN_ASYMPTOTICS.md` BEFORE the pilot output was read
(file write precedes first read; both timestamps in git). No gate or constant
was tuned after reading any `m ≥ 66` output. The registered outcome run below
re-executes the entire table fresh.

## Registered outcome run (single pass, exit 0 = complete)

1. **P1 (gated):** `kmin_asymptotics_v1.py validate 5 48` — DP must equal the
   frozen float harness exactly (integer equality of `floor(G/(2k-1))+1`) for
   every `m = 5..48`. Any mismatch → abort, terminal `KMIN_ASYM_VALIDATE_FAIL`
   (exit 3), no law claims.
2. **Table:** `kmin_asymptotics_v1.py law 49 140` — exact `Kmin(m,1)`, the
   realizing profile, `γ*(m) = Kmin/2^(m-2)`, `b(m)`, `γ*/2^b(m)`.
3. **Law checks (registered):**
   - **P2 (discriminating):** `γ*(129) ∈ (14, 20)` and closer to `2^(b(129)-4)
     = 16` than to `4·b(129) - 20 = 12` — decides exponential-in-`b` vs
     linear-in-`b` for the band jump. Authored pre-read (see disclosure).
   - **L1 (band jump):** `γ*(129)/γ*(128) ∈ (1.5, 2.2)`.
   - **L2 (band interior):** for all `m ∈ [65, 128]`: `γ*(m) ∈ 2^(b-4)·(1,
     1.35]`; for all `m ∈ [129, 140]`: `γ*(m) ∈ 2^(b-4)·(1, 1.35]`.
   - **L3 (profile family):** every argmax profile for `m ≥ 65` has maximum
     block size in `{2^(b(m)-3), 2^(b(m)-2)}` and anchor size `≤ 2^(b(m)-3)`.
   - **L4 (ε envelope):** `ε(m) = γ*(m)/2^(b(m)-4) - 1 ∈ [0, 0.25]` for all
     `m ∈ [49, 140]`.
4. Output artifacts: `RESULTS_KMIN_ASYMPTOTICS_V1.json` (validation verdicts,
   full table, law-check verdicts), `RUN_validate_5_48.log`, `RUN_law_49_140.log`,
   `SHA256SUMS`, `FINDINGS_KMIN_ASYNPTOTICS_V1.md`.

Terminal `KMIN_ASYM_DETERMINED` (exit 0) requires P1 pass + all of P2, L1–L4
evaluated and reported (each PASS/FAIL recorded; L-check failures do not abort
— they falsify the conjecture and are reported as such, terminal
`KMIN_ASYM_LAW_REFUTED` exit 1 if P2 or ≥2 of L1–L4 fail).

## Discipline

No fitted parameter anywhere; the DP is the frozen harness's exact arithmetic
(integer form of `block_term`/`profile_cost`/`kmin_profile`). The parent
package is untouched; this successor is additive. L > 1 is out of scope
(`Kmin(m,L) = L·Kmin(m,1) + O(m)` up to floor effects — recorded as open).
The `O(B)` constants in the derivation's pinch are proven in the findings note
only for the construction side; the Jensen upper-bound side is stated with
its proof sketch and verified numerically against the exact table.
