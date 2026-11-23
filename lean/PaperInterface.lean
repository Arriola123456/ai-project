import Arriola26VotingHabit.MainTheorems
import Arriola26VotingHabit.Assumptions

/-!
# Human-Facing Paper Interface: Voto obligatorio a los 70 años: el salto, la edad y la costumbre de votar

This is the compact Lean file a human should read after formalization to check
whether the paper's definitions and named theorem statements were represented
correctly. Keep the row-level dashboard and LLM audit statements in this file
for every paper. Move implementation details, proof aliases, and bulky helper
lemmas behind imported modules such as `AuditInterface.lean`, but expose the
audited paper-facing statements directly here; do not use
`paper_interface.audit_surface_path`.

Rules for completing this file:

- Keep the paper's definitions/formatted objects first, in source order.
- Expose the actual paper formulas here; do not only point to generic library
  definitions or implementation witnesses.
- A material reusable `AppliedModelingLib` primitive may remain a reference here only
  after `audit/library_semantic_review.json` records its exact bounded library
  declaration and an explicit byte-pinned paper-source connection. The
  dashboard and human-review packet show and source-check that declaration
  before the dependent Spec; a library name, docstring, or glossary is not a
  semantic bridge. Do not add a duplicate paper claim merely to restate it.
- If a named theorem needs a hypothesis that is not derived from earlier Lean
  declarations, declare that hypothesis in `Assumptions.lean` and list it in
  `status.json` `review_surface.assumption_names`.
- Then state the named results directly, with assumptions visible in each
  theorem signature by referencing named paper assumptions imported from
  `Assumptions.lean`.
- In the statement-first phase, write every complete source-facing statement as
  a transparent `<name>Spec : Prop` here, exactly once. Put the paired
  theorem/lemma of that exact type in `ProofInterface.lean`; its temporary
  proof body may be `by sorry` only in a private draft. This separation keeps
  the human semantic surface free of thin wrapper declarations.
- Before drafting that Lean surface, independently inventory every material
  source atom from exact pinned source quote bytes. Do not infer source atoms
  from declaration, binder, field, function, or source-map names.
- Run raw-source-to-expanded-Spec statement matching plus Lean-emitted
  premise/conclusion claim-atom review on the skeleton. The semantic comparison uses
  only byte-pinned source quotes (and separately pinned source context) against
  the expanded transparent Spec; map summaries and proof wrappers are not
  semantic inputs. Then freeze each canonical Lean declaration-manifest digest.
- In the proof phase, replace the `ProofInterface.lean` `sorry` with a short
  proof that calls into `MainTheorems.lean` or lower proof files without
  changing the specification or theorem type. Any specification/type change
  invalidates the freeze and requires a fresh statement audit.
- At formalized closeout, complete the v11 realization receipt: Lean Meta checks
  the theorem has exactly the transparent Spec type; each source atom is bound
  to the elaborated Spec surface; closure traversal includes proof and instance
  arguments; and every material terminal has a source, approved correction or
  additional assumption, checked derivation, or version-pinned foundation
  disposition. No data, container, or identifier-based exemption is allowed.
- The transparent `...Spec` is the sole semantic-review target for its source
  claim. The paired theorem/lemma is a proof endpoint whose exact Spec type is
  verified by Lean Meta, not a duplicate source-to-Lean comparison row.
- Keep proof endpoints, exhaustive endpoint aliases, and proof-seam checks in
  `ProofInterface.lean`, implementation modules, or `ProofLedger.lean`, not
  here. Do not create new `PostPaperAudit.lean` or `AuditLedger.lean` files;
  those names are legacy.

## Named Results

Each entry has one semantic-review target (`Spec`) and one proof endpoint (the
paired theorem/lemma). The human dashboard and review packet present that pair
once rather than treating the two declarations as duplicate paper claims.

