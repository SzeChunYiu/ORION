# What issue #1701's checkboxes actually track

**Count at the time of writing: 177 unchecked, 123 checked.**

The unchecked boxes are **scientific execution tasks**, not publication packaging. This matters because publication work — author blocks, venue metadata, internal-label removal, submission packages — moves none of them, and checking one for packaging work would falsely mark a science task complete.

## Evidence

Leading verbs across the 177 unchecked items:

```
11 Use      11 Freeze    7 Require    6 If       5 Reconcile
 5 Finish    5 Finalize   5 Do         5 Close
```

The 11 `Freeze` items are the clearest case. Every one is a **pre-registration freeze** — protocol discipline before outcomes are seen:

- *Freeze item IDs, evidence snapshot, both instrument outputs, score rule and stopping rule now.*
- *Freeze obstruction basis and a deterministic `n=5` challenge before any n=5 exact labels.*
- *Freeze 3 model families from E16 by exact model revision SHA before scoring packets.*
- *Freeze exact commits/tool versions/feature config/change selection/baselines.*

None is a publication freeze. A keyword sweep for packaging terms returns 28 apparent hits, but they are false positives — `metadata` in *"Gold must come from each native verifier/metadata semantics"* is schema semantics, not submission metadata.

Only three unchecked items name a paper and a deliverable:

- ORION-17: recover/audit the 5/5 prospective density result; resolve governance; write standalone manuscript.
- ORION-09: integrate four-feature separator result and correct stale abstract.
- ORION-16: complete real authoritative graph campaign.

Each requires new science, not packaging.

## Consequence

Two independent axes are being conflated:

| axis | tracked by | current state |
|---|---|---|
| scientific execution | #1701 checkboxes | 123/300 |
| publication readiness | freeze ledgers, package guards | separate |

Progress on one will not show on the other. Reporting publication work as #1701 progress would misrepresent both. The box count should be expected to stay flat during packaging passes, and that is correct behaviour rather than a stall.
