# Theorem: State Optionality and Future-Query Coverage V1

Status: EXACT CONTROLLED THEOREM / NOT A GENERAL MEMORY LOWER BOUND
Frozen: 2026-08-20

## Setup

Let a latent state support N mutually independent query components `z_1,...,z_N in {-1,+1}`. A current query requests r distinct components, and a minimal query-conditioned compiled state stores exactly those r component values and discards both the other components and the raw source state.

A future query independently asks for one component chosen uniformly from the N-component family.

## Theorem 1 — one-step optionality

Without raw-state recoverability, the probability that the minimal compiled state can answer the future component query exactly is

`r / N`.

Proof: the future query is answerable exactly iff its requested component is among the r retained components. Under uniform sampling, that event has probability r/N.

## Theorem 2 — cached compilation coverage

Suppose K independent current query sets, each a uniformly sampled r-subset of the N components, are compiled and their component values are cached. Let U_K be the union of cached component identities. Then the expected fraction of the future query family covered exactly is

`E[|U_K| / N] = 1 - (1 - r/N)^K`.

Proof: for any fixed component i, the probability it is absent from one random r-subset is `1-r/N`. Independence across K query sets gives absence probability `(1-r/N)^K`. Sum inclusion indicators over N components and divide by N.

## Corollary — expected uncovered optionality debt

Expected uncovered future-query fraction is

`(1-r/N)^K`.

Thus aggressive current-query compilation can be extremely accessible for the current task while retaining negligible option value for future unknown tasks when r << N and raw state is discarded.

## Raw-retention comparison

If the raw source state is retained and a valid compiler can regenerate any component, future query **coverage** remains 1, but a future recompilation cost is incurred. Hence raw+compiled state occupies a distinct resource point:
- higher retained memory than compiled-only;
- lower immediately accessible dimensionality than universal materialization;
- full recoverability subject to compiler cost.

This distinction motivates separate notions of:
- **accessibility**: can the current downstream system use the state directly?;
- **recoverability**: can an adequate accessible state be regenerated within a bounded compilation cost?;
- **optionality**: what fraction/distribution of future tasks remains serviceable without returning to an unavailable source?

## Boundaries

The theorem assumes a controlled independent-component query family and uniform future query in the closed form above. Nonuniform query distributions use weighted coverage instead. It is not a universal lower bound on memory systems, coding schemes, nonlinear decoders, or learned generative reconstruction.

The intended programme contribution is the representation-resource interpretation and measured agent/formal-system phase diagram, not the elementary occupancy calculation itself.
