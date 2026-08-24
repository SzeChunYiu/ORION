# P13+P14 live-Git acquisition runner freeze

## Atomic question

Can an AI session re-observe every license-eligible pinned repository through
live Git, retain fail-closed command receipts, and derive only object, direct
parent, recorded timestamp and license-blob facts without creating a campaign
result or semantic authority?

## Donors and conflict boundary

The frozen 45-repository corpus contains 31 license-eligible entries across 14
organizations. The separate 30-repository pilot adds stricter relational
metadata, but neither artifact has executed a live Git acquisition. This runner
uses the 45-repository corpus because its objective-gold contract explicitly
binds that corpus. It does not merge the two populations or count them as
replications.

## Frozen implementation hypothesis

For each of the 31 eligible entries, a depth-two, no-tag fetch of the exact
40-hex pinned commit should permit the runner to verify commit-object existence,
observe all direct parents, record the committer epoch, extract the license path
named by the frozen evidence URL, and compare the license bytes to the frozen
SHA-256. Each command retains argv, exit code and stdout/stderr digests. A fetch,
parse, object-access or digest-computation failure yields `CANNOT_CHECK`. A
license digest that is successfully computed but differs from the frozen digest
is adverse observed evidence and remains `OBJECTIVE_MISMATCH`, not missingness.
No row is dropped.

## Chronology and authority

This increment freezes the protocol and runner only. It contains no acquisition
receipt and no policy/comparator result. Execution must occur from a later main
commit, bind that commit plus the exact protocol/runner/corpus/contract bytes,
and retain all 45 corpus rows (including the 14 license-ineligible exclusions).

Scientific-authority delta: **NONE**. The issue external-campaign gate remains
`OPEN`; independent adjudication, protected custody, semantic governance and
population inference remain `CANNOT_CHECK`.
