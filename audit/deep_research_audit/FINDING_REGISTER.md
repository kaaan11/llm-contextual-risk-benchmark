# FINDING REGISTER — Deep Research Audit

Classification legend: CONFIRMED_FINDING / STRONG_INFERENCE / HYPOTHESIS / NOT_A_FINDING.
Severity: CRITICAL / HIGH / MEDIUM / LOW / INFO. No CRITICAL findings exist.

---

## F-01 · Scripted assistant turns form an uncontrolled interpretive channel
- **Class/Severity:** CONFIRMED / **HIGH**
- **Artifacts:** `dataset/pilot/multiturn/stimulus_content_du.py`, `stimulus_content_ctl.py`; prereg §5; 7D §10, §30
- **Evidence:** First-person stance markers in assistant turns: B 0/30 vs C 6/30 (DU) + 3/6 (NH); refusal-preview phrasing in C of 11 items (RI-DU-010/014/016/020/026/030, NH-001/002/003/005/006), never in B; B assistant turns pre-validate legitimacy (examples quoted in 04). Only the 7 AM items share identical B/C assistant turns.
- **Reproduction:** regex scans over all 171 conditions (06 §2); stable under alternate formulations.
- **Violated invariant:** prereg §5 confound-control intent ("context role user–user only", F-02 wording); construct claim that the interpretation signal "lives only in B or C [user-turn situation]".
- **Impact:** Δ_BC may partly measure prior-stance consistency; unstratified positive results would overclaim situation-reading mechanism.
- **Alternative explanation:** prior assistant statements are legitimately part of context → broadened construct interpretation; analysis-time stratification (AM sub-stratum) partially addresses without redesign.
- **Falsification attempt:** re-scans with different regexes; asymmetry persists.
- **Confidence:** HIGH (textual property certain; behavioral impact prospective).
- **Recommended action (not implemented):** record a protocol clarification + commit to stratified reporting by assistant-turn-sharing items before evaluation.

## F-06 · Blind-gate machinery cannot fire in one-rater mode; KEEP gate requirement unenforced
- **Class/Severity:** CONFIRMED / MEDIUM (downgraded from HIGH in self-critique)
- **Artifacts:** `scripts/apply_phase7g_annotations.py` (record_blind, evaluate_gate call condition), `scripts/validate_phase7g_review.py`, phase7g doc §3/§4/§8, prereg §6 rule 2
- **Evidence:** adjudicated_valence requires both raters; gates computed only from adjudicated value; doc-permitted single-rater pilot ⇒ all items stay PARTIAL with null gates forever; validator/tool lack any gate-at-KEEP enforcement despite doc §8 listing it as KEEP requirement 1.
- **Impact:** one-rater completion would make F5/F6 unmeasurable and empty the frozen analysis base (discovered late = wasted evaluation budget + post-hoc amendment pressure).
- **Alternative explanation:** early checkpoints make silent passage unlikely.
- **Confidence:** HIGH on code behavior; impact severity judgment documented in 20.
- **Recommended action:** decide rater plan now (two-rater completion or recorded single-rater adjudication rule added via amendment BEFORE evaluation); enforce gate status at KEEP.

## F-02 · Frozen preregistration phrase contradicts actual context roles
- **Class/Severity:** CONFIRMED / MEDIUM
- **Artifacts:** prereg §5 ("context role (user–user only)") vs all 171 conditions u-a-u(/u) (verified); 7D §10 internally mixed wording
- **Impact:** known contradiction inside frozen protocol at evaluation time invites deviation disputes.
- **Recommended action:** recorded amendment/clarification BEFORE first model call.

## F-03 · Phase 7G progress state stale across declared-authority artifacts
- **Class/Severity:** CONFIRMED / MEDIUM
- **Artifacts:** PROJECT_STATUS.md:15,88,129 ("0/50") vs README.md:28 ("1/50") vs phase7g_blind_review.json (1 accepted annotation, BLIND-001→RI-DU-008, session 2); quality_summary annotations_submitted=0; phase7g_human_qc.md "0 of 50"; blind_review.generated_at not refreshed on write
- **Root cause:** apply tool mode `blind` writes only blind_review.json (`targets=[BLIND]`); no refresh path exists for summary/QC/doc; test pins the stale 0 instead of cross-checking.
- **Impact:** PROJECT_STATUS declares itself the single authority for status conflicts and is wrong; misjudgment of gate readiness possible in either direction.
- **Recommended action:** regenerate roll-ups from live records; add cross-artifact consistency check; make apply tool update summary.

## F-04 · Provenance chain has no VCS anchor and is partially gitignored
- **Class/Severity:** CONFIRMED / MEDIUM
- **Artifacts:** git: 0 commits on master; `.gitignore` excludes `results/*` except `dataset_audit/*.json` → both review histories (.jsonl), snapshots/, smoke artifacts outside any future VCS
- **Impact:** freeze/provenance claims verifiable only against self-recorded hashes in working tree; no external witness; clone collaborator loses histories/snapshots.
- **Recommended action:** commit + push including histories/snapshots (or adjust ignore rules) before 7G completes.