- `lemma1_couplingSpec` -> `lemma1_coupling`: Lema 1 (Acoplamiento del hábito), Section 4 (Resultados), page 4: Lema 1 (Acoplamiento del hábito); the definition of the thresholds θj on page 4.
- `prop1_lifecycleSpec` -> `prop1_lifecycle`: Proposición 1 (Ciclo de vida), Section 4 (Resultados), page 4: Proposición 1 (Ciclo de vida).
- `prop2_jumpSpec` -> `prop2_jump`: Proposición 2 (El salto no contiene hábito y el hábito lo achica), Section 4 (Resultados), page 4: Proposición 2 (El salto no contiene hábito y el hábito lo achica); the definition of the thresholds θj on page 4.
- `prop3_stepsSpec` -> `prop3_steps`: Proposición 3 (La huella del hábito: escalones cada d años), Section 4 (Resultados), page 5: Proposición 3 (La huella del hábito: escalones cada d años); the stationarity paragraph before Proposición 3 on page 5.
- `prop4_rising_persistenceSpec` -> `prop4_rising_persistence`: Proposición 4 (Persistencia creciente con la edad), Section 4 (Resultados), page 5: Proposición 4 (Persistencia creciente con la edad); the stationarity paragraph before Proposición 3 on page 5.
- `remark1_heterogeneitySpec` -> `remark1_heterogeneity`: Observación 1 (Heterogeneidad cuando la mayoría vota), Section 4 (Resultados), page 6: Observación 1 (Heterogeneidad cuando la mayoría vota); the comparative-statics paragraph and equation (5) on page 6.
-/

namespace Arriola26VotingHabit

/--
Lema 1 (Acoplamiento del hábito)

Paper statement: Lema 1 (Acoplamiento del hábito). Fije ηi y los shocks (εi1 , εi2 , . . . ) de un ciudadano, y sean (hj ) y (h′j ) sus trayectorias de hábito en dos entornos con 0 ≤ λ ≤ λ′ y θj ≤ θj′ en cada elección j . Entonces 0 ≤ hj ≤ h′j para cada j , y si el ciudadano vota en j en el primer entorno, también vota en el segundo.

