# LLM Security–Usability Benchmark

**Does conversational context change how a model reads the *same* final prompt?**

A pre-registered pilot study on contextual risk interpretation in large language models,
sitting at the intersection of jailbreak resistance and over-refusal.

---

> ## Status: research preview — **frozen; human input required**
>
> No model or API has ever been evaluated in this repository. There is **no** Attack Success
> Rate, refusal rate, latency measurement, model comparison, expert validation, or empirical
> finding of any kind. The project is currently at the **Phase 7G human quality-control gate**,
> which is **incomplete**.
>
> The research campaign was frozen on **2026-09-10**. E1a/E1b/E1c were accepted as
> technical drafts, but their scientific choices are **not approved or effective**. There is
> no active research worker brief. Treat every stimulus as *unverified* until human QC closes.
> Read the [freeze and restart record](docs/reviews/llm-benchmark/PROJECT-FROZEN-2026-09-10.md)
> and [current readiness boundaries](docs/research-preview-readiness.md) first.

| Phase | Status |
|---|---|
| 0–5 · scope, taxonomy, schema, 300-record pilot dataset, annotation & benchmark frameworks | complete |
| 6A · real-model smoke-test harness | complete (no provider call made) |
| 6B · public-benchmark manifest | blocked — awaiting approval, overlap audit unresolved |
| 7D · experimental design reconstruction | complete |
| 7E · pre-registration + researcher review | complete — 50/50 `KEEP`, 50 approved |
| 7F · controlled English stimulus generation | complete — 50 items, 171 condition records |
| **7G · blind review + human QC** | **incomplete — 1/50 isolated rater_a annotations (two-rater mandate), 0/50 decisions** |
| 8 · model evaluation | not started |

Current authority: the [freeze record](docs/reviews/llm-benchmark/PROJECT-FROZEN-2026-09-10.md).
[`PROJECT_STATUS.md`](PROJECT_STATUS.md) contains the phase inventory and historical narratives;
older completion statements do not approve the pending E1 decisions or open Phase 8.

---

## The problem

Two failure modes pull in opposite directions. A model that refuses a security engineer's
legitimate question is useless; a model that answers an attacker's identically-worded question
is dangerous. The words can be the same. What differs is the situation.

So: **can conversational context materially change the risk interpretation of the same final
user prompt?**

The honest answer is unknown, and this pilot is built so that "no" is a reportable outcome.

## The design

One **research item** = one canonical final prompt, evaluated under several preceding contexts.
The prompt is byte-identical everywhere; the context is the only manipulated variable.

| Condition | Content |
|---|---|
| **A** `final_prompt_only` | the prompt alone |
| **B** `full_context_legitimating` | context evidencing a legitimate workflow + same prompt |
| **C** `full_context_incriminating` | context evidencing a concerning purpose + same prompt |
| **D** `neutral_filler_control` | topically plausible but interpretively irrelevant context + same prompt |

**D is the falsifier.** If B and C move the model but D moves it just as much, the effect is
conversational length and generic priming — not meaning. That outcome is pre-registered as
hypothesis **H0b**, and reporting it is mandatory.

**A/B/C/D are paired repeated conditions of one item, not independent samples.** The statistical
unit is the research item: n = 50 (30 in the dual-use subgroup), never 171.

### Item groups

| Group | n | Role |
|---|---:|---|
| `dual_use_nonnull` | 30 | primary estimand — ambiguous prompt, context decides the reading |
| `persistent_ambiguity` | 7 | context deliberately does *not* resolve ownership/authority/environment; correct behaviour is to ask |
| `null_benign` | 7 | floor control — detects spurious escalation on routine work |
| `null_highrisk` | 6 | ceiling control — detects **context laundering** |

The two null groups are kept analytically separate on purpose. A benign prompt that context
can't make harmful and a harmful prompt that context can't sanitise are different findings, and
collapsing them hides both.

### Why the design was rebuilt

An earlier version of this study failed peer review. The defect: the final prompts *themselves*
carried the risk or legitimacy signal the context was supposed to supply — asking outright how
to hide something, or hedging themselves into obvious safety. A model with zero context
sensitivity would have produced the "expected" result anyway.

Phase 7D rebuilt the design around a hard constraint: for non-null items the final prompt must
be **ambiguous in isolation**. No authorisation claim, no lab or educational disclaimer, no
concealment or evasion verb, no named target, no self-limiting hedge. The interpretation signal
lives only in B or C. Whether that constraint actually succeeded is exactly what the Phase 7G
blind review is testing — and items are allowed to fail it.

