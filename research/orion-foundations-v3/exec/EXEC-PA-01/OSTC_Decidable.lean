/-
EXEC-PA-01 -- Lean 4 reconstruction of the decidable OSTC obligations.

Independent of the Python enumerations in the other jobs: different engine,
different encoding, and `#print axioms` at the end shows what each result
depends on. A theorem that depends on nothing is not resting on a hidden
assumption I introduced.

Scope: the decidable fragment only. This is not a reconstruction of the full
derivations in THEOREM_DERIVATIONS_T0_T23_V1.md.
-/

namespace OSTC

/-- A SANF witness: six factors. -/
structure Witness where
  R : Bool
  V : Bool
  X : Bool
  S : Bool
  E : Bool
  B : Bool
deriving DecidableEq, Repr

/-- T7: a witness admits exactly when all six factors hold. -/
def admits (w : Witness) : Bool := w.R && w.V && w.X && w.S && w.E && w.B

/-! ## T8 -- factor independence

For each factor there is a matched countermodel: an admitting witness whose
variant with that factor dropped does not admit. All other factors are held
fixed, which is what makes it independence rather than mere sensitivity. -/

def full : Witness := ⟨true, true, true, true, true, true⟩

theorem t8_R : admits full = true ∧ admits { full with R := false } = false := by
  constructor <;> rfl
theorem t8_V : admits full = true ∧ admits { full with V := false } = false := by
  constructor <;> rfl
theorem t8_X : admits full = true ∧ admits { full with X := false } = false := by
  constructor <;> rfl
theorem t8_S : admits full = true ∧ admits { full with S := false } = false := by
  constructor <;> rfl
theorem t8_E : admits full = true ∧ admits { full with E := false } = false := by
  constructor <;> rfl
theorem t8_B : admits full = true ∧ admits { full with B := false } = false := by
  constructor <;> rfl

/-- No factor is eliminable: dropping any one breaks an admitting witness. -/
theorem t8_no_factor_eliminable :
    (admits { full with R := false } = false) ∧
    (admits { full with V := false } = false) ∧
    (admits { full with X := false } = false) ∧
    (admits { full with S := false } = false) ∧
    (admits { full with E := false } = false) ∧
    (admits { full with B := false } = false) := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩ <;> rfl

/-! ## T10 -- composition retains blockers

Composition unions support while retaining unresolved blockers. The obligation
is that a blocker present in either input is present in the output. -/

def composeBlockers (a b : Bool) : Bool := a || b

theorem t10_left_blocker_retained (a b : Bool) :
    a = true → composeBlockers a b = true := by
  intro h; simp [composeBlockers, h]

theorem t10_right_blocker_retained (a b : Bool) :
    b = true → composeBlockers a b = true := by
  intro h; simp [composeBlockers, h]

/-- Composition never silently clears a blocker. -/
theorem t10_no_blocker_lost (a b : Bool) :
    composeBlockers a b = false → a = false ∧ b = false := by
  intro h
  simp [composeBlockers] at h
  exact h

/-! ## T11 -- survival under revocation

j survives iff some minimal support family is disjoint from the revoked set.
Encoded over lists: survival is existence of a family with no revoked member. -/

def disjointFrom (F R : List Nat) : Bool := F.all (fun t => !R.contains t)

def survives (minsup : List (List Nat)) (R : List Nat) : Bool :=
  minsup.any (fun F => disjointFrom F R)

theorem t11_survival_iff_some_family_clean
    (minsup : List (List Nat)) (R : List Nat) :
    survives minsup R = true ↔ ∃ F ∈ minsup, disjointFrom F R = true := by
  simp [survives, List.any_eq_true]

/-- Nothing survives an empty support set, whatever is revoked. -/
theorem t11_no_support_no_survival (R : List Nat) : survives [] R = false := by
  rfl

/-! ## T20 -- execution/science noninterference

State is E x V x A. An execution-only transformation is (f, id, id), so it
cannot alter validity or authority. -/

structure St where
  exec  : Nat
  valid : Nat
  auth  : Nat
deriving DecidableEq, Repr

def execOnly (f : Nat → Nat) (s : St) : St := ⟨f s.exec, s.valid, s.auth⟩

theorem t20_validity_unchanged (f : Nat → Nat) (s : St) :
    (execOnly f s).valid = s.valid := by rfl

theorem t20_authority_unchanged (f : Nat → Nat) (s : St) :
    (execOnly f s).auth = s.auth := by rfl

/-- No execution-only transformation, for any f and any state, touches V or A. -/
theorem t20_noninterference (f : Nat → Nat) (s : St) :
    (execOnly f s).valid = s.valid ∧ (execOnly f s).auth = s.auth :=
  ⟨rfl, rfl⟩

/-! ## Vacuity guards

If the encoding could not reject anything, every theorem above would be
worthless. These show it rejects. -/

theorem guard_admits_is_not_constant :
    admits full = true ∧ admits ⟨false, true, true, true, true, true⟩ = false := by
  constructor <;> rfl

theorem guard_blockers_not_constant :
    composeBlockers true false = true ∧ composeBlockers false false = false := by
  constructor <;> rfl

theorem guard_survival_not_constant :
    survives [[1, 2]] [] = true ∧ survives [[1, 2]] [1] = false := by
  constructor <;> rfl

end OSTC

#print axioms OSTC.t8_no_factor_eliminable
#print axioms OSTC.t10_no_blocker_lost
#print axioms OSTC.t11_survival_iff_some_family_clean
#print axioms OSTC.t20_noninterference
#print axioms OSTC.guard_survival_not_constant