Source location: Section 4 (Resultados), page 4: Lema 1 (Acoplamiento del hábito); the definition of the thresholds θj on page 4
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def lemma1_couplingSpec : Prop :=
  ∀ (ρ θ θ' ε : ℕ → ℝ) (lam lam' : ℝ) (h h' : ℕ → ℝ),
      (∀ j, 0 ≤ ρ j) → 0 ≤ lam → lam ≤ lam' → (∀ j, θ j ≤ θ' j) →
      h 0 = 0 → (∀ j, h (j + 1) = ρ j * h j + (if ε j < θ j + lam * h j then 1 else 0)) →
      h' 0 = 0 → (∀ j, h' (j + 1) = ρ j * h' j + (if ε j < θ' j + lam' * h' j then 1 else 0)) →
      ∀ j, 0 ≤ h j ∧ h j ≤ h' j ∧
        (if ε j < θ j + lam * h j then (1 : ℝ) else 0) ≤
          (if ε j < θ' j + lam' * h' j then 1 else 0)

/--
Proposición 1 (Ciclo de vida)

Paper statement: Proposición 1 (Ciclo de vida). Bajo el Supuesto 1, b es estrictamente cóncava en a > 0 y alcanza su máximo único en a∗ = (︂ Aα κβ )︂1/(β−α) . Si β = 1, b′ (a) → −κ cuando a → ∞: la caída del bene cio se vuelve lineal. Si β > 1, b′ (a) → −∞: la caída se acelera.

Source location: Section 4 (Resultados), page 4: Proposición 1 (Ciclo de vida)
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def prop1_lifecycleSpec : Prop :=
  ∀ (A α κ β : ℝ), 0 < A → 0 < κ → 0 < α → α < 1 → 1 ≤ β →
      let b : ℝ → ℝ := fun a => A * a ^ α - κ * a ^ β
      let astar : ℝ := (A * α / (κ * β)) ^ (1 / (β - α))
      StrictConcaveOn ℝ (Set.Ioi 0) b ∧ 0 < astar ∧ deriv b astar = 0 ∧
      (∀ a, 0 < a → a ≠ astar → b a < b astar) ∧
      (β = 1 → Filter.Tendsto (deriv b) Filter.atTop (nhds (-κ))) ∧
      (1 < β → Filter.Tendsto (deriv b) Filter.atTop Filter.atBot)

/--
Proposición 2 (El salto no contiene hábito y el hábito lo achica)

Paper statement: Proposición 2 (El salto no contiene hábito y el hábito lo achica). Bajo los Supuestos 14, el hábito de quien tiene 70 años se acumuló bajo obligación, y τ 70 en (3) es la masa de cumplidores condicional en ese hábito. Si gε es unimodal con moda m y c̄ ≥ m en cada punto del soporte de (η, h70 ), entonces τ 70 es no creciente en λ: el hábito atenúa el salto.

Source location: Section 4 (Resultados), page 4: Proposición 2 (El salto no contiene hábito y el hábito lo achica); the definition of the thresholds θj on page 4
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def prop2_jumpSpec : Prop :=
  (∀ d : ℕ, 1 ≤ d → ∀ j, j < (70 - 18) / d → 70 - ((70 - 18) / d - j) * d < 70) ∧
    (∀ c S e : ℝ, 0 ≤ S →
      (if e < c + S then (1 : ℝ) else 0) - (if e < c then 1 else 0) =
        if c ≤ e ∧ e < c + S then 1 else 0) ∧
    (∀ {Ω : Type} [Fintype Ω] (w : Ω → ℝ) (n : ℕ) (ρ : ℕ → ℝ) (θ ε : Ω → ℕ → ℝ)
        (B : Ω → ℝ) (S m lam lam' : ℝ) (G g : ℝ → ℝ) (h : Ω → ℝ → ℕ → ℝ),
      (∀ ω, 0 ≤ w ω) → (∀ j, 0 ≤ ρ j) → 0 ≤ S → 0 ≤ lam → lam ≤ lam' →
      (∀ x, HasDerivAt G (g x) x) → MonotoneOn g (Set.Iic m) → AntitoneOn g (Set.Ici m) →
      (∀ ω l, h ω l 0 = 0 ∧
        ∀ j, h ω l (j + 1) = ρ j * h ω l j + (if ε ω j < θ ω j + l * h ω l j then 1 else 0)) →
      (∀ ω, m ≤ B ω + lam * h ω lam n) →
      let τ : ℝ → ℝ := fun l => ∑ ω, w ω * (G (B ω + l * h ω l n + S) - G (B ω + l * h ω l n))
      τ lam' ≤ τ lam)

/--
Proposición 3 (La huella del hábito: escalones cada d años)

Paper statement: Proposición 3 (La huella del hábito: escalones cada d años). Bajo los Supuestos 14, con ρ constante y un entorno estacionario, H(a) = ∑︂ ρk P (a − (k + 1)d). k≥0, a−(k+1)d≥18 Si además a ≥ 18 y a + 1 − 18 no es múltiplo de d, ∑︂ [︁ ]︁ ρk P (a + 1 − (k + 1)d) − P (a − (k + 1)d) . H(a + 1) − H(a) = k≥0, a−(k+1)d≥18 En particular, con d = 5, entre 74 y 75 años el término k = 0 es P (70)−P (69), que contiene el salto en el umbral, y entre 73 y 74 todos los términos son diferencias de un año entre edades obligadas.

Source location: Section 4 (Resultados), page 5: Proposición 3 (La huella del hábito: escalones cada d años); the stationarity paragraph before Proposición 3 on page 5
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def prop3_stepsSpec : Prop :=
  ∀ {Ω : Type} [Fintype Ω] (w : Ω → ℝ) (d : ℕ) (r : ℝ) (θ ε : Ω → ℕ → ℕ → ℝ) (lam : ℝ)
      (P : ℕ → ℝ) (h : Ω → ℕ → ℕ → ℝ),
      1 ≤ d → (∀ ω, 0 ≤ w ω) → ∑ ω, w ω = 1 →
      let n : ℕ → ℕ := fun a => (a - 18) / d
      let age : ℕ → ℕ → ℕ := fun a j => a - (n a - j) * d
      (∀ ω a, h ω a 0 = 0 ∧ ∀ j, h ω a (j + 1) = r * h ω a j +
        (if ε ω a j < θ ω a j + lam * h ω a j then 1 else 0)) →
      (∀ a j, j < n a →
        ∑ ω, w ω * (if ε ω a j < θ ω a j + lam * h ω a j then 1 else 0) = P (age a j)) →
      let H : ℕ → ℝ := fun a => ∑ ω, w ω * h ω a (n a)
      (∀ a k, k ∈ Finset.range (n a) ↔ 18 + (k + 1) * d ≤ a) ∧
      (∀ a, H a = ∑ k ∈ Finset.range (n a), r ^ k * P (a - (k + 1) * d)) ∧
      (∀ a, 18 ≤ a → ¬ d ∣ (a + 1 - 18) →
        H (a + 1) - H a = ∑ k ∈ Finset.range (n a), r ^ k * (P (a + 1 - (k + 1) * d) - P (a - (k + 1) * d))) ∧
      (d = 5 → (¬ d ∣ (74 + 1 - 18) ∧ 74 + 1 - (0 + 1) * d = 70 ∧ 74 - (0 + 1) * d = 69) ∧
        (¬ d ∣ (73 + 1 - 18) ∧ ∀ k ∈ Finset.range (n 73), 73 + 1 - (k + 1) * d < 70 ∧ 73 - (k + 1) * d < 70))

/--
Proposición 4 (Persistencia creciente con la edad)

Paper statement: Proposición 4 (Persistencia creciente con la edad) ∏︁ . Bajo los supuestos de la Proposición 3, pero k con ∑︁ ρ no decreciente en la edad, sea Πk (a) = j=1 ρ(a − jd), con Π0 (a) = 1. Entonces H(a) = k≥0, a−(k+1)d≥18 Πk (a)P (a − (k + 1)d) y, si a + 1 − 18 no es múltiplo de d, H(a + 1) − H(a) = ∑︂ [︁ ]︁ Πk (a + 1) P (a + 1 − (k + 1)d) − P (a − (k + 1)d) + R(a), k R(a) = ∑︂[︁ ]︁ Πk (a + 1) − Πk (a) P (a − (k + 1)d) ≥ 0, k con las sumas sobre k ≥ 0 y a−(k+1)d ≥ 18. Con ρ constante, R = 0 y se recupera la Proposición 3. En el escalón entre 70 ∏︁ + (k + 1)d − 1 y 70 + (k + 1)d, la diferencia P (70) − P (69) entra con peso Πk (70 + (k + 1)d) = ki=1 ρ(70 + id) ≥ ρ(70)k : el salto se propaga al menos tanto como con ρ constante igual a ρ(70).

Source location: Section 4 (Resultados), page 5: Proposición 4 (Persistencia creciente con la edad); the stationarity paragraph before Proposición 3 on page 5
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def prop4_rising_persistenceSpec : Prop :=
  ∀ {Ω : Type} [Fintype Ω] (w : Ω → ℝ) (d : ℕ) (ρ : ℕ → ℝ) (θ ε : Ω → ℕ → ℕ → ℝ) (lam : ℝ)
      (P : ℕ → ℝ) (h : Ω → ℕ → ℕ → ℝ),
      1 ≤ d → (∀ ω, 0 ≤ w ω) → ∑ ω, w ω = 1 → Monotone ρ → (∀ x, 0 ≤ ρ x) →
      let n : ℕ → ℕ := fun a => (a - 18) / d
      let age : ℕ → ℕ → ℕ := fun a j => a - (n a - j) * d
      (∀ ω a, h ω a 0 = 0 ∧ ∀ j, h ω a (j + 1) = ρ (age a j) * h ω a j +
        (if ε ω a j < θ ω a j + lam * h ω a j then 1 else 0)) →
      (∀ a j, j < n a →
        ∑ ω, w ω * (if ε ω a j < θ ω a j + lam * h ω a j then 1 else 0) = P (age a j)) →
      let H : ℕ → ℝ := fun a => ∑ ω, w ω * h ω a (n a)
      let Pi : ℕ → ℕ → ℝ := fun k a => ∏ i ∈ Finset.range k, ρ (a - (i + 1) * d)
      let R : ℕ → ℝ := fun a => ∑ k ∈ Finset.range (n a), (Pi k (a + 1) - Pi k a) * P (a - (k + 1) * d)
      (∀ a, H a = ∑ k ∈ Finset.range (n a), Pi k a * P (a - (k + 1) * d)) ∧
      (∀ a, 18 ≤ a → ¬ d ∣ (a + 1 - 18) →
        H (a + 1) - H a =
          ∑ k ∈ Finset.range (n a), Pi k (a + 1) * (P (a + 1 - (k + 1) * d) - P (a - (k + 1) * d)) + R a ∧
        0 ≤ R a) ∧
      (∀ k, ρ 70 ^ k ≤ Pi k (70 + (k + 1) * d))

/--
Observación 1 (Heterogeneidad cuando la mayoría vota)

Paper statement: Observación 1 (Heterogeneidad cuando la mayoría vota). Con F = Φ normal, z ϕ(z) es creciente en [0, 1] y decreciente en [1, ∞), y z = 1 corresponde a una participación de Φ(1) = 0.841. Por ciudadano, con z0 < z1 : (a) si P0 ≤ 0.50 < P1 , ∂τ /∂s < 0; (b) si 0.50 < P0 < P1 ≤ 0.841, ∂τ /∂s < 0; (c) si 0.841 ≤ P0 < P1 , ∂τ /∂s > 0; y (d) si 0.50 < P0 < 0.841 < P1 , existe un único z1∗ > 1 con z1∗ ϕ(z1∗ ) = z0 ϕ(z0 ), y ∂τ /∂s < 0 si y solo si P1 < P1∗ = Φ(z1∗ ). Con P0 = 0.78, z0 = 0.772, z1∗ = 1.247 y P1∗ = 0.894: si P1 (70) < 0.894, más heterogeneidad achica el salto; si P1 (70) > 0.894, lo agranda.

Source location: Section 4 (Resultados), page 6: Observación 1 (Heterogeneidad cuando la mayoría vota); the comparative-statics paragraph and equation (5) on page 6
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def remark1_heterogeneitySpec : Prop :=
  ∀ (Φ : ℝ → ℝ),
    let φ : ℝ → ℝ := fun z => Real.exp (-(z ^ 2) / 2) / Real.sqrt (2 * Real.pi)
    (∀ x, HasDerivAt Φ (φ x) x) → Φ 0 = 1 / 2 →
    let τ : ℝ → ℝ → ℝ → ℝ := fun c S s => Φ ((c + S) / s) - Φ (c / s)
    (∀ c S s, 0 < s →
      HasDerivAt (fun s' => τ c S s')
        (-(1 / s) * ((c + S) / s * φ ((c + S) / s) - c / s * φ (c / s))) s) ∧
    StrictMonoOn (fun z => z * φ z) (Set.Icc 0 1) ∧
    StrictAntiOn (fun z => z * φ z) (Set.Ici 1) ∧
    (∀ c S s, 0 < s → 0 < S →
      let z0 := c / s
      let z1 := (c + S) / s
      ((Φ z0 ≤ 1 / 2 ∧ 1 / 2 < Φ z1) → deriv (fun s' => τ c S s') s < 0) ∧
      ((1 / 2 < Φ z0 ∧ Φ z1 ≤ Φ 1) → deriv (fun s' => τ c S s') s < 0) ∧
      (Φ 1 ≤ Φ z0 → 0 < deriv (fun s' => τ c S s') s) ∧
      ((1 / 2 < Φ z0 ∧ Φ z0 < Φ 1 ∧ Φ 1 < Φ z1) →
        ∃! z1s : ℝ, 1 < z1s ∧ z1s * φ z1s = z0 * φ z0 ∧
          (deriv (fun s' => τ c S s') s < 0 ↔ Φ z1 < Φ z1s)))

end Arriola26VotingHabit
