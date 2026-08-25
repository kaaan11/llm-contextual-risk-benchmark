# 02 — Artifact Inventory (Audit A)

133 canonical files inventoried; authority relationships and anomalies noted. Counts verified
programmatically where possible.

## Canonical datasets

| Artifact | Role | Verified |
|---|---|---|
| `dataset/schema.json` | JSON-Schema v0.2.0 (base 0.1.0) | required-root list confirmed |
| `dataset/pilot/pilot_dataset.json` (+ `records.jsonl`, `attribution.json`) | Phase 3 pilot: **300 records** = 120 benign / 100 adversarial / 80 multi_turn; language tr; annotations/evaluations empty on all 300 | counts + uniqueness verified |
| `dataset/pilot/multiturn/multiturn_dataset.json` (+ records.jsonl) | Phase 7B Turkish exploratory corpus, 50 conversations, 178 turns; superseded design lineage | hash-protected |
| `dataset/pilot/multiturn/design_specification.json` | Phase 7C design spec — SUPERSEDED by 7D, retained historically | present |
| `dataset/pilot/multiturn/EXPLORATORY_DRAFT_V0.1_TR.json` | metadata-only preservation profile for TR corpus (`status preserved_unmodified`) | hash-protected |
| `dataset/pilot/multiturn/stimulus_dataset_v1.json` (+ stimulus_records.jsonl) | **Phase 7F primary stimuli**: 50 items / 171 condition instances; v1 PENDING everywhere | full forensic pass (05) |
| `stimulus_content_du.py`, `stimulus_content_ctl.py` | authored content modules (builder inputs) | read in full |

## Frozen protocol layer

| Artifact | Status |
|---|---|
| `docs/phase7e_preregistration.md` | FROZEN v1.0.1, SHA-256 verified against manifest |
| `docs/phase7e_annotation_protocol.md` | FROZEN, SHA-256 verified |
| `docs/PHASE_7D_EXPERIMENTAL_DESIGN.md` | frozen-in-manifest (with 7E amendment header), SHA-256 verified |
| `docs/PHASE_7D_DESIGN_TABLE.md` | generated table, SHA-256 verified |
| `results/dataset_audit/phase7e_design_snapshot.json` | immutable 50-design snapshot, SHA-256 verified |
| `results/dataset_audit/phase7e_preregistration_hash.json` | integrity manifest; composite recomputed OK |

Composite verification (auditor re-execution): all five protocol files match recorded hashes;
composite `d945d441…46819` reproduces exactly from the documented method; six protected datasets
match baselines; two declared-mutable files match their recorded current values.

## Review state layer

| Artifact | Live state | Consistency |
|---|---|---|
| `results/dataset_audit/phase7e_review.json` | REVIEW_COMPLETE, 50/50 KEEP @14:00Z, reviewer_id null | matches history + PROJECT_STATUS |
| `phase7e_review_history.jsonl` | 51 events (init + 50 KEEP), append-only | truncation detected by tests (M-12 killed) |
| snapshots: pre_execution, 140000Z | pre-write captures (PENDING state) | naming = write timestamp; content = prior state (explained) |
| `docs/phase7e_researcher_review.md` | static packet still saying "ALL 50 PENDING" | STALE → F-05 |
| `phase7g_blind_review.json` | 49 PENDING + 1 PARTIAL_ONE_RATER (BLIND-001 accepted in session 2) | authoritative for annotations |
| `phase7g_blind_key.json` | sealed mapping incl. category+expected_valence per entry; `opened:false` is self-referential | see M-13 |
| `phase7g_human_qc.json` | all PENDING, sections NOT_STARTED | consistent with decisions=0 |
| `phase7g_quality_summary.json` | says annotations_submitted=0 | **STALE vs blind_review** → F-03 |
| `phase7g_review_history.jsonl` | init event only | gitignored (F-04) |

## Code layer

- `scripts/`: build_pilot_manifest, build_multiturn_dataset, build_researcher_design,
  build_multiturn_researcher_review, build_phase7e_review, apply_phase7e_decisions,
  freeze_phase7e_preregistration, validate_phase7e_review, build_stimulus_dataset,
  build_phase7g_review, apply_phase7g_annotations, validate_phase7g_review,
  validate_multiturn_design, validate_multiturn_researcher_review.
- `benchmark/`: loader, types, errors, latency, refusal(heuristic_v2), metrics(v0.2.0),
  logging, metadata, retry(max2/0.5s→4s), runner(serial), dry_run, smoke_test, adapters
  (mock/openai/anthropic/open-weight). Never run live (providers `not_evaluated`).
- `tests/`: 16 files, 314 tests incl. negative controls; pass on pristine tree.
- `configs/`: phase6a_smoke (20-record manifest, seed 20260814), phase6b_sources,
  phase7b_multiturn_construction.

## Duplicates / orphans / masqueraders

- No duplicate sources of truth found for counts/statuses except the stale narrative artifacts
  listed above (F-03/F-05).
- `design_specification.json` + 7C review artifacts are superseded-but-retained historical
  layers, clearly labelled as such (not masquerading).
- Generated-as-canonical boundary is clean: DESIGN_TABLE declares its generator; snapshot files
  declare immutability; builder embeds approved designs verbatim with test enforcement.
- Orphan/dead code (LOW): `benchmark/latency.measure_call` never called; `SCHEMA_PATH` unused in
  `dataset/validate.py`; no-op consecutive-user-turn block in `build_stimulus_dataset.py`
  structural_validation (lines 361–366).

## VCS exposure anomaly (F-04 summary)

`.gitignore`: `results/*` ignored except `!results/dataset_audit/*.json`; therefore
`phase7e_review_history.jsonl`, `phase7g_review_history.jsonl`, `snapshots/**`,
`results/smoke_test/**`, `benchmark/runs/**` are excluded from version control. With zero
commits the entire provenance chain currently exists only as working-tree bytes whose integrity
is anchored solely by self-recorded hashes.
