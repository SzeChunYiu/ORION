# ORION-24 External Pilot Protocol — V1 (FROZEN)

Status: `FROZEN`. This document, the generator, the three packet-spec modules, the
generated packet/evidence/gold files, and the pilot runner are frozen together.
After the first green CI run binds the receipt, none of these may change; any
revision requires a new version directory (`external_v2/`) and a new receipt.
The state of the paper stays `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-
CONFORMANCE_RESULT` until the gates at the end of this protocol close.

## 1. Purpose and standing

This protocol operationalises the external governance evaluation required by
`P14_EXTERNAL_GOVERNANCE_PROTOCOL_V1.md` and audited by
`check_external_contract_v1.py` (which this package must not weaken). Two things
are delivered:

1. **The protected packet suite** — 67 packets, 3 domains, 8 scientific-state
   families, ≥2 packets per family, 3 longitudinal round-pairs — generated
   deterministically (`generate_p14_external_packets_v1.py`, stdlib only, no
   clock, no network, no randomness) and validated against the repo's
   `P14_EXTERNAL_PACKET_SCHEMA_V1.json`.
2. **A wiring pilot** — a no-network, two-system end-to-end run that proves the
   decision-output contract, blinded worksheet production, gold binding, and
   metric computation, and establishes the governance-blind reference contrast.

The pilot is **not** an evaluation result. Both pilot systems are deterministic
substring procedures recorded with `authority_status=NOT_AUTHORITY`. No pilot
output may be cited as adjudication of any claim.

## 2. Partitions

| Partition | Path | Visibility |
|---|---|---|
| Agent-visible packets | `packets/p14_external_packets_v1.jsonl` | external systems |
| Agent-visible evidence | `evidence/p14_external_evidence_v1.jsonl` | external systems |
| Protected gold | `protected/p14_external_gold_v1.jsonl` | adjudication only |

Gold identity enters the agent-visible partition only as `gold_record_digest`
(sha256 of the canonical gold record). The generator's leakage guard and the
validator's leakage layer both assert that no adjudication token (`PROMOTE`,
`SUBSUMED`, `INTERACTION_ONLY`, `NULL_LIVE`, `NEGATIVE`, `NON_IDENTIFIABLE`,
`CANNOT_CHECK`, `REOPEN`, `STOP`, `NOT_AUTHORITY`, `EXTERNALLY_AUTHORIZED`),
programme name, or terminal label appears in any agent-visible byte.

## 3. Systems

- **System-A** — governance-blind reference (vulnerable baseline). Novelty-greedy
  substring procedure: positive-looking evidence ⇒ advance the claim. It performs
  no donor accounting, no negative accounting, and no abstention by design. Its
  role is to make the co-primary metrics non-degenerate: its measured
  false-novelty rate on this suite is the reference contrast.
- **System-B** — contract-level governance check. Applies fixed-priority
  obligation checks (regime-change, identifiability, missing discriminator,
  certified refutation, donor mechanism-identity, factorial marginals, parent
  separation, certificate discharge) and abstains when nothing discharges. It is
  expected to be imperfect; its confusion matrix is reported unedited.

## 4. Metrics (computed identically for every system, pilot or external)

Against the protected gold: `false_novelty_rate` (share of `PROMOTE` calls whose
gold is not `PROMOTE`), `subsumption_detection_rate`, `cannot_check_precision/
recall`, `negative_loss_rate` (gold `NEGATIVE` not answered `NEGATIVE`/`REOPEN`),
`useful_discovery_recall`, `reopen_recall`, `abstention_rate`, raw agreement,
Cohen's kappa, and the full confusion matrix. Definitions live in
`run_p14_external_pilot_v1.py::system_metrics` and must be reused verbatim by the
external-round analytics.

## 5. Co-primary promotion condition

Exactly as in `P14_EXTERNAL_GOVERNANCE_PROTOCOL_V1.md`: (i) false-novelty
reduction of the governed flow versus the governance-blind reference, and
(ii) useful-discovery non-inferiority. Both must be evaluated on **external**
systems (frontier agents under the packet contract) and confirmed by
**independent human adjudication**. Until both external rounds complete, the
analytics record `co_primary_promotion_condition.status = PENDING_EXTERNAL`.

## 6. External execution rounds (not yet run)

1. **R1 — frontier-agent round.** ≥2 external agent systems execute the 67
   packets under `allowed_tools`/`resource_budget`, seeing only the two
   agent-visible partitions. Decisions must validate against
   `P14_EXTERNAL_DECISION_SCHEMA_V1.json`.
2. **R2 — blinded human adjudication.** Independent experts (not the authors)
   adjudicate from the same worksheets; the worksheet carries no system identity
   and no gold. Adjudicator separation follows the gold-authority order in the
   governance protocol; original authors never grade their own material.
3. **R3 — longitudinal ablation.** Re-run R1 on the round-pair subset with the
   negative-history subset withheld versus present, scoring reopen accuracy and
   negative loss under the frozen metric definitions.

## 7. Hostile checks before any promotion claim

- Leakage re-scan of every artifact handed to R1 (same token set as §2).
- Decision-schema conformance of every R1 decision (fail closed).
- Determinism re-verification: regeneration into a scratch directory must be
  byte-identical to the committed suite (CI gate, §8).
- Gold-file digest chain: the worksheet and analytics embed the sha256 of the
  gold file bytes; any post-hoc gold edit invalidates every downstream artifact.

## 8. CI gate

`.github/workflows/p14-external-pilot-v1.yml` (ubuntu-latest, Python 3.11):
checkout → regenerate to a scratch directory → byte-compare the three generated
files against the committed suite → validate the committed suite → run the pilot
into a scratch directory → byte-compare pilot outputs against the committed
pilot outputs → all diffs empty ⇒ green. Any byte difference, validator failure,
or schema non-conformance fails the gate.

## 9. Receipt binding

After the first green CI run, the receipt records run id, artifact id, and
sha256 digests, and states plainly what remains open: R1–R3 have not run; no
pilot system carries authority; the paper's state does not change.
