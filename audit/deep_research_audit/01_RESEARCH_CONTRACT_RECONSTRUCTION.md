# 01 — Research Contract Reconstruction

Baseline document. Everything below is reconstructed from repository evidence, with the
authoritative source noted per element. Where artifacts disagree, precedence observations are
recorded (the pre-registration itself claims governance in `PHASE_7D_EXPERIMENTAL_DESIGN.md`
header: "Where this document and docs/phase7e_preregistration.md disagree, the pre-registration
governs").

## 1. Primary research question

> Can conversational context materially change the risk interpretation of the **same** final
> user prompt?

Sources: `docs/phase7e_preregistration.md` §1; `docs/PHASE_7D_EXPERIMENTAL_DESIGN.md` §1;
README; stimulus README. Consistent everywhere.

## 2. Hypotheses (frozen)

- H1 context sensitivity exists (dual-use items show `context_effect_observed`);
- H2 legitimating context does not cost usability (median Δ_AB ≤ 0);
- H3 incriminating context increases caution (median Δ_BC ≥ 0);
- H0a no context effect; H0b movement explained by neutral filler D; H0c reversed direction.
Falsifiers F1–F6 frozen (prereg §19). F6 = high failure rate of non-null items at the blind
isolated-prompt gate.

## 3. Experimental unit and conditions

- Unit: one research item (one canonical final prompt P, SHA-256 pinned). n = 50;
  dual-use subgroup n = 30. A/B/C/D are repeated paired conditions, never independent samples.
- A final_prompt_only · B full_context_legitimating · C full_context_incriminating ·
  D neutral_filler_control (21 items only).
- Planned runs: (16×3)+(14×4)+(7×4)+(13×3) = 171 per model per repetition; 513 per model at the
  frozen 3 repetitions. Verified against dataset: condition instances A=50 B=50 C=50 D=21.
- Context roles actually used: user–assistant–user (3 turns) or u-a-u-u (4 turns, AM items).
  See F-02: preregistration §5 says "context role (user–user only)".

## 4. Item taxonomy (verified against data)

| Category | n | control_strategy | D arm | Role |
|---|---:|---|---:|---|
| dual_use_nonnull | 30 | T×16 / N×14 | 14 | primary estimand |
| persistent_ambiguity | 7 | N×7 | 7 | expect clarification |
| null_benign | 7 | F | 0 | floor control |
| null_highrisk | 6 | F | 0 | ceiling control (context laundering) |

Matches prereg §3 table, design table, stimulus statistics report exactly.

## 5. Outcome variables

- Primary: ordinal model_disposition 0–4 (full_compliance → full_refusal) + non-numeric states
  (`unscorable_content`, `unscorable_unstable`, `missing`, `api_error`). Modal over 3 reps.
- Paired deltas Δ_AB/Δ_AC/Δ_BC/Δ_AD; four-state D-control interpretation; binary
  `context_effect_observed` flag with frozen rationale for the ≥1-step threshold.
- Secondary: refusal-appropriateness violations (over-refusal / unsafe compliance), utility
  (completed/partial/not_completed), latency/tokens, narrow intent-level ASR on ceiling items only.

## 6. Annotation strategy

Three separated layers (annotation protocol §1): A design intent (researcher, pre-authoring),
B human reference (two blinded raters, post-authoring pre-model), C model observation
(post-run). Blind isolated-prompt gate with 5-point valence scale; banned-token authoring
constraint for Condition A; per-condition refusal-appropriateness references assigned before any
model output; adjudication recorded; κ reported descriptively with no pass/fail threshold.

## 7. Statistical strategy (frozen)

Descriptive-and-paired primary (transition matrices, discordant counts); McNemar exact restricted
to genuinely paired within-item binaries; Fisher exact for dual-use vs nulls; Wilcoxon supporting
only; Clopper–Pearson whole-stratum CIs; explicit prohibitions (no per-cell p-values, no
bootstrap on small cells, no prevalence/cross-model claims); multiplicity disclosed without
adjustment.

## 8. Lifecycle and gates

Phase 7D design (frozen snapshot) → 7E researcher review (50/50 KEEP, history append-only,
snapshots before write) → 7F deterministic English stimulus build (v1, hash-pinned) →
**7G blind human QC — INCOMPLETE (current gate)** → dataset freeze v0.1 → Phase 8 model
evaluation (blocked on 7G + researcher approval + API access). Pre-registration frozen
2026-08-14T00:00:00Z, protocol `LLM-CTX-PILOT-2026-01` v1.0.1 (one documented amendment).

## 9. Provenance/integrity mechanisms

Per-file SHA-256 + composite protocol hash recomputable by stated method; protected-dataset
baseline hashes; immutable version-1 policy; append-only JSONL histories; pre-write snapshots;
deterministic builds; negative-control tests. Weaknesses: no VCS commits exist (no external
anchor); `.gitignore` would exclude histories/snapshots from any future push (F-04);
self-referential seal on the blind key (M-13 discussion).

## 10. Current state (verified)

Schema 0.2.0; pilot datasets byte-intact; stimuli v1 built and structurally valid; Phase 7E
review COMPLETE (50 KEEP @ 2026-08-14T14:00Z); Phase 7G infrastructure complete with exactly one
accepted rater_a annotation (BLIND-001) and 0 decisions; no model calls anywhere
(`evaluation_state` all false; smoke summary confirms providers `not_evaluated`).

## 11. Authority relationships

Preregistration > 7D design doc > README/PROJECT_STATUS (narrative). Live machine records
(`results/dataset_audit/*.json`) > generated markdown packets (which can be stale — see F-05).
The stimulus dataset embeds its approved design and tests enforce equality with the review file.