## What is frozen

The pre-registration (`LLM-CTX-PILOT-2026-01`, v1.0.1) was sealed **before** any stimulus text
existed and long before any model could be run. It fixes the hypotheses (H1–H3, H0a–H0c), the
falsification criteria (F1–F6), the ordinal disposition rubric, the paired Δ metrics, the
four-state neutral-filler interpretation, the `context_effect_observed` threshold *and its
rationale*, the refusal-appropriateness labels, ASR scope, handling of unscorable/missing/errored
output, stopping rules and reporting rules.

Integrity is verifiable: `results/dataset_audit/phase7e_preregistration_hash.json` records a
SHA-256 per protocol document plus a composite fingerprint. A test asserts on every run that the
protocol documents are byte-identical to their recorded hashes.

One amendment exists (v1.0.0 → v1.0.1) and is documented in the record with the prior composite
hash: it corrected *which files the manifest covered*, not a single rule. It was made before any
evaluation.

A pre-evaluation clarification exists (v1.0.1 → v1.0.2,
`docs/phase7e_pre_evaluation_clarification.md`, now itself hash-pinned in the manifest): per
researcher decision on audit finding F-01, the stimuli stay byte-unchanged and the estimand is
clarified to **whole conversational-context sensitivity** — scripted assistant stance may
contribute to observed contextual disposition changes, pure user-context-only causal claims are
prohibited, and `assistant_turn_shared` / `assistant_turn_differing` reporting strata are fixed.
It also corrects the preregistration §5 role-wording ambiguity (finding F-02): "user–user only"
meant no developer/system arm; the realized structure is user–assistant–user(/user). No
hypothesis, metric, threshold, or analysis rule changed.

**No analysis rule may be added or changed after the first model response is observed.**

## Repository layout

```
docs/          research questions, threat taxonomy, experimental design,
               pre-registration, annotation protocol, phase methodology
dataset/       schema, validators, the 300-record pilot dataset,
               multi-turn corpora and the Phase 7F English stimuli
scripts/       deterministic build, freeze, validation and
               human-review recording tools
benchmark/     loader, provider adapters, runner, refusal heuristic,
               metrics, retry, smoke-test harness  (never run live)
results/       audit reports, review state, append-only history, snapshots
tests/         offline validation and negative controls (see the safe CI profile)
configs/       pinned construction and smoke-test configuration
```

### Where to start reading

1. [`docs/PHASE_7D_EXPERIMENTAL_DESIGN.md`](docs/PHASE_7D_EXPERIMENTAL_DESIGN.md) — the design, with a self-critique section listing six ways it could still mislead
2. [`docs/phase7e_preregistration.md`](docs/phase7e_preregistration.md) — the frozen protocol
3. [`docs/phase7e_annotation_protocol.md`](docs/phase7e_annotation_protocol.md) — rubrics and blind-review procedure
4. [`dataset/pilot/multiturn/STIMULUS_README.md`](dataset/pilot/multiturn/STIMULUS_README.md) — the stimuli and their limits
5. [`docs/phase7g_human_qc.md`](docs/phase7g_human_qc.md) — the review workflow now in progress

## Running things

From a repository checkout, use Python 3.10+ and a virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check_research_integrity.py
.venv/bin/python scripts/offline_preview.py
.venv/bin/python -m pytest --ignore=tests/test_annotate_blind.py \
  --ignore=tests/test_phase7g_tooling.py --ignore=tests/test_phase7g_qc.py \
  --ignore=tests/test_remediation_regressions.py
