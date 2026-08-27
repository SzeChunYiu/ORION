/-
ORION-03 Round 1: independent Lean core for typed versus flat construction.

This file proves only the frozen finite origin propositions below.  It does not
formalize Cedar semantics and grants no external, novelty or journal authority.
-/

structure Record where
  origin : Nat
  atoms : List Nat
  retracted : Bool
deriving DecidableEq, Repr

def FlatConstructs (required : List Nat) (records : List Record) : Prop :=
  ∀ atom, atom ∈ required →
    ∃ record, record ∈ records ∧ record.retracted = false ∧ atom ∈ record.atoms

def TypedConstructs (required : List Nat) (records : List Record) : Prop :=
  ∃ record, record ∈ records ∧ record.retracted = false ∧
    ∀ atom, atom ∈ required → atom ∈ record.atoms

def FlatCheck (required : List Nat) (records : List Record) : Bool :=
  required.all fun atom =>
    records.any fun record => !record.retracted && record.atoms.contains atom

def TypedCheck (required : List Nat) (records : List Record) : Bool :=
  records.any fun record =>
    !record.retracted && required.all fun atom => record.atoms.contains atom

theorem typed_implies_flat
    {required : List Nat} {records : List Record}
    (typed : TypedConstructs required records) :
    FlatConstructs required records := by
  intro atom atom_required
  rcases typed with ⟨record, record_present, not_retracted, carries_all⟩
  exact ⟨record, record_present, not_retracted, carries_all atom atom_required⟩

def hostileRequired : List Nat := [0, 1]

def hostilePartialRecords : List Record :=
  [ { origin := 0, atoms := [0], retracted := false },
    { origin := 1, atoms := [1], retracted := false } ]

theorem two_origin_flat_but_not_typed :
    FlatCheck hostileRequired hostilePartialRecords = true ∧
    TypedCheck hostileRequired hostilePartialRecords = false := by
  decide

def alternativeCompleteRecords : List Record :=
  hostilePartialRecords ++
    [{ origin := 2, atoms := [0, 1], retracted := false }]

theorem alternative_complete_origin_is_typed :
    TypedCheck hostileRequired alternativeCompleteRecords = true := by
  decide

inductive UnsupportedCycle : Nat → Prop where
  | fromB : UnsupportedCycle 1 → UnsupportedCycle 0
  | fromA : UnsupportedCycle 0 → UnsupportedCycle 1

theorem unsupported_positive_cycle_is_empty (atom : Nat) :
    ¬ UnsupportedCycle atom := by
  intro derivation
  induction derivation with
  | fromB _ impossible => exact impossible
  | fromA _ impossible => exact impossible
