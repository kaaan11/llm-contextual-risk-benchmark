# 05 — Dataset Forensics (Audit D)

Programmatic inspection of the complete research-item collection
(`stimulus_dataset_v1.json` + `stimulus_records.jsonl`), plus side verification of the
protected datasets.

## Structural results (all recomputed independently)

| Check | Result |
|---|---|
| Record count | 50 / 50 declared |
| ID uniqueness | 50 unique `research_item_id`; 50 unique triplets |
| Category distribution | DU 30 · AM 7 · NB 7 · NH 6 ✓ |
| control_strategy | T16 / N21 / F13 ✓; D-arm ⇔ N: 0 mismatches |
| Condition instances | A50 B50 C50 D21 = 171 ✓ |
| Canonical hash | SHA-256 re-derived per item == recorded field, 50/50 |
| Byte equality | final user turn of **every** condition == canonical prompt, 171/171; `final_user_turn_text` and `is_canonical_final_prompt` flag consistent everywhere |
| Final role | user in every condition's last turn |
| Turn-count deviation | 0 on all 50 |
| B/C(/D) turn-count equality within item | 50/50 |
| Context token spread | mean 9.6, median 7.5, max 33 est-tokens; no item ≥40 |
| JSONL ↔ JSON mirror | byte-equivalent record objects (0 diffs) |
| Embedded design vs Phase 7E review current-version design | 50/50 exact match (sort-keys JSON compare) |
| Must-stay-null fields (`isolated_prompt_valence_observed`, `adjudicated_valence`, `refusal_appropriateness_reference`, `model_observed_effect`) | null on all 50 |
| `researcher_qc` / review status | false / PENDING ×50; external_validation not_reviewed ×50 |
| Malformed records / missing fields / unexpected nulls | none found |
| Schema version fields | dataset 0.3.0, schema_version 0.2.0, stimulus_version 1, phase 7F — consistent across all records |

## Semantic inspection

- **Near-duplicates:** max pairwise Jaccard between canonical prompts = 0.27 (NH-002/NH-003);
  no pair ≥0.45. No cross-item reuse of any context turn text (0 collisions over all context
  turns). Within item, AM items share identical assistant turns by documented design.
- **Thematic clustering:** mechanisms unique 49/50 — the single repeat is coarse label
  "research method" shared by RI-NB-002/RI-NB-007 (two distinct floor-control tasks:
  inter-rater methodology vs limitations write-up). Distinct prompts and contexts; judged
  non-redundant → INFO-03 only.
- **Prompt intents:** 50/50 unique strings.
- **Within-category coherence:** DU mechanisms map 1:1 to distinct infra domains (audit log,
  detection thresholds, IAM, sessions, snapshots, mail rules, pipelines, env config, local data,
  cron, secrets rotation, capture, integrity monitors, resets, routing, logs, containers,
  lockouts, export, service accounts, net paths, obfuscation, telemetry, credential storage,
  recovery, enumeration, disposal, escalation paths) — broad coverage, no dominant domain.
- **Category contamination:** none observed — NB prompts are plainly routine; NH prompts are
  plainly harmful requests at intent level with zero operational content (verified by reading
  all six + safety-scan patterns); AM prompts are genuinely under-determined asks.

## Protected corpora spot-verification

`pilot_dataset.json`: 300 records; memberships 120 benign / 100 adversarial / 80 multi_turn;
unique sample_ids 300/300; annotations and evaluations empty on all; language tr;
sensitivity public_sanitized. Matches every documented claim.

## Verdict

No structural or semantic defect found in the stimulus collection. The collection is clean
enough that the material risks live entirely in the text-level construct issues covered in
04/06 and in process artifacts (03).
