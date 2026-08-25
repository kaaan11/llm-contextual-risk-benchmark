# Remediation Campaign — Baseline

Captured at campaign start, BEFORE any modification. Machine-readable companions:
`baseline_hashes.json` (full tree), `protected_artifacts_baseline.json` (protected subset).

## Git state

- Branch `master`, **0 commits**; every file untracked (`git status --porcelain` all `??`).
- No remotes/tags configured.

## Test / validator status at baseline

| Check | Result |
|---|---|
| `pytest -q` | **314 passed** |
| `scripts/validate_phase7e_review.py` | VALID — 50 items, 0 pending, 50 approved |
| `scripts/validate_phase7g_review.py` | VALID — pending=50 keep=0 … approved=0, phase_complete=False, inter_rater=not_available |

## Phase 7G live state (canonical sources)

- `results/dataset_audit/phase7g_blind_review.json`: status BLIND_ANNOTATION_IN_PROGRESS;
  exactly **1** accepted rater_a annotation — BLIND-001 → RI-DU-008, valence `probably_benign`,
  confidence low, annotated_at 2026-08-14T20:15:00Z, accepted_in_session 2 (session 1 was
  invalidated for anchoring contamination; provenance recorded inside presentation_sessions).
  rater_b empty on all items.
- `results/dataset_audit/phase7g_human_qc.json`: all 50 PENDING, sections NOT_STARTED,
  researcher_qc false ×50.
- `phase7g_quality_summary.json`: STALE (says annotations_submitted=0) — F-03 target.
- `phase7g_review_history.jsonl`: init event only.

## Existing human annotation — preservation decision (R2 compatibility)

The single rater_a annotation is **structurally compatible** with the two-rater mandate:
it occupies the rater_a slot with reviewer_role recorded and session provenance intact.
It is preserved untouched and remains valid partial input awaiting rater_b.

## Freeze / integrity state

- Preregistration manifest v1.0.1, composite `d945d441…46819`; five protocol files verified.
- Six protected datasets byte-identical to audit-campaign baselines.
- Stimulus snapshot equality test passing (v1 preserved).

## Baseline invariants this campaign must preserve

1. All 13 protected artifacts byte-identical (list above).
2. Original preregistration document bytes unchanged (clarification via NEW amendment artifact).
3. Existing review-history entries append-only; no edits/deletions.
4. BLIND-001 rater_a annotation content/provenance unchanged.
5. 50 item ids / design fields / 171 condition instances unchanged.
