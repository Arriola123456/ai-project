# Final validation report: Arriola26VotingHabit

**Source.** Manuel Alfredo Arriola Montenegro, *Voto obligatorio a los 70 años: el salto, la
edad y la costumbre de votar*. Unpublished manuscript, `paper/paper.pdf` at commit
`7fa3a62e4e8f161ddfc1412f53b1eb8fa008ceb1` of `github.com/Arriola123456/ai-project`
(SHA-256 `6c8a6837e3fc254d7f853e617d7e4005430db8251a8394b57e83195710f75db0`).

**Status: formalized with caveat.** Every numbered result of the source (Lemma 1 and
Propositions 1-4, Section 4) and Observation 1 has a transparent `...Spec : Prop` in
`PaperInterface.lean` and a closed proof endpoint of exactly that type in
`ProofInterface.lean`. `lake build Arriola26VotingHabit` and `check Arriola26VotingHabit
--fast` pass; `#print axioms` lists only `propext`, `Classical.choice` and `Quot.sound` for
the six endpoints (`docs/CHECK_FAST_OUTPUT.txt`).

## Results

| Source result (page) | Spec / endpoint | What the Spec states |
|---|---|---|
| Lemma 1, p. 4 | `lemma1_couplingSpec` / `lemma1_coupling` | With `rho >= 0`, `0 <= lambda <= lambda'` and thresholds `theta <= theta'`, two habit paths that satisfy `h_0 = 0`, `h_{j+1} = rho_j h_j + 1[eps_j < theta_j + lambda h_j]` are ordered, `0 <= h_j <= h'_j`, and so are the votes. |
| Proposition 1, p. 4 | `prop1_lifecycleSpec` / `prop1_lifecycle` | For `A, kappa > 0`, `0 < alpha < 1 <= beta`: `A a^alpha - kappa a^beta` is strictly concave on `(0, inf)`; `a* = (A alpha/(kappa beta))^(1/(beta-alpha)) > 0`, `b'(a*) = 0` and `a*` is the unique maximiser; `b' -> -kappa` if `beta = 1` and `b' -> -inf` if `beta > 1`. |
| Proposition 2, p. 4 | `prop2_jumpSpec` / `prop2_jump` | The past elections of a 70-year-old are at ages below 70; the integrand of `tau70` is the complier indicator; with `G' = g`, `g` unimodal with mode `m`, `S >= 0` and every `c-bar >= m`, `tau70` is non-increasing in `lambda` (habits recomputed for each `lambda`). |
| Proposition 3, p. 5 | `prop3_stepsSpec` / `prop3_steps` | Under stationarity (the mean past vote at age `x` equals `P(x)`), the index set `k < floor((a-18)/d)` iff `18 + (k+1)d <= a`; `H(a) = sum_k rho^k P(a-(k+1)d)`; the difference identity when `d` does not divide `a+1-18`; and the 73-74 and 74-75 instances for `d = 5`. |
| Proposition 4, p. 5 | `prop4_rising_persistenceSpec` / `prop4_rising_persistence` | With `rho` monotone and non-negative: `H(a) = sum_k Pi_k(a) P(a-(k+1)d)`; the difference identity with the remainder `R(a) = sum_k [Pi_k(a+1) - Pi_k(a)] P(a-(k+1)d) >= 0`; and `Pi_k(70+(k+1)d) >= rho(70)^k`. |
| Observation 1, p. 6 | `remark1_heterogeneitySpec` / `remark1_heterogeneity` | With `phi` the standard normal density and `Phi' = phi`, `Phi(0) = 1/2`: the derivative of `tau(s) = Phi((c+S)/s) - Phi(c/s)` is `-(1/s)[z1 phi(z1) - z0 phi(z0)]`; `z phi(z)` is strictly increasing on `[0,1]` and strictly decreasing on `[1, inf)`; for `s, S > 0`, cases (a)-(c) give the sign of `d tau / d s`, and in case (d) there is a unique `z1* > 1` with `z1* phi(z1*) = z0 phi(z0)`, and `d tau / d s < 0` iff `P1 < Phi(z1*)`. |

## Caveat

1. **Expectations over a finite population.** The source treats the persistent cost and past
   shocks as continuous random variables. The Specs average over a finite type `Omega` of
   citizens with non-negative weights; today's transitory shock is integrated through `G`.
   The general-measure version needs the monotonicity of the integral and is not done.
2. **Decimals in Observation 1.** The thresholds `0.50` and `0.841` are stated as `Phi(0)` and
   `Phi(1)`; the decimals and the 2016 example (`z0 = 0.772`, `z1* = 1.247`, `P1* = 0.894`) are
   numerical and are checked in `code/heterogeneity.py`, not in Lean.
3. **Semantic audit lanes not run.** The LLM-as-judge sidecars in `audit/` are the scaffold
   stubs; no context-isolated semantic review or final adversarial audit was run.
4. **Agent and imports.** The run was executed by Claude Code, not by the Codex configuration
   that the course issue names, and the paper modules import nine Mathlib modules instead of
   `import Mathlib` / `import AppliedModelingLib` (see `docs/RUN_LOG.md`).

## Relation to the earlier run

The earlier run (`Arriola26TurnoutGap`, draft commit `feb0cf2`) found that the draft's
rising-persistence identity needed the remainder `R(a) >= 0`; that correction is in the final
paper and in Proposition 4 here. Its Proposition 3 (the gap bound) is retired in the final
paper, because with exact-age data the jump is measured directly.
