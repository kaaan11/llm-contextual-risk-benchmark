# FINAL PRE-7G REMEDIATION REPORT

Campaign: implementation/validation/remediation of accepted audit findings under researcher
decisions **R1** and **R2**. Evidence set: `BASELINE.md`, `change_manifest.json`,
`WORK_QUEUE.md`, `LOW_FINDING_TRIAGE.md`, `MUTATION_REGRESSION.md`, `REMEDIATION_AUDIT.md`,
`REMEDIATION_CHALLENGE.md`.

---

## Executive verdict

## **READY_FOR_PHASE_7G_HUMAN_QC**

All in-campaign work is complete and validated; the two-rater human QC can begin on the
remediated tooling. The single open item (executing the VCS anchor) is a researcher action that
does not gate 7G annotations — though executing it before or during early batches is strongly
advised. Phase 8 remains blocked.

## Researcher decisions implemented

- **R1 (F-01, Option A):** stimuli byte-unchanged (hash-proven); construct clarified to whole
  conversational-context sensitivity via `docs/phase7e_pre_evaluation_clarification.md`, now
  hash-pinned as protocol manifest v1.0.2; interpretation constraints C1–C10 recorded exactly.
- **R2 (F-06):** two-independent-blind-rater mandate enforced end-to-end (tooling + validator +
  tests); the one existing rater_a annotation preserved with provenance; no second rating
  fabricated; adjudication exists only as the documented recorded flow.

## Finding disposition table

| Finding | Disposition |
|---|---|
| F-01 | CLOSED — Option A faithfully recorded; boundary enforceably visible pre-evaluation |
| F-02 | CLOSED — historical prereg intact; explicit pre-evaluation clarification |
| F-03 | CLOSED — canonical→derived architecture with fail-closed consistency validation |
| F-04/F-23 | PARTIALLY_CLOSED — ignore rules + anchor plan ready; commit/push reserved to researcher |
| F-06 | CLOSED — one-rater completion impossible via tooling; independence enforced where identity exists, process-documented where anonymous |
| F-08 | CLOSED (defined scope) — full denominator accounting + duplicate detection + append guard; retry-trace detail deferred |
| F-10 | CLOSED (supported scope) — frozen-config preflight + digest + strict wiring + Anthropic guard; honesty note on metadata-only version |
| F-05 FIX_NOW · F-07 DOCUMENT_ONLY · F-11 NO_ACTION · F-18 DOCUMENT_ONLY · F-20 FIX_NOW · F-21 DOCUMENT_ONLY · F-24 split (guard FIXED / atomic writes DEFERRED) · F-26 DOCUMENT_ONLY · F-27 FIX_NOW · F-28 FIX_NOW | see LOW_FINDING_TRIAGE.md |

## Files modified (21)

`.gitignore` · `PROJECT_STATUS.md` · `README.md` · `benchmark/{adapters/providers,dry_run,
errors,logging,metrics,runner,smoke_test}.py` · `docs/phase7e_researcher_review.md` ·
`docs/phase7f_stimulus_generation.md` · `docs/phase7g_human_qc.md` ·
`results/dataset_audit/phase7e_preregistration_hash.json` (regenerated manifest v1.0.2) ·
`results/dataset_audit/phase7g_quality_summary.json` (derived roll-up regenerated) ·
`scripts/{apply_phase7g_annotations,freeze_phase7e_preregistration,validate_phase7g_review}.py`
· `tests/{test_phase7e_review,test_phase7f_stimulus,test_phase7g_qc}.py`

## New artifacts (4 code/tests + campaign docs)

`benchmark/preflight.py` · `docs/phase7e_pre_evaluation_clarification.md` ·
`scripts/refresh_phase7g_rollups.py` · `tests/test_remediation_regressions.py`;
plus `remediation/pre_eval/**` (this report set, baseline hashes, change manifest).

## Protected artifacts (before → after)

13/13 byte-identical: both stimulus files, pilot dataset trio, multiturn corpus pair,
TR exploratory profile, preregistration doc, annotation protocol, both 7D docs, design
snapshot. Existing review histories: append-only, untouched. BLIND-001 rater_a annotation:
untouched (`probably_benign`, session-2 provenance intact). Full diff inventory:
`change_manifest.json` (added 4 / modified 21 / removed 0).

## Tests

```
/tmp/opencode/audit_venv/bin/python -m pytest -q -p no:cacheprovider   # 335 passed (was 314)
python scripts/validate_phase7e_review.py                              # VALID — 50 approved
python scripts/validate_phase7g_review.py                              # VALID — incl. new summary cross-checks
```

Two legacy tests replaced with invariant-based versions (rationales in-code); helper corrected
to the mandated two-rater flow; 18 new regression tests added. No existing test weakened.

## Mutation regression

12 mutation classes executed on an isolated snapshot of the remediated tree:
**12 killed / 0 survived** — including the prior campaign's lone survivor (stale summary),
now detected. Full table: `MUTATION_REGRESSION.md`.

## Remaining risks

1. External anchoring not yet executed (no commits exist by prohibition) — execute
   `VCS_ANCHOR_PLAN.md`; optionally timestamp composite `47ae3fed…bcfc6f`.
2. Anonymous-role rater independence is process-enforced only (inherent limitation, documented).
3. Direct non-metadata adapter usage bypasses preflight — Phase 8 entry script must use strict
   runners (recorded requirement).
4. Per-attempt retry traces and atomic artifact writes deferred post-pilot.
5. Roll-up refresh remains a manual step after apply commands; omission fails validators loudly
   rather than silently (by design).

## Human work still required

**Phase 7G two-rater human QC is INCOMPLETE**: rater_a 1/50 (BLIND-001 accepted),
rater_b 0/50, ADJUDICATED 0/50, context/safety/naturalness reviews 0/50, decisions 0/50.
Nothing in this campaign performed, simulated, or auto-completed any of it.

## Phase 8 status

**BLOCKED.** Requires: completed two-rater Phase 7G with all gates/adjudications, researcher
approval, provider access, execution of the prereg §16 freeze list through the new preflight
(strict mode), and the researcher-run provenance anchor. This campaign did not and will not
begin Phase 8.
