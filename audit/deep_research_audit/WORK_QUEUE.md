# Deep Research Audit — Work Queue

Auditor: independent methodology / benchmark-integrity / reproducibility audit.
Mode: READ-ONLY vs canonical artifacts. All executable and mutation work was run in
`/tmp/opencode/AI_Search_snapshot` (full copy taken at campaign start).
The canonical tree received only `audit/deep_research_audit/**`.

## Environment / guarantees

| Item | Value |
|---|---|
| Canonical dir | `/home/kaan/AI_Search` |
| Working snapshot | `/tmp/opencode/AI_Search_snapshot` |
| Baseline hashes | `evidence/baseline_hashes.json` (133 canonical files, SHA-256 + size + mtime) |
| Test runner | `/tmp/opencode/audit_venv` (pytest 9.1.1, Python 3.14.4) |
| Git state of canonical repo | **0 commits on master** — no VCS history exists at all |
| Full suite result | **314 passed** in snapshot (18.8s) |

## Queue status

| # | Audit task | Output file | Status | Findings |
|---|---|---|---|---|
| 0 | Environment setup, snapshot, baseline hashes | WORK_QUEUE.md | DONE | — |
| 1 | Initial reconstruction (research contract) | 01_RESEARCH_CONTRACT_RECONSTRUCTION.md | DONE | — |
| A | Repository and artifact inventory | 02_ARTIFACT_INVENTORY.md | DONE | F-04 (gitignore/VCS) |
| B | Cross-artifact consistency | 03_CROSS_ARTIFACT_CONSISTENCY.md | DONE | F-03, F-05, NAF-01, NAF-02 |
| C | Research design / construct validity | 04_RESEARCH_DESIGN_AUDIT.md | DONE | F-01, F-02, HYP-01 |
| D | Dataset forensics (programmatic) | 05_DATASET_FORENSICS.md | DONE | INFO-03, NAF-03 |
| E | Condition leakage & confound campaign | 06_LEAKAGE_AND_CONFOUND_AUDIT.md | DONE | F-01 (quantified), F-07 |
| F | Null and control conditions | 07_CONTROL_CONDITION_AUDIT.md | DONE | F-18 |
| G | Annotation and label validity | 08_ANNOTATION_AUDIT.md | DONE | F-06 |
| H | Metric validity | 09_METRIC_VALIDITY_AUDIT.md | DONE | F-08, F-11 |
| I | Statistical design | 10_STATISTICAL_AUDIT.md | DONE | F-21 |
| J | Preregistration integrity | 11_PREREGISTRATION_INTEGRITY.md | DONE | F-22, positive controls |
| K | Versioning and provenance | 12_VERSIONING_AND_PROVENANCE.md | DONE | F-04, F-23 |
| L | Reproducibility | 13_REPRODUCIBILITY_AUDIT.md | DONE | F-10 |
| M | Validator & test audit + mutation tests | 14_VALIDATOR_AND_MUTATION_AUDIT.md | DONE | 14 mutations recorded |
| N | Failure-mode campaign | 15_FAILURE_MODE_AUDIT.md | DONE | F-09, F-24 |
| O | Researcher degrees of freedom | 16_RESEARCHER_DEGREES_OF_FREEDOM.md | DONE | F-20 |
| P | Phase-gate audit | 17_PHASE_GATE_AUDIT.md | DONE | F-25 |
| Q | Documentation vs reality | 18_DOCUMENTATION_REALITY_AUDIT.md | DONE | F-03/F-05 consolidated |
| 2 | Adversarial challenge pass | 19_ADVERSARIAL_CHALLENGE_PASS.md | DONE | HYP-02, NAF-04 |
| 3 | Self-critique pass | 20_FINDING_SELF_CRITIQUE.md | DONE | 2 downgrades, 0 retractions |
| 4 | Finding register maintenance | FINDING_REGISTER.md | FINALIZED | see register |
| 5 | Master report | AUDIT_MASTER_REPORT.md | DONE | verdict: READY WITH CONDITIONS |

## Evidence log (chronological)

1. Baseline hashed 133 canonical files before any work (`evidence/baseline_hashes.json`).
2. Recomputed all five preregistration protocol-file SHA-256s → all match manifest.
3. Recomputed composite protocol hash from manifest method → matches `d945d4…6819`.
4. Verified six protected datasets byte-identical to baselines.
5. Stimulus dataset forensics: 50/50/50/50 A/B/C(+21 D)=171 conditions; byte-equality of final
   turns verified against canonical prompt in every condition; SHA-256 re-derived per item;
   JSONL mirror identical to JSON; embedded designs equal phase7e_review current-version designs.
6. Blind-packet forensics: prompts match stimulus dataset exactly for all 50; mapping bijective;
   shuffle deterministic (fixed seed); batch/category composition extracted.
7. Discovered live Phase 7G annotation state: exactly 1 accepted rater_a annotation
   (BLIND-001 → RI-DU-008, probably_benign, low confidence, session 2 after invalidated session 1)
   vs quality_summary/human_qc/doc claiming 0.
8. Ran full test suite in pristine snapshot: 314 passed.
9. Read builder (`build_stimulus_dataset.py`), annotation apply tool, 7G validator in full.
10. Quantitative leakage analysis (stance markers, lexicon densities, turn reuse, banned tokens,
    D-arm neutrality) over all 171 conditions.
11. Redundancy analysis: max pairwise prompt Jaccard 0.27; no cross-item context-turn reuse;
    49/50 unique mechanisms ('research method' ×2 among NB items).
12. Mutation campaign M-01…M-14 on snapshot (see 14_VALIDATOR_AND_MUTATION_AUDIT.md).
13. Verified corpus_segment_count=768 reproducible from corpora.
14. Verified .gitignore exclusion set; confirmed zero-commit git state.

## Unresolved questions

- UQ-01: Whether the single BLIND-001 annotation was produced under the documented clean-session
  procedure cannot be verified beyond the file's own session record (self-reported).
- UQ-02: Researcher intent behind preregistration phrase "context role (user–user only)" vs
  user–assistant–user stimuli — resolvable only by a researcher clarification (recorded as F-02,
  does not block other audit work; escalation not required since 7D §10 states the rationale).
