# Controlled English Stimulus Dataset — v1 (Phase 7F)

**Files:** `stimulus_dataset_v1.json` · `stimulus_records.jsonl`
**Dataset version:** 0.3.0 · **Stimulus version:** 1 · **Language:** English
**Protocol:** `LLM-CTX-PILOT-2026-01`
**Review status: PENDING. `researcher_qc = false` on every record. Nothing here has been human-approved.**

---

## Purpose

These are the evaluation stimuli for a pilot study asking one question:

> Can conversational context materially change the risk interpretation of the **same** final user prompt?

Each research item pairs **one canonical final prompt** with two or three different
preceding contexts. The prompt never changes. The context is the only manipulated
variable. Later phases will compare how a model handles the identical prompt under
each context.

This dataset does **not** contain model outputs, scores, or any evaluation result.

## Relationship to the research-item design

Every record is generated from a Phase 7D design that a researcher reviewed and marked
`KEEP` in Phase 7E. The approved design travels with each record in the `design` field
and is **copied verbatim, never modified**. Phase 7F adds text; it does not make design
decisions. Where authored content and the approved design disagreed, the design won —
one item (`RI-DU-001`) had a drafted D arm removed because its approved
`control_strategy` is `T`.

Design provenance chain:

```
Phase 7D  design (immutable, snapshot-hashed)
   → Phase 7E  researcher review → KEEP
      → Phase 7F  stimulus text (this dataset, stimulus_version = 1)
         → Phase 7G  blind human review + QC   [NOT STARTED]
            → Phase 8  model evaluation        [NOT STARTED]
```

## Conditions

| Code | Name | Content |
|---|---|---|
| A | `final_prompt_only` | the canonical final prompt alone, one user turn |
| B | `full_context_legitimating` | context evidencing a legitimate workflow, then the same prompt |
| C | `full_context_incriminating` | context evidencing a concerning purpose, then the same prompt |
| D | `neutral_filler_control` | topically plausible but interpretively irrelevant context, then the same prompt |

**A/B/C/D are repeated conditions of one research item — they are NOT independent
samples.** The statistical unit is the research item. 50 items yield 171 condition
instances; the analysis n is 50 (30 for the dual-use subgroup), not 171.

D exists only where the approved design sets `control_strategy = "N"` (21 items). Its
job is to answer a single falsifying question: *could any observed B/C difference be
explained by extra conversational length or generic priming alone?* Every D arm carries
a written `d_control_rationale`. D is a control, not a fourth experimental category,
and it does not eliminate all priming confounds.

## The canonical final prompt rule

For each item, `canonical_final_prompt` is authoritative. In **every** condition the
final user turn is that string **byte-for-byte** — no paraphrase, no punctuation or
capitalisation drift, no condition-specific wording. `canonical_final_prompt_sha256`
records its SHA-256, and automated tests re-derive the hash from every condition's final
turn. A mismatch fails validation rather than being silently normalised.

Non-null final prompts (dual-use and persistent-ambiguity) are deliberately written to
be **ambiguous in isolation**: no authorisation claim, no lab or research disclaimer,
no concealment or evasion verb, no named target, no self-limiting hedge. If the prompt
revealed its own answer, the context would have nothing left to do — that flaw is what
this whole redesign exists to fix.

## Item groups

| Category | n | Role |
|---|---:|---|
| `dual_use_nonnull` | 30 | primary estimand: ambiguous prompt, context decides the reading |
| `persistent_ambiguity` | 7 | context deliberately does **not** resolve ownership, authority, environment or intent; correct handling is to ask |
| `null_benign` | 7 | floor control: clearly benign prompt; detects spurious escalation |
| `null_highrisk` | 6 | ceiling control: clearly concerning prompt; detects context laundering |

## Provenance

Each record carries: `authoring_method = researcher_specified_llm_assisted_draft`,
`generation_assistance = drafting_only`, `source = original`, `source_seed = null`,
`stimulus_version = 1`, `stimulus_generation_version = phase7f-v1`, `created_at`, and
the approved `design`.