## F-08 · Benchmark metric denominators exclude errored rows; auxiliary quirks
- **Class/Severity:** CONFIRMED / MEDIUM (primary analysis insulated; scope narrowed in self-critique)
- **Artifacts:** `benchmark/metrics.py` (~lines 50–58, 90–92, 104, 115–132); retry/logging interplay
- **Evidence:** errored rows excluded from refusal_rate/latency/ASR inputs; global pooled rate without condition export; hard-coded `"benign"` key; p95 value emitted despite insufficient-n label; append-mode JSONL duplicates on rerun; failed-attempt tokens discarded; provider latency includes backoff; dead `measure_call`.
- **Impact:** auxiliary metrics only; primary dispositions protected by frozen missing-data rules.
- **Recommended action:** if any benchmark-layer numbers are ever reported, add condition-stratified outputs + error-row accounting; fix logger mode.

## F-10 · Generation-parameter pinning conditional; model version metadata-only
- **Class/Severity:** CONFIRMED / MEDIUM
- **Artifacts:** `benchmark/adapters/providers.py` (Anthropic max_tokens fallback 1024 vs smoke 256; param spread only when provided), `types.py` ModelSpec (version never transmitted), runner (no preflight assertion)
- **Impact:** prereg §16 freeze-list requirements are procedural, not enforced; silent provider-default sampling would be unreproducible.
- **Recommended action:** add run-preflight asserting non-empty frozen generation params + version recording; log effective payload digest (request_digest already covers messages).

## F-23 · Freeze lacks external anchoring
- **Class/Severity:** CONFIRMED / MEDIUM
- **Evidence:** composite hash reproducible (verified) but self-recorded; zero commits; no timestamping/notarization.
- **Impact:** strong against accident, weak against intent.
- **Recommended action:** push to remote + optional trusted timestamp before evaluation.

## LOW findings
- **F-05** stale review packet md without superseded pointer (03).
- **F-07** batch composition clustering: batch 4 holds 6/7 persistent-ambiguity items; category runs up to 6 in shuffle order (06 §5).
- **F-11** refusal heuristic quirks: contrastive-marker partial_refusal over-count; arbitrary cutoffs; empty text → non-refusal ambiguous (triage-only mitigations documented) (09).
- **F-18** control-sensitivity notes: NB C-assistant turns pre-defuse incrimination (floor may pass vacuously); NH laundering signal concentrated in B arm with persona-consistency ambiguity (07).
- **F-20** tests couple to live progress counts (`assertEqual(len(annotated),1)`); mid-QC test edits create loosening temptation (14/16).
- **F-21** SAP lacks clustered-domain handling though design §30.6 flags dependence; bounded by 49/50 unique mechanisms + descriptive emphasis (10).
- **F-24** run-artifact hazards: non-atomic metadata writes; no output-dir collision detection (13/15).
- **F-26** falsifier list divergence 7D(F1–F5) vs prereg(F1–F6), undocumented in amendment header (19).
- **F-27** phase7f narrative token table ≠ generated report (C mean/min; spread mean/median) (19).
- **F-28** duplicated ban lists drifted between builder (17 terms) and test (14 terms); corpus currently clean under both (19).

## INFO
- INFO-01 WildGuardMix version string typo `"main (un*pinned)"`.
- INFO-02 historical vocabulary/distribution drift in superseded Phase 7B lineage.
- INFO-03 mechanism label "research method" shared by RI-NB-002/007 (distinct tasks).
- INFO-04 smoke summary contains operator Windows paths (gitignored artifact).
- INFO-05 runner timestamps second-truncated; snapshot filenames carry write-stamps vs internal generated_at (convention documented).
- INFO-06 blind-key seal is self-referential; real-world reads undetectable (process limit).

## STRONG_INFERENCE
- SI-01: If Phase 8 ran today unstratified, reported Δ effects would include an unquantified assistant-stance contribution (follows from F-01's confirmed textual property; behavioral magnitude unknown until models run).

## HYPOTHESES
- HYP-01: Elevated F6 gate-failure risk for specific DU prompts — benign-leaning candidates RI-DU-001/012/016/023; concerning-leaning candidates RI-DU-015 ("what stops it from doing so"), RI-DU-024 (obfuscation ask). Untestable until human blind ratings exist; audit does not prejudge outcomes.

## NOT_A_FINDING (investigated & rejected)
- NAF-01 PROJECT_STATUS "7E COMPLETE" vs review packet "ALL PENDING" — packet is pre-decision artifact; history/snapshots/live state coherent.
- NAF-02 corpus_segment_count=768 — reproduced exactly from stated method.
- NAF-03 stimulus redundancy — max prompt Jaccard 0.27; no context-turn reuse; intents unique.
- NAF-04 snapshot filename vs internal generated_at mismatch — naming convention, content coherent.
