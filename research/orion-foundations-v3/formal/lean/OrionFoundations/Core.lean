import Init
import Init.Omega

namespace OrionFoundations

universe u v w

/-! T1: conservative simulation of donor-native traces. -/
structure CoupledStep (Extended : Type u) (Donor : Type v)
    (project : Extended → Donor) where
  extended : Extended → Extended
  donor : Donor → Donor
  commutes : ∀ s, project (extended s) = donor (project s)


def runExtended {Extended : Type u} {Donor : Type v} {project : Extended → Donor} :
    List (CoupledStep Extended Donor project) → Extended → Extended
  | [], s => s
  | step :: rest, s => runExtended rest (step.extended s)


def runDonor {Extended : Type u} {Donor : Type v} {project : Extended → Donor} :
    List (CoupledStep Extended Donor project) → Donor → Donor
  | [], s => s
  | step :: rest, s => runDonor rest (step.donor s)


theorem ostc_t1_donor_conservativity
    {Extended : Type u} {Donor : Type v} {project : Extended → Donor}
    (steps : List (CoupledStep Extended Donor project)) (s : Extended) :
    project (runExtended steps s) = runDonor steps (project s) := by
  induction steps generalizing s with
  | nil => rfl
  | cons step rest ih =>
      simp only [runExtended, runDonor]
      rw [ih, step.commutes]

/-! T2/T3/T9: target sufficiency and full abstraction. -/
def FiberConstant (interface : α → β) (target : α → γ) : Prop :=
  ∀ x y, interface x = interface y → target x = target y

noncomputable def decoderOfFiberConstant [Inhabited γ]
    (interface : α → β) (target : α → γ)
    (h : FiberConstant interface target) : β → γ :=
  fun z =>
    if hz : ∃ x, interface x = z then
      target (Classical.choose hz)
    else
      default


theorem decoderOfFiberConstant_spec [Inhabited γ]
    (interface : α → β) (target : α → γ)
    (h : FiberConstant interface target) (x : α) :
    target x = decoderOfFiberConstant interface target h (interface x) := by
  classical
  unfold decoderOfFiberConstant
  have hx : ∃ y, interface y = interface x := ⟨x, rfl⟩
  rw [dif_pos hx]
  exact h x (Classical.choose hx) (Classical.choose_spec hx).symm


theorem ostc_t2_exact_target_sufficiency [Inhabited γ]
    (interface : α → β) (target : α → γ) :
    (∃ decode : β → γ, ∀ x, target x = decode (interface x)) ↔
      FiberConstant interface target := by
  constructor
  · intro hexists
    cases hexists with
    | intro decode hdecode =>
        intro x y hxy
        calc
          target x = decode (interface x) := hdecode x
          _ = decode (interface y) := congrArg decode hxy
          _ = target y := (hdecode y).symm
  · intro h
    exact ⟨decoderOfFiberConstant interface target h,
      decoderOfFiberConstant_spec interface target h⟩


theorem ostc_t3_fiberwise_optimality
    (score : β → γ → Nat) (best candidate : β → γ)
    (hbest : ∀ z y, score z y ≤ score z (best z)) :
    ∀ z, score z (candidate z) ≤ score z (best z) := by
  intro z
  exact hbest z (candidate z)


theorem ostc_t9_full_abstraction
    (interface : α → β) (target : α → γ)
    (left right : β → γ)
    (hleft : ∀ x, target x = left (interface x))
    (hright : ∀ x, target x = right (interface x)) :
    ∀ x, left (interface x) = right (interface x) := by
  intro x
  calc
    left (interface x) = target x := (hleft x).symm
    _ = right (interface x) := hright x

/-! T4/T5/T15: least derivation closure and no amplification. -/
structure Rule (Judgment : Type u) where
  premises : List Judgment
  conclusion : Judgment

inductive Derivable {Judgment : Type u}
    (registered : Rule Judgment → Prop) (seeds : Judgment → Prop) : Judgment → Prop
  | seed {j} : seeds j → Derivable registered seeds j
  | step (rule : Rule Judgment) :
      registered rule →
      (∀ p, p ∈ rule.premises → Derivable registered seeds p) →
      Derivable registered seeds rule.conclusion


theorem derivable_seed_simulation
    {Judgment : Type u} {registered : Rule Judgment → Prop}
    {sourceSeeds targetSeeds : Judgment → Prop}
    (simulate : ∀ j, targetSeeds j → Derivable registered sourceSeeds j) :
    ∀ {j}, Derivable registered targetSeeds j → Derivable registered sourceSeeds j := by
  intro j derivation
  induction derivation with
  | seed hseed => exact simulate _ hseed
  | step rule hregistered hpremises ih =>
      exact Derivable.step rule hregistered (fun p hp => ih p hp)


