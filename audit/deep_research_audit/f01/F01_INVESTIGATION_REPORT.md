# F01_INVESTIGATION_REPORT

Focus investigation of audit finding F-01 — *scripted assistant turns form an uncontrolled
interpretive channel*. Read-only: no canonical artifact, stimulus, protocol, or status file was
modified. Evidence base: `stimulus_dataset_v1.json` (171 condition instances),
`stimulus_content_du.py`, `stimulus_content_ctl.py`, preregistration §5/§8, annotation protocol,
Phase 7G tooling/state. Machine layer: `item_level_assistant_channel.csv/.json`; item map:
`ITEM_LEVEL_ASSISTANT_CHANNEL_MAP.md`.

---

## Executive conclusion

**F-01 confirmed but impact likely bounded** — *conditional* on how the researcher frames the
estimand. The textual and semantic asymmetry is real, near-universal across the
assistant-turn-different stratum, and survives every falsification attempt except one partial
(balance of generic caution language). What remains genuinely unknown is behavioral magnitude,
which cannot be known without model evaluation. Impact is bounded **if** the estimand is
clarified and reporting is stratified (both available now, pre-evaluation, without touching
frozen analysis rules); it becomes material **only if** unstratified Δ results are reported as
pure situation-interpretation effects.

## Exact scope

| Stratum | n | B/C assistant turns | Differential interpretive channel |
|---|---:|---|---|
| dual_use_nonnull | 30 | differ in 30/30 | **present, strong**: C-assistant performs the concerning reading in 25/30 explicitly (+5 implicitly); first-person commitments 6; refusal previews 6 |
| persistent_ambiguity | 7 | **byte-identical 7/7** | absent by construction |
| null_benign | 7 | differ 7/7 | present but *inverted*: C-assistant defuses/re-benigns the frame 7/7 |
| null_highrisk | 6 | differ 6/6 | present, maximal and symmetric-in-direction: B previews compliance 6/6, C previews refusal 6/6 |
| **Total** | **50** | differ 43 / shared 7 | channel exists in 43 items |

No condition lacks an assistant turn (A has none by definition; every B/C(/D) has exactly one
prior assistant turn, which the evaluated model will treat as its own prior statement).

## Mechanism taxonomy (quantified)

Counts are items; strata noted. Full per-item coding in the map file.

| Category | B side | C side | D side |
|---|---|---|---|
| Neutral/procedural acknowledgement | DU 26 · AM 7(both arms) · NB 7 | AM 7(shared) | AM 7 procedural-topical |
| Legitimacy validation (light→explicit) | DU ~4 (RI-DU-001/019/021/028) | — | — |
| Risk interpretation (explicit naming/reframe of intent) | 0 anywhere | **DU 25** (+5 implicit = 30/30 carry direction) | — |
| Benign reframe / defuse of concerning frame | — | NB **7/7** (inverted use of same mechanism) | — |
| Refusal preview | 0 | DU 6 · NH **6/6** | — |
| Compliance preview (incl. conditional "I can talk at conceptual level") | NH **6/6** | DU 1 (RI-DU-001 conditional high-level) | — |
| First-person commitment markers | 0 | DU 6 (010/014/016/020/026/030); NH refusals are themselves commitments | — |
| Previous-answer stance (structural) | all 43 differing-asst items | same | AM unaffected |
| Semantic narrowing of final prompt | mild (helpful-task framing) | DU narrows toward cautious reading 30/30; NB toward benign 7/7; NH both directions | none |
| No meaningful directional signal | — | AM 7 (differential) | AM 7 |

Key structural fact: because the evaluated model authored (per its role) the prior assistant
turn, the final-turn disposition is measured under self-consistency pressure toward the scripted
stance. This applies in **both** directions (helpful B tone ↔ cautious C tone); the strict
first-person/refusal-preview markers are one-directional (C only).

## Falsification attempts

| Alternative explanation | Test | Result |
|---|---|---|
| Harmless conversational naturalness | realism was a design goal; natural ≠ non-confounding | **Partially upheld, does not exonerate**: naturalness explains why the channel exists, not what the final-turn disposition measures |
| Lexical differences without directional meaning | four independent lexicons (stance, authority-normative, reframe, previews) + full manual reading | **Rejected**: directional content is semantic (names who decides, what policy requires, what the request "really is"), not mere word-frequency noise |
| Equivalent information already in user context | new-information test: normative/authority tokens in C-assistant absent from C-user turns | **Split**: 17/30 DU assistants *add* normative framing the user turn lacked; in 13 the user turn already carries much of the signal (assistant reinforces) |
| Assistant merely restating | user→assistant token-overlap ratios | **Rejected**: overlap 0.04–0.24 in every stratum — assistants add new material everywhere |
| Concentrated in too few items | coverage counts | **Rejected**: differential assistant text in 43/50 items; interpretation-performing in 25/30 DU alone |
| Balanced B/C signals missed by regex | applied caution/validation lexicons symmetrically | **Partially upheld at generic level**: B aggregate engineering-caution hits exceed C (48 vs 36 in DU) — B turns are task-helpful with real caveats, not cheerleading. But stance-commitment/refusal-preview/authority-framing asymmetry is robust across all detectors. Note: bidirectional tonal steering is itself the confound, so balance at the generic level does not rescue attribution |

