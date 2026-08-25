# 20 — Finding Self-Critique

Every HIGH/MEDIUM finding attacked. Decisions: CONFIRMED / DOWNGRADED / RETRACTED / UNRESOLVED.

---

## F-01 — Assistant-turn interpretive channel uncontrolled (initial: HIGH)

1. **Restated.** B/C contexts embed scripted assistant turns; first-person commitment and
   refusal-preview phrasing occurs only in C (6/30 DU, 3/6 NH; preview regex hits 11 items);
   B assistant turns pre-validate legitimacy. Δ effects may partly measure prior-stance
   consistency rather than situation reading; D does not isolate this channel.
2. **Strongest evidence.** Quantified asymmetry (04/06); verbatim examples; AM items (shared
   assistant turn) are the exception that proves the design knows the channel matters.
3. **Strongest counterargument.** Prior assistant statements ARE conversational context in
   deployment; the research question ("can context change interpretation") is broad enough to
   include them; no frozen rule is violated; analysis can stratify by assistant-turn-sharing
   (AM) vs differing (DU/NB/NH) items post-hoc without redesign.
4. **Repository evidence for the counterargument.** 7D §10 rationale explicitly permits prior
   assistant turns; prereg §8.2's flag is defined on observed dispositions regardless of channel;
   design §30 self-critique shows the authors systematically enumerated threats — its silence here
   is an oversight, not an accepted-risk note.
5. **Reproduction attempt.** Re-ran stance/preview scans with alternate regex formulations —
   asymmetry persists under all variants (B never exceeds C).
6. **Decision: CONFIRMED, severity retained at HIGH**, with scope clarified: this is an
   *attribution/interpretation* bias of the primary estimand, not measurement corruption; frozen
   statistics remain internally valid for the broader construct "context effect including prior
   assistant stance". Retaining HIGH because H1–H3 are phrased around risk *interpretation* and
   the unstratified headline would overclaim that mechanism.

## F-06 — Gate machinery dead in one-rater mode + KEEP gate requirement unenforced (initial: HIGH)

1. **Restated.** `adjudicated_valence` requires both raters → in the documented one-rater mode
   gates never fire for any item → F5/F6 inputs and prereg inclusion rule 2 unsatisfiable;
   additionally no tool enforces doc §8's "isolated gate passed or explicitly judged acceptable"
   KEEP condition.
2. **Strongest evidence.** Code path (`record_blind`, `evaluate_gate` call condition); validator
   has no gate-at-KEEP check; doc §3 permits single-rater pilot.
3. **Strongest counterargument.** Failure surfaces before damage: `phase_complete` cannot be
   reached silently without decisions, and a researcher applying the frozen SAP would discover
   an empty eligible set during analysis planning — most plausibly *before* spending evaluation
   budget; impact is then procedural delay, not invalid inference.
4. **Evidence for counterargument.** Multiple independent checkpoints (7G counts, prereg freeze
   list, QC sign-off block) make silent passage unlikely.
5. **Reproduction.** Mutation M-series confirmed tools behave as coded; simulated one-rater
   completion state leaves every item PARTIAL with gate_result null (by construction).
6. **Decision: CONFIRMED, DOWNGRADED to MEDIUM** — blocking-with-warning rather than
   biasing; still must be resolved (two-rater completion, or a recorded adjudication rule added)
   before Phase 8.

## F-03 — Stale status artifacts contradict live record (MEDIUM)

Counterargument: README is correct and is the public front document; PROJECT_STATUS is internal
narrative. Rebuttal: PROJECT_STATUS declares itself "tek yetkili kaynak" (single authoritative
source) for phase-status conflicts — and it is the one that is wrong. Tooling root cause proven
(apply-tool write scope). **CONFIRMED, MEDIUM.**

## F-04 — Provenance chain outside VCS / zero commits (MEDIUM)

Counterargument: local-only policy is deliberate (`results/*` gitignored per retention rules);
hash verification works locally on every run. Rebuttal: deliberate exclusion of *raw responses*
does not explain excluding append-only decision histories and snapshots; zero commits means even
the freeze claim has no external witness. **CONFIRMED, MEDIUM** (anchoring weakness, not data
defect).

## F-02 — Frozen "user–user only" wording vs u-a-u(/u) stimuli (MEDIUM)

Counterargument: intent recoverable from 7D §10 ("no developer/system arm") — same paragraph,
same document family; no analysis rule depends on the phrase. Rebuttal: prereg governs by its
own declaration; leaving a known contradiction inside a frozen protocol into evaluation invites
a post-hoc deviation dispute. **CONFIRMED, MEDIUM** (fixable only by amendment before Phase 8).

## F-08 — Metric denominator exclusions & auxiliary quirks (MEDIUM)

Counterargument: errored-row exclusion is standard practice and success_rate/error_count are
reported alongside; triage layer is explicitly non-authoritative. Rebuttal stands partially:
condition-correlated error exclusion biases paired contrasts; paired deltas are computed from
human-scored dispositions where missing states are handled by frozen rules — so the *primary*
path is protected and the exposure is mostly in auxiliary benchmark metrics. **CONFIRMED but
DOWNGRADED scope note to MEDIUM-(low): primary analysis insulated; benchmark-layer metrics need
care if ever reported.**

## F-10 — Generation-parameter pinning conditional (MEDIUM)

Counterargument: prereg §16 makes fixing params a procedural requirement; smoke path demonstrates
correct usage. Rebuttal: procedures without enforcement failed exactly once already in this repo's
history (the stale-summary pattern). **CONFIRMED, MEDIUM.**

## F-23 — No external anchoring of the freeze (MEDIUM)

Counterargument: threat model for a pre-publication pilot is accident, not adversary; tests give
tamper-evidence. Rebuttal: tamper-evidence ≠ tamper-*proof*; a commit+push costs minutes.
**CONFIRMED, MEDIUM** as a pre-evaluation action item.

## LOW findings spot-check

F-05, F-07, F-11, F-18, F-20, F-21, F-24, F-26, F-27, F-28 re-verified against evidence; none
promoted (impact bounded), none retracted.

## RETRACTIONS

None required — no finding collapsed under its counterargument. Two initial classifications were
adjusted (F-06 HIGH→MEDIUM; F-08 scope narrowed), recorded above.

## UNRESOLVED

HYP-01 (which specific prompts will fail the blind gate) — resolvable only by the human review
itself; audit intentionally does not pre-judge it beyond flagging candidates.
