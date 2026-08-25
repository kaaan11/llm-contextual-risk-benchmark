# 12 — Versioning and Provenance (Audit K)

Lifecycle traces of representative items.

## Trace 1 — ordinary KEEP item (RI-DU-001)

7D design v1 (`created_at` 2026-08-14T00:00Z) → immutable snapshot `phase7e_design_snapshot.json`
(hash-pinned) → review packet row PENDING → decision KEEP @14:00Z (history event #2;
pre-write snapshot captured; `reviewer_role` records self-review session explicitly, reviewer_id
null-by-declaration) → stimulus v1 embeds design verbatim (equality test-enforced) → blind packet
entry BLIND-001 (prompt byte-matches dataset). One documented deviation: a drafted D arm was
REMOVED because approved strategy is T — design won over draft, recorded in 7F doc §2. Chain is
complete and non-overwritable by tooling (re-decide = conflict, M-series evidence).

## Trace 2 — revised item

No REVISE exists yet (50/50 KEEP at 7E; 0 decisions at 7G). Machinery verified by negative tests:
REVISE preserves version 1, opens pending version-2 request with reason + re-review flag if the
prompt changes (M-series + unit tests kill violations).

## Trace 3 — null item (RI-NH-003)

Design F-strategy ceiling control → KEEP → stimulus: plain intent-level request; scripted C-turn
refusal capped; safety patterns clean; blind packet contains only opaque id + prompt. Provenance
fields complete (`source original`, seed null, authoring method declared).

## Trace 4 — control-bearing item (RI-DU-003, N-strategy)

D arm present with written rationale; condition availability consistent across dataset, review
state, blind key mapping (category/expected_valence sealed inside key).

## Immutability mechanics verified

- Append-only histories: truncation detected by tests (MUT M-12 killed).
- Pre-write snapshots exist for both 7E execution and each 7G write path; snapshot overwrite
  refused by tool.
- Version-1 preservation asserted for stimuli (`test_phase7f_stimulus_v1_preserved` compares live
  bytes to pre-QC snapshot) — killed under mutation in M-01 family.
- Re-deciding a decided item raises conflict (tool + validator + tests agree).

## Weaknesses found

**F-04 (MEDIUM):** `.gitignore` excludes `results/*` except `dataset_audit/*.json`; therefore
both append-only JSONL histories, all snapshots/, smoke artifacts and mock runs are outside any
future VCS; combined with **zero commits existing today**, the whole provenance chain has no
repository anchor (see 11 §Gaps). Not a data defect — an anchoring/exposure defect.

**F-23b (INFO):** blind-key seal is a boolean inside the sealable file; no external notarization
of "unopened" state exists (tests catch naive flips only).

**Timestamp semantics (INFO):** snapshot filenames carry write-time stamps while internal
`generated_at` fields keep build times (documented in NAF-01 to prevent misreading); runner-side
timestamps are second-truncated (sub-second ordering unrecoverable — future evaluation concern,
LOW).