Distinct conclusions by level: **textual asymmetry — confirmed** (strict markers C-only);
**semantic asymmetry — confirmed** (interpretation performed in C, defused in NB-C);
**directional stance asymmetry — confirmed** (previews/commitments one-directional);
**behavioral impact — unknown without evaluation.**

## Causal interpretation

Intended: `user-context situation → interpretation of final prompt → disposition`.

Additional pathway present in 43/50 items:
`scripted assistant stance → continuation/self-consistency pressure → disposition`,
plus an interaction term (situation reads differently once the partner has framed it).

Separability within existing stimuli:

| Stratum | situation effect | stance effect | general multi-turn priming | separable? |
|---|---|---|---|---|
| AM (n=7, shared assistant, D arm) | primary signal | none differential | controlled by D | **yes, within-stratum** |
| DU/NB/NH (n=43) | entangled with stance | entangled | D controls generic priming only | **no, within-item** |
| A vs B/C/D contrasts | mix "any context" + content | — | — | no |

The two pathways point in the same direction for DU (C-situation and C-stance both restrictive;
B-situation and B-tone both permissive), so bias operates as **inflation of Δ magnitude and
potential fabrication of existence** where situation-only sensitivity is weak — directly relevant
to H1's existence claim. For NB, the defuse mechanism predicts floor passes that may reflect
assistant reframing rather than model robustness (weakens the spurious-escalation detector). For
NH, laundering detection runs almost entirely through the B arm and a positive B result is
ambiguous between frame-laundering and scripted-partner compliance pressure.

## AM natural-control assessment (conservative)

- Sample size: 7 vs DU 30 — adequate only for existence/direction, not magnitude.
- Construct similarity: moderate. AM contexts are *designed* to stay unresolved, which is
  plausibly why their assistant turns could remain neutral — neutrality co-occurs with item
  type (**selection confound** for using AM as "clean-channel control").
- Outcome topology differs: AM expects movement toward clarification (disposition 2), DU expects
  signed B→C restriction. Not exchangeable for estimating how much of DU's Δ_BC is stance-driven.
- Topic/risk distribution: workplace-governance flavored, milder than DU infra-security; all-N
  control strategy vs DU's T16/N14 mix.
- **AM comparisons CAN support:** existence/direction of user-turn-driven effects on
  clarification-seeking uncontaminated by differential assistant stance; a qualitative bound on
  "models read user-carried situation at all".
- **AM comparisons CANNOT support:** quantitative decomposition of DU effects; claims about
  dual-use restriction behavior; any prevalence-style statement (n=7).

## What can be concluded without model evaluation

1. The channel exists, its location (43 items), and its direction structure are established
   facts of the stimuli.
2. It is not isolated by any control arm, falsifier, or frozen metric; design §30's threat list
   omits it.
3. Preregistration §5's frozen confound language ("context role (user–user only)") is in
   tension with the realized u-a-u(/u) structure regardless of F-01 (audit F-02) — the same
   amendment event covers both.
4. Current sunk cost exposure: exactly one completed annotation (BLIND-001 → RI-DU-008,
   isolated prompt only) and zero context/safety/naturalness reviews — see timing fact below.

## What cannot be concluded without model evaluation

Whether stance-consistency actually contributes to observed dispositions; its size relative to
situation-reading; whether models distinguish scripted-partner framing from user-carried
situation; whether the NB defuse materially weakens the floor in practice; whether NH B-arm
compliance (if any) is laundering or persona continuation.

## Researcher decision options (decision space only — none implemented)

### Option A — No stimulus changes; clarify estimand + stratified reporting
- Addresses: attribution ambiguity in reporting; keeps all integrity chains intact.
- Remains: single unstratified headline would still overreach if discipline slips; mechanism
  never physically separated.
- Stimuli change: **no**. Frozen artifacts implicated: yes, one clarification/amendment note
  (prereg v1.0.2, permitted pre-evaluation) covering estimand wording incl. F-02's role phrase.
