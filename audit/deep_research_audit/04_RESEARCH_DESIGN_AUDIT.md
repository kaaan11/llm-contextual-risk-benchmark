# 04 — Research Design / Construct Validity (Audit C)

Question audited: could a model produce the expected A/B/C differences **without** exercising
the intended contextual-reasoning mechanism? Answer: yes — through at least one channel the
controls do not isolate, and one frozen-text ambiguity. Findings below; no redesign proposed.

## The construct as operationalized

The intended mechanism: the model reads situational evidence in preceding turns (ownership,
authority, environment, purpose) and re-interprets a byte-identical final prompt. Signals are
required to be *shown-not-asserted*; banned: standalone disclaimers/authorization claims.

## F-01 (HIGH) — Scripted assistant turns form an uncontrolled interpretive channel

**Evidence (programmatic + qualitative, full corpus):**

1. In all 30 dual-use items and all 13 null items, B and C have **different** assistant turns;
   only the 7 persistent-ambiguity items share identical assistant turns across B/C.
2. First-person stance markers in assistant turns (`I'd want/pause/stop`, `I can't help`,
   `not something I'll help with`, …): **B = 0 occurrences across 30 DU assistant turns;
   C = 6/30 DU + 3/6 NH**. An explicit refusal-preview regex hits **11 items**
   (RI-DU-010/014/016/020/026/030 + all six NH), always in C, never in B. Examples:
   - RI-DU-020 C assistant: "Working through a list of passwords against an account is the
     exact pattern lockout thresholds exist to stop, so I'd want to understand the situation
     before going further."
   - RI-DU-030 C assistant: "…gaining privileges beyond what you were given is the part I'd
     stop at…"
   - RI-NH-001 C assistant: "I'm not able to help with getting into a system that isn't yours."
3. Conversely, B assistant turns frequently pre-validate the legitimate frame
   ("Alert fatigue like that is its own risk", "Decommissioned-service snapshots are usually the
   easiest win").

**Why this matters.** A model continuing these conversations is under self-consistency /
persona-persistence pressure to align its final-turn disposition with the stance its scripted
prior turn already took. Part of Δ_BC may therefore measure *prior-stance following*, not
independent risk interpretation from user-turn situation evidence. The D arm cannot isolate this:
D assistant turns are topically neutral, so D controls generic length/priming but not
directional endorsement. No falsifier (F1–F6) detects it; the design's own self-critique §30
lists six other threats but not this one.

**Alternative explanation considered (and why the finding stands):** one can argue that in real
deployment an assistant's prior statements ARE part of conversational context, so stance-following
is legitimately inside the construct "context changes interpretation". That argument supports
external validity of a broad claim, but it does not support the specific mechanistic claim H1–H3
are phrased around (risk *interpretation* of the situation), nor does any control attribute the
two channels. The preregistration itself froze the confound framing that makes this matter (F-02).
Severity HIGH because it directly qualifies what a positive result would mean; it does not
invalidate measurement mechanics.

## F-02 (MEDIUM) — Frozen ambiguity: "context role (user–user only)"

Preregistration §5 lists among controlled confounds: "context role (**user–user only**)". Every
one of the 171 context conditions is u-a-u or u-a-u-u (verified programmatically). 7D §10 both
asserts "user–user multi-turn context only" and, in the same paragraph, permits "prior
`assistant`" turns — internally inconsistent shorthand whose intent (no developer/system arm) is
clear from rationale but whose literal wording contradicts the stimuli. Because the protocol is
frozen and uneditable post-evaluation, this requires a recorded clarification/amendment BEFORE
Phase 8 (allowed now; forbidden after first model response).

## Alternative explanations examined

| Channel | Status |
|---|---|
| Lexical risk cues in final prompt | Banned-list scan clean (06); residual paraphrase risk → HYP-01/gate |
| Authorization/disclaimer cues | none found in prompts or contexts as standalone assertions |
| Verbosity / length | controlled: mean |Δwords| B vs C = 5.0, max 25; token spread ≤33 est.; D arm for priming |
| Turn count / structure | matched within item (0 deviations); roles fixed |
| Position/recency | final prompt always last-user-turn by construction (uniform, non-confounding) |
| Assistant-stance channel | **NOT isolated** → F-01 |
| Genre reaction to suspicious text | acknowledged by design §30.1; quantified in 06 (RISK lexicon ~9× denser in C user turns); unavoidable component of the treatment, bounded by D + human gates |
| Item-domain clustering | mechanisms 49/50 unique; SAP lacks cluster handling → F-21 note |
| Topic difficulty asymmetry | same final prompt across conditions — eliminated by design |

## Verdict

The core instrument (byte-identical prompt, paired contexts, filler falsifier, human blind gate)
is sound and unusually well hardened for a pilot. The residual threat is F-01's attribution gap
plus the F-02 wording defect; both should be resolved on paper before Phase 8 (clarification,
stratified reporting by assistant-turn-sharing items [AM] vs differing-assistant items) — noting
that AM items (shared assistant turn, user-turn-only signal) already provide an internal
sub-stratum relevant to F-01, which analysis could exploit without redesign.
