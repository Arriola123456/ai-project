# Formalization Notes

This file preserves the previous hand-written paper-folder README content.
The paper-folder `README.md` is now a generated status overview.

# La brecha de participación a los 70 años sobrestima el efecto del voto obligatorio: ciclo de vida, hábito y una calibración con datos de la ONPE

## Source Version

- Paper: *La brecha de participación a los 70 años sobrestima el efecto del voto obligatorio: ciclo de vida, hábito y una calibración con datos de la ONPE*
- Authors: Manuel Alfredo Arriola Montenegro
- Version formalized: Unpublished manuscript (draft for the final presentation), ai-project commit feb0cf24c0b8f825861a31c118896c20bb8ec7f2, paper/paper.pdf, 31 October 2026
- Official URL: https://github.com/Arriola123456/ai-project
- Public PDF: https://github.com/Arriola123456/ai-project/blob/feb0cf24c0b8f825861a31c118896c20bb8ec7f2/paper/paper.pdf

Without a statement spec, a downloaded PDF is cached as `source.pdf` and ignored
by Git. A statement spec's SHA-256-verified source bytes are copied to a stable
paper-local `source-audited.*` path recorded in `audit/paper_statement_map.json`.
These artifacts are ignored by default. Unignore one only after an explicit
redistribution-rights review; machines without the private bytes must leave the
source-evidence gate unresolved rather than accepting the digest alone.
The extracted text cache is `source.txt` when `pdftotext` succeeds, and is also
ignored by Git in public workspaces unless redistribution rights have been
checked separately.

## Paper-Facing Ledger

- Implementation theorem file: `Arriola26TurnoutGap/MainTheorems.lean`
- Source-semantic interface: `Arriola26TurnoutGap/PaperInterface.lean`
- Proof-endpoint interface: `Arriola26TurnoutGap/ProofInterface.lean`
- Machine-readable status source: `Arriola26TurnoutGap/status.json`
- Private outside-Lean proof plan: `Arriola26TurnoutGap/docs/FORMALIZATION_PLAN.md`
- Final validation report: `Arriola26TurnoutGap/FINAL_VALIDATION_REPORT.md`
- Dependency DAG: `Arriola26TurnoutGap/docs/DependencyDAG.tex`
- Rendered DAG: `Arriola26TurnoutGap/docs/DependencyDAG.pdf`
- LLM/source audit sidecars: `Arriola26TurnoutGap/audit/*.json`

`PaperInterface.lean` should be readable on its own: expose actual source
definitions/models and one transparent statement specification for each
selected source claim. Put each distinct theorem/lemma proof endpoint in
`ProofInterface.lean`, with a short closed proof that calls into
`MainTheorems.lean`. Do not duplicate the proof endpoint in the semantic
interface. Do not mark a row `formalized` unless the endpoint is closed and the
remaining assumptions cell is `None`.
Keep the dashboard surface curated but complete for source-labelled formal
material: definitions, formulas, propositions, theorems/corollaries, named
claims, and main-text lemmas that a reviewer or LLM-as-judge should inspect.
Do not omit source-visible named material merely to keep the dashboard compact.
Inventory every named appendix theorem, corollary, lemma, and definition under
the paper's single `closeout_review_policy`. The prospective default gives all
named theory an initial source-to-Lean review and repeats terminal adversarial
review for main-text material plus any explicitly promoted appendix item that
governs it. Record one complete content-pinned `source_region_partition`; do not
infer a tier from a Lean name, helper name, or proof location. Catalog
unnumbered prose assertions separately. They are claim-bearing but are not
independent theorem targets under named-theory scope unless the chosen policy
explicitly selects all prose.

Use the controlled status vocabulary from `../../docs/STATUS.md`. Public-facing
rows should use `partially formalized` for results that still depend on an
external theorem, certificate, or proof boundary, and should name that boundary
in the final column rather than using `conditional` as a separate status label.
Keep theorem/status content synchronized with the current Lean graph before
marking a row `formalized`. The planner creates the final Dependency DAG later,
from that stable graph. Keep `status.json` as the source of truth for review
rows, artifact paths, and the paper's top-level public status.

## Current Workflow

1. Byte-pin the exact source version and complete the source-only inventory,
   formula sanity pass, scope decisions, shared-library search, and
   `docs/FORMALIZATION_WORKING_MEMO.md`.
2. Put actual source models/definitions and one complete transparent
   `<name>Spec : Prop` per selected source claim in `PaperInterface.lean`.
   Put its distinct theorem/lemma endpoint in `ProofInterface.lean`; use
   `by sorry` only as a temporary private proof body.
3. Run the one non-certifying architecture pre-pass, repair role confusion or
   hidden result packages, and materialize the reviewed source map from
   `audit/v11_source_map_preparation_config.json`.
4. Prove the fixed Specs with targeted Lean builds. Record possible source
   clarifications, genuine additional assumptions, and proof deviations in the
   working memo; it is a lead log, not evidence.
5. Begin or resume audit and closeout with
   `python3 scripts/closeout_reuse_plan.py --paper Arriola26TurnoutGap` and execute only
   its `next_action`.

The current semantic judge compares the ordered byte-pinned source-anchor
bundle directly with the fully expanded transparent Spec emitted by Lean. A
Lean-to-TeX translation, curator paraphrase, theorem name, wrapper theorem,
source-map summary, or code location is never semantic evidence. The same
standard applies to material paper-local and reusable-library prerequisites;
Lean's graph owns recursive declarations, premises, proof routes, instances,
and axiom closure.

