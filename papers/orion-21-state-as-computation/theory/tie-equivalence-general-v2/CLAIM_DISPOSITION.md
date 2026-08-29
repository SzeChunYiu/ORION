# ORION-21 general tie-equivalence theorem — claim disposition

**Terminal:** `GENERAL_P_IMPOSSIBILITY_PROVED_FOR_COMPLETE_SIGN_ROW_READOUT`  
**Scientific authority delta:** `NONE`

## Earned

The V1 `p<=5` restriction is removed from the structural theorem.

For every \(p\ge2\), arbitrary integer correlation vector \(c\), and
\(1\le r\le p\), under the complete sign-row bank:

1. a non-singleton tie-equivalence class is prediction-benign **iff** its
   boundary correlation magnitude is zero;
2. every non-singleton positive-boundary class contains supports with different
   prediction streams;
3. the full state domain contains such a class for every \(p\ge2\);
4. consequently no invariant of any size/language can be both
   representative-independent and determine the prediction stream on all
   realized outcomes.

The proof is constructive and does not depend on the V1 enumeration.

## Preserved negatives / non-claims

This does not reopen NR07, the width law, or the tie-robust-phase experiment.
The complete row bank is essential: restricted banks can miss disagreement
rows. No empirical prevalence, magnitude, production value, or external
authority is created.

The V1 terminal remains valid as its finite exhaustive certificate; V2 explains
why its central structural finding generalizes beyond the enumerated domain.

## Regression status

The independent checker exhaustively validates the exact benign/binding
biconditional for \(p=2..6\), \(c\in\{-1,0,1\}^p\), all \(r\), and separately
checks the general witness construction through \(p=12\). The checker is a
regression only; the theorem text carries the proof.