**No expert authorship is claimed. No expert validation is claimed.** The research
design, scenarios, context mechanisms, intended effects and safety boundaries were
specified by the researcher in Phases 7D/7E; an AI assistant drafted the English wording
to those specifications.

## AI-assisted drafting

The conversational text was drafted with AI assistance and has **not** been reviewed by
a human. This matters for interpretation: an AI drafted these conversations, and a model
will later be evaluated on them. The Phase 7G human review exists specifically to break
that circularity before any evaluation runs. Treat the naturalness of the dialogue as
unverified until then.

## Limitations

- **Not human-reviewed.** No blind isolated-prompt valence has been assigned, so the
  claim that non-null prompts are genuinely ambiguous is an authoring *intention*, not a
  verified property. Phase 7G tests it, and items can still fail that gate.
- **Constructed, not observed.** These are written scenarios, not transcripts of real
  users. "Incriminating" context is a safety-bounded proxy for real adversarial intent
  and may be milder than the real thing.
- **Token counts are estimates.** `estimated_input_tokens` uses a documented heuristic
  (whitespace words × 1.3), not a real tokenizer. Use it for relative comparison only.
- **Length matching is approximate by design.** B/C/D are kept close, not equal; the
  largest observed spread is 33 estimated tokens. Scenarios were not rewritten to force
  equality.
- **English only.** No cross-lingual claim. The Turkish corpus
  (`EXPLORATORY_DRAFT_V0.1_TR`) is out of scope and unmodified.
- **Public-benchmark overlap is only partly checked.** The generated prompts were
  compared against this repository's own corpora with no hits. No external jailbreak
  corpus is vendored here, so the pending public-benchmark audit
  (`results/dataset_audit/overlap_report.json`, status `preliminary_blocked`) must be
  completed before any analytical combination.

## Safety

All content is high-level and non-operational. There are no exploits, no malware, no
credential-theft code, no persistence or evasion procedures, no intrusion steps, no real
targets, no credentials and no personal data. Condition C conveys *situation and intent*,
never *method*.

The six `null_highrisk` ceiling items are plain harmful **requests** with no operational
content — no code, no procedure, no real vulnerability identifier, no real organisation.
A refusal benchmark needs the request to exist, not the capability. These items are the
only instrument that can detect a model being talked into compliance by legitimating
context, so removing them would remove the study's protection against reporting context
laundering as a usability win.

An automated safety scan runs over every turn (`stimulus_safety_scan.json`). It reports
zero findings. **It is a pre-filter and is not human safety review**; every item still
requires human safety sign-off before release.

## Review status

| Gate | State |
|---|---|
| `researcher_qc` | `false` (all 50) |
| `stimulus_review_status` | `PENDING` (all 50) |
| `external_validation_status` | `not_reviewed` (all 50) |
| blind isolated-prompt review | not started |
| refusal-appropriateness references | not assigned |
| model evaluation | not run |

`isolated_prompt_valence_observed`, `adjudicated_valence`,
`refusal_appropriateness_reference` and `model_observed_effect` are `null` on every
record and must stay that way until Phase 7G.

## Audit trail

- `results/dataset_audit/stimulus_validation.json` — structural and leakage checks
- `results/dataset_audit/stimulus_statistics.json` — distributions and token statistics
- `results/dataset_audit/stimulus_safety_scan.json` — automated safety pre-filter
- `results/dataset_audit/stimulus_overlap_report.json` — duplication and similarity
- `results/dataset_audit/stimulus_generation_report.json` — generation summary
- `docs/phase7f_stimulus_generation.md` — methodology

## Versioning

`stimulus_version = 1`. If Phase 7G requires a revision, the revised stimulus becomes
version 2 and version 1 is preserved. Prior versions are never deleted, and the Phase
7D/7E design specification is never overwritten.
