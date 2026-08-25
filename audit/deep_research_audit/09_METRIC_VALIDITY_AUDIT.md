# 09 — Metric Validity (Audit H)

Traceability INPUT → TRANSFORMATION → AGGREGATION → INTERPRETATION for each planned metric.
Primary metrics are pre-registered and human-scored; benchmark-package metrics are auxiliary
triage. Both audited.

## 1. model_disposition (primary)

- Input: 3 repetitions per condition → TRANSFORMATION: frozen rubric §6 (5-point ordinal,
  boundary rules 0/1, 1/3, 2/3 frozen) → AGGREGATION: modal; all-differ ⇒ `unscorable_unstable`
  → INTERPRETATION: ordinal only (deltas interpreted by sign/rank, never magnitude).
- Validity strengths: rubric boundary questions are unusually explicit; tone excluded;
  clarifying-question-vs-partial-refusal distinction operationalized.
- Residual risks (documented in design §30.2): rubric author/adjudicator saw hypotheses →
  directional drift possible on n=50; mitigation is blinded shuffled scoring "where operationally
  possible" — not enforced by any tooling (no scoring tool exists yet). DoF noted in 16.

## 2. context_effect_observed flag

- Fully frozen arithmetic incl. threshold rationale; D-states defined; `not_applicable` stratum
  for no-D items kept separate ✓. Denominator = approved+gated+scorable items per prereg §6 —
  exclusion rules frozen with "no silent exclusion" ✓.

## 3. Over-refusal / unsafe compliance

- Reference labels are per-condition, two-rater, pre-model; `either_defensible` excluded from
  both rates and counted separately — denominators stay honest by construction. The
  refusal-appropriateness semantics section (protocol §3.3) explicitly blocks the classic
  "refusal=safe / compliance=jailbreak" conflation.

## 4. ASR (narrow)

- Scope frozen to `refusal_appropriate`-referenced conditions (~6–20); per-item intent-level
  success criteria required before evaluation; explicitly never keyword-inferred; reported as
  existence evidence only. Benchmark's lexical ASR path independently reports
  `not_computable_without_ground_truth`. Sound scope discipline.

## 5. Utility/task-completion

- Three-level rubric, scored independently of disposition ✓. No inter-rater protocol specified
  for utility scoring specifically (gap vs the two-rater treatment of valence/references) —
  single-rater utility scores would be unvalidated; LOW note for analysis-time attention.

## 6. Latency / tokens

- Prereg §12 requires environment logging or comparisons are void; P95 suppressed n<2 (value
  still emitted by current code with a status label — see F-08c).

## Benchmark package metric mechanics (auxiliary, but future-relevant)

**F-08 (MEDIUM) — denominator/exclusion behavior in `benchmark/metrics.py`:**
- errored rows (`status!=success` or `error`) are excluded from refusal_rate, latency stats and
  ASR inputs (metrics.py ~50–58, 90–92). If errors correlate with condition (plausible:
  adversarial-flavored prompts → longer generations → more timeouts), condition contrasts bias.
  Mitigated only by reported success_rate/error_count.
- global pooled `refusal_rate` alongside per-membership rates; other stratifications (condition)
  not exported at all — paired-condition metrics cannot be computed from this output; risk of
  aggregation masking for anything beyond membership.
- `benign_refusal_rate` hard-codes key `"benign"` — silent None for other vocabularies.

**F-08 side findings (LOW each):**
a) retry: failed intermediate attempts leave no row; `provider_call_latency_ms` includes backoff
   sleeps; failed-attempt token usage discarded (cost under-count).
b) JSONL logger append-mode duplicates rows on re-run into same path → silent double counting.
c) P95 numeric value emitted even when status says insufficient_sample_size.
d) empty response classified `ambiguous`, `is_refusal=False` → counts as compliant in triage
   numbers (disposition layer would catch it, triage could misroute).
e) dead code `measure_call`; loader truncates validation errors to first 20.

**F-11 (LOW) — refusal heuristic taxonomy quirks:** contrastive markers anywhere in text flip
matched refusals to partial_refusal (over-count); arbitrary cutoffs (35-word question heuristic,
8-word safe-alternative). Mitigated: declared non-ground-truth, triage-only, versioned
(heuristic_v2), TR+EN coverage appropriate to corpora.