def AuthorityNeutral {Judgment : Type u}
    (registered : Rule Judgment → Prop)
    (sourceSeeds targetSeeds : Judgment → Prop) : Prop :=
  ∀ j, targetSeeds j → Derivable registered sourceSeeds j


theorem ostc_t4_no_silent_amplification
    {Judgment : Type u} {registered : Rule Judgment → Prop}
    {sourceSeeds targetSeeds : Judgment → Prop}
    (neutral : AuthorityNeutral registered sourceSeeds targetSeeds) :
    ∀ {j}, Derivable registered targetSeeds j → Derivable registered sourceSeeds j :=
  derivable_seed_simulation neutral


theorem authorityNeutral_trans
    {Judgment : Type u} {registered : Rule Judgment → Prop}
    {s₀ s₁ s₂ : Judgment → Prop}
    (h01 : AuthorityNeutral registered s₀ s₁)
    (h12 : AuthorityNeutral registered s₁ s₂) :
    AuthorityNeutral registered s₀ s₂ := by
  intro j hj
  exact derivable_seed_simulation h01 (h12 j hj)


theorem ostc_t5_bridge_necessity
    {Judgment : Type u} {registered : Rule Judgment → Prop}
    {sourceSeeds targetSeeds : Judgment → Prop} {j : Judgment}
    (outside : ¬ Derivable registered sourceSeeds j)
    (neutral : AuthorityNeutral registered sourceSeeds targetSeeds) :
    ¬ Derivable registered targetSeeds j := by
  intro derived
  exact outside (derivable_seed_simulation neutral derived)


theorem ostc_t15_old_closure_obstruction
    {Judgment : Type u} {oldRules newRules : Rule Judgment → Prop}
    {seeds : Judgment → Prop} {target : Judgment}
    (oldObstruction : ¬ Derivable oldRules seeds target)
    (newReach : Derivable newRules seeds target) :
    (¬ Derivable oldRules seeds target) ∧ Derivable newRules seeds target :=
  ⟨oldObstruction, newReach⟩

/-! T6/T7/T23: normal-form mutual simulation. -/
structure NormalizationSystem (Judgment : Type u) where
  Operational : Judgment → Type v
  NormalForm : Judgment → Type w
  extract : {j : Judgment} → Operational j → NormalForm j
  replay : {j : Judgment} → NormalForm j → Operational j


def OperationallyAdmitted {Judgment : Type u}
    (system : NormalizationSystem Judgment) (j : Judgment) : Prop :=
  Nonempty (system.Operational j)


def HasNormalForm {Judgment : Type u}
    (system : NormalizationSystem Judgment) (j : Judgment) : Prop :=
  Nonempty (system.NormalForm j)


theorem ostc_t6_normal_form_soundness
    {Judgment : Type u} (system : NormalizationSystem Judgment) {j : Judgment} :
    HasNormalForm system j → OperationallyAdmitted system j := by
  intro h
  cases h with
  | intro normal => exact ⟨system.replay normal⟩


theorem ostc_t7_normal_form_completeness
    {Judgment : Type u} (system : NormalizationSystem Judgment) {j : Judgment} :
    OperationallyAdmitted system j → HasNormalForm system j := by
  intro h
  cases h with
  | intro operational => exact ⟨system.extract operational⟩


def ScientificAdvance (available admitted : δ → Prop) (j : δ) : Prop :=
  available j ∧ admitted j


theorem ostc_t23_coupled_advance (available admitted : δ → Prop) (j : δ) :
    ScientificAdvance available admitted j ↔ available j ∧ admitted j :=
  Iff.rfl

/-! T8: explicit factor independence witnesses. -/
structure FactorVector where
  reachable : Bool
  nativeValid : Bool
  executionValid : Bool
  sufficient : Bool
  entitled : Bool
  supported : Bool
  deriving DecidableEq, Repr


def FactorVector.accepts (f : FactorVector) : Bool :=
  f.reachable && f.nativeValid && f.executionValid &&
    f.sufficient && f.entitled && f.supported


def missReach : FactorVector := ⟨false, true, true, true, true, true⟩
def missNative : FactorVector := ⟨true, false, true, true, true, true⟩
def missExecution : FactorVector := ⟨true, true, false, true, true, true⟩
def missSufficiency : FactorVector := ⟨true, true, true, false, true, true⟩
def missEntitlement : FactorVector := ⟨true, true, true, true, false, true⟩
def missSupport : FactorVector := ⟨true, true, true, true, true, false⟩


