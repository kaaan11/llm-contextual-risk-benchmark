# Independent Remediation Audit — skeptical pass

Written in the role of an auditor who did NOT implement the remediation. Every claim was
re-verified against repository evidence (hashes, code paths, test output, validator exits),
not against the implementer's assertions.

## Per-finding dispositions

### F-01 — assistant-stance channel / construct clarity → **CLOSED** (Option A faithfully recorded)
Evidence: `docs/phase7e_pre_evaluation_clarification.md` exists, is a member of
`protocol_files` at manifest v1.0.2, and its required markers are asserted by
`test_clarification_document_is_a_frozen_member_with_required_content`. Constraints C1–C10 map
one-to-one onto Decision R1's items 1–10; no stance covariate entered the primary analysis
(C9/C10). Stimuli bytes unchanged (protected-hash test + change manifest). CLOSED means the
researcher-selected boundary is recorded and enforceably visible pre-evaluation — the channel
itself remains in the stimuli **by decision**, and is not claimed remediated physically.

### F-02 — frozen role wording vs realized structure → **CLOSED**
Original preregistration byte-hash still asserted (`7d46e0fb…`, test + OM-04 mutation killed).
Clarification §2 states exactly what was wrong, the actual u-a-u(/u) structure with counts,
the preserved intent (no developer/system arm), and pre-evaluation timing distinct from
result-driven change. No hypothesis/rule text altered.

### F-03 — status/derived-state drift → **CLOSED**
Architecture is now canonical-live → deterministic roll-up: `refresh_phase7g_rollups.py`
derives summary from blind+QC; `validate_summary()` fails the validator on any drift
(demonstrated: stale injection produced INVALID; pristine tree VALID). The two hard-coded
progress tests were replaced by derivation-equality tests with documented replacement notes.
PROJECT_STATUS/README/7G-doc now state live truth (1 rater_a / 0 decisions / two-rater mandate).

### F-04 + F-23 — provenance anchoring → **PARTIALLY_CLOSED (preparation complete; anchor = researcher)**
Ignore rules narrowed exactly to histories/snapshots/smoke-summary; `git status -uall` shows
the intended set trackable; no secrets or large transients exposed (contents inspected).
`VCS_ANCHOR_PLAN.md` specifies commit boundaries and commands. The campaign is prohibited from
committing/pushing, so external anchoring necessarily remains open until the researcher executes
the plan (and optionally timestamps the composite hash).

### F-06 — one-rater Phase 7G completion → **CLOSED**
End-to-end: NM-01 shows KEEP refused at PARTIAL via the real tool flow; NM-02 shows adjudication
impossible without both ratings; disagreement→KEEP refused→recorded adjudication→gate computed→
KEEP succeeds is unit-proven; validator flags approved-over-PARTIAL and phase_complete-without-
full-adjudication; same-reviewer_id double-slotting refused where identity exists. The existing
rater_a annotation survives untouched and compatible. Honest boundary recorded: with anonymous
role-only raters, independence is process-level, not technically provable — as the brief itself
directs rather than pretending enforcement.

### F-08 — errored/excluded observations invisible → **CLOSED (defined scope)**
`calculate_metrics` emits `denominator_accounting` (n_expected/n_observed/n_error/latency-
missing/refusal & ASR denominators/duplicate rows/membership denominators); rates themselves
unchanged (frozen semantics respected). Duplicate rerun rows are reported and now also blocked
at write time by default. Deferred remainder (per-attempt retry traces inside successful rows)
is recorded as DEFERRED_POST_PILOT — visibility of totals is unaffected.

### F-10 — undocumented provider defaults in canonical runs → **CLOSED (supported scope)**
`assert_run_config_frozen` enforces provider/model id/version, temperature/top_p/max_output_
tokens, retry+timeout, dataset identity; smoke `--live` wires strict mode; strict runners record
`run_config_digest`; Anthropic's silent 1024 fallback raises under enforcement; metadata honesty
field states version is NOT transmitted. Direct `GenerationRequest` use without metadata bypasses
preflight by construction — documented residual, irrelevant to canonical metadata-driven runs.

## LOW triage verification

F-05 banner present · F-07/F-21/F-26 documented in clarification §3 / 7G doc · F-18 → C8 ·
F-20 tests de-hardcoded (stronger) · F-27 numbers corrected with note · F-28 union list ·
F-11 NO_ACTION justified (triage-only, versioned, calibration pending) · F-24 split:
duplicate-guard FIXED, atomic writes DEFERRED.

## Test-integrity check

Suite grew 314 → 335, all green. Two legacy tests were replaced (not deleted): each old
assertion value survives against its historical anchor or a derived invariant; replacement
rationales are in-code comments referencing R1/R2. Helper `_fully_review` corrected to the now-
mandated two-rater flow — it exercises MORE of the pipeline than before, not less.

## Verdict summary

6 CLOSED, 1 PARTIALLY_CLOSED (F-04/F-23, awaiting researcher-executed anchor), 0 OPEN.
No evidence of scope creep into stimulus text, frozen rules, hypotheses, or Phase 8 enablement.
