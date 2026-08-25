# 18 — Documentation vs Reality (Audit Q)

Documentation claims treated as hypotheses and verified against files/code/hashes/tests.

## Claims verified TRUE

| Claim | Verification |
|---|---|
| "314 tests" pass | ran suite: 314 passed |
| Byte-identical canonical prompts across conditions | recomputed 171/171 |
| SHA-256 recorded == derived | 50/50 |
| Protocol documents byte-identical to sealed hashes | recomputed incl. composite |
| Turkish + public-benchmark corpora unchanged | baselines match |
| D arm exactly on strategy-N items (21) | per-record check |
| No reuse of context turns across items | programmatic scan 0 collisions |
| Deterministic builds / seeded shuffle | code inspection + constants |
| No model/API calls ever; providers `not_evaluated` | smoke summary + negative-claims block + artifact absence |
| Zero safety-scan findings; human review NOT performed | scan file (`human_review_performed: false`) |
| Overlap vs internal corpora clean; external overlap unresolved (`preliminary_blocked`) | report + recomputed segment count |
| No expert authorship/validation claimed anywhere | consistent negatives across docs+reports |
| reviewer identity never invented | all reviewer_id null; role strings describe session honestly |
| README progress "1/50 isolated annotations" | matches blind_review.json (the only artifact that agrees!) |

## Claims FALSE or stale

| Claim (location) | Reality | Finding |
|---|---|---|
| PROJECT_STATUS.md ×3: "insan annotation 0/50", "hiçbir insan annotation" | 1 accepted annotation exists | **F-03** |
| `phase7g_quality_summary.json`: annotations_submitted 0, valence distribution zeros | 1 valence recorded | **F-03** |
| `docs/phase7g_human_qc.md` header "0 of 50 items reviewed"; sign-off block | 1 partial review | **F-03** |
| `docs/phase7e_researcher_review.md`: "ALL 50 ITEMS ARE PENDING" | REVIEW_COMPLETE 50/50 KEEP since 14:00Z | **F-05** |
| phase7f doc §6 token table (C mean 76.0/min 40; spread mean 9.9/median 8) | report + recomputation: C mean 76.3/min 46; spread 9.6/7.5 | **F-27 (NEW, LOW)** — hand-copied numbers drifted from the generated report |
| 7D doc falsifier list F1–F5 (§29) | governing prereg uses F1–F6 with different assignments; amendment header lists three superseded provisions but not this renumbering | **F-26 (NEW, LOW)** |
| blind_review `generated_at` 16:00Z | file rewritten later (sessions 19:00–20:15Z inside) without refreshing field | folds into **F-03** (tooling never updates roll-up metadata) |

## Overstatement scan

No instance found of results claimed, ASR/rates implied, expertise asserted, or completeness
exaggerated. The project's dominant documentation pathology is the opposite: **under-refreshed
narrative around an active gate**, while machine records stay honest.
