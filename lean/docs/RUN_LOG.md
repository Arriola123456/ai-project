# Run log for `papers/Arriola26TurnoutGap` (student run, 2026-10-31)

This note records how this paper folder was produced.

## Agent and tools

**Claude Code (Claude Opus 5.5, Anthropic)**, driven by the student from Windows, in the
WSL2 Ubuntu 26.04 clone of AppliedModelingLib (`nikhgarg/EconCSLib`), pulled to
`194edcc9` on 2026-10-31 before the run; Lean `v4.30.0-rc2`. **Not Codex.** Issue #7 of the
course asks for GPT-5.6 Sol (`gpt-5.6-sol`, effort `xhigh`). As in Repositories 5 and 6, the
student chose Claude Code instead; this is disclosed in the course repository's
`prompts.md` and in the paper's appendices.

## Source

The student's own unpublished manuscript, `paper/paper.pdf` of
`https://github.com/Arriola123456/ai-project` at commit `feb0cf24c0b8f825861a31c118896c20bb8ec7f2`
(`https://github.com/Arriola123456/ai-project/blob/feb0cf24c0b8f825861a31c118896c20bb8ec7f2/paper/paper.pdf`),
SHA-256 `ff56ddf24e5cd3ea9d1442e52678d51e2bf9c5ed0c428ed9015f5247ff119fb7`. There is no arXiv record.

## Steps

1. Before the scaffold, the six statements (Lemma 1 and Propositions 1-5) were written as
   transparent `Spec : Prop` declarations over the model primitives and proved in a scratch
   file with `lake env lean`. Writing Proposition 5 this way exposed an error in the paper
   draft: with age-dependent persistence the identity of Proposition 4 does not hold with the
   products of persistences alone; it needs the remainder `R(a) >= 0`. The paper was
   corrected (and its unstated assumptions `lambda >= 0`, `S >= 0` and the stationary
   environment of Propositions 4-5 were made explicit) **before** it was committed and pinned.
2. `python3 scripts/paper_contribution.py init-spec paper.pdf --version "..."`, then the
   statement spec was filled with the six targets: page-level locators, the literal source
   statements extracted from the pinned PDF, and the Lean propositions verbatim from the
   scratch file.
3. `python3 scripts/paper_contribution.py new <pinned URL> --folder Arriola26TurnoutGap ...
   --statement-spec ...` (exit 0; every Spec Lean-validated by `#assert_scaffold_spec`).
   **Deviation, stated exactly.** The library root `AppliedModelingLib.olean` is not built on
   this machine (see the Repository 5 run). For this one command the scaffold's validation
   import in `scripts/new_paper.py` was pointed at the five Mathlib modules that the paper
   modules import, and the script was restored with `git checkout` right after (the clone
   shows no diff in `scripts/`). `PYTHONPATH=<clone root>` is needed because
   `new_paper.py` imports `scripts.formalization_protocol`.
4. The helper lemmas went to `MainTheorems.lean` and the six proof endpoints to
   `ProofInterface.lean`, with the Spec text untouched. `MainTheorems.lean` imports
   `Mathlib.Tactic`, `Mathlib.Data.Real.Basic`, `Mathlib.Analysis.SpecialFunctions.Pow.Deriv`,
   `Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics` and `Mathlib.Analysis.Convex.Deriv`
   instead of the scaffold's `import Mathlib`.
5. `lake build Arriola26TurnoutGap`: Build completed successfully (3314 jobs; the four paper modules in 80 s, 12 s, 21 s and 4 s).
   `python3 scripts/paper_contribution.py check Arriola26TurnoutGap --fast`: exit code 0. `#print axioms` on the six endpoints lists only `propext`, `Classical.choice` and `Quot.sound`.
   Both outputs are in `docs/CHECK_FAST_OUTPUT.txt`.

## Iteration record

- The first pinned commit (`e32c141`) was rejected by `new`: the scaffold's placeholder filter
  matches the word `TODO` case-insensitively, and the Spanish source statements of Lemma 1 and
  Proposition 2 contain the word "todo" ("para todo j", "en todo el soporte"). The paper was
  reworded ("para cada j", "en cada punto del soporte"), with no change of content, and the
  new commit `feb0cf2` was pinned.
- The second attempt failed in the scaffold's Lean validation: one `range` inside a Spec
  relied on `open Finset` in the scratch file. All Spec identifiers are now fully qualified
  (`Finset.range`, `Finset.Icc`, `Filter.Tendsto`, `Filter.atTop`, `nhds`), checked by
  elaborating the Specs alone with no `open`.
- The build passed at the first attempt; three `show` tactics that changed the goal were
  replaced by `change` to silence the style linter.

## What Lean verifies and what it does not

All six numbered results are proved, with no `sorry`:

- Lemma 1: coupling of habit paths (pointwise order of habits and votes).
- Proposition 1: strict concavity of `A a^alpha - kappa a^beta` on `(0, inf)`, positivity of
  `a*`, `b'(a*) = 0`, `a*` the unique maximiser, and the limits of `b'` for `beta = 1` and
  `beta > 1`.
- Proposition 2: the past elections of a 70-year-old are compulsory, the integrand of
  `tau70` is the complier indicator, and `tau70` is non-increasing in `lambda` when the
  density is unimodal and every `c-bar` is above the mode.
- Proposition 3: `Delta = tau70 + E + D` with `E >= 0` and `D >= 0`, where `P`, `P1` and `P^f`
  are defined from the primitives (cutoff rule, habit recursion at the ages
  `a - (n - j) d`) and (H) is the paper's hypothesis on them.
- Proposition 4: the index set, the closed form of the mean habit, the difference identity,
  and the 73-74 and 74-75 instances with `d = 5`.
- Proposition 5: the closed form with products of persistences, the corrected difference
  identity with the remainder `R(a) >= 0`, and the weight bound `rho(70)^k`.

The representation that is not literally in the paper: expectations over the persistent
cost and the past shocks are weighted averages over a finite population (a `Fintype` of
citizens with non-negative weights); today's transitory shock is integrated through `G`.
The calibration, the simulations and the numerical claims of the paper are not part of the
Lean run; `code/verify.py` checks them.

The audit sidecars under `audit/` are the scaffold-generated stubs; the LLM-as-judge lanes
that populate them were not run.
