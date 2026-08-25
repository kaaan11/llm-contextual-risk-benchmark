# 13 — Reproducibility Audit (Audit L)

Question: could an independent researcher clone this repository and reproduce the intended
experiment?

## What is already reproducible (verified)

- **Deterministic builds:** stimulus builder has no RNG/network/API; re-run reproduces identical
  bytes (hard-coded CREATED_AT; verified by reading + negative controls). Blind shuffle uses a
  fixed seed (`build_phase7g_review.py` `random.Random(SHUFFLE_SEED)`).
- **Environment:** Python 3.11+ required; stdlib-only runtime observed (pytest only for tests).
  Auditor reproduced the full suite on Python 3.14.4 / pytest 9.1.1: 314/314 pass — no version
  fragility observed in range.
- **Commands documented** (README): tests, builders, validators — all ran successfully during
  this audit from a clean copy.
- **Integrity verification:** composite hash recomputation is fully specified and reproducible.

## Gaps that will bite at Phase 8 unless closed first

**F-10 (MEDIUM) — generation-parameter pinning is conditional:**
- If `ExperimentMetadata.generation_parameters` is empty, OpenAI/OpenWeight payloads carry no
  sampling params (provider defaults apply, unrecorded); Anthropic silently receives
  `max_tokens=1024` while smoke configures 256. Prereg §16 requires temperature/top_p/max_tokens
  fixed-and-recorded before evaluation; the runner records what it is given but does not *require*
  it. A preflight assertion ("generation_parameters non-empty and within frozen values") does not
  exist outside the smoke path.
- Model **version** strings are metadata-only; requests transmit only the model id → server-side
  alias drift possible between repetitions/days; prereg §16 requires exact version recording,
  which the framework supports but cannot enforce against the provider.

**F-24 (LOW/MEDIUM) — run-artifact hazards:**
- JSONL response logger opens append-mode: re-running into the same output dir silently
  duplicates rows (double-counting downstream).
- Metadata/metrics written with plain `write_text` (non-atomic; last-writer-wins on crash).
- No run-ID collision detection on output directories.

## Ordering / randomization / caching

Runner is strictly serial in dataset order; no shuffling (fine — order is deterministic and
recorded); no client caching; `"store": false` hard-coded for OpenAI (good for privacy and
cache-free reproducibility). Concurrency absent → latency comparisons uncontaminated by
self-induced load, at time cost.

## Timeout/retry policy

Frozen values exist in config (30s smoke; provider defaults 60/60/120s; retry max 2, backoff
0.5→4s, retryable classes defined). Retry internals partially invisible (F-08a). Adequate for a
pilot if prereg §12's logging requirements are honored.

## Environment provenance

Smoke summary records absolute Windows paths (`C:\Users\Kaan\...`) — an environment fingerprint
in an artifact (gitignored, local-only). Harmless now; would leak operator paths if ever
committed. INFO.

## Verdict

Pre-evaluation layers are effectively reproducible today. Phase 8 reproducibility depends on
closing F-10/F-24 in the runner configuration *before* the first live call, per prereg §16's own
freeze list.
