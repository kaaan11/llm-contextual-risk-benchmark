# 08 — Annotation and Label Validity (Audit G)

Audits the annotation architecture without performing any future annotation.

## Architecture as built

- Layer separation (design intent / human reference / model observation) is enforced by field
  discipline + tests (`model_observed_effect` null everywhere; loader refuses
  `allow_observed_effect` records).
- Blinding: opaque BLIND-ids, deterministic seeded shuffle, sealed key, validator scans packet
  for design-term leakage (mutation-killed), invalidated-session machinery exists and was used
  once correctly (session 1 anchored → invalidated; session 2 clean → single accepted
  annotation).
- Two-rater protocol: rater fields exist; agreement statistics computed only from two real
  raters; fabricated-statistics mutation killed (M-04); no κ pass/fail threshold with recorded
  justification.

## F-06 (HIGH) — Gate machinery cannot fire in a one-rater pilot

Code path facts:
- `apply_phase7g_annotations.py::record_blind` sets `adjudicated_valence` only when **both**
  raters agree; `evaluate_gate()` runs only `if item["adjudicated_valence"]`.
- The documented one-rater mode ("A one-rater pilot is allowed", phase7g doc §3) therefore
  leaves every item `PARTIAL_ONE_RATER` with `gate_result=None` **permanently**.
- Consequences: falsification criteria F5/F6 — whose inputs are gate outcomes — become
  unmeasurable in exactly the mode the tooling permits; prereg §6 inclusion rule 2 (adjudicated
  valence) can never be satisfied, so *no item* would enter primary analysis.
- Additional gap: neither `record_decision` KEEP checks nor `validate_phase7g_review.py`
  enforce the documented requirement that KEEP needs "isolated gate passed or explicitly judged
  acceptable" (doc §8). A hypothetical two-rater flow could KEEP a `ISOLATED_VALENCE_GATE_FAIL`
  item with nothing recording an explicit judgement; prereg inclusion rules would still exclude
  it from analysis, but the QC gate would diverge from its documented semantics silently.
- Mitigating context: currently 1 rater has begun; if the researcher completes via one-rater
  mode, Phase 8's analysis base is empty under the frozen rules — this would surface before any
  evaluation, so the defect wastes effort rather than corrupting results. Severity HIGH for
  pipeline validity; blocking only if one-rater completion is attempted without adding an
  adjudication rule (which must itself be recorded pre-evaluation).

## Circularity check

Searched for model→human→reference→model loops: none possible in current architecture — Layer B
is timestamped before evaluation; disqualifying raters who saw output is specified (§1); no
field back-fills from Layer C (tests pin C-fields to null). Post-treatment labels: refusal-
appropriateness references are per-condition, assigned pre-model ✓; utility rubric applied post-
hoc but scored independently of disposition ✓ (frozen).

## Missing-label / ambiguity handling

Non-scorable states defined; modal-over-3 rule; disagreement → adjudication → REVISE fallback;
no forced labels; exclusions reported. Sound on paper; execution risk concentrates in F-06.

## Blind-integrity residuals

- Key seal is self-referential (`opened:false` inside the openable file). M-13: naive flip is
  caught by tests, but a real-world "opened it and put it back" leaves no trace. Process-level
  limitation inherent to repo-only enforcement → INFO/MEDIUM note (F-23b).
- Batch composition clustering (F-07) gives sequential raters base-rate hints (see 06 §5).