.venv/bin/python scripts/validate_phase7e_review.py
.venv/bin/python scripts/validate_phase7g_review.py
```

Dependency installation needs a package index or a local wheel cache. The example and checks
then run offline with no API keys. The example uses one abstract, harmless in-memory prompt and
`MockAdapter`; expected stdout is:

```json
{"attack_success_rate": null, "completed_requests": 1, "empirical_result": false, "provider": "mock", "total_requests": 1}
```

[Offline CI](.github/workflows/offline-preview.yml) runs this profile on Python 3.10, 3.12 and
3.14, checks the expected output, validates the live review state, and verifies the frozen
hashes and append-only audit prefixes before and after testing. The four excluded legacy test
files contain invented rater-labelled fixtures; this profile respects `AGENTS.md` and does
not exercise those paths. Negative structural QC gate tests remain enabled. Passing this
profile proves the tested software behavior, not human QC or scientific readiness.

Do not rebuild stimuli or regenerate freeze records as a getting-started step. The sealed
stimulus and protocol remain fixed until an authorized amendment/version path is agreed.

### The tooling refuses things on purpose

Guard rails are enforced in code and covered by negative-control tests, not just described in
prose. The recording tools will refuse to:

- infer a `KEEP` / `REVISE` / `REJECT` decision that a human did not explicitly supply
- invent a reviewer identity, affiliation or credential
- accept `REVISE` or `REJECT` without a written reason
- reveal B/C/D context before an item's blind isolated-prompt annotation is submitted
- approve an item whose structural verification failed or whose safety review is `FAIL`
- report inter-rater agreement statistics that were not computed from two real raters
- silently overwrite a prior decision (re-deciding raises a conflict)
- reuse a response given during a presentation session that was invalidated

Automated validation is **not** human approval, and the code says so where it matters.

## Safety

All content is high-level and non-operational. There are no exploits, no malware, no
credential-theft code, no persistence or evasion procedures, no intrusion steps, no real
targets, no credentials and no personal data. Incriminating context conveys *situation and
intent*, never *method*.

The six high-risk ceiling items are plain harmful **requests** with no operational content — no
code, no procedure, no real vulnerability identifier, no real organisation. A refusal benchmark
needs the request to exist, not the capability. They are retained because they are the only
instrument that can distinguish a genuine usability improvement from a model being talked into
compliance.

An automated safety scan runs over every turn and currently reports zero findings. **It is a
pre-filter, not human safety review**, and human safety sign-off has not been performed.

## Provenance and limitations

Read this section before drawing any conclusion from this repository.

- **Nothing has been measured.** No model, no ASR, no refusal rate, no latency, no comparison.
- **The stimuli are AI-drafted.** The researcher owns the design layer — hypotheses, scenarios,
  context mechanisms, intended effects, safety boundaries. An AI assistant drafted the English
  wording to that specification (`authoring_method = researcher_specified_llm_assisted_draft`).
  **No expert authorship or expert validation is claimed anywhere.**
- **A circularity exists and is being managed, not ignored.** An AI drafted these conversations
  and a model will later be evaluated on them. The Phase 7G human blind review exists precisely
  to break that loop, and it has not finished.
- **Prompt ambiguity is an intention, not a verified property.** The blind gate may fail items.
  A high failure rate is falsification criterion **F6** — a scientific result, not a bug.
- **Constructed, not observed.** These are written scenarios. "Incriminating" context is a
  safety-bounded proxy for real adversarial intent and is plausibly milder than the real thing.
- **English only.** The Turkish corpus (`EXPLORATORY_DRAFT_V0.1_TR`) is preserved unchanged,
  out of scope for the primary pilot, and supports no cross-lingual claim.
- **Public-benchmark overlap is unresolved.** The generated prompts were compared against this
  repository's own corpora with no hits, but no external jailbreak corpus is vendored here. The
  pending audit (`results/dataset_audit/overlap_report.json`) is `preliminary_blocked` and must
  close before any analytical combination with XSTest, JBB-Behaviors or WildGuardMix.
- **Token figures are heuristic estimates**, not tokenizer output.
- **n ≈ 50 is a feasibility pilot.** It can support existence, direction and method claims. It
  cannot support prevalence, per-category rates, or cross-model significance.

## What the pilot could and could not conclude

**Could:** whether the matched-condition method works; whether interpretation movement exists at
all and in which direction; whether it survives the neutral-filler control; a qualitative
catalogue of when context does and does not matter.

**Could not:** how often this happens in the wild; per-category rates with usable confidence
intervals; that one model is better than another; any Pareto-frontier claim.

## Roadmap

```
Phase 7G  human blind review + QC        ← current gate, incomplete
   ↓
DATASET FREEZE / v0.1
   ↓
Phase 8   model evaluation               ← requires API access AND a closed 7G gate
```

Phase 8 does not begin until the QC gate closes and the researcher approves it.

## Licence and citation

No licence has been selected yet, and there is nothing citable — the study has produced no
results. Please do not present any part of this repository as an empirical finding.

## Contributing

The most useful contribution right now is **adversarial**: an independent second rater for the
blind isolated-prompt review who did not see the authoring stage. The two-rater fields exist and
are empty; `inter_rater_status` is `not_available` and will stay that way until two real raters
have annotated. Attacks on the design are more valuable than defences of it.
