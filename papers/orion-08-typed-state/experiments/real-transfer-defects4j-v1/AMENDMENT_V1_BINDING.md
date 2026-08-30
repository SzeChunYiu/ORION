# Amendment 1 to the Defects4J protocol — the refined binding

**Made before any catch rate, utility or terminal was computed.** The only
quantities consulted are fibre counts and fibre sizes, which are properties of
the metadata's shape and carry no information about which tests catch which bugs.

## What was wrong

`PROTOCOL_V1.md` fixed the refined binding as the pair of the full modified class
name and the full test class name. Measured over the fetched metadata:

| project | rows | refined fibres | singletons |
|---|---|---|---|
| Chart | 4,732 | 4,186 | 3,822 |
| Cli | 3,003 | 1,309 | 693 |
| Closure | 41,412 | 17,850 | 8,568 |
| Codec | 504 | 308 | 224 |
| Collections | 1,344 | 912 | 720 |
| Compress | 3,713 | 1,975 | 1,343 |
| Csv | 208 | 78 | 26 |
| Gson | 1,530 | 1,105 | 850 |
| Lang | 7,808 | 4,736 | 2,944 |
| Math | 60,738 | 45,267 | 37,245 |
| Mockito | 11,362 | 8,372 | 6,279 |
| Time | 3,146 | 1,815 | 1,210 |
| **total** | **139,500** | **87,913** | **63,924 (72.7%)** |

Nearly three quarters of the refined fibres contain exactly one row. The theorem
is about the optimal action *of a fibre*, estimated from the mass in it. A binding
whose fibres are mostly single rows does not estimate a fibre's optimal action; it
reproduces the row. Refinement to it would decrease measured regret to zero on
every project by construction, and the "exactly when" clause — the part that can
actually fail — would never be exercised. The test would return a pass that means
nothing.

This is the same class of error as scoring the theorem out-of-sample on the CC18
leg: a defensible-sounding choice that quietly removes the possibility of failure.

## What replaces it

- **coarse** — `package(test class)`, the full package. This says *where in the
  test suite* a candidate lives and knows nothing about what changed.
- **refined / typed** — `(package(test class), name_match)` where `name_match ∈
  {exact, prefix, none}` compares the test's simple name against the simple names
  of the modified classes: `exact` when the test is `<Class>Test` or `Test<Class>`,
  `prefix` when a modified class's simple name appears in the test's, `none`
  otherwise.

The refinement adds exactly one thing: whether this test targets the class that
changed. That is the change-to-test binding, and it is the typed-state content the
theorem is about. The coarse binding is a strict coarsening of it, so this remains
a refinement in the theorem's sense.

## A degeneracy gate, in the runner

The runner refuses to assign a terminal if more than half the refined fibres of
any project are singletons, and emits `CANNOT_CHECK_DEGENERATE_BINDING` instead.
The failure above was found by looking; it should not have needed looking.

## What is not changed

The utility matrix, the in-sample scoring rule, the `MIN_MASS = 1` convention, the
arms, the two-stratum requirement and every terminal stay exactly as committed in
`PROTOCOL_V1.md`. The prediction is still computed from a training half alone.
