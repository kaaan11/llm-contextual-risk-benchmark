# LOW-Finding Triage — pre_eval remediation

Criteria per campaign brief: FIX_NOW / DOCUMENT_ONLY / DEFER_POST_PILOT / NO_ACTION.

| ID | Finding | Decision | Action taken | Rationale |
|---|---|---|---|---|
| F-05 | Stale 7E review packet presented as current | **FIX_NOW** | Superseded banner added to `docs/phase7e_researcher_review.md` pointing at live state | One-line doc edit; removes a real misreading hazard; touches no frozen artifact |
| F-07 | Batch-4 clustering of AM items | **DOCUMENT_ONLY** | Caveat paragraph added to `docs/phase7g_human_qc.md` §9 and clarification doc §3 | Re-shuffling would alter the sealed blind packet mid-review — worse than documenting; per-item blinding unaffected |
| F-11 | Refusal heuristic quirks | **NO_ACTION** | None beyond existing in-repo documentation | Detector is versioned, self-declared non-ground-truth, triage-only by frozen protocol; changing heuristics now would add unvalidated variance before calibration exists |
| F-18 | NB defuse / NH preview properties | **DOCUMENT_ONLY** | Recorded as binding limitation C8 inside the frozen clarification document (R1 constraint 8) | Changing stimuli is prohibited by R1; visibility-before-evaluation is the requested remedy |
| F-20 | Tests hard-coding live progress counts | **FIX_NOW** | `test_summary_declares_phase_incomplete` replaced by derivation-equality test; annotation-count test now derives from append-only history | Removes mid-QC test-editing pressure (a degrees-of-freedom hazard); assertions got stronger, not weaker |
| F-21 | No clustered-domain handling in SAP | **DOCUMENT_ONLY** | Governance note in clarification §3 (preregistration governs; narrative limitation required) | Adding statistical corrections now would change frozen analysis rules — prohibited |
| F-24 | Non-atomic metadata writes; rerun duplicates | **PARTIALLY FIX_NOW, rest DEFERRED** | Duplicate-row detection + fail-closed JSONL append guard implemented (F-08); atomic-write hardening deferred | Duplicate rows are a silent-bias vector (fixed); crash-window torn writes are an operational nuisance at pilot scale |
| F-26 | Falsifier numbering divergence 7D vs prereg | **DOCUMENT_ONLY** | Governance note in clarification §3 (prereg §19 governs) | 7D design file is hash-frozen; editing it would break the integrity chain for zero analytical gain |
| F-27 | Narrative token table ≠ generated report | **FIX_NOW** | `docs/phase7f_stimulus_generation.md` numbers corrected to match `stimulus_statistics.json`, with correction note | Pure factual drift in a non-frozen methodology doc; eliminates future contradiction |
| F-28 | Duplicated ban lists drifted | **FIX_NOW** | Test list extended to the union of both implementations (test is now strictly strongest); comment documents single-source intent | Frozen prompts already satisfy both lists (verified); union prevents silent future divergence without touching builder behavior or stimuli |

INFO findings: none required action beyond what the clarification document already records
(INFO-04/05 remain noted in the audit register).
