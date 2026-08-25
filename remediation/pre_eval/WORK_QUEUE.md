# Remediation Work Queue — pre_eval

Researcher decisions R1 (F-01 Option A: stimuli unchanged; construct clarified) and R2
(Phase 7G two-rater mandate) are immutable inputs. Statuses: TODO / IN_PROGRESS /
BLOCKED_RESEARCHER / IMPLEMENTED / VALIDATED / DEFERRED / REJECTED_AS_UNNECESSARY.

| # | Finding | Intended change | Affected artifacts | Protected invariants | Validation | Status | Disposition |
|---|---|---|---|---|---|---|---|
| T0 | — | Baseline capture | remediation/pre_eval/BASELINE.md + hashes | all | hash inventory, tests, validators | VALIDATED | baseline fixed |
| T1 | F-01 | Record R1 Option A construct clarification (whole conversational-context sensitivity; constraints C1–C10) as pre-evaluation protocol clarification | docs/phase7e_pre_evaluation_clarification.md (NEW); freeze manifest v1.0.2 | stimuli bytes; frozen docs bytes; hypotheses/rules unchanged | freeze recompute; marker-content test; protected-diff | VALIDATED | CLOSED (Option A recorded) |
| T2 | F-02 | Role-structure correction recorded in same clarification artifact; historical prereg untouched | same as T1 | original prereg hash 7d46e0fb… intact | byte-check test (existing) + new chain test | IMPLEMENTED | CLOSED |
| T3 | F-06 | Two-rater mandate enforced: adjudicate mode; KEEP⇒ADJUDICATED; independence guard on reviewer_id; validator rules; doc updates; negative tests | scripts/apply_phase7g_annotations.py; scripts/validate_phase7g_review.py; docs/phase7g_human_qc.md; tests/test_phase7g_qc.py | BLIND-001 annotation preserved; history append-only; no fabricated ratings | new TwoRaterGateTests; validators VALID; mutations | VALIDATED | CLOSED |
| T4 | F-03 | Deterministic roll-up refresh script; validator cross-checks summary↔live; de-hardcode progress tests; refresh stale artifacts now | scripts/refresh_phase7g_rollups.py (NEW); validator; phase7g_quality_summary.json; PROJECT_STATUS.md; README.md; docs/phase7g_human_qc.md; tests | live records not rewritten by roll-up (read-only derivation) | consistency validator; mutation: stale summary detected | IMPLEMENTED | CLOSED |
| T5 | F-04+F-23 | Narrow .gitignore un-ignore of provenance-essential files; VCS_ANCHOR_PLAN with exact first-anchor contents/commands (no commit/push) | .gitignore; remediation/pre_eval/VCS_ANCHOR_PLAN.md | no secrets/transients exposed; histories/snapshots included | git check-ignore dry-run verification | VALIDATED | PARTIALLY_CLOSED (anchor = researcher) |
| T6 | F-08 | Error-accounted denominators block in metrics; duplicate-row detection; append-guard on JSONL logger (explicit opt-in); p95 semantics documented | benchmark/metrics.py; benchmark/logging.py; dry_run/smoke call sites; tests | primary analysis rules untouched (additive fields only) | unit tests incl. high-error run visibility | VALIDATED | CLOSED |
| T7 | F-10 | Pre-evaluation frozen-config preflight: required generation params, model id/version, retry/timeout; run-config digest; strict-mode wiring; Anthropic hidden-default guard | benchmark/preflight.py (NEW); runner.py; smoke_test.py; adapters/providers.py; tests | no provider params invented; no API calls | preflight unit tests; mutation: missing param blocked | IMPLEMENTED | CLOSED |
| T8 | LOW triage | Per-finding dispositions | LOW_FINDING_TRIAGE.md + small doc edits (F-05 banner, F-27 numbers, F-28 list unification, F-26/F-21/F-18 notes in clarification) | frozen docs not edited (7D falsifier note lives in clarification, not 7D file) | content checks + suite | VALIDATED | dispositions in file |
| T9 | — | Full suite + validators re-run; fresh-snapshot mutation regression | tests/*; MUTATION_REGRESSION.md | — | all green (335) ; 12/12 mutations killed | VALIDATED | — |
| T10 | — | Independent remediation audit + self-challenge + final report | REMEDIATION_AUDIT.md; REMEDIATION_CHALLENGE.md; FINAL_REMEDIATION_REPORT.md | — | — | IMPLEMENTED | verdict in final report |

## Explicitly out of scope (no authority)

- Any stimulus text change, stimulus v2, or assistant-turn edit (R1).
- Completing Phase 7G, fabricating rater_b, or LLM-as-rater (R2).
- Phase 8 enablement of any kind.
- Git commit/push/tag/remotes.
