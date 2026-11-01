import Arriola26TurnoutGap.MainTheorems
import Arriola26TurnoutGap.Assumptions

/-!
# Human-Facing Paper Interface: La brecha de participación a los 70 años sobrestima el efecto del voto obligatorio: ciclo de vida, hábito y una calibración con datos de la ONPE

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

- `lemma1_couplingSpec` -> `lemma1_coupling`: Lema 1 (Acoplamiento del hábito), Section 4 (Resultados), page 3: Lema 1 (Acoplamiento del hábito).
- `prop1_lifecycleSpec` -> `prop1_lifecycle`: Proposición 1 (Ciclo de vida), Section 4 (Resultados), page 3: Proposición 1 (Ciclo de vida).
- `prop2_jumpSpec` -> `prop2_jump`: Proposición 2 (El salto no contiene hábito), Section 4 (Resultados), page 3: Proposición 2 (El salto no contiene hábito); the stationarity paragraph (or the definition of the thresholds) on page 3.
- `prop3_boundSpec` -> `prop3_bound`: Proposición 3 (La brecha es una cota superior), Section 4 (Resultados), page 3: Proposición 3 (La brecha es una cota superior).
- `prop4_stepsSpec` -> `prop4_steps`: Proposición 4 (La huella del hábito), Section 4 (Resultados), page 4: Proposición 4 (La huella del hábito); the stationarity paragraph (or the definition of the thresholds) on page 4.
- `prop5_rising_persistenceSpec` -> `prop5_rising_persistence`: Proposición 5 (Persistencia creciente con la edad), Section 4 (Resultados), page 4: Proposición 5 (Persistencia creciente con la edad); the stationarity paragraph (or the definition of the thresholds) on page 4.
-/

namespace Arriola26TurnoutGap

/--
Lema 1 (Acoplamiento del hábito)

Paper statement: Lema 1 (Acoplamiento del hábito). Fije ηi y los shocks (εi1 , εi2 , . . . ) de un ciudadano, y sean (hj ) y (h′j ) sus trayectorias de hábito en dos entornos con 0 ≤ λ ≤ λ′ y θj ≤ θj′ en cada elección j . Entonces 0 ≤ hj ≤ h′j para cada j , y si el ciudadano vota en j en el primer entorno, también vota en el segundo.

Source location: Section 4 (Resultados), page 3: Lema 1 (Acoplamiento del hábito)
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

Paper statement: Proposición 1 (Ciclo de vida). Bajo el Supuesto 1, b es estrictamente cóncava en a > 0 y alcanza su máximo único en (︂ )︂1/(β−α) a∗ = Aα κβ . Si β = 1, b′ (a) → −κ cuando a → ∞: la caída del bene cio se vuelve lineal. Si β > 1, b′ (a) → −∞: la caída se acelera.

Source location: Section 4 (Resultados), page 3: Proposición 1 (Ciclo de vida)
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
Proposición 2 (El salto no contiene hábito)

Paper statement: Las Proposiciones 2 y 3 comparan trayectorias de hábito de un mismo ciudadano bajo dos entornos. Sea θj = b(aj ) + Oaj Sj − µj − ηi el umbral de la elección j , sin el hábito, para un ciudadano que en ella tiene edad aj . [...] Proposición 2 (El salto no contiene hábito). Bajo los Supuestos 14, el hábito de quien tiene 70 años se acumuló bajo obligación, y τ 70 en (3) es la masa de cumplidores condicional en ese hábito. Si gε es unimodal con moda m y c̄ ≥ m en cada punto del soporte de (η, h70 ), entonces τ 70 es no creciente en λ: el hábito atenúa el salto.

Source location: Section 4 (Resultados), page 3: Proposición 2 (El salto no contiene hábito); the stationarity paragraph (or the definition of the thresholds) on page 3
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
Proposición 3 (La brecha es una cota superior)

