# 19 — Adversarial Challenge Pass

Second independent pass assuming the first audit missed something. New probes run and their
outcomes:

## New findings surfaced by this pass

**F-26 (LOW) — falsification-criteria divergence between layers.**
`PHASE_7D_EXPERIMENTAL_DESIGN.md` §29 defines F1–F5; governing `phase7e_preregistration.md` §19
defines F1–F6 with different assignments (e.g., 7D-F4 "effect only on leaked items" has no
prereg number; prereg-F6 blind-gate failure rate does not exist in 7D). The 7E amendment header
documents three superseded provisions plus count changes but never mentions the falsifier
renumbering. A reader quoting "F4" from the wrong document misquotes a frozen criterion.

**F-27 (LOW) — narrative token statistics drifted from the generated report.**
phase7f doc §6 table: Condition C mean 76.0 / min 40; spread mean 9.9 / median 8.
Generated report + auditor recomputation: C mean 76.3 / min 46; spread mean 9.6 / median 7.5.
Hand-transcribed numbers superseded by regeneration were never refreshed.

**F-28 (LOW, NEW) — duplicated ban-list implementations have drifted apart.**
Builder `VALENCE_LEAK_TERMS` (17 terms) vs test `BANNED` tuple (14 terms):
builder-only terms: `conceal from, evading, i'm authorized, in my authorized, without leaving a
trace`; test-only term: `conceal` (broader). Neither list contains the other; two sources of
truth for one invariant. Current corpus satisfies both lists (auditor extended scan: 0 hits), so
no live defect — a maintenance hazard only.

**Stale-metadata extension of F-03:** `phase7g_blind_review.json.generated_at` remains
16:00Z although the tool rewrote the file at ~20:15Z (session events inside). Roll-up fields are
never refreshed on write anywhere in the 7G tooling — meaning even a fully completed QC would
leave the quality summary stale unless someone remembers to hand-rebuild it.

## Fresh probes that came back CLEAN (recorded to prevent re-litigation)

| Probe | Result |
|---|---|
| Full determinism replay: re-ran `build_stimulus_dataset.py` on snapshot | output dataset byte-identical (`2f78e79e…`); validation report identical — **strong positive control** |
| Prereg §3 arithmetic vs data (16T/14N; 171 runs; 3 reps → 513/model) | exact match |
| H2/H3 sign conventions vs 7D §16 comments | consistent (Δ_AB ≤ 0, Δ_BC ≥ 0) |
| RI-DU-001 drafted-D removal comment vs approved strategy T | consistent |
| BLIND-001 annotation vs gate semantics under single-rater state | consistent (gate correctly null) |
| Session timeline (rev 19:00Z → session2 20:00Z → annotation 20:15Z) | coherent |
| `apply_phase7e_decisions.py` full read | transcription-only design holds; notes verbatim; duplicates refused |
| Unicode/format anomalies in all prompts | none (safety patterns double as fingerprint scan) |
| `benchmark/runs/mock-dry-run` artifacts | gitignored per local-only policy, consistent with claims |

## Hidden-dependency sweep

Cross-artifact dependencies checked for silent coupling: embedded designs ↔ review versions
(test-bound); blind packet ↔ stimulus prompts (test-bound); snapshots ↔ live files (test-bound);
manifest ↔ protected corpora (test-bound); ban lists ↔ texts (**drifted — F-28**); narrative
stats ↔ generated reports (**drifted — F-27**); status documents ↔ machine state (**stale — F-03**).
The pattern is consistent: byte/hash-level dependencies are tightly enforced; human-readable
narrative layers lag behind.
