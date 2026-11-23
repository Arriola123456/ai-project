# Run log for `papers/Arriola26VotingHabit` (student run, 2026-11-23)

This note records how this paper folder was produced. It replaces the earlier run
`Arriola26TurnoutGap` (2026-10-31), which formalized a draft of the paper (commit `feb0cf2`)
with a different numbering and a proposition that the final paper retires.

## Agent and tools

**Claude Code (Claude Opus 5.5, Anthropic)**, driven by the student from Windows, in the
WSL2 Ubuntu 26.04 clone of AppliedModelingLib (`nikhgarg/EconCSLib`) at `194edcc9`; Lean
`v4.30.0-rc2`. **Not Codex.** Issue #7 of the course asks for GPT-5.6 Sol (`gpt-5.6-sol`,
effort `xhigh`). The student asked Claude Code to do the run ("haz tu la corrida de lean");
this is disclosed in the course repository's `prompts.md` and in the paper's appendices.

## Source

The student's own unpublished manuscript, `paper/paper.pdf` of
`https://github.com/Arriola123456/ai-project` at commit `7fa3a62e4e8f161ddfc1412f53b1eb8fa008ceb1`
(`https://github.com/Arriola123456/ai-project/blob/7fa3a62e4e8f161ddfc1412f53b1eb8fa008ceb1/paper/paper.pdf`),
SHA-256 `6c8a6837e3fc254d7f853e617d7e4005430db8251a8394b57e83195710f75db0`. There is no arXiv record.

## Steps

1. **Carried over from the earlier run.** Lemma 1 and Propositions 1-2 of the final paper have
   the same content as in the draft, and Propositions 3-4 (steps; rising persistence) are the
   draft's Propositions 4-5. Their Lean types are reused verbatim and renamed
   (`prop4_steps` -> `prop3_steps`, `prop5_rising_persistence` -> `prop4_rising_persistence`).
   The draft's Proposition 3 (the gap bound, `prop3_bound`) is retired in the final paper and
   has no counterpart here; its helper `habit_congr` was dropped.
2. **New: Observation 1 (heterogeneity).** Its statement was written as a transparent
   `Spec : Prop` and proved in a scratch file with `lake env lean` before the scaffold. The
   standard normal density is written out, `phi(z) = exp(-z^2/2)/sqrt(2 pi)`, and the CDF
   `Phi` is any function with `Phi' = phi` and `Phi(0) = 1/2` (which pins it down).
   `tau(s) = Phi((c+S)/s) - Phi(c/s)` is the comparative-statics object of equation (5).
3. `python3 scripts/paper_contribution.py init-spec paper.pdf --version "..." --output ...`,
   then the six targets were filled by a script: page-level locators, the literal source
   statements extracted with `pdftotext` from the pinned PDF, and the Lean propositions.
4. `python3 scripts/paper_contribution.py new <pinned URL> --folder Arriola26VotingHabit ...
   --statement-spec ...` (exit 0; every Spec Lean-validated by `#assert_scaffold_spec`).
   **Deviation, stated exactly.** The library root `AppliedModelingLib.olean` is not built on
   this machine. For this one command the scaffold's validation import in
   `scripts/new_paper.py` was pointed at the nine Mathlib modules that the paper modules
   import, and the script was restored with `git checkout` right after (the clone shows no
   diff in `scripts/`). `PYTHONPATH=<clone root>` is needed because `new_paper.py` imports
   `scripts.formalization_protocol`.
5. The helper lemmas went to `MainTheorems.lean` and the six proof endpoints to
   `ProofInterface.lean`, with the Spec text untouched. `MainTheorems.lean` imports
   `Mathlib.Tactic`, `Mathlib.Data.Real.Basic`, `Mathlib.Analysis.SpecialFunctions.Pow.Deriv`,
   `Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics`, `Mathlib.Analysis.Convex.Deriv`,
   `Mathlib.Analysis.SpecialFunctions.ExpDeriv`, `Mathlib.Analysis.SpecialFunctions.Sqrt`,
   `Mathlib.Analysis.Calculus.MeanValue` and `Mathlib.Topology.Order.IntermediateValue`
   instead of the scaffold's `import Mathlib`.
6. `lake build Arriola26VotingHabit`: Build completed successfully (3315 jobs).
   `python3 scripts/paper_contribution.py check Arriola26VotingHabit --fast`: exit code 0.
   `#print axioms` on the six endpoints lists only `propext`, `Classical.choice` and
   `Quot.sound`. The outputs are in `docs/CHECK_FAST_OUTPUT.txt`.

## Iteration record

- The scratch proof of Observation 1 needed three passes: a `simp` with no progress in the
  uniqueness step (replaced by an explicit `show ... by rw`), deprecated `push_neg` calls
  (replaced by `simp only [not_lt]` / `[not_le]`) and unused `simp` arguments.
- The first `new` attempt kept the default validation import, because the patch to
  `new_paper.py` was written through a shell heredoc that collapsed `\\n`; the patch was
  rewritten as a Python file and the scaffold then validated at the first try.
- The first build passed; four `show` tactics that changed the goal were replaced by `change`
  to silence the style linter.

## What Lean verifies and what it does not

All six results are proved, with no `sorry`:

- Lemma 1: coupling of habit paths (pointwise order of habits and votes).
- Proposition 1: strict concavity of `A a^alpha - kappa a^beta` on `(0, inf)`, positivity of
  `a*`, `b'(a*) = 0`, `a*` the unique maximiser, and the limits of `b'` for `beta = 1` and
  `beta > 1`.
- Proposition 2: the past elections of a 70-year-old are compulsory, the integrand of
  `tau70` is the complier indicator, and `tau70` is non-increasing in `lambda` when the
  density is unimodal and every `c-bar` is above the mode.
- Proposition 3: the index set, the closed form of the mean habit, the difference identity,
  and the 73-74 and 74-75 instances with `d = 5`.
- Proposition 4: the closed form with products of persistences, the difference identity with
  the remainder `R(a) >= 0`, and the weight bound `rho(70)^k`.
- Observation 1: the derivative of `tau(s)` (equation (5)), `z phi(z)` strictly increasing on
  `[0,1]` and strictly decreasing on `[1, inf)`, and, for `s > 0`, `S > 0`, the sign of
  `d tau / d s` in cases (a), (b) and (c), and in case (d) the unique `z1* > 1` with
  `z1* phi(z1*) = z0 phi(z0)` and `d tau / d s < 0` iff `P1 < Phi(z1*)`.

The representation that is not literally in the paper: expectations over the persistent
cost and the past shocks are weighted averages over a finite population (a `Fintype` of
citizens with non-negative weights); today's transitory shock is integrated through `G`. In
Observation 1 the thresholds `0.50` and `0.841` appear as `Phi(0) = 1/2` and `Phi(1)`; the
decimals (`Phi(1) = 0.841`, `z0 = 0.772`, `z1* = 1.247`, `P1* = 0.894`) are numerical and are
checked by `code/heterogeneity.py`, not by Lean. The calibration, the simulations and the other
numerical claims of the paper are not part of the Lean run; `code/verify.py` checks them.

The audit sidecars under `audit/` are the scaffold-generated stubs; the LLM-as-judge lanes
that populate them were not run.
