# Remediation Self-Challenge

Adversarial pass against my own remediation. Each question attacked with repository evidence.

**1. Did remediation silently alter research design?**
No. `change_manifest.json` shows 0 deletions and a modified-file list confined to tooling,
narrative docs, derived roll-ups, and the manifest. Stimuli, content modules, design snapshot,
frozen protocol docs, review histories, blind packet annotation state: byte-identical
(protected-artifact test + suite). The only research-semantic artifact added is the R1-mandated
clarification.

**2. Did amendment language expand hypotheses?**
No. The clarification contains no new hypothesis, metric, threshold, or test; it states the
opposite in its header and C9/C10, and `rules_changed: false` is asserted by test on the v1.0.2
chain entry.

**3. Did the F-01 clarification accidentally become a new primary analysis?**
No covariate was introduced anywhere (no schema field, no analysis code touched). C10 explicitly
requires any future stance analysis to have its own pre-evaluation record.

**4. Can one-rater completion still sneak through another code path?**
Paths audited: `record_decision` KEEP (blocked unless ADJUDICATED), validator approval rules
(flag PARTIAL/PENDING), phase_complete cross-check (all items must be ADJUDICATED),
`adjudicate` (requires both ratings; refuses agreement-shortcut; conflict on re-adjudication).
Residual: hand-editing JSON files then never running validators — but every gate consumer
(validator, tests) fails closed, and history/append-only layers make silent divergence visible.
Also intentional non-change: context *reveal* after one rating stays allowed — that is the
blind-ordering rule, not a completion gate; completion remains gated at decision time.

**5. Can status artifacts drift again?**
Yes, files can always be edited — but now `validate_phase7g_review.py` FAILS on summary↔live
mismatch (proven by OM-01), so drift is detected rather than silent. The apply tool still does
not auto-regenerate the summary; running `refresh_phase7g_rollups.py` after apply is a documented
step, and forgetting it fails the validator loudly (fail-closed choice over convenience).

**6. Can provider defaults still enter canonical runs?**
Canonical = metadata-driven runs. Strict mode requires all frozen params up front; empty params
fail on required keys; Anthropic fallback raises under enforcement. Residual (documented):
constructing adapters/requests directly without metadata bypasses preflight — out of canonical
scope and recorded as a remaining risk for the Phase 8 entry script to honor.

**7. Can errored observations disappear from reported denominators?**
They are excluded from the frozen rate definitions (unchanged, per contract) but can no longer
do so invisibly: n_expected/n_error/denominator fields are emitted alongside every aggregate,
and duplicates are counted. A "deceptively successful" high-error run now self-reports its
8%-success denominator (unit-proven).

**8. Did .gitignore changes expose secrets or huge transient artifacts?**
Reviewed every newly trackable class: histories (reviewer roles, no PII/secrets), snapshots
(same content class as already-tracked audit JSONs), smoke summary (sanitized metadata; no keys;
Windows path note already INFO-tracked). Mock dry-run artifacts remain governed by their nested
ignore and are three small files. No `.env`, cache, or response payloads exposed.

**9. Did tests get easier?**
No: 314 → 335 passing. Two pinned-progress tests were replaced by derivation-equality invariants
(strictly stronger); `_fully_review` now exercises both raters + adjudicated gate; the new file
adds 18 negative/invariant tests including end-to-end refusals.

**10. Are original preregistration and stimuli preserved EXACTLY?**
Yes: OM-04 killed a one-byte prereg edit; protected-hash test covers stimuli + corpora + snapshot
against campaign baseline; change manifest lists them under neither modified nor removed.

**Extra probe — does anything now WRITE to canonical live records uninvited?**
`refresh_phase7g_rollups.py` writes ONLY the derived summary; apply-tool writes unchanged in
kind (snapshot → write → append history). Freeze script writes only its own manifest. No new
writer of blind/QC/review/state exists.

**Extra probe — could the clarification doc be edited later without notice?**
It is hash-pinned inside protocol_files from v1.0.2; any edit breaks per-file and composite
checks on every test run (same regime as the original four documents).