- Completed review invalidation: **none** (annotation is prompt-isolated; prompts unchanged).
- Hashes/build outputs: unchanged. Phase 7G restart: **no**. Primary estimand: broadened/
  clarified ("context includes conversational partner stance"), not structurally changed.

### Option B — Limited assistant-turn revision (proceduralize C interpretations / B previews; keep prompts and user turns byte-stable)
- Addresses: severs the stance channel physically for the 43 items; restores clean
  situation-reading estimand.
- Remains: topical priming (D still covers); revision introduces new authoring variance needing
  re-validation.
- Stimuli change: **yes** → sanctioned `stimulus_version 2`, v1 preserved (machinery exists:
  REVISE semantics; snapshot test updated through the documented flow).
- Frozen artifacts: protocol manifest untouched (stimuli are outside it); prereg amendment still
  advisable for §5 role wording.
- Review invalidation: **none retroactively** — the doc's own rule requires blind re-review only
  if the *canonical prompt* changes; prompts stable ⇒ BLIND-001 stays valid. Context/safety/
  naturalness reviews: none exist yet, so none to redo **today**.
- Hashes/build: stimulus dataset + reports regenerate (deterministic builder verified); protected
  corpora untouched. Phase 7G: continues on v2 without restart; batches not yet started in
  earnest. Estimand: returns to the original narrow form.

### Option C — Broader revision (user turns / regeneration)
- Only warranted if user turns themselves are judged defective — no audit evidence requires this;
  user-turn signal is the intended treatment. Highest cost; triggers blind re-review wherever
  prompts change. Listed for completeness.

### Option D — Analysis/instrument-layer alternatives (no stimulus edit)
- D1: pre-register (NOW, before evaluation) a stance-intensity covariate: code each item's
  assistant-turn stance during Phase 7G context review, report primary results with and without
  high-stance items. Requires recording the rule pre-evaluation to stay inside frozen-rules
  discipline; instrument field addition needs a recorded note (7G record_version bump).
- D2: physical counterfactual arms (C-situation with neutral assistant) — **design change,
  effectively redesign; unavailable without violating frozen structure**. Not recommended space.

Evidence dominance: no option strictly dominates. A minimizes cost and preserves every chain;
B uniquely restores the narrow mechanistic estimand; D1 combines cheaply with A and hedges the
main risk of A.

## Decision criteria (for researcher adjudication)

**Keep stimuli unchanged (A, optionally +D1) if any of these hold:**
1. The research claim of interest is the broad deployment-relevant one: *"does surrounding
   conversation — including an assistant's own expressed stance — change handling of an
   identical request?"* Under this wording the channel is part of the treatment, not a bug.
2. Reporting commitments will bind: stratified presentation (AM stratum; assistant-shared vs
   assistant-different) and mechanism-phrased limitations are written into the reporting plan
   BEFORE evaluation.
3. External validity is weighted above mechanistic attribution (real conversations contain
   partner stances; models deferring to their own prior statements is real-world behavior).

**Revise stimuli (B) before evaluation if any of these hold:**
1. Downstream use requires attributing effects to *situation reading specifically* (e.g.,
   benchmark consumers comparing models' contextual reasoning; theory-testing claims about risk
   interpretation).
2. The intended headline is H1-existence where a stance-driven artifact would be
   indistinguishable from the target phenomenon — i.e., no stratification safeguard will be
   enforced.
3. Cost is acceptable: today it is minimal (one prompt-isolated annotation survives; zero
   context reviews exist). This cost rises monotonically with every completed 7G batch — which
   makes **timing**, not evidence, the operative discriminator between A and B.

Objective trigger for deciding NOW under either choice: any further 7G context-review batch on
current text increases Option-B rework; nothing in the repository forces either branch.

## Recommendation on whether F-01 must be resolved before continuing Phase 7G

**Not strictly blocking, but economically it is a now-decision.** Nothing already completed is
invalidated by either branch (the sole annotation is prompt-isolated; no KEEP exists; no context
review exists). However, continuing batches before choosing A/B converts a currently-free
revision option into one that invalidates human work proportionally. The smallest-risk sequence
consistent with the evidence: decide A-vs-B (+optional D1) **before the next context-review
batch**; if A, register the clarifying amendment and stratification commitment immediately; if
B, execute the limited revision while rework is still zero. No recommendation between A and B
is made here — the criteria above are sufficient for the researcher to choose without auditor
preference.

---
*Investigation only. No canonical artifact, stimulus, protocol, rubric, status file, or frozen
hash was modified; verification against `evidence/baseline_hashes.json` remains valid.*