Do not generate legacy `lean_to_tex_llm.json`,
`statement_match_llm.json`, `review_surface_llm.json`,
`paper_coverage_llm.json`, `source_record_audit.json`, or
`source_record_match_llm.json` for this current-protocol paper. The planner
schedules current graph acquisition, semantic-review deltas, complete
tracked-module elaboration, theorem realization, final holistic source review,
terminal report/DAG/status work, and the one issuer-protected strict
transaction.

The dashboard and PDF packet are optional human-review presentations generated
from the current graph after the source map and interfaces are stable. Human
annotations may not be fabricated or auto-closed, but missing annotations do
not block Lean closeout.

## Theorem Status

| Paper item | Lean declaration | Status | File | Remaining assumptions / notes |
|---|---|---|---|---|
| Lema 1 (Acoplamiento del hábito) (Section 4 (Resultados), page 3: Lema 1 (Acoplamiento del hábito)) | `lemma1_couplingSpec` -> `lemma1_coupling` | statement specification + proof stub | `PaperInterface.lean` | The transparent `...Spec : Prop` is the statement-audit target; the proof body is `by sorry`; raw-source-to-expanded-Spec judgment and premise provenance pending |
| Proposición 1 (Ciclo de vida) (Section 4 (Resultados), page 3: Proposición 1 (Ciclo de vida)) | `prop1_lifecycleSpec` -> `prop1_lifecycle` | statement specification + proof stub | `PaperInterface.lean` | The transparent `...Spec : Prop` is the statement-audit target; the proof body is `by sorry`; raw-source-to-expanded-Spec judgment and premise provenance pending |
| Proposición 2 (El salto no contiene hábito) (Section 4 (Resultados), page 3: Proposición 2 (El salto no contiene hábito); the stationarity paragraph (or the definition of the thresholds) on page 3) | `prop2_jumpSpec` -> `prop2_jump` | statement specification + proof stub | `PaperInterface.lean` | The transparent `...Spec : Prop` is the statement-audit target; the proof body is `by sorry`; raw-source-to-expanded-Spec judgment and premise provenance pending |
| Proposición 3 (La brecha es una cota superior) (Section 4 (Resultados), page 3: Proposición 3 (La brecha es una cota superior)) | `prop3_boundSpec` -> `prop3_bound` | statement specification + proof stub | `PaperInterface.lean` | The transparent `...Spec : Prop` is the statement-audit target; the proof body is `by sorry`; raw-source-to-expanded-Spec judgment and premise provenance pending |
| Proposición 4 (La huella del hábito) (Section 4 (Resultados), page 4: Proposición 4 (La huella del hábito); the stationarity paragraph (or the definition of the thresholds) on page 4) | `prop4_stepsSpec` -> `prop4_steps` | statement specification + proof stub | `PaperInterface.lean` | The transparent `...Spec : Prop` is the statement-audit target; the proof body is `by sorry`; raw-source-to-expanded-Spec judgment and premise provenance pending |
| Proposición 5 (Persistencia creciente con la edad) (Section 4 (Resultados), page 4: Proposición 5 (Persistencia creciente con la edad); the stationarity paragraph (or the definition of the thresholds) on page 4) | `prop5_rising_persistenceSpec` -> `prop5_rising_persistence` | statement specification + proof stub | `PaperInterface.lean` | The transparent `...Spec : Prop` is the statement-audit target; the proof body is `by sorry`; raw-source-to-expanded-Spec judgment and premise provenance pending |

## Intake Checklist

- [ ] Pin the exact source bytes and version.
- [ ] Complete the source-only selected-presentation and material-atom inventory.
- [ ] Complete the outside-Lean formula/dependency sanity pass and working memo.
- [ ] Search Mathlib, Cslib, Optlib, AppliedModelingLib, and relevant upstream
      Lean sources before introducing paper-local abstractions.
- [ ] Create actual source definitions/models and one transparent Spec per
      selected claim in `PaperInterface.lean`.
- [ ] Create each distinct proof endpoint in `ProofInterface.lean`.
- [ ] Run the architecture pre-pass and repair role confusion before freezing
      the source map and beginning expensive proof work.
- [ ] Keep final validation reports and Dependency DAGs absent until the
      planner schedules terminal closeout documents.

## Closeout Checklist

- [ ] Start with `python3 scripts/closeout_reuse_plan.py --paper Arriola26TurnoutGap` and
      execute only its current `next_action`.
- [ ] Resolve every raw-source-to-expanded-Spec, material-prerequisite,
      assumption, proof-route, axiom, realization, and source-coverage finding.
- [ ] Let the complete tracked-module checkpoint use the Git-owned module
      inventory and one dependency-aware `lake --rehash build` transaction.
- [ ] When `complete_terminal_closeout_documents` is scheduled, write the
      final report and paper-facing DAG from the current graph, compile and
      visually inspect the DAG, update paper-local status, and replan.
- [ ] Complete the independent holistic source audit only after the final
      source/interface/proof surface is fixed. Record each required distinct
      reviewer and exact audit-document hash in
      `docs/FINAL_ADVERSARIAL_REVIEW_PANEL.json`; a later count increase keeps
      valid prior entries for unchanged comparison material and adds only the
      missing review.
- [ ] Run only the exact strict worker command printed for the frozen plan.
      Acceptance exists only when that in-process transaction publishes the
      accepted obligation graph.
- [ ] Generate the packet/dashboard from the accepted current graph for optional
      human review; never manufacture reviewer annotations.
