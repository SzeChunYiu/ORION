# Development packet — issue #210 remaining preparatory freeze

Status: **PREPARATORY_AWAITING_ACTIVATION.** This packet and the modules it
describes close no gate, grant no authority, activate no workflow, and do not
authorize a self-sustaining research programme. Issue #210 remains blocked on
issue #209 (Phase-3 closure), which remains blocked on issue #76.

## Development question

PR #268 landed protocol prose and accidentally-live GitHub Actions templates.
PR #276 pre-registers the K/W/M schemas, dependency/reopening model, and
anti-collapse battery. Steps 3, 4, 6 and 7 of #210 still had no machine-readable
record shapes. The question is: what can be authored now that is a genuine
pre-registration of those shapes, and how is it kept inert while #209 is open?

Authoring receipt *results* or epoch *data* would be fabrication. Authoring
receipt *shapes*, an unbound governance freeze, and a workflow-activation lock
is the remaining preparatory work.

## Atomic fibres

1. relocate the `#268` `p4-*.template.yml` files out of `.github/workflows/` so
   GitHub cannot treat them as live workflows;
2. freeze programme governance policy as an unbound, sealed document;
3. freeze the nine-step cycle protocol and a per-cycle receipt shape that
   refuses `PASS` without bound replay/fresh-transfer/assurance hashes;
4. freeze the epoch-manifest shape and refuse populated/frozen live epochs;
5. freeze the eight longitudinal claims as `CANNOT_CHECK` with zero epochs;
6. freeze programme-receipt and archival-strategy shapes with an empty archive;
7. make regeneration of trajectories return `CANNOT_CHECK` rather than invent;
8. keep every `grants_*` property and `activation_authorized()` hardwired `False`.

## Incumbent mechanics and negative history

- `orion.programme` from PR #276 — sealing, three-valued `Outcome`, withheld
  terminal marker, fail-closed hostile battery. This packet adds sibling modules
  in the same package and does not edit `#276`'s `__init__` or identity registry.
- `orion.self_orion.phase3_preflight` — unbound SHA-256 sentinel and hardwired
  `grants_*`. The sentinel is duplicated rather than imported so programme code
  does not take a Self-ORION dependency.
- Negative history: `.github/workflows/p4-*.template.yml` registered as **active**
  GitHub Actions workflows and failed on every push. A `.template.yml` suffix is
  still `.yml`. Templates now live under `research/phase-4-protocol/workflows/`
  with a `.yml.template` suffix.

## Saturation assessment

Saturated when: every Step-3 policy field is present and unbound; the nine cycle
steps are listed by identity; a `PASS` receipt without bound hashes is refused;
longitudinal assessment cannot return `PASS`; no live programme workflow remains
under `.github/workflows/`; `src/phase4/` does not exist.

## Challenge to the saturation basis

A preparatory freeze can still fail by (1) leaving a live workflow in Actions,
(2) emitting a fabricated PASS/epoch, (3) granting authority via a defaulted
boolean, or (4) writing a runner tree the templates could invoke. Each has a
test.

## Reopen triggers

- Issue #209 closes with independent Phase-3 evidence.
- An external host explicitly authorizes programme operation on #210.
- A live `p4-programme*` / `p4-epoch-manifest*` / `p4-anti-collapse*` YAML
  reappears under `.github/workflows/`.

## Frozen implementation hypothesis

Additive modules under `src/orion/programme/` plus relocated inert templates.
No live workflow, no `src/phase4/` runners, no tick of execution/evidence boxes,
no `PHASE_4_SELF_SUSTAINING_RESEARCH_PROGRAM_CLOSED`.
