# AUDIT_MASTER_REPORT — Deep Research Audit

**Scope:** full campaign A–Q + adversarial pass + self-critique, executed read-only against
canonical artifacts; executable work confined to an isolated snapshot; 14 mutation experiments;
canonical-tree integrity re-verifiable against `evidence/baseline_hashes.json`.

---

## Executive verdict

## **READY WITH CONDITIONS**

No fundamental design failure exists. The measurement instrument is internally coherent,
byte-level integrity claims verify end-to-end, the statistical plan matches the design, the
tooling survived 13/14 mutation attacks, and the current phase gate (7G) is honestly blocked.
One HIGH finding qualifies the *interpretation* of the primary result (not its mechanics), one
frozen-protocol wording defect and one annotation-pipeline gap must be settled before any model
call, and status-narrative hygiene needs repair. All conditions are resolvable without touching
frozen analysis rules or regenerating stimuli.

## Research contract summary

Per repository evidence: a pre-registered (`LLM-CTX-PILOT-2026-01` v1.0.1, composite hash
recomputed OK) matched-within-item pilot asking whether conversational context changes risk
interpretation of a byte-identical final prompt. 50 research items (30 dual-use estimand, 7
persistent-ambiguity, 7 benign floor, 6 harmful ceiling), A/B/C contexts plus D filler on 21
items = 171 paired condition instances, ordinal disposition outcome, human blinded reference
labels assigned pre-model, descriptive-and-paired statistics with explicit prohibitions. Current
gate: Phase 7G human blind QC — 1 of 50 isolated annotations submitted, 0 decisions.

## Finding counts

| Severity | n | IDs |
|---|---:|---|
| CRITICAL | 0 | — |
| HIGH | 1 | F-01 |
| MEDIUM | 7 | F-02, F-03, F-04, F-06, F-08, F-10, F-23 |
| LOW | 10 | F-05, F-07, F-11, F-18, F-20, F-21, F-24, F-26, F-27, F-28 |
| INFO | 6 | INFO-01…06 |
| STRONG_INFERENCE | 1 | SI-01 |
| HYPOTHESIS | 1 | HYP-01 |
| NOT_A_FINDING | 4 | NAF-01…04 |

## Blocking findings (must be resolved before Phase 8)

1. **F-01 (HIGH):** scripted assistant turns carry directional interpretive/refusal-preview
   content exclusively in C (and validating content in B); D does not isolate this channel.
   Condition: record a protocol clarification of the estimand and commit to stratified reporting
   (assistant-turn-shared AM items vs differing-turn DU/NB/NH items) in the frozen reporting
   frame — before first model call.
2. **F-02 (MEDIUM):** preregistration §5 "context role (user–user only)" contradicts the actual
   u-a-u(/u) stimuli. Condition: documented amendment/clarification before evaluation (permitted
   now, forbidden after).
3. **F-06 (MEDIUM):** blind gates cannot be computed in the doc-permitted one-rater mode, and no
   tool enforces the documented isolated-gate KEEP requirement. Condition: fix the rater plan
   (two-rater completion, or recorded single-rater adjudication rule added pre-evaluation).

## Non-blocking findings

F-03 (stale status artifacts incl. the self-declared authoritative PROJECT_STATUS),
F-04+F-23 (provenance lacks any VCS anchor; histories/snapshots gitignored), F-08/F-10
(benchmark-layer metric denominators; conditional generation-param pinning), plus the ten LOW
and six INFO items — hygiene, robustness, and documentation currency.

## Strong inferences (separate from confirmed findings)

- SI-01: unstratified Phase 8 results would include an unquantified assistant-stance component
  in Δ effects (behavioral magnitude unknowable until models run).

## Unresolved hypotheses (separate from findings)

- HYP-01: elevated F6 gate-failure risk concentrated in specific prompts (candidates listed);
  only the pending human review can resolve it — by design.

## Successful controls (survived adversarial review)

- Byte-identical canonical prompts across all 171 conditions; SHA-256 chain fully reproducible,
  including the composite hash and the six protected datasets.
- Deterministic stimulus build replayed byte-identically during the audit.
- Blind-instrument integrity: opaque ids, seeded shuffle, leak-scan validator (mutation-killed),
  invalidated-session machinery used correctly once.
- Anti-fabrication guards: agreement statistics, reviewer identity, auto-approval, re-decision
  conflicts, append-only histories — all enforced and mutation-tested.
- Honest negative bookkeeping everywhere else: no results, no expert claims, providers
  `not_evaluated`, overlap audit openly blocked.
- The falsifier-first architecture (D arm, H0a–c, F1–F6 as reportable outcomes) is genuinely
  falsifiable as built.

## Audit coverage

All 17 audits A–Q completed. Read in full: preregistration, annotation protocol, 7D design +
table, 7F/7G methodology docs, both stimulus content modules, builder, apply/validate tools
(7E+7G), key benchmark modules (via structured digest + targeted verification), schemas,
PROJECT_STATUS/README, all dataset_audit JSON reports. Programmatic forensics: counts, hashes,
byte-equality, duplicates, lexical/stance features, redundancy, batch composition, determinism
replay. Tests: full suite executed (314 pass); validators executed; 14 mutations recorded.
Coverage gaps listed below.

## Limitations

- No model was run; all behavioral claims about models remain prospective.
- Git history absent → timeline verification relies on internal timestamps' mutual consistency,
  not independent witnesses.
- Human-judgment constructs (prompt ambiguity, context realism) were assessed textually and
  programmatically, not by eliciting new human ratings (out of scope for an auditor).
- External benchmark overlap cannot be audited from this repository (sources not vendored).
- The single existing annotation's clean-session provenance is self-reported within artifacts.

## Recommendation

Proceed to complete **Phase 7G**, after: (i) settling the rater plan per F-06, (ii) recording the
F-02 clarification and the F-01 estimand note as pre-evaluation amendments, and (iii) repairing
status-roll-up hygiene (F-03) and VCS anchoring (F-04/F-23). Then, before Phase 8: execute the
prereg §16 freeze list with enforced generation-parameter pinning (F-10) and error-accounted
metric outputs (F-08). No stimulus regeneration, no rule changes, and no redesign are required
by any finding.
