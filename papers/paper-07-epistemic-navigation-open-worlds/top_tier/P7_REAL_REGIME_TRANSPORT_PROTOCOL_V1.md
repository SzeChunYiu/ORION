# P7 real regime transport protocol V1

**Programme:** #977  
**Purpose:** execute Scientific Regime Transport on two qualitatively different non-synthetic regimes: public research-standard evolution and real-data ontology/objective refinement.

## Chronology

`P7_REAL_REGIME_SOURCES_2026-08-23.md` and this protocol are committed before the runner/outcome. The public-source URI mappings and the wine responsibility map may not be changed after protected results are observed.

## Domain A — RO-Crate 1.2 -> 1.3 representation identity

Freeze the four actual Bioschemas binding changes recorded in the source file plus two unchanged control terms:

- changed: `ComputationalWorkflow`, `FormalParameter`, `input`, `output`;
- unchanged controls: Schema.org `name`, `description`.

For each changed term construct three evidence-transport conditions:

1. **COMPLETE_ALIAS:** old and new canonical URIs plus the registered version-change correspondence are available;
2. **NO_ALIAS_WITNESS:** lexical JSON key/value payload is preserved but the canonical URI correspondence is absent;
3. **WRONG_ALIAS:** a conflicting target URI is supplied.

Gold scientific-closure dispositions:

- COMPLETE_ALIAS -> `TRANSPORT`;
- NO_ALIAS_WITNESS -> `CANNOT_CHECK`;
- WRONG_ALIAS -> `REOPEN`.

Unchanged controls -> `TRANSPORT` without a special alias witness.

### Donor comparators

- `VALUE_ONLY`: transports whenever lexical key and payload are unchanged;
- `ALWAYS_REOPEN`: reopens every version transition;
- `WITNESS_AWARE` (P7): applies the registered URI/epoch correspondence and fails closed when it is missing/conflicting.

This does not claim P7 invented schema/alias migration. A donor given the same complete support/alias witness should become equivalent on this domain; the experiment tests the scientific-closure layer above value preservation.

## Domain B — Wine fine/coarse ontology and objective change

Use `sklearn.datasets.load_wine()` with scikit-learn `1.7.1`. No model is trained; observed class labels are the evidence atoms.

Fine regime:

`R_fine`: responsibility is exact class in `{0,1,2}`.

Coarse regime:

`R_coarse`: responsibility is `class0_vs_other`, with map `0->1`, `1->0`, `2->0`.

### B1 fine -> coarse

Fine evidence deterministically transports to coarse evidence for every sample. Gold = `TRANSPORT`. Reopening raw evidence is unnecessary work.

### B2 coarse -> fine with fine support discarded

- coarse value `1` uniquely identifies fine class `0`: `TRANSPORT`;
- coarse value `0` merges fine classes `1` and `2`: `CANNOT_CHECK`.

A value-only inverse that maps every coarse `0` to one fine class is a false closure declaration on the other class.

### B3 sequential fine -> coarse -> fine

Compare two histories:

- **support retained:** the original fine evidence/support witness remains registered through the coarse regime; returning to the fine objective may `TRANSPORT` from retained support;
- **support discarded:** only the coarse evidence remains; the same return-to-fine regime must follow B2 and be `CANNOT_CHECK` for merged classes.

This directly tests that local value maps do not compose into scientific closure after intermediate support loss.

## Primary endpoints

Across both domains report:

- false closure-preservation count;
- missed valid transport count;
- unnecessary reopen count;
- correct `CANNOT_CHECK` count;
- sequential composition errors;
- evidence/raw revalidation reads;
- exact agreement with independent gold rules;
- deterministic replay.

## Positive terminal

`P7_REAL_REGIME_TRANSPORT_V1_SUPPORTED` requires:

- WITNESS_AWARE exact disposition accuracy `1.0` in both domains;
- VALUE_ONLY makes at least one false closure-preservation decision in each domain;
- ALWAYS_REOPEN makes at least one unnecessary reopen decision in each domain;
- all complete RO-Crate alias cases transport and all missing/conflicting alias cases fail closed correctly;
- wine fine->coarse transports all samples without raw reread;
- wine coarse->fine returns `CANNOT_CHECK` exactly on the non-identifiable merged classes;
- support-retained vs support-discarded sequential histories receive different dispositions where required;
- deterministic replay.

A positive closes two non-synthetic regime-change domains and supports the higher claim that value/representation preservation is weaker than scientific support/closure transport. It does not establish arbitrary world-model/objective transport in live autonomous agents.
