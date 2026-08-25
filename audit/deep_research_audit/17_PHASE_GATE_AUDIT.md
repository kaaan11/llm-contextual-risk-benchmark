# 17 — Phase-Gate Audit (Audit P)

Reconstructed transitions with inputs/outputs/criteria and bypass risk.

| Phase | Inputs | Outputs | Completion criteria | Gate integrity |
|---|---|---|---|---|
| 0–5 | scope docs | taxonomy, schema 0.1.0, 300-record pilot, annotation+benchmark frameworks | documented + tested | OK (historical) |
| 6A | smoke config | harness, 20-record manifest, preflight; providers `not_evaluated` | infra complete; **no live call** — correctly reported as such | OK |
| 6B | public source metadata | source inventory, overlap report `preliminary_blocked`, sampling `blocked` | deliberately blocked pending pinned sources + approval | OK — blockage itself is recorded honestly |
| 7B | TR construction config | 50 TR conversations + stats | built+validated; exploratory label; out of primary scope | OK (superseded lineage preserved) |
| 7C/7C-REVIEW | AI-proposed EN design | design spec + review table all PENDING | SUPERSEDED by external methodological review — artifacts retained, clearly labelled | OK |
| 7D | review findings | rebuilt matched-quadruplet design, 50 items metadata-only | frozen snapshot; "no stimulus text" honored | OK |
| 7E | prereg freeze → decisions | v1.0.1 manifest; 50/50 KEEP @14:00Z; append-only history; snapshots | tool-enforced identity/no-auto-approval rules | OK |
| 7F | approved designs + authored content | stimuli v1 (171 conds), 5 audit reports, deterministic build | structural/safety/leakage/overlap zero-flag; review fields stay PENDING | OK |
| **7G** | blind packet + tools | annotations, context/safety/naturalness reviews, decisions | requires human annotations + explicit KEEP per item; phase_complete ⇔ pending==0 | **IN PROGRESS — current gate.** Status reporting inconsistent (F-03); one-rater path would deadlock gate outcomes (F-06) |
| 8 | API access + closed 7G | model runs, dispositions, metrics | prereg §16 freeze list must be executed first | NOT STARTED; blocked correctly by `model_evaluation_permitted=false` and QC counts |

## Can status advance while evidence is incomplete?

Mechanically: no single flag flips the project forward — `stimulus_generation_permitted`,
`model_evaluation_permitted`, `phase_complete`, and per-item `researcher_qc` are separate, and
tests pin them to honest values. The observed failure mode is not premature advancement but
**stale narration around an active gate** (F-03/F-05): documents lagging the live state could
cause a human to misjudge readiness in either direction.

## Rollback / revision semantics

REVISE preserves v1 + opens v2 request (+blind re-review if prompt changes); REJECT preserves
record with reason; re-deciding conflicts; invalidated sessions refuse annotation reuse.
Semantics are sound and mutation-tested.

## Gate-criterion gaps

- 7G's documented KEEP requirement "isolated gate passed or explicitly judged acceptable" is not
  enforced by tooling (F-06b).
- No explicit criterion defines how many raters are *required* before 7G may close: one-rater
  completion is permitted by doc §3 but would leave gates uncomputed (F-06a) and F5/F6
  unmeasurable — an implicit gate contradiction between §3 (one rater allowed) and §4/prereg §6
  (adjudicated valence required). Needs a researcher decision before QC resumes.
