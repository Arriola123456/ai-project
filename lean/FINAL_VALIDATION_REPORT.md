# Final validation report: Arriola26TurnoutGap

**Source.** Manuel Alfredo Arriola Montenegro, *La brecha de participación a los 70 años
sobrestima el efecto del voto obligatorio: ciclo de vida, hábito y una calibración con datos de
la ONPE*. Unpublished manuscript, `paper/paper.pdf` at commit
`feb0cf24c0b8f825861a31c118896c20bb8ec7f2` of `github.com/Arriola123456/ai-project`
(SHA-256 `ff56ddf24e5cd3ea9d1442e52678d51e2bf9c5ed0c428ed9015f5247ff119fb7`).

**Status: formalized with caveat.** Every numbered result of the source (Lemma 1 and
Propositions 1-5, Section 4) has a transparent `...Spec : Prop` in `PaperInterface.lean` and a
closed proof endpoint of exactly that type in `ProofInterface.lean`. `lake build
Arriola26TurnoutGap` and `check Arriola26TurnoutGap --fast` pass; `#print axioms` lists only
`propext`, `Classical.choice` and `Quot.sound` for the six endpoints
(`docs/CHECK_FAST_OUTPUT.txt`).

## Results

| Source result (page) | Spec / endpoint | What the Spec states |
|---|---|---|
| Lemma 1, p. 3 | `lemma1_couplingSpec` / `lemma1_coupling` | With `rho >= 0`, `0 <= lambda <= lambda'` and thresholds `theta <= theta'`, two habit paths that satisfy `h_0 = 0`, `h_{j+1} = rho_j h_j + 1[eps_j < theta_j + lambda h_j]` are ordered, `0 <= h_j <= h'_j`, and so are the votes. |
| Proposition 1, p. 3 | `prop1_lifecycleSpec` / `prop1_lifecycle` | For `A, kappa > 0`, `0 < alpha < 1 <= beta`: `A a^alpha - kappa a^beta` is strictly concave on `(0, inf)`; `a* = (A alpha/(kappa beta))^(1/(beta-alpha)) > 0`, `b'(a*) = 0` and `a*` is the unique maximiser; `b' -> -kappa` if `beta = 1` and `b' -> -inf` if `beta > 1`. |
| Proposition 2, p. 3 | `prop2_jumpSpec` / `prop2_jump` | The past elections of a 70-year-old are at ages below 70; the integrand of `tau70` is the complier indicator; with `G' = g`, `g` unimodal with mode `m`, `S >= 0` and every `c-bar >= m`, `tau70` is non-increasing in `lambda` (habits recomputed for each `lambda`). |
| Proposition 3, p. 3-4 | `prop3_boundSpec` / `prop3_bound` | `P`, `P1` and `P^f` defined from the primitives (cutoff rule, observed and compulsory habit histories at the ages `a - (floor((a-18)/d) - j) d`); under (H) on `P1` and `P^f`, `Delta = tau70 + E + D` with `E >= 0`, `D >= 0`, hence `tau70 <= Delta`. |
| Proposition 4, p. 4 | `prop4_stepsSpec` / `prop4_steps` | Under stationarity (the mean past vote at age `x` equals `P(x)`), the index set `k < floor((a-18)/d)` iff `18 + (k+1)d <= a`; `H(a) = sum_k rho^k P(a-(k+1)d)`; the difference identity when `d` does not divide `a+1-18`; and the 73-74 and 74-75 instances for `d = 5`. |
| Proposition 5, p. 4-5 | `prop5_rising_persistenceSpec` / `prop5_rising_persistence` | With `rho` monotone and non-negative: `H(a) = sum_k Pi_k(a) P(a-(k+1)d)`; the difference identity with the remainder `R(a) = sum_k [Pi_k(a+1) - Pi_k(a)] P(a-(k+1)d) >= 0`; and `Pi_k(70+(k+1)d) >= rho(70)^k`. |

## Caveat

1. **Expectations over a finite population.** The source treats the persistent cost and past
   shocks as continuous random variables. The Specs average over a finite type `Omega` of
   citizens with non-negative weights; today's transitory shock is integrated through `G`.
   The general-measure version needs the monotonicity of the integral and is not done.
2. **Semantic audit lanes not run.** The LLM-as-judge sidecars in `audit/` are the scaffold
   stubs; no context-isolated semantic review or final adversarial audit was run.
3. **Agent and imports.** The run was executed by Claude Code, not by the Codex configuration
   that the course issue names, and the paper modules import five Mathlib modules instead of
   `import Mathlib` / `import AppliedModelingLib` (see `docs/RUN_LOG.md`).

## Finding reported back to the source

Writing Proposition 5 as a Lean statement showed that the draft's version (the identity of
Proposition 4 with products of persistences in place of `rho^k`, and no remainder) is false;
the source was corrected to the remainder form before it was pinned. The source's unstated
assumptions `lambda >= 0`, `S >= 0` and the stationary environment of Propositions 4-5 were
also made explicit before pinning.
