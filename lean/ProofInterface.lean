import Arriola26TurnoutGap.PaperInterface

/-!
# Proof Interface: La brecha de participación a los 70 años sobrestima el efecto del voto obligatorio: ciclo de vida, hábito y una calibración con datos de la ONPE

This file contains exact-type proof endpoints for the transparent propositions
in `PaperInterface.lean`. It is not a human semantic-review surface: one source
claim is reviewed once, against its expanded `...Spec : Prop` declaration.
-/

open Real Filter Topology Finset

namespace Arriola26TurnoutGap

/--
Lean proof endpoint for `lemma1_couplingSpec`.

This theorem is intentionally outside `PaperInterface.lean`: Lean Meta checks
that it has exactly the transparent Spec type, while source-to-Lean semantic
review compares the raw source bundle only to that Spec.
-/
theorem lemma1_coupling :
  lemma1_couplingSpec := by
  intro ρ θ θ' ε lam lam' h h' hρ hlam hll hθ h0 hs h0' hs'
  have thr : ∀ j, 0 ≤ h j → h j ≤ h' j → θ j + lam * h j ≤ θ' j + lam' * h' j := by
    intro j hn hle
    have : lam * h j ≤ lam' * h' j :=
      calc lam * h j ≤ lam' * h j := mul_le_mul_of_nonneg_right hll hn
        _ ≤ lam' * h' j := mul_le_mul_of_nonneg_left hle (le_trans hlam hll)
    linarith [hθ j]
  have key : ∀ j, 0 ≤ h j ∧ h j ≤ h' j := by
    intro j
    induction j with
    | zero => simp [h0, h0']
    | succ j ih =>
      obtain ⟨hn, hle⟩ := ih
      rw [hs j, hs' j]
      exact ⟨add_nonneg (mul_nonneg (hρ j) hn) (vote_nonneg _ _),
        add_le_add (mul_le_mul_of_nonneg_left hle (hρ j)) (vote_mono (thr j hn hle))⟩
  intro j
  obtain ⟨hn, hle⟩ := key j
  exact ⟨hn, hle, vote_mono (thr j hn hle)⟩

/--
Lean proof endpoint for `prop1_lifecycleSpec`.

This theorem is intentionally outside `PaperInterface.lean`: Lean Meta checks
that it has exactly the transparent Spec type, while source-to-Lean semantic
review compares the raw source bundle only to that Spec.
-/
theorem prop1_lifecycle :
  prop1_lifecycleSpec := by
  intro A α κ β hA hκ hα hα1 hβ b astar
  have hβα : 0 < β - α := by linarith
  have hβpos : 0 < β := by linarith
  set r : ℝ := A * α / (κ * β) with hr_def
  have hr : 0 < r := by positivity
  have hderiv : ∀ a, 0 < a → deriv b a = A * (α * a ^ (α - 1)) - κ * (β * a ^ (β - 1)) :=
    fun a ha => (b_hasDerivAt A α κ β a ha).deriv
  have hfactor : ∀ a, 0 < a →
      A * (α * a ^ (α - 1)) - κ * (β * a ^ (β - 1)) =
        a ^ (α - 1) * (A * α - κ * β * a ^ (β - α)) := by
    intro a ha
    have : a ^ (β - 1) = a ^ (β - α) * a ^ (α - 1) := by
      rw [← rpow_add ha]; ring_nf
    rw [this]; ring
  have hastar_pos : 0 < astar := rpow_pos_of_pos hr _
  have hastar_pow : astar ^ (β - α) = r := by
    change (r ^ (1 / (β - α))) ^ (β - α) = r
    rw [← rpow_mul hr.le, one_div_mul_cancel hβα.ne', rpow_one]
  have hκr : κ * β * r = A * α := by
    rw [hr_def]; field_simp
  have hcont : ∀ D : Set ℝ, D ⊆ Set.Ioi 0 → ContinuousOn b D := by
    intro D hD x hx
    exact (b_hasDerivAt A α κ β x (hD hx)).continuousAt.continuousWithinAt
  -- sign of b'
  have hpos : ∀ a, 0 < a → a < astar → 0 < deriv b a := by
    intro a ha hlt
    rw [hderiv a ha, hfactor a ha]
    have h1 : a ^ (β - α) < astar ^ (β - α) := rpow_lt_rpow ha.le hlt hβα
    rw [hastar_pow] at h1
    have h2 : κ * β * a ^ (β - α) < A * α := by
      rw [← hκr]; exact mul_lt_mul_of_pos_left h1 (by positivity)
    exact mul_pos (rpow_pos_of_pos ha _) (by linarith)
  have hneg : ∀ a, astar < a → deriv b a < 0 := by
    intro a hlt
    have ha : 0 < a := lt_trans hastar_pos hlt
    rw [hderiv a ha, hfactor a ha]
    have h1 : astar ^ (β - α) < a ^ (β - α) := rpow_lt_rpow hastar_pos.le hlt hβα
    rw [hastar_pow] at h1
    have h2 : A * α < κ * β * a ^ (β - α) := by
      rw [← hκr]; exact mul_lt_mul_of_pos_left h1 (by positivity)
    exact mul_neg_of_pos_of_neg (rpow_pos_of_pos ha _) (by linarith)
  refine ⟨?_, hastar_pos, ?_, ?_, ?_, ?_⟩
  · -- strict concavity: b' strictly decreasing on (0, ∞)
    apply StrictAntiOn.strictConcaveOn_of_deriv (convex_Ioi 0) (hcont _ subset_rfl)
    rw [interior_Ioi]
    intro x hx y hy hxy
    have hx' : (0 : ℝ) < x := hx
    have hy' : (0 : ℝ) < y := hy
    rw [hderiv x hx', hderiv y hy']
    have h1 : y ^ (α - 1) < x ^ (α - 1) := rpow_lt_rpow_of_neg hx' hxy (by linarith)
    have h2 : x ^ (β - 1) ≤ y ^ (β - 1) := rpow_le_rpow hx'.le hxy.le (by linarith)
    have h3 : A * (α * y ^ (α - 1)) < A * (α * x ^ (α - 1)) :=
      mul_lt_mul_of_pos_left (mul_lt_mul_of_pos_left h1 hα) hA
    have h4 : κ * (β * x ^ (β - 1)) ≤ κ * (β * y ^ (β - 1)) :=
      mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left h2 hβpos.le) hκ.le
    linarith
  · rw [hderiv astar hastar_pos, hfactor astar hastar_pos, hastar_pow, hκr]; ring
  · intro a ha hne
    rcases lt_or_gt_of_ne hne with hlt | hgt
    · have hmono : StrictMonoOn b (Set.Icc a astar) := by
        apply strictMonoOn_of_deriv_pos (convex_Icc a astar)
          (hcont _ (fun x hx => lt_of_lt_of_le ha hx.1))
        rw [interior_Icc]
        intro x hx
        exact hpos x (lt_trans ha hx.1) hx.2
      exact hmono ⟨le_rfl, hlt.le⟩ ⟨hlt.le, le_rfl⟩ hlt
    · have hanti : StrictAntiOn b (Set.Icc astar a) := by
        apply strictAntiOn_of_deriv_neg (convex_Icc astar a)
          (hcont _ (fun x hx => lt_of_lt_of_le hastar_pos hx.1))
        rw [interior_Icc]
        intro x hx
        exact hneg x hx.1
      exact hanti ⟨le_rfl, hgt.le⟩ ⟨hgt.le, le_rfl⟩ hgt
  · intro hβ1
    have h0 : Tendsto (fun a : ℝ => a ^ (α - 1)) atTop (𝓝 0) := by
      have := tendsto_rpow_neg_atTop (show 0 < 1 - α by linarith)
      simpa [neg_sub] using this
    have hlim : Tendsto (fun a : ℝ => A * (α * a ^ (α - 1)) - κ) atTop (𝓝 (-κ)) := by
      have := ((h0.const_mul α).const_mul A).sub (tendsto_const_nhds (x := κ))
      simpa using this
    apply hlim.congr'
    filter_upwards [eventually_gt_atTop 0] with a ha
    rw [hderiv a ha, hβ1]; simp
  · intro hβ1
    have h0 : Tendsto (fun a : ℝ => A * (α * a ^ (α - 1))) atTop (𝓝 0) := by
      have := tendsto_rpow_neg_atTop (show 0 < 1 - α by linarith)
      have h' : Tendsto (fun a : ℝ => a ^ (α - 1)) atTop (𝓝 0) := by
        simpa [neg_sub] using this
      simpa using (h'.const_mul α).const_mul A
    have h1 : Tendsto (fun a : ℝ => κ * (β * a ^ (β - 1))) atTop atTop :=
      ((tendsto_rpow_atTop (by linarith : (0 : ℝ) < β - 1)).const_mul_atTop hβpos).const_mul_atTop hκ
    have hlim : Tendsto (fun a : ℝ => A * (α * a ^ (α - 1)) + -(κ * (β * a ^ (β - 1)))) atTop atBot :=
      h0.add_atBot (tendsto_neg_atTop_atBot.comp h1)
    apply hlim.congr'
    filter_upwards [eventually_gt_atTop 0] with a ha
    rw [hderiv a ha]; ring

/--
Lean proof endpoint for `prop2_jumpSpec`.

This theorem is intentionally outside `PaperInterface.lean`: Lean Meta checks
that it has exactly the transparent Spec type, while source-to-Lean semantic
review compares the raw source bundle only to that Spec.
-/
theorem prop2_jump :
  prop2_jumpSpec := by
  refine ⟨?_, ?_, ?_⟩
  · intro d hd j hj
    have : 0 < ((70 - 18) / d - j) * d := Nat.mul_pos (Nat.sub_pos_of_lt hj) hd
    omega
  · intro c S e hS
    by_cases h1 : e < c
    · have h2 : e < c + S := by linarith
      have h3 : ¬ (c ≤ e ∧ e < c + S) := fun h => absurd h.1 (not_le.mpr h1)
      simp [h1, h2]
    · by_cases h2 : e < c + S
      · have h3 : c ≤ e ∧ e < c + S := ⟨le_of_not_gt h1, h2⟩
        simp [h1, h2, h3]
      · have h3 : ¬ (c ≤ e ∧ e < c + S) := fun h => h2 h.2
        simp [h1, h2]
  · intro Ω _ w n ρ θ ε B S m lam lam' G g h hw hρ hS hlam hll hG hgmono hganti hh hm τ
    have hconc : ConcaveOn ℝ (Set.Ici m) G := by
      have hderivG : deriv G = g := funext fun x => (hG x).deriv
      apply AntitoneOn.concaveOn_of_deriv (convex_Ici m)
      · exact fun x _ => (hG x).continuousAt.continuousWithinAt
      · exact fun x _ => (hG x).differentiableAt.differentiableWithinAt
      · rw [hderivG, interior_Ici]; exact hganti.mono Set.Ioi_subset_Ici_self
    apply Finset.sum_le_sum
    intro ω _
    apply mul_le_mul_of_nonneg_left _ (hw ω)
    obtain ⟨h0, hs⟩ := hh ω lam
    obtain ⟨h0', hs'⟩ := hh ω lam'
    obtain ⟨hn, hle, -⟩ := lemma1_coupling ρ (θ ω) (θ ω) (ε ω) lam lam' (h ω lam) (h ω lam')
      hρ hlam hll (fun _ => le_rfl) h0 hs h0' hs' n
    have hc : B ω + lam * h ω lam n ≤ B ω + lam' * h ω lam' n := by
      have : lam * h ω lam n ≤ lam' * h ω lam' n :=
        calc lam * h ω lam n ≤ lam' * h ω lam n := mul_le_mul_of_nonneg_right hll hn
          _ ≤ lam' * h ω lam' n := mul_le_mul_of_nonneg_left hle (le_trans hlam hll)
      linarith
    exact concave_increment hconc (hm ω) (show m ≤ B ω + lam' * h ω lam' n + S by linarith [hm ω])
      hc hS

/--
Lean proof endpoint for `prop3_boundSpec`.

This theorem is intentionally outside `PaperInterface.lean`: Lean Meta checks
that it has exactly the transparent Spec type, while source-to-Lean semantic
review compares the raw source bundle only to that Spec.
-/
theorem prop3_bound :
  prop3_boundSpec := by
  intro Ω _ w d amax ρ base ε S lam G wb wv hobs hcomp hd hw hρ hS hlam hG hwb hwv hwb1 hwv1
    n age O hobs_rec hcomp_rec P P1 Pf hH1 hH2 Δ τ E D
  have hOle : ∀ x, O x * S ≤ S := by
    intro x
    by_cases hx : x < 70
    · simp [O, hx]
    · simp [O, hx, hS]
  -- at 70 every past election was compulsory, so both histories coincide
  have hpast70 : ∀ j, j < n 70 → O (age 70 j) = 1 := by
    intro j hj
    have : 0 < (n 70 - j) * d := Nat.mul_pos (Nat.sub_pos_of_lt hj) hd
    have hlt : age 70 j < 70 := by
      change 70 - (n 70 - j) * d < 70
      omega
    simp [O, hlt]
  have hsame : ∀ ω, hobs ω 70 (n 70) = hcomp ω 70 (n 70) := by
    intro ω
    obtain ⟨h0, hs⟩ := hobs_rec ω 70
    obtain ⟨h0', hs'⟩ := hcomp_rec ω 70
    exact habit_congr (θ := fun j => base ω (age 70 j) + O (age 70 j) * S)
      (θ' := fun j => base ω (age 70 j) + S) (n 70)
      (fun j hj => by simp only [hpast70 j hj, one_mul]) h0 hs h0' hs' _ le_rfl
  have hPf70 : Pf 70 = P 70 := by
    simp only [Pf, P]
    apply Finset.sum_congr rfl
    intro ω _
    rw [hsame ω]
    simp [O]
  -- before 70 the current election is compulsory: P = P1
  have hP1P : ∀ a ∈ Icc 60 69, P1 a = P a := by
    intro a ha
    have hlt : a < 70 := by have := (mem_Icc.1 ha).2; omega
    simp only [P1, P]
    simp [O, hlt]
  -- coupling: the compulsory history dominates after 70
  have hPPf : ∀ a, 70 ≤ a → P a ≤ Pf a := by
    intro a ha
    simp only [P, Pf]
    apply Finset.sum_le_sum
    intro ω _
    apply mul_le_mul_of_nonneg_left _ (hw ω)
    obtain ⟨h0, hs⟩ := hobs_rec ω a
    obtain ⟨h0', hs'⟩ := hcomp_rec ω a
    obtain ⟨-, hle, -⟩ := lemma1_coupling (fun j => ρ (age a j))
      (fun j => base ω (age a j) + O (age a j) * S) (fun j => base ω (age a j) + S)
      (ε ω a) lam lam (hobs ω a) (hcomp ω a) (fun j => hρ _) hlam le_rfl
      (fun j => by simp only; linarith [hOle (age a j)]) h0 hs h0' hs' (n a)
    have hOa : O a = 0 := by simp [O, show ¬ a < 70 by omega]
    apply hG
    rw [hOa, zero_mul, add_zero]
    linarith [mul_le_mul_of_nonneg_left hle hlam]
  -- the two halves of the ageing term
  have hE1 : P1 70 ≤ ∑ a ∈ Icc 60 69, wb a * P1 a := by
    calc P1 70 = ∑ a ∈ Icc 60 69, wb a * P1 70 := by rw [← Finset.sum_mul, hwb1, one_mul]
      _ ≤ ∑ a ∈ Icc 60 69, wb a * P1 a := by
        apply Finset.sum_le_sum
        intro a ha
        have h1 := (mem_Icc.1 ha).1
        have h2 := (mem_Icc.1 ha).2
        exact mul_le_mul_of_nonneg_left (hH1 a 70 h1 (by omega) le_rfl) (hwb a)
  have hE2 : ∑ a ∈ Icc 70 amax, wv a * Pf a ≤ Pf 70 := by
    calc ∑ a ∈ Icc 70 amax, wv a * Pf a ≤ ∑ a ∈ Icc 70 amax, wv a * Pf 70 := by
          apply Finset.sum_le_sum
          intro a ha
          exact mul_le_mul_of_nonneg_left (hH2 70 a le_rfl (mem_Icc.1 ha).1) (hwv a)
      _ = Pf 70 := by rw [← Finset.sum_mul, hwv1, one_mul]
  have hD : ∑ a ∈ Icc 70 amax, wv a * P a ≤ ∑ a ∈ Icc 70 amax, wv a * Pf a := by
    apply Finset.sum_le_sum
    intro a ha
    exact mul_le_mul_of_nonneg_left (hPPf a (mem_Icc.1 ha).1) (hwv a)
  have hsumP1 : ∑ a ∈ Icc 60 69, wb a * P1 a = ∑ a ∈ Icc 60 69, wb a * P a :=
    Finset.sum_congr rfl (fun a ha => by rw [hP1P a ha])
  have hdec : Δ = τ + E + D := by
    simp only [Δ, τ, E, D]
    rw [hsumP1, hPf70]
    ring
  have hE : 0 ≤ E := by simp only [E]; linarith
  have hD' : 0 ≤ D := by simp only [D]; linarith
  refine ⟨hdec, hE, hD', ?_⟩
  rw [hdec]; linarith

/--
Lean proof endpoint for `prop4_stepsSpec`.

This theorem is intentionally outside `PaperInterface.lean`: Lean Meta checks
that it has exactly the transparent Spec type, while source-to-Lean semantic
review compares the raw source bundle only to that Spec.
-/
theorem prop4_steps :
  prop4_stepsSpec := by
  intro Ω _ w d r θ ε lam P h hd hw hw1 n age hrec hstat H
  have hcf : ∀ a, H a = ∑ k ∈ range (n a), r ^ k * P (a - (k + 1) * d) := by
    intro a
    have := mean_habit_closed_form w d (fun _ => r) θ ε lam P h a (fun ω => hrec ω a) (hstat a)
    simp only [Finset.prod_const, Finset.card_range] at this
    exact this
  refine ⟨fun a k => range_n_iff d a k hd, hcf, ?_, ?_⟩
  · intro a ha hnd
    have hn : n (a + 1) = n a := n_succ d a ha hnd
    rw [hcf (a + 1), hcf a, hn, ← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro k _
    ring
  · intro hd5
    subst hd5
    refine ⟨⟨by decide, by norm_num, by norm_num⟩, ⟨by decide, ?_⟩⟩
    intro k _
    constructor <;> omega

/--
Lean proof endpoint for `prop5_rising_persistenceSpec`.

This theorem is intentionally outside `PaperInterface.lean`: Lean Meta checks
that it has exactly the transparent Spec type, while source-to-Lean semantic
review compares the raw source bundle only to that Spec.
-/
theorem prop5_rising_persistence :
  prop5_rising_persistenceSpec := by
  intro Ω _ w d ρ θ ε lam P h hd hw hw1 hmono hρ n age hrec hstat H Pi R
  have hcf : ∀ a, H a = ∑ k ∈ range (n a), Pi k a * P (a - (k + 1) * d) := fun a =>
    mean_habit_closed_form w d ρ θ ε lam P h a (fun ω => hrec ω a) (hstat a)
  have hPnn : ∀ a k, k < n a → 0 ≤ P (a - (k + 1) * d) := by
    intro a k hk
    have := hstat a (n a - 1 - k) (by omega)
    simp only [age] at this
    rw [show n a - (n a - 1 - k) = k + 1 by omega] at this
    rw [← this]
    exact Finset.sum_nonneg (fun ω _ => mul_nonneg (hw ω) (vote_nonneg _ _))
  refine ⟨hcf, ?_, ?_⟩
  · intro a ha hnd
    have hn : n (a + 1) = n a := n_succ d a ha hnd
    refine ⟨?_, ?_⟩
    · rw [hcf (a + 1), hcf a, hn]
      simp only [R]
      rw [← Finset.sum_add_distrib, ← Finset.sum_sub_distrib]
      apply Finset.sum_congr rfl
      intro k _
      ring
    · apply Finset.sum_nonneg
      intro k hk
      apply mul_nonneg _ (hPnn a k (Finset.mem_range.1 hk))
      apply sub_nonneg.mpr
      apply Finset.prod_le_prod (fun i _ => hρ _)
      intro i _
      exact hmono (Nat.sub_le_sub_right (Nat.le_succ a) _)
  · intro k
    calc ρ 70 ^ k = ∏ i ∈ range k, ρ 70 := by rw [Finset.prod_const, Finset.card_range]
      _ ≤ Pi k (70 + (k + 1) * d) := by
        apply Finset.prod_le_prod (fun i _ => hρ _)
        intro i hi
        apply hmono
        have hik : i < k := Finset.mem_range.1 hi
        have : (i + 1) * d ≤ (k + 1) * d := Nat.mul_le_mul_right d (by omega)
        generalize (i + 1) * d = Y at *
        generalize (k + 1) * d = X at *
        omega

end Arriola26TurnoutGap
