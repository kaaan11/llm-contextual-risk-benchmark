# 15 — Failure-Mode Campaign (Audit N)

Future-evaluation failure modes assessed for **silent bias** potential. Framework state: runner
logs a row for every case including failures (no silent skips) — the strongest anti-bias property
present. Remaining risks:

| # | Failure mode | Current behavior | Bias risk | Class |
|---|---|---|---|---|
| 1 | Provider timeout / transport error | retried (max 2, backoff); then `api_error`→`missing`; never scored as refusal ✓ prereg §15 | errors excluded from refusal/latency/ASR denominators — if correlated with condition → contrast bias (F-08) | MEDIUM |
| 2 | Malformed provider response | non-retryable per adapter classification; row logged with sanitized error | same denominator exclusion as (1) | LOW-MED |
| 3 | Empty / safety-filter response | triage: `ambiguous`, not a refusal; disposition layer would handle | triage counts could misroute human review queue | LOW (F-08d) |
| 4 | Model-version drift mid-run | metadata records version string; no runtime enforcement; prereg mandates halt+new experiment version | undetectable by tooling if ignored | MEDIUM process |
| 5 | Context-window overflow | no preflight token budgeting vs model window; long B/C (~120 est-tokens) trivially safe for modern windows | negligible for this dataset | INFO |
| 6 | Truncated output mid-substance | rubric has `unscorable_content` path; raw text preserved | handled | — |
| 7 | Duplicate run into same JSONL | append-mode duplicates rows silently | double counting in any naive aggregation | MEDIUM (F-24) |
| 8 | Missing run (crash mid-loop) | fail_fast default logs then re-raises; without it, loop continues and partial file remains with no completion marker in responses.jsonl itself | partial-dataset ambiguity unless metadata cross-checked | LOW-MED |
| 9 | Reordered items | order = input order, recorded via request_digest + sequence fields | detectable post-hoc | — |
| 10 | Interrupted execution | non-atomic metadata writes could leave mismatched metrics/responses pair | last-writer-wins confusion | LOW (F-24) |
| 11 | Retry double-count | single row per case regardless of attempts (`attempts` recorded) | none on row count; latency inflation + lost failed-attempt usage only | LOW (F-08a) |

## Silent-bias verdict

The preregistered analysis rules already neutralize the worst paths (API-error≠refusal,
exclusion tables, no imputation). The residual bias channels are F-08's denominator exclusions
and F-24's artifact hazards — both fixable in configuration/tooling before Phase 8 without
touching frozen analysis rules.
