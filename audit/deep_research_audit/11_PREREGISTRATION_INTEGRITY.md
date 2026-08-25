# 11 — Preregistration Integrity (Audit J)

## What is frozen and how

Manifest `results/dataset_audit/phase7e_preregistration_hash.json`: protocol
`LLM-CTX-PILOT-2026-01` v1.0.1, frozen_at 2026-08-14T00:00:00Z, SHA-256 per file +
composite ("sha256 over newline-joined `<rel>:<sha256>` lines, sorted, UTF-8").

Auditor recomputation: all five protocol files match recorded hashes; composite reproduces
byte-exactly; six protected datasets equal baselines; declared-mutable files equal their
recorded current values.

Frozen content verified by reading: hypotheses H1–H3/H0a–c, falsifiers F1–F6, disposition rubric,
Δ metrics + D-states + flag threshold with rationale, refusal-appropriateness semantics, ASR
scope, utility rubric, latency rules, unscorable/missing/error handling, model/runtime freeze
list, stopping rules, reporting rules, language freeze, authorship separation, safety constraints,
claims boundaries. The frozen boundary is explicit and complete enough that PRE vs POST-HOC is
determinable from artifacts alone — for anything covered.

## Amendment audit

Single amendment v1.0.0→v1.0.1 documented in-record with prior composite hash:
manifest-scope correction (mutable review file out, immutable design snapshot in), zero rule
changes, made before any evaluation. Timeline consistent: freeze 00:00Z → decisions 14:00Z →
stimuli 15:00Z → blind infra 16:00Z → interface rev 19:00Z → invalidated session → clean session
20:00Z → first annotation 20:15Z. No post-hoc edit path exists without breaking the composite;
tests enforce byte-identity on every run (MUT M-02 killed).

## Gaps / limitations of the freeze

1. **No external anchor (F-23, MEDIUM).** Zero git commits exist; hashes are self-recorded.
   A motivated actor could rewrite docs + manifest + tests together and leave no trace. The
   freeze is therefore strong against *accident*, weak against *intent*. Standard remediation
   (commit + push, timestamping service, or third-party registration) is a researcher action —
   noted, not performed.
2. **Frozen-text defect inside the boundary:** prereg §5 "context role (user–user only)" vs
   u-a-u(/u) stimuli → F-02. Fixable only by amendment before evaluation.
3. **Boundary ambiguities resolved favorably during audit:** design-table counts superseded by
   generated table (declared in header); review packet md is not part of the manifest (correctly,
   since it is narrative).
4. `evaluation_state` flags (`model_evaluation_performed`, etc.) live in the same writable tree;
   they are corroborated by independent negatives (no runs dir contents, smoke summary
   `not_evaluated`, absence of any response artifacts) — consistency supports them, but they are
   not cryptographically bound into the composite.

## Verdict

PRE vs POST-HOC distinguishability: YES for analysis rules, thresholds, rubrics, exclusions,
hypotheses — verifiable today by hash recomputation alone, no researcher memory required.
Weakened only by absent external anchoring and the F-02 wording defect.
