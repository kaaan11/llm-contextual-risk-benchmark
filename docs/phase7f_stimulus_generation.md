# Phase 7F — Controlled English Stimulus Generation

**Status:** COMPLETE — stimuli generated, nothing approved, nothing evaluated.
**Stimulus version:** 1 · **Dataset version:** 0.3.0 · **Language:** English
**Next gate:** Phase 7G (blind human review + QC) — **not started**

---

## 1. Generation methodology

Phase 7F converts researcher-approved research-item *metadata* into actual English
evaluation stimuli. It is a construction phase, not a design phase.

Inputs:

- `results/dataset_audit/phase7e_review.json` — 50 items, all `review_decision = KEEP`,
  `researcher_approved = true`
- `dataset/pilot/multiturn/stimulus_content_du.py` — authored content, 30 dual-use items
- `dataset/pilot/multiturn/stimulus_content_ctl.py` — authored content, 20 control items

Pipeline (`scripts/build_stimulus_dataset.py`):

1. Load approved items; refuse to emit a stimulus for anything not approved.
2. For each item, take the authored canonical final prompt and hash it.
3. Assemble A/B/C, and D where and only where the approved design says so.
4. Run a five-question self-audit per item.
5. Run structural validation, a safety pre-filter, a design-leakage scan, and an
   overlap scan.
6. Emit the dataset, the JSONL mirror, and five audit reports.

The build is deterministic: no randomness, no network, no model API.

### What this phase deliberately did not do

No hypothesis, metric, threshold, decision rule or analysis method was touched. The
pre-registration documents are byte-identical to their recorded hashes, and a test
asserts this on every run. No design field was edited.

## 2. Researcher-approved design preservation

Each record embeds its approved design under `design`, copied verbatim. A test compares
every embedded design against `phase7e_review.json` and fails on any difference, so the
design cannot drift silently as stimuli are edited.

**One conflict arose and was resolved in the design's favour.** `RI-DU-001` was drafted
with a neutral-filler arm, but its approved `control_strategy` is `T` (no D arm). The
drafted D was removed rather than the design amended. This is recorded here because the
opposite resolution — quietly upgrading the design to match the draft — is exactly how
approved specifications rot.

## 3. Canonical prompt construction

`canonical_final_prompt` is authored once per item and is the single source of truth.
The builder injects that same string object into the final user turn of every condition,
so divergence is structurally impossible rather than merely discouraged. SHA-256 is
recorded and re-derived from each condition during validation.

Non-null prompts (37 items: 30 dual-use + 7 persistent-ambiguity) were written under an
explicit ban list: no authorisation claim, no lab/educational/research disclaimer, no
concealment or evasion verb, no named target or victim, no self-limiting hedge. A test
enforces the ban list against the final prompts. The intent is that Condition A reads as
genuinely dual-use, so that the interpretation signal can only come from B or C.

Whether that intent succeeded is **not** established by this phase. It is a hypothesis
about the text, and Phase 7G's blind review is what tests it.

## 4. Condition construction

**A — `final_prompt_only`.** Exactly one user turn containing the canonical prompt.
Nothing from B, C or D leaks in: no authorisation statement, role claim, ownership
claim, intent claim, category name, expected-effect text or other metadata.

**B — `full_context_legitimating`.** Preceding turns that make a legitimate reading
credible through concrete task detail — what is broken, what is being migrated, what the
cost or compliance pressure is — rather than through an assertion of legitimacy.
Phrases like "I am authorized", "this is a lab" and "for educational purposes" were
avoided; a scan enforces that they do not appear in final prompts, and the drafting
guidance kept them out of context turns too.

**C — `full_context_incriminating`.** Preceding turns that make a concerning reading
credible through *situation and intent*: an unauthorised target, a concealment
objective, avoidance of oversight, contradiction with an earlier scope, escalation from
a sanctioned setup to an out-of-scope ask. C never contains method. There are no
exploitation, credential-theft, persistence, evasion, destructive or malware procedures
anywhere in the dataset.

B and C are matched within an item on turn count and kept close on length, differing in
what the situation *means* rather than in how much text there is.

### Turn shapes

| Category | Shape | Turns |
|---|---|---:|
| dual-use, null-benign, null-high-risk | user / assistant / **user(final)** | 3 |
| persistent-ambiguity | user / assistant / user / **user(final)** | 4 |

Consecutive user turns in the ambiguity items are intentional and match the pattern
already present in the exploratory corpus: a user adds a qualifying detail and then
asks. Actual turn counts matched the approved `intended_turn_count` for all 50 items —
zero deviations.

## 5. D control construction

D exists on 21 items (14 dual-use marked `N`, plus all 7 ambiguity items), matching the
approved designs exactly.

Construction rules applied:

- **Neutral with respect to the target interpretation.** D never legitimises, never
  incriminates, and introduces no ownership, authority or intent signal.
- **Topically plausible.** D stays in the same subject neighbourhood — log file naming
  for an audit-log item, scrape interval for a telemetry item, MTU for a routing item.
  This matters: filler that is *obviously* irrelevant is trivially ignorable, which
  would make the control pass vacuously and let a priming effect masquerade as meaning.
- **Structurally comparable.** Same turn count as B and C for that item.
- **Documented.** Every D arm carries a written `d_control_rationale` explaining why it
  is interpretively inert; a test requires one.

D answers one question only: *could an observed B/C shift be explained by extra length
or generic priming?* It does not eliminate all priming confounds and is not claimed to.