Paper statement: Proposición 3 (La brecha es una cota superior). Bajo los Supuestos 14, sea P1 (a) la participación a la edad a si la elección actual fuera obligatoria para esa edad, de modo que P1 (a) = P (a) si a < 70. Para a ≥ 70, sea P f (a) la participación de esos mismos ciudadanos si hubieran estado obligados en todas las elecciones anteriores y libres en la actual. Suponga (H): P1 es no creciente en [60, 70] y P f es no creciente en [70, ∞). Entonces ∆ = τ 70 + E + D ≥ τ 70 , 3 f donde el envejecimiento E = [P̄6069 − P1 (70)] + [P f (70) − P̄70+ ] ≥ 0 y el decaimiento del hábito f D = P̄70+ − P̄70+ ≥ 0, y las barras son promedios ponderados por electores dentro de cada grupo. La condición (H) no se sigue de a∗ ≤ 60: si el hábito todavía se acumula entre los 60 y los 70 años, b(a) + λE[ha ] puede crecer aunque b decrezca.

Source location: Section 4 (Resultados), page 3: Proposición 3 (La brecha es una cota superior)
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def prop3_boundSpec : Prop :=
  ∀ {Ω : Type} [Fintype Ω] (w : Ω → ℝ) (d amax : ℕ) (ρ : ℕ → ℝ) (base : Ω → ℕ → ℝ)
      (ε : Ω → ℕ → ℕ → ℝ) (S lam : ℝ) (G : ℝ → ℝ) (wb wv : ℕ → ℝ)
      (hobs hcomp : Ω → ℕ → ℕ → ℝ),
      1 ≤ d → (∀ ω, 0 ≤ w ω) → (∀ x, 0 ≤ ρ x) → 0 ≤ S → 0 ≤ lam → Monotone G →
      (∀ a, 0 ≤ wb a) → (∀ a, 0 ≤ wv a) →
      ∑ a ∈ Finset.Icc 60 69, wb a = 1 → ∑ a ∈ Finset.Icc 70 amax, wv a = 1 →
      let n : ℕ → ℕ := fun a => (a - 18) / d
      let age : ℕ → ℕ → ℕ := fun a j => a - (n a - j) * d
      let O : ℕ → ℝ := fun x => if x < 70 then 1 else 0
      (∀ ω a, hobs ω a 0 = 0 ∧ ∀ j, hobs ω a (j + 1) = ρ (age a j) * hobs ω a j +
        (if ε ω a j < base ω (age a j) + O (age a j) * S + lam * hobs ω a j then 1 else 0)) →
      (∀ ω a, hcomp ω a 0 = 0 ∧ ∀ j, hcomp ω a (j + 1) = ρ (age a j) * hcomp ω a j +
        (if ε ω a j < base ω (age a j) + S + lam * hcomp ω a j then 1 else 0)) →
      let P : ℕ → ℝ := fun a => ∑ ω, w ω * G (base ω a + O a * S + lam * hobs ω a (n a))
      let P1 : ℕ → ℝ := fun a => ∑ ω, w ω * G (base ω a + S + lam * hobs ω a (n a))
      let Pf : ℕ → ℝ := fun a => ∑ ω, w ω * G (base ω a + lam * hcomp ω a (n a))
      (∀ a a', 60 ≤ a → a ≤ a' → a' ≤ 70 → P1 a' ≤ P1 a) →
      (∀ a a', 70 ≤ a → a ≤ a' → Pf a' ≤ Pf a) →
      let Δ := ∑ a ∈ Finset.Icc 60 69, wb a * P a - ∑ a ∈ Finset.Icc 70 amax, wv a * P a
      let τ := P1 70 - P 70
      let E := (∑ a ∈ Finset.Icc 60 69, wb a * P1 a - P1 70) + (Pf 70 - ∑ a ∈ Finset.Icc 70 amax, wv a * Pf a)
      let D := ∑ a ∈ Finset.Icc 70 amax, wv a * Pf a - ∑ a ∈ Finset.Icc 70 amax, wv a * P a
      Δ = τ + E + D ∧ 0 ≤ E ∧ 0 ≤ D ∧ τ ≤ Δ

/--
Proposición 4 (La huella del hábito)

Paper statement: Las Proposiciones 4 y 5 necesitan un supuesto más, que la calibración ya usa: el entorno es estacionario, con µt = µ y St = S en la elección actual y en todas las anteriores. Así, la participación a la edad x en una elección pasada es la misma P (x) de hoy. Sea H(a) = E[h] entre los ciudadanos de edad a. Todos ellos votaron antes a las edades a − d, a − 2d, . . . que son al menos 18. [...] Proposición 4 (La huella del hábito). Bajo los Supuestos 14, con ρ constante y un entorno estacionario, ∑︂ H(a) = ρk P (a − (k + 1)d). k≥0, a−(k+1)d≥18 Si además a ≥ 18 y a + 1 − 18 no es múltiplo de d, ∑︂ ρk P (a + 1 − (k + 1)d) − P (a − (k + 1)d) . [︁ ]︁ H(a + 1) − H(a) = k≥0, a−(k+1)d≥18 En particular, entre 74 y 75 años el término k = 0 es P (70) − P (69), que contiene el salto en el umbral, y entre 73 y 74 todos los términos son diferencias de un año entre edades obligadas.

Source location: Section 4 (Resultados), page 4: Proposición 4 (La huella del hábito); the stationarity paragraph (or the definition of the thresholds) on page 4
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def prop4_stepsSpec : Prop :=
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
Proposición 5 (Persistencia creciente con la edad)

Paper statement: Las Proposiciones 4 y 5 necesitan un supuesto más, que la calibración ya usa: el entorno es estacionario, con µt = µ y St = S en la elección actual y en todas las anteriores. Así, la participación a la edad x en una elección pasada es la misma P (x) de hoy. Sea H(a) = E[h] entre los ciudadanos de edad a. Todos ellos votaron antes a las edades a − d, a − 2d, . . . que son al menos 18. [...] Proposición 5 (Persistencia creciente con la edad) ∏︁ . Bajo los supuestos de la Proposición 4, pero k con ∑︁ ρ no decreciente en la edad, sea Πk (a) = j=1 ρ(a − jd), con Π0 (a) = 1. Entonces H(a) = k≥0, a−(k+1)d≥18 Πk (a)P (a − (k + 1)d) y, si a + 1 − 18 no es múltiplo de d, ∑︂ [︁ ]︁ H(a + 1) − H(a) = Πk (a + 1) P (a + 1 − (k + 1)d) − P (a − (k + 1)d) + R(a), k ∑︂[︁ ]︁ R(a) = Πk (a + 1) − Πk (a) P (a − (k + 1)d) ≥ 0, k 4 con las sumas sobre k ≥ 0 y a−(k+1)d ≥ 18. Con ρ constante, R = 0 y se recupera la Proposición 4. En el escalón entre 70 ∏︁ + (k + 1)d − 1 y 70 + (k + 1)d, la diferencia P (70) − P (69) entra con peso Πk (70 + (k + 1)d) = ki=1 ρ(70 + id) ≥ ρ(70)k : el salto se propaga al menos tanto como con ρ constante igual a ρ(70).

Source location: Section 4 (Resultados), page 4: Proposición 5 (Persistencia creciente con la edad); the stationarity paragraph (or the definition of the thresholds) on page 4
Source status: pinned statement-spec transcription; independent source audit pending

This transparent proposition is the exact statement-audit target. It is not
proof evidence. Its exact-type proof endpoint is declared in
`ProofInterface.lean`, so this human-facing file presents the full semantic
proposition once. At closeout, source atoms must be independently inventoried
from pinned source quote bytes and bound to this elaborated proposition rather
than inferred from identifiers.
-/
def prop5_rising_persistenceSpec : Prop :=
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

end Arriola26TurnoutGap
