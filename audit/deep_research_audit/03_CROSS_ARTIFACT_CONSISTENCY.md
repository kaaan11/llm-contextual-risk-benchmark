# 03 — Cross-Artifact Consistency (Audit B)

Systematic comparison of claims across authoritative artifacts. Verdicts: CONSISTENT unless
flagged.

## Counts and structure

| Claim | Sources | Verdict |
|---|---|---|
| 50 research items | prereg §3, design table, review.json, stimulus stats, blind packet, human_qc, quality summary, tests | CONSISTENT (7 independent artifacts) |
| Categories 30/7/7/6 | all above + embedded designs | CONSISTENT |
| 171 condition instances (A50/B50/C50/D21) | prereg arithmetic, dataset, stats report, README | CONSISTENT; recomputed from data = 171 |
| D arm ⇔ control_strategy N | prereg, dataset per-record check, validation report, tests | CONSISTENT (0 mismatches) |
| Turn shapes u-a-u / u-a-u-u; intended_turn_count deviation 0 | 7F doc §4, dataset | CONSISTENT |
| 513 runs/model at 3 reps | prereg §3 arithmetic | arithmetic verified |
| Phase 7E 50/50 KEEP @2026-08-14T14:00Z, reviewer_id null, self-review role | PROJECT_STATUS, live review.json, history jsonl, snapshot sequence | CONSISTENT |
| Prereg frozen v1.0.1 2026-08-14T00:00:00Z, one scope-only amendment w/ prior hash | manifest + amendment block + freeze script | CONSISTENT; hashes recomputed |
| No model calls / no results anywhere | generation report negative-claims block, evaluation_state, smoke summary (`not_evaluated` ×3), `test_no_model_results_anywhere` | CONSISTENT |
| Protected datasets byte-identical | manifest baselines vs actual files | CONSISTENT (recomputed) |

## Contradictions found

### F-03 — Phase 7G progress state disagrees across artifacts (CONFIRMED)
- `README.md:28`: "incomplete — **1/50 isolated annotations**, 0/50 decisions".
- `results/dataset_audit/phase7g_blind_review.json`: exactly 1 accepted rater_a annotation
  (BLIND-001 → RI-DU-008, probably_benign, confidence low, annotated_at 2026-08-14T20:15Z,
  accepted_in_session 2 after invalidated session 1). README is the artifact that matches.
- `PROJECT_STATUS.md:15,88,129`: "insan annotation **0/50**" — contradicts live record.
- `phase7g_quality_summary.json`: `annotations_submitted: 0`, valence distribution all zeros.
- `docs/phase7g_human_qc.md`: "0 of 50 items reviewed".
Root cause (code-level): `scripts/apply_phase7g_annotations.py` mode `blind` snapshots and
writes ONLY `phase7g_blind_review.json` (`targets = [BLIND]`, lines ~413–438); no tool
regenerates the summary/QC/doc afterwards. Test `test_summary_declares_phase_incomplete`
pins `annotations_submitted == 0`, i.e. codifies the stale value instead of cross-checking it.
Impact: status ambiguity around the active gate; a reader trusting PROJECT_STATUS or the
quality summary miscounts real progress. Severity MEDIUM.

### F-05 — Stale narrative packets presented as current (CONFIRMED, LOW)
- `docs/phase7e_researcher_review.md` header: "Status: AWAITING_HUMAN_REVIEW — ALL 50 ITEMS ARE
  PENDING", KEEP 0/PENDING 50, sign-off `<not supplied>` — while live state is REVIEW_COMPLETE
  50/50 KEEP. The file lacks a "superseded — see phase7e_review.json" pointer (the design table
  does carry such a pointer; this packet does not).
- An explore-level first reading of these two layers produced a false "largest inconsistency"
  hypothesis; resolved by history/snapshot chronology (see NAF-01).

## Resolved suspicions (NOT_A_FINDING)

### NAF-01 — "Phase 7E COMPLETE vs ALL PENDING" contradiction
Resolved: `docs/phase7e_researcher_review.md` is the pre-decision review packet;
`snapshots/phase7e_review.v1.pre_execution.json` (PENDING) precedes the decision write at
14:00:00Z recorded in the append-only history; live `phase7e_review.json` = REVIEW_COMPLETE.
Snapshot filename `...140000Z` carries the write-time stamp while internal `generated_at` stays
at build time — explainable naming convention, documented here to prevent future confusion.

### NAF-02 — corpus_segment_count=768 "unexplained"
Recomputed exactly from the stated method (prompt/text/canonical fields + every turn of both
corpora): 768 segments. NOT_A_FINDING.

### Minor vocabulary drift (INFO-02, historical only)
Phase 7B plan cells `context_has_no_material_effect`/`ambiguous_or_borderline` vs realized
statistics names `context_does_not_change_interpretation`/`ambiguous_borderline_context`; and
realized context_effect_distribution (17/8/6/15/4, no irrelevant cell) differs from the earlier
AI-proposed plan (18/7/7/10/5/3). Both concern the SUPERSEDED exploratory TR lineage, clearly out
of primary-pilot scope. INFO.

### INFO-01 — typo in source inventory
WildGuardMix version string `"main (un*pinned)"` stray asterisk. Cosmetic.

## Terminology audit

Condition codes/names, category labels, disposition vocabulary, gate flag names, and decision
vocabularies are consistent across prereg ↔ annotation protocol ↔ builder ↔ validators ↔ tests.
One frozen-text ambiguity (context role phrasing) is handled under F-02 in the design audit.
