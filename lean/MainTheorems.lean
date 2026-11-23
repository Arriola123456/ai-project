import Mathlib.Tactic
import Mathlib.Data.Real.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics
import Mathlib.Analysis.Convex.Deriv
import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Topology.Order.IntermediateValue

/-!
# Paper-Facing Theorems: Voto obligatorio a los 70 años: el salto, la edad y la costumbre de votar

This file is the implementation theorem layer for the source paper. Keep
source-faithful definitions and theorem wrappers here, and expose only the
compact human-review subset in `PaperInterface.lean`.

During the statement-first phase, each exact paper-facing proposition lives in a
transparent `<name>Spec : Prop` declaration in `PaperInterface.lean`; the paired
theorem/lemma endpoint belongs in `ProofInterface.lean` and has exactly that
type. Add proof implementations here only after those specifications pass v11
raw-source-to-expanded-Spec review and recursive premise provenance audit. Before full closeout, the v11
realization audit independently binds pinned source atoms to the elaborated Spec
and accounts for the complete Lean closure; a proof hole or a declaration name
is never evidence for that correspondence.

Import note (student run, 2026-11-23): the scaffold writes `import Mathlib`
here and validates the statement spec under `import AppliedModelingLib`. The
library root is not built on this laptop (see `docs/RUN_LOG.md`), so the paper
modules import only the Mathlib modules they use: tactics, the reals, real
powers with their derivatives and limits, convexity from derivatives, the
exponential and the square root with their derivatives, the mean value theorem
and the intermediate value theorem. No AppliedModelingLib declaration is used
by any Spec or proof.

Helper lemmas used by the proof endpoints in `ProofInterface.lean`: the cutoff
vote indicator is monotone in the threshold; the derivative of
`A a^α - κ a^β`; increments of a concave function fall; the closed form of the
AR(1) recursion and of the mean habit; the index set `k < ⌊(a-18)/d⌋`;
`⌊(a+1-18)/d⌋ = ⌊(a-18)/d⌋` when `d ∤ a+1-18`; and, for the heterogeneity
remark, the standard normal density `normalPdf`, the derivative of `z φ(z)`,
its monotonicity on `[0,1]` and `[1,∞)`, the bound `z φ(z) < 2/(z√(2π))`, the
derivative of `τ(s) = Φ((c+S)/s) - Φ(c/s)` and the strict monotonicity of `Φ`.
-/

open Real Filter Topology Finset

namespace Arriola26VotingHabit