theorem ostc_t8_factor_independence :
    missReach.accepts = false ∧ missNative.accepts = false ∧
    missExecution.accepts = false ∧ missSufficiency.accepts = false ∧
    missEntitlement.accepts = false ∧ missSupport.accepts = false := by
  decide

/-! T10: typed, attenuating certificate composition. -/
structure Contract where
  object : Nat
  responsibility : Nat
  scope : Nat
  content : Nat
  epoch : Nat
  deriving DecidableEq, Repr

structure Certificate where
  source : Contract
  target : Contract
  sourceAuthority : Nat
  targetAuthority : Nat
  attenuates : targetAuthority ≤ sourceAuthority


def Composable (left right : Certificate) : Prop :=
  left.target = right.source ∧ right.sourceAuthority ≤ left.targetAuthority


def Certificate.trans (left right : Certificate) (h : Composable left right) : Certificate where
  source := left.source
  target := right.target
  sourceAuthority := left.sourceAuthority
  targetAuthority := right.targetAuthority
  attenuates := Nat.le_trans right.attenuates (Nat.le_trans h.2 left.attenuates)


theorem ostc_t10_composition_attenuates
    (left right : Certificate) (h : Composable left right) :
    (left.trans right h).targetAuthority ≤ (left.trans right h).sourceAuthority :=
  (left.trans right h).attenuates


theorem certificate_trans_source
    (left right : Certificate) (h : Composable left right) :
    (left.trans right h).source = left.source := rfl


theorem certificate_trans_target
    (left right : Certificate) (h : Composable left right) :
    (left.trans right h).target = right.target := rfl

/-! T11: exact alternative-support revocation. -/
def FamilyValid (revoked : Token → Prop) (family : List Token) : Prop :=
  ∀ token, token ∈ family → ¬ revoked token


def JudgmentSurvives (families : List (List Token)) (revoked : Token → Prop) : Prop :=
  ∃ family, family ∈ families ∧ FamilyValid revoked family


theorem ostc_t11_exact_revocation
    (families : List (List Token)) (revoked : Token → Prop) :
    (¬ JudgmentSurvives families revoked) ↔
      ∀ family, family ∈ families → ∃ token, token ∈ family ∧ revoked token := by
  classical
  constructor
  · intro noSurvivor family hfamily
    by_contra noBrokenToken
    apply noSurvivor
    refine ⟨family, hfamily, ?_⟩
    intro token htoken hrevoked
    exact noBrokenToken ⟨token, htoken, hrevoked⟩
  · intro everyBroken survivor
    cases survivor with
    | intro family hrest =>
        cases hrest with
        | intro hfamily valid =>
            obtain ⟨token, htoken, hrevoked⟩ := everyBroken family hfamily
            exact valid token htoken hrevoked

/-! T12/T14/T19: indistinguishability impossibilities. -/
theorem ostc_t12_open_world_impossibility
    (observe : World → Observation) (truth : World → Terminal)
    (w₀ w₁ : World) (sameObservation : observe w₀ = observe w₁)
    (differentTruth : truth w₀ ≠ truth w₁) :
    ∀ decide : Observation → Terminal,
      decide (observe w₀) ≠ truth w₀ ∨ decide (observe w₁) ≠ truth w₁ := by
  intro decide
  by_cases correct₀ : decide (observe w₀) = truth w₀
  · right
    intro correct₁
    apply differentTruth
    calc
      truth w₀ = decide (observe w₀) := correct₀.symm
      _ = decide (observe w₁) := congrArg decide sameObservation
      _ = truth w₁ := correct₁
  · exact Or.inl correct₀


theorem ostc_t14_collision_defeats_diagnosis
    (signature : Cause → Intervention → Response)
    (c d : Cause) (differentCauses : c ≠ d)
    (sameSignature : signature c = signature d) :
    ¬ ∃ decode : (Intervention → Response) → Cause,
      decode (signature c) = c ∧ decode (signature d) = d := by
  intro h
  cases h with
  | intro decode hpairs =>
      cases hpairs with
      | intro hc hd =>
          apply differentCauses
          calc
            c = decode (signature c) := hc.symm
            _ = decode (signature d) := congrArg decode sameSignature
            _ = d := hd


