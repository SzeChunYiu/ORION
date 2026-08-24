# P6 first execution attempt — no result

## Terminal

`P6_PUBLIC_SELECTIVE_REVALIDATION_V1_NO_RESULT__LAZY_BLOB_FETCH_INTERRUPTED`

The first attempt started from clean `main` at
`bae81f6a1b5f9f395508deedf6034b97ee36135a`. During the first domain's graph
parse, the partial clone fetched one missing source blob per `git show` call.
This operational path would make the later Mathlib graph impractically slow, so
the process was interrupted rather than allowed to consume an unbounded series
of network round trips.

The exclusive result destination did not exist after interruption. No domain
count, graph count, change-set row, saving estimate, resampling quantity, gate,
or scientific result was emitted. This is an execution-path diagnosis, not a
negative scientific result and not a `CANNOT_CHECK` domain receipt from the
runner.

The prospective repair is one detached checkout of the already verified exact
frozen ref before parsing. That changes acquisition mechanics only. Dataset
heads, licenses, sampling, selectors, endpoints, mutations, gates and authority
boundaries remain unchanged. A later result is admissible only after this
amended no-results freeze is merged and executed unchanged from clean `main`.