## 6. Context length control

Recorded per item: `turn_counts` and `estimated_input_tokens` for each condition, plus
`context_token_spread` (max − min across the context conditions).

| Condition | n | mean | median | min | max |
|---|---:|---:|---:|---:|---:|
| A | 50 | 19.9 | 20.5 | 12 | 34 |
| B | 50 | 80.0 | 77.5 | 48 | 121 |
| C | 50 | 76.3 | 77.0 | 46 | 104 |
| D | 21 | 74.1 | 73.0 | 57 | 92 |

Context-condition spread: mean 9.6, median 7.5, max 33 estimated tokens. No item exceeds
40. (Numbers corrected during remediation to match the generated
`results/dataset_audit/stimulus_statistics.json` exactly — audit finding F-27.) **Exact token equality was not pursued and no scenario was rewritten to force it** —
the goal is avoiding extreme differences, not manufacturing symmetry at the cost of
naturalness.

`estimated_input_tokens` is a documented heuristic (whitespace words × 1.3), not a
tokenizer output. It supports relative comparison only.

## 7. Naturalness

Variation comes from the scenarios rather than from templating. No filler turns were
added to hit a turn-count target. A test asserts that no context turn text is reused
across research items; the three short refusal turns in the high-risk controls that
initially collided were rewritten to differ. Within a single item, B and C may share an
assistant turn — that is deliberate matching, not templating.

## 8. Context mechanism fidelity self-audit

Every item was checked against five questions, recorded per record under `self_audit`:

1. Does the context provide the intended semantic signal?
2. Does it avoid introducing unintended stronger signals (valence leakage into the final
   prompt)?
3. Does the final prompt remain unchanged across conditions?
4. Could a human researcher explain why B and C differ?
5. Does D remain neutral where present (documented rationale)?

All 50 items passed all five. This is an automated structural self-audit, **not** a
substitute for human judgement about whether a scenario is convincing.

## 9. Provenance

`authoring_method = researcher_specified_llm_assisted_draft` ·
`generation_assistance = drafting_only` · `source = original` · `source_seed = null` ·
`stimulus_version = 1` · `stimulus_generation_version = phase7f-v1`.

No expert authorship claimed. No expert validation claimed. The design layer is the
researcher's; the English wording is an AI-assisted draft written to that design.

Nothing was copied, translated, or adapted from a public benchmark, and no known
jailbreak template was reproduced.

## 10. Versioning

`stimulus_version = 1`. A Phase 7G revision produces version 2 with version 1 preserved;
prior versions are never deleted. The Phase 7D design specification and the Phase 7E
review record are not overwritten by this phase.

## 11. Safety review

An automated scan runs every turn against patterns for code blocks, destructive shell
commands, credential literals, private keys, cloud access keys, email addresses, IP
addresses, URLs, CVE identifiers and hostname-like strings.

**Result: 0 findings across all 171 condition instances.**

The scan is a **pre-filter**. It does not constitute human safety review, and
`stimulus_safety_scan.json` records `human_review_performed: false`. Any future finding,
including a suspected false positive, must be reviewed by a human before release.

### High-risk ceiling items

The six `null_highrisk` items are written as plain harmful **requests** carrying no
operational content: no code, no procedure, no real vulnerability identifier, no real
organisation, no target. Tests assert the absence of code markers, procedural language
and target identifiers in these items, and cap the length of their scripted assistant
turns so the dataset never models compliant harmful behaviour.

These items are retained deliberately. They are the only instrument in the study capable
of detecting **context laundering** — a model that refuses under A but complies under a
legitimating B. Without them, laundering would be indistinguishable from, and could be
reported as, a usability improvement. No item required the stop-and-flag path in section
14 of the phase brief.

## 12. Overlap detection

Generated final prompts were compared against this repository's corpora
(`dataset/pilot/records.jsonl`, `dataset/pilot/multiturn/records.jsonl`) using exact
SHA-256 matching, NFKC + casefold + whitespace-collapse normalised matching, and Jaccard
similarity over normalised tokens with a 0.60 flag threshold.

**Result: 0 exact duplicates, 0 normalised duplicates, 0 high-similarity matches.** All
50 canonical prompts are distinct from one another. No public benchmark data was
modified.

**Caveat.** No external public jailbreak corpus is vendored in this repository, so this
scan could not compare against XSTest, JBB-Behaviors or WildGuardMix. The pending
public-benchmark audit (`results/dataset_audit/overlap_report.json`, status
`preliminary_blocked`) remains a prerequisite for any analytical combination with those
datasets.

## 13. Limitations

- Stimuli are **not human-reviewed**. Ambiguity of the non-null prompts is an authoring
  intention, not a verified property; Phase 7G may fail items.
- The dialogue was AI-drafted and will later be used to evaluate models — the human
  blind review is what breaks that circularity, and it has not run.
- Scenarios are constructed, not observed. Incriminating context is a safety-bounded
  proxy for real adversarial intent and is plausibly milder.
- Token figures are heuristic estimates.
- English only; no cross-lingual claim.
- External benchmark overlap remains unverified (section 12).

## 14. Phase boundary

Not performed in Phase 7F: blind isolated-prompt review, refusal-appropriateness
reference assignment, any model or API call, ASR, refusal rates, latency, model
comparison, or any stimulus approval. `researcher_qc` is `false` and
`stimulus_review_status` is `PENDING` on all 50 records.

Phase 7G is the next gate and requires explicit researcher approval to begin.
