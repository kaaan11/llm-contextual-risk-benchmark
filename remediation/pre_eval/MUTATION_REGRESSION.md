# Mutation Regression — pre_eval remediation

Executed on an isolated snapshot of the REMEDIATED tree
(`/tmp/opencode/AI_Search_remediated`); canonical tree untouched. Prior-campaign
mutations re-run where still relevant (OM-*), plus new mutations targeting each
remediated weakness (NM-*). Unit-level equivalents already live in
`tests/test_remediation_regressions.py`.

| ID | Target finding | Mutation | Expected | Actual | Killed? | Implication |
|---|---|---|---|---|---|---|
| OM-01 | F-03 | Stale `quality_summary.annotations_submitted=0` while blind packet holds 1 | validator INVALID | INVALID — `annotations_submitted 0 != live 1` + valence-distribution mismatch; exit 1 | **KILLED** (was the M-09 survivor pre-remediation) | roll-up drift now fail-closed |
| OM-02 | F-06/Fabrication | percent_agreement=0.92, kappa=0.87 while status not_available | validator INVALID | exit 1 — fabricated-statistics guard intact | KILLED | anti-fabrication preserved |
| OM-03 | F-06 | KEEP+researcher_qc=true with sections COMPLETE but blind PENDING | validator INVALID | exit 1 — "approved without a blind isolated-prompt annotation" (+count drift) | KILLED | approval residue still caught; PARTIAL-state variant covered by unit test `test_validator_flags_keep_over_partial_state` |
| OM-04 | F-02/Freeze | Append byte to frozen preregistration | tests fail | 2 failed (byte-identity + composite) / 100 passed | KILLED | historical preservation enforced |
| OM-05 | Protected data | Modify Turkish exploratory dataset | tests fail | IntegrityTests 1 failed | KILLED | protected layer intact |
| OM-06 | Blinding seal | Flip `blind_key.opened=true` | tests fail | 2 failed (seal assertions) | KILLED (repo-state); process limit documented (F-23b/INFO-06) | unchanged boundary |
| NM-01 | F-06 | Full apply-tool flow to KEEP with only rater_a annotated (PARTIAL) and all reviews complete | QCError two-rater mandate | `two-rater mandate — … PARTIAL_ONE_RATER, not ADJUDICATED. Refused.` | KILLED | one-rater completion impossible via tooling |
| NM-02 | F-06 | `record_adjudication` for an item with no/one rating | QCError requires two ratings | `adjudication requires two submitted blind ratings` | KILLED | fabricated adjudication cannot bypass |
| NM-03 | F-06 | Adjudication after disagreement skipped → direct KEEP | QCError ADJUDICATED required | covered by unit test disagreement→KEEP-refused→adjudicate→KEEP-ok | KILLED | adjudication is the only bypass-free path |
| NM-04 | F-10 | Strict preflight with generation_parameters missing top_p/max_output_tokens | PreflightError | raised listing both keys | KILLED | undocumented defaults cannot enter canonical runs |
| NM-05 | F-08/F-24 | Open existing non-empty responses.jsonl without append_ok | LoggingError | raised | KILLED | rerun duplicate rows blocked by default |
| NM-06 | F-03 | Same reviewer_id on both rater slots (IDs present) | validator INVALID | unit test asserts error `independence violated`; tool refuses at record time | KILLED | identity-based independence check live |
| NM-07 | F-10 | ModelSpec.version empty under strict mode | PreflightError | raised (honest metadata-only note included) | KILLED | version freeze enforced as recorded fact |

## Survivors

None. Every mutation class attempted was killed at tooling or test layer.

## Notes

- OM-01 was the audit campaign's known survivor (M-09); its conversion to killed
  is the direct evidence that F-03's consistency invariant now exists.
- Direct hand-editing of JSON state files always remains *possible* (no database);
  the guarantee is detection-and-refusal at validation/gate time, which is the
  strongest enforcement this repository architecture supports.