theorem ostc_t19_reflexive_custody_impossibility
    (visible : World → Transcript) (protectedTruth : World → Bool)
    (good gaming : World) (sameVisible : visible good = visible gaming)
    (differentProtectedTruth : protectedTruth good ≠ protectedTruth gaming) :
    ∀ internalGate : Transcript → Bool,
      internalGate (visible good) ≠ protectedTruth good ∨
      internalGate (visible gaming) ≠ protectedTruth gaming :=
  ostc_t12_open_world_impossibility visible protectedTruth good gaming
    sameVisible differentProtectedTruth

/-! T13: regime transport coherence. -/
theorem ostc_t13_transport_associativity
    (f : A → B) (g : B → C) (h : C → D) :
    (fun x => h (g (f x))) = (fun x => (h ∘ g) (f x)) := by
  rfl


theorem regime_path_dependence_witness
    (via : A → C) (direct : A → C) (x : A)
    (mismatch : via x ≠ direct x) : via ≠ direct := by
  intro equalFunctions
  exact mismatch (congrFun equalFunctions x)

/-! T16/T17: placement and allocation lower bounds. -/
theorem ostc_t16_break_even (compileCost repeatedBase repeatedSaving : Nat) :
    compileCost + repeatedBase < repeatedBase + repeatedSaving ↔
      compileCost < repeatedSaving := by
  omega


theorem ostc_t17_coarsened_signal_regret
    (policy : Signal → Bool) (signal : Signal)
    (caseOneTrue caseOneFalse caseTwoTrue caseTwoFalse : Nat)
    (caseOnePrefersTrue : caseOneTrue < caseOneFalse)
    (caseTwoPrefersFalse : caseTwoFalse < caseTwoTrue) :
    (policy signal = true ∧
      caseTwoFalse < (if policy signal then caseTwoTrue else caseTwoFalse)) ∨
    (policy signal = false ∧
      caseOneTrue < (if policy signal then caseOneTrue else caseOneFalse)) := by
  cases h : policy signal <;> simp [h, caseOnePrefersTrue, caseTwoPrefersFalse]

/-! T18: responsibility-relative state sufficiency. -/
def SufficientFor (state : Ω → Stored) (target : Ω → Decision) : Prop :=
  ∀ x y, state x = state y → target x = target y


theorem ostc_t18_joint_responsibility_sufficiency
    (state : Ω → Stored) (first : Ω → D₁) (second : Ω → D₂) :
    SufficientFor state (fun x => (first x, second x)) ↔
      SufficientFor state first ∧ SufficientFor state second := by
  constructor
  · intro joint
    constructor
    · intro x y hxy
      exact congrArg Prod.fst (joint x y hxy)
    · intro x y hxy
      exact congrArg Prod.snd (joint x y hxy)
  · intro separate
    cases separate with
    | intro hfirst hsecond =>
        intro x y hxy
        exact Prod.ext (hfirst x y hxy) (hsecond x y hxy)

/-! T20: execution/science noninterference. -/
structure LayeredState (Execution : Type u) (Validity : Type v) (Authority : Type w) where
  execution : Execution
  validity : Validity
  authority : Authority


def executionOnly (f : Execution → Execution₂)
    (state : LayeredState Execution Validity Authority) :
    LayeredState Execution₂ Validity Authority where
  execution := f state.execution
  validity := state.validity
  authority := state.authority


theorem ostc_t20_execution_noninterference_validity
    (f : Execution → Execution₂) (state : LayeredState Execution Validity Authority) :
    (executionOnly f state).validity = state.validity := rfl


theorem ostc_t20_execution_noninterference_authority
    (f : Execution → Execution₂) (state : LayeredState Execution Validity Authority) :
    (executionOnly f state).authority = state.authority := rfl

/-! T21: well-founded recursive evolution. -/
theorem ostc_t21_no_infinite_nat_descent
    (rank : Nat → Nat) (decreases : ∀ n, rank (n + 1) < rank n) : False := by
  have bounded : ∀ n, rank n + n ≤ rank 0 := by
    intro n
    induction n with
    | zero => simp
    | succ n ih =>
        have step := decreases n
        omega
  have impossible := bounded (rank 0 + 1)
  omega

/-! T22: supplied certificates are checkable without solving search. -/
structure CertificateProblem where
  Witness : Type u
  Valid : Witness → Prop


def CertificateProblem.HasSolution (problem : CertificateProblem) : Prop :=
  ∃ witness, problem.Valid witness


theorem ostc_t22_supplied_witness_checks
    (problem : CertificateProblem) (witness : problem.Witness)
    (checked : problem.Valid witness) : problem.HasSolution :=
  ⟨witness, checked⟩

end OrionFoundations
