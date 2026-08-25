# Phase 7E — Pre-Evaluation Clarification and Interpretation Record

**Protocol ID:** `LLM-CTX-PILOT-2026-01`
**Registers as:** protocol manifest version **1.0.2** (from 1.0.1)
**Type:** `pre_evaluation_clarification` — **rules_changed: false**
**Declared:** BEFORE the first model evaluation of this protocol. No model response exists for
any item of `llm-ctx-pilot-stimuli-en` v1 as of this record.
**Traceability:** remediation of audit findings **F-01** and **F-02**
(`audit/deep_research_audit/FINDING_REGISTER.md`;
`audit/deep_research_audit/f01/F01_INVESTIGATION_REPORT.md`), implementing researcher decisions
**R1** and recorded in `remediation/pre_eval/`.

> **What this document is not.** It does not add, remove, or modify any hypothesis (H1–H3,
> H0a–H0c), falsification criterion (F1–F6), metric, threshold, disposition rubric, exclusion
> rule, statistical test, or stopping/reporting rule. The frozen documents
> (`docs/phase7e_preregistration.md`, `docs/phase7e_annotation_protocol.md`,
> `docs/PHASE_7D_EXPERIMENTAL_DESIGN.md`, `docs/PHASE_7D_DESIGN_TABLE.md`,
> `results/dataset_audit/phase7e_design_snapshot.json`) remain byte-identical to their recorded
> hashes; this file is added to the integrity manifest so that it, too, is tamper-evident from
> now on. It interprets; it does not legislate.

---

## 1. Construct clarification (Decision R1 — resolves F-01)

The estimand of this pilot is **whole conversational-context sensitivity**: the change in a
model's handling of a byte-identical final user prompt when that prompt is preceded by
different preceding conversation. The preceding conversation in the frozen stimuli includes a
scripted prior assistant turn. The F-01 investigation established that for the
assistant-turn-differing stratum those scripted turns carry directional interpretive content
(legitimacy validation on one arm; explicit risk/intent interpretation and, on some items,
refusal previews on the other), which the D filler arm does **not** isolate.

### C1 — Interpretation constraint (binding on reporting)

Results MUST NOT be presented as identifying a pure causal effect of user-provided context
alone. Any observed contextual disposition change under this protocol is attributable to the
whole preceding conversation, of which scripted assistant stance is one component.

### C2 — Known pre-evaluation limitation

Assistant-turn stance contribution is a known interpretation limitation, identified and
documented BEFORE any model output existed (F-01 investigation; item-level map
`audit/deep_research_audit/f01/ITEM_LEVEL_ASSISTANT_CHANNEL_MAP.md`). It is neither a post-hoc
excuse nor a result-driven reinterpretation.

### C3 — Reporting strata (defined before evaluation)

- **`assistant_turn_shared`** stratum: the 7 persistent-ambiguity items
  RI-AM-001 … RI-AM-007, whose B and C assistant turns are byte-identical.
- **`assistant_turn_differing`** stratum: the remaining 43 items
  (RI-DU-001…030, RI-NB-001…007, RI-NH-001…006).
These labels are fixed by the frozen stimulus bytes and are reproducible from
`dataset/pilot/multiturn/stimulus_dataset_v1.json`.

### C4 — AM diagnostic/falsifier use

The `assistant_turn_shared` (AM) items MAY be used as a diagnostic/falsifier stratum: they are
the cleanest available within-design probe of user-carried situation signal uncontaminated by
differential assistant stance (expected movement toward clarification per the frozen design).

### C5 — AM non-control limitation

AM items MUST NOT be described as a randomized causal control for DU/NB/NH. They differ in n
(7 vs 30/7/6), construct (persistent ambiguity with deliberately unresolved context), expected
outcome topology (movement toward clarification, not signed restriction), topic mix, and control
strategy composition. Cross-stratum comparisons are diagnostic, not causal decompositions.

### C6 — D-arm limitation

The D neutral-filler arm controls generic length/priming only. It does **not** isolate or
control the assistant-stance channel. `negligible_filler_movement` must never be reported as
evidence that the assistant channel was ruled out.

### C7 — Aggregate-claim discipline

Aggregate context effects MUST NOT by themselves be described as demonstrating pure
situation-reading if the effect is materially concentrated in the `assistant_turn_differing`
stratum. Stratified presentation accompanies any aggregate claim.

### C8 — NH/NB standing limitations

The following F-01 investigation properties remain visible as limitations wherever NH/NB results
are reported: all six NH B arms script conditional compliance previews while all six NH C arms
script outright refusals (so laundering detection is effectively B-arm-biased and a positive B
result is ambiguous between frame-laundering and continuation of a willing prior turn); all
seven NB C arms defuse/re-benign the incriminating frame (so floor passes may partly reflect
scripted reframing rather than model robustness).

### C9 — No new primary covariate

No stance-intensity covariate is introduced into the primary analysis by this clarification.
The frozen primary analysis (ordinal transition matrices, paired deltas, D-states,
`context_effect_observed`, appropriateness violations) is unchanged.

### C10 — Exploratory/sensitivity space

If a stance-intensity analysis is ever performed, it may exist ONLY as an explicitly
pre-evaluation EXPLORATORY/SENSITIVITY analysis, clearly separated from the primary reporting
frame. None is registered by this document; registering one later would require its own
pre-evaluation record before any model output is observed.

## 2. Role-structure correction (resolves F-02)

Frozen preregistration §5 lists among controlled confounds: *"context role (user–user only)"*.
The frozen Phase 7F stimuli realize every context condition as **user → assistant → user**, and
for the seven persistent-ambiguity items as **user → assistant → user → user** (121 u-a-u and 21
u-a-u-u condition instances including D arms; zero system/developer roles anywhere).

- What was wrong: the phrase "user–user only" literally contradicts the realized structure.
- What was intended, and is hereby clarified as governing: **no developer/system-instruction
  context arm** (Phase 7D §10 rationale — developer framing is a different construct); prior
  *assistant* turns were explicitly permitted by the same design paragraph.
- This correction changes no hypothesis, metric, threshold, decision rule, or analysis method;
  it aligns the frozen wording with the frozen stimuli.
- Timing: recorded BEFORE first model evaluation; it is a clarification of ambiguity discovered
  by audit, not a result-driven change. Under the preregistration amendment rule, any change
  after the first observed model response would instead require a new protocol version AND a new
  experiment run.

## 3. Governance notes recorded at the same event

- **Falsifier numbering:** where `PHASE_7D_EXPERIMENTAL_DESIGN.md` §29 (F1–F5) and
  preregistration §19 (F1–F6) diverge, the preregistration governs and its numbering is
  authoritative (audit F-26). The superseded 7D list is historical.
- **Domain clustering:** item domains are largely distinct (49/50 unique mechanisms) but are not
  randomized; clustered-domain dependence remains a stated interpretive limitation (audit F-21),
  to be acknowledged in analysis narrative rather than corrected statistically in-pilot.
- **Blinding batch note:** the deterministic shuffle places 6 of 7 AM items in batch 4; reviewers
  proceeding batch-wise receive distributional hints for that batch (audit F-07). Per-item
  blinding is unaffected.

## 4. Verification hooks

- This file is a member of `protocol_files` in
  `results/dataset_audit/phase7e_preregistration_hash.json` from manifest version 1.0.2 onward;
  tests assert its byte-integrity on every run.
- The four original protocol documents remain asserted byte-identical to their v1.0.0 baselines.
- Protected datasets and the stimulus snapshot chain are untouched by this clarification.
