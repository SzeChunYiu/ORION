# An arm whose answers are a function of the symbol alphabet, not the semantics

**Found 2026-08-21**, running P9's `H_FMT` format-prior attack — one of two
hostile alternatives P9's own successor manuscript names as *mandatory* and
which had never been run.

## The finding

`TYPED_SERIALIZED_BAG` was scored on D1 v1.2's 128 protected cases. Apply a
bijection to the value alphabet — 220 atoms to 220 distinct images, every one of
the 512 gold labels preserved and verified — and:

| | accuracy | distinct predictions | informedness |
|---|---|---|---|
| base | 0.75 | 2 | 0.5 |
| semantic orbit | **0.50** | 1 | **0.0** |

32 of 128 protected predictions move. A scratch diagnostic sharpens it further:
the orbit is an *exact renaming of that arm's feature keys* — 279 keys before
and after, 26 surviving in-vocabulary protected keys, the same seven distinct
protected rows with multiplicities `[48, 32, 15, 14, 11, 4, 4]`. Nothing changed
but column names, and a whole 32-case group changed answer.

The published constant `0.50` is one point of that orbit. So the reported
`+0.50` typed-minus-serialized margin cannot carry the manuscript's sentence
that "explicit relational comparison makes those fields more useful": the
serialized arm's number is a property of which symbols were drawn, not of the
information the representation carries.

## Why this is its own failure class

It is adjacent to `2026-08-unresponsive-comparator-prior-valued-margin`, and it
is not the same thing. There the comparator does not move when the evidence
moves. Here the comparator moves when *nothing* moves — the semantics, the
information content and the labels are all invariant under the transform, and
the answer changes anyway.

The two have opposite diagnostics and the same consequence. A margin against an
unresponsive comparator measures the comparator's prior; a margin against an
alphabet-sensitive comparator measures the draw. Neither measures the mechanism
the paper is about.

## What makes it hard to see

The same-information property was **true and checked**: all 512 serialized token
lists decode back to their typed payload exactly. That is a real invariance and
it is the reason the arm looks like a fair comparator. But carrying the
information is not the same as answering from it, and only a symmetry the
representation should be invariant under can tell the two apart.

## The diagnostic

Apply a transform the answer must be invariant under, and check that it is.
Concretely: remint the symbol alphabet under a bijection, verify the gold labels
are preserved, and require the protected predictions not to move. Any arm whose
answers move is answering from the symbols.

The check is cheap and the invariance is not optional — which is why P9's own
manuscript listed it as mandatory. It had simply never been run, and an unrun
hostile alternative is not a refuted one.

## General lesson candidate

**An invariance a representation claims must be tested by a transform, not by an
argument.** "Same information" is a statement about what can be decoded; it says
nothing about what is used. The gap between the two is exactly where a format
prior lives, and the only way to measure it is to vary the format while holding
the information fixed.