theorem vote_mono {c c' e : ℝ} (hc : c ≤ c') :
    (if e < c then (1 : ℝ) else 0) ≤ (if e < c' then 1 else 0) := by
  by_cases h1 : e < c
  · have h2 : e < c' := lt_of_lt_of_le h1 hc
    simp [h1, h2]
  · by_cases h2 : e < c' <;> simp [h1, h2]

theorem vote_nonneg (c e : ℝ) : 0 ≤ (if e < c then (1 : ℝ) else 0) := by
  split_ifs <;> norm_num

theorem b_hasDerivAt (A α κ β a : ℝ) (ha : 0 < a) :
    HasDerivAt (fun x : ℝ => A * x ^ α - κ * x ^ β)
      (A * (α * a ^ (α - 1)) - κ * (β * a ^ (β - 1))) a :=
  ((hasDerivAt_rpow_const (Or.inl ha.ne')).const_mul A).sub
    ((hasDerivAt_rpow_const (Or.inl ha.ne')).const_mul κ)

theorem concave_increment {G : ℝ → ℝ} {D : Set ℝ} (hG : ConcaveOn ℝ D G) {x y S : ℝ}
    (hx : x ∈ D) (hyS : y + S ∈ D) (hxy : x ≤ y) (hS : 0 ≤ S) :
    G (y + S) - G y ≤ G (x + S) - G x := by
  rcases eq_or_lt_of_le (add_nonneg (sub_nonneg.mpr hxy) hS) with hL | hL
  · have hyx : y = x := by linarith
    have hS0 : S = 0 := by linarith
    subst hyx; subst hS0; simp
  · set L := y - x + S with hL_def
    have hL0 : L ≠ 0 := hL.ne'
    have ha : 0 ≤ (y - x) / L := div_nonneg (sub_nonneg.mpr hxy) hL.le
    have hb : 0 ≤ S / L := div_nonneg hS hL.le
    have hab : (y - x) / L + S / L = 1 := by rw [← add_div, ← hL_def, div_self hL0]
    have hba : S / L + (y - x) / L = 1 := by linarith
    have h1 := hG.2 hx hyS ha hb hab
    have h2 := hG.2 hx hyS hb ha hba
    simp only [smul_eq_mul] at h1 h2
    have e1 : (y - x) / L * x + S / L * (y + S) = x + S := by
      field_simp; ring
    have e2 : S / L * x + (y - x) / L * (y + S) = y := by
      field_simp; ring
    rw [e1] at h1; rw [e2] at h2
    have hsum : G x + G (y + S) =
        ((y - x) / L * G x + S / L * G (y + S)) + (S / L * G x + (y - x) / L * G (y + S)) := by
      have : G x + G (y + S) = ((y - x) / L + S / L) * (G x + G (y + S)) := by rw [hab]; ring
      rw [this]; ring
    linarith

theorem ar_closed_form (r V M : ℕ → ℝ) (h0 : M 0 = 0) (hs : ∀ j, M (j + 1) = r j * M j + V j) :
    ∀ N, M N = ∑ k ∈ range N, (∏ i ∈ range k, r (N - 1 - i)) * V (N - 1 - k) := by
  intro N
  induction N with
  | zero => simp [h0]
  | succ N ih =>
    have hidx : ∀ i, N + 1 - 1 - (i + 1) = N - 1 - i := by intro i; omega
    have hN : N + 1 - 1 - 0 = N := by omega
    rw [hs N, ih, Finset.sum_range_succ', Finset.mul_sum]
    congr 1
    · apply Finset.sum_congr rfl
      intro k _
      rw [Finset.prod_range_succ']
      simp only [hidx, hN]
      ring
    · simp

theorem mean_habit_closed_form {Ω : Type} [Fintype Ω] (w : Ω → ℝ) (d : ℕ) (ρ : ℕ → ℝ)
    (θ ε : Ω → ℕ → ℕ → ℝ) (lam : ℝ) (P : ℕ → ℝ) (h : Ω → ℕ → ℕ → ℝ) (a : ℕ)
    (hrec : ∀ ω, h ω a 0 = 0 ∧ ∀ j, h ω a (j + 1) = ρ (a - ((a - 18) / d - j) * d) * h ω a j +
      (if ε ω a j < θ ω a j + lam * h ω a j then 1 else 0))
    (hstat : ∀ j, j < (a - 18) / d →
      ∑ ω, w ω * (if ε ω a j < θ ω a j + lam * h ω a j then 1 else 0) =
        P (a - ((a - 18) / d - j) * d)) :
    ∑ ω, w ω * h ω a ((a - 18) / d) =
      ∑ k ∈ range ((a - 18) / d), (∏ i ∈ range k, ρ (a - (i + 1) * d)) * P (a - (k + 1) * d) := by
  set N := (a - 18) / d with hN
  set M : ℕ → ℝ := fun j => ∑ ω, w ω * h ω a j with hM
  set V : ℕ → ℝ := fun j => ∑ ω, w ω * (if ε ω a j < θ ω a j + lam * h ω a j then 1 else 0)
  set r : ℕ → ℝ := fun j => ρ (a - (N - j) * d)
  have hM0 : M 0 = 0 := by simp [M, (hrec _).1]
  have hMs : ∀ j, M (j + 1) = r j * M j + V j := by
    intro j
    simp only [M, V, r]
    rw [Finset.mul_sum, ← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro ω _
    rw [(hrec ω).2 j]; ring
  have hcf := ar_closed_form r V M hM0 hMs N
  change M N = _
  rw [hcf]
  apply Finset.sum_congr rfl
  intro k hk
  have hkN : k < N := Finset.mem_range.1 hk
  have hV : V (N - 1 - k) = P (a - (k + 1) * d) := by
    have := hstat (N - 1 - k) (by omega)
    rw [show N - (N - 1 - k) = k + 1 by omega] at this
    exact this
  rw [hV]
  congr 1
  apply Finset.prod_congr rfl
  intro i hi
  have hik : i < k := Finset.mem_range.1 hi
  simp only [r]
  rw [show N - (N - 1 - i) = i + 1 by omega]

theorem range_n_iff (d a k : ℕ) (hd : 1 ≤ d) :
    k ∈ range ((a - 18) / d) ↔ 18 + (k + 1) * d ≤ a := by
  have hX : 1 ≤ (k + 1) * d := Nat.mul_pos (by omega) (by omega)
  rw [Finset.mem_range, Nat.lt_iff_add_one_le, Nat.le_div_iff_mul_le (by omega)]
  generalize (k + 1) * d = X at *
  omega

theorem n_succ (d a : ℕ) (ha : 18 ≤ a) (hnd : ¬ d ∣ (a + 1 - 18)) :
    (a + 1 - 18) / d = (a - 18) / d := by
  have e : a + 1 - 18 = (a - 18) + 1 := by omega
  rw [e] at hnd ⊢
  exact Nat.succ_div_of_not_dvd hnd

/-- The standard normal density. -/
noncomputable def normalPdf (z : ℝ) : ℝ := Real.exp (-(z ^ 2) / 2) / Real.sqrt (2 * Real.pi)

theorem sqrt_two_pi_pos : 0 < Real.sqrt (2 * Real.pi) := Real.sqrt_pos.2 (by positivity)

theorem φ_pos (z : ℝ) : 0 < normalPdf z := div_pos (Real.exp_pos _) sqrt_two_pi_pos

theorem φ_hasDerivAt (z : ℝ) : HasDerivAt normalPdf (-z * normalPdf z) z := by
  have h1 : HasDerivAt (fun z : ℝ => -(z ^ 2) / 2) (-(2 * z) / 2) z := by
    have := ((hasDerivAt_pow 2 z).neg).div_const 2
    simpa using this
  have h2 := (h1.exp).div_const (Real.sqrt (2 * Real.pi))
  unfold normalPdf
  convert h2 using 1
  ring

theorem zφ_hasDerivAt (z : ℝ) :
    HasDerivAt (fun z => z * normalPdf z) (normalPdf z * (1 - z ^ 2)) z := by
  have := (hasDerivAt_id z).mul (φ_hasDerivAt z)
  convert this using 1
  simp; ring

theorem zφ_cont : Continuous (fun z => z * normalPdf z) :=
  continuous_iff_continuousAt.2 fun z => (zφ_hasDerivAt z).continuousAt

theorem zφ_mono : StrictMonoOn (fun z => z * normalPdf z) (Set.Icc 0 1) := by
  apply strictMonoOn_of_deriv_pos (convex_Icc 0 1) zφ_cont.continuousOn
  intro x hx
  rw [interior_Icc] at hx
  rw [(zφ_hasDerivAt x).deriv]
  have : 0 < 1 - x ^ 2 := by nlinarith [hx.1, hx.2]
  exact mul_pos (φ_pos x) this

theorem zφ_anti : StrictAntiOn (fun z => z * normalPdf z) (Set.Ici 1) := by
  apply strictAntiOn_of_deriv_neg (convex_Ici 1) zφ_cont.continuousOn
  intro x hx
  rw [interior_Ici] at hx
  rw [(zφ_hasDerivAt x).deriv]
  have : 1 - x ^ 2 < 0 := by nlinarith [show (1 : ℝ) < x from hx]
  exact mul_neg_of_pos_of_neg (φ_pos x) this

/-- `z normalPdf(z) < 2 / (z √(2π))` for `z > 0`. -/
theorem zφ_lt (z : ℝ) (hz : 0 < z) : z * normalPdf z < 2 / z / Real.sqrt (2 * Real.pi) := by
  unfold normalPdf
  have hs := sqrt_two_pi_pos
  have he : z ^ 2 / 2 < Real.exp (z ^ 2 / 2) := by
    have := Real.add_one_lt_exp (show z ^ 2 / 2 ≠ 0 by positivity)
    linarith
  have hneg : Real.exp (-(z ^ 2) / 2) = (Real.exp (z ^ 2 / 2))⁻¹ := by
    rw [← Real.exp_neg]; ring_nf
  rw [hneg, mul_div_assoc', div_lt_div_iff_of_pos_right hs]
  have hE : 0 < Real.exp (z ^ 2 / 2) := Real.exp_pos _
  rw [← div_eq_mul_inv, div_lt_div_iff₀ hE hz]
  nlinarith

theorem tau_hasDerivAt (Φ : ℝ → ℝ) (hΦ : ∀ x, HasDerivAt Φ (normalPdf x) x) (c S s : ℝ) (hs : 0 < s) :
    HasDerivAt (fun s' => Φ ((c + S) / s') - Φ (c / s'))
      (-(1 / s) * ((c + S) / s * normalPdf ((c + S) / s) - c / s * normalPdf (c / s))) s := by
  have hinv : HasDerivAt (fun s' : ℝ => s'⁻¹) (-(s ^ 2)⁻¹) s := hasDerivAt_inv hs.ne'
  have hA : HasDerivAt (fun s' : ℝ => (c + S) / s') ((c + S) * (-(s ^ 2)⁻¹)) s := by
    simpa [div_eq_mul_inv] using hinv.const_mul (c + S)
  have hB : HasDerivAt (fun s' : ℝ => c / s') (c * (-(s ^ 2)⁻¹)) s := by
    simpa [div_eq_mul_inv] using hinv.const_mul c
  have h := ((hΦ _).comp s hA).sub ((hΦ _).comp s hB)
  convert h using 1
  field_simp
  ring

theorem Phi_strictMono (Φ : ℝ → ℝ) (hΦ : ∀ x, HasDerivAt Φ (normalPdf x) x) : StrictMono Φ :=
  strictMono_of_deriv_pos fun x => by rw [(hΦ x).deriv]; exact φ_pos x

end Arriola26VotingHabit
