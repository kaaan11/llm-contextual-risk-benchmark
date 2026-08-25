# 14 — Validator and Test Audit + Mutation Campaign (Audit M)

314 tests pass on the pristine tree. This audit inspects what the tests *actually* guarantee,
then attacks validators with mutations on the isolated snapshot copy. Canonical tree untouched.

## Properties actually tested (strong)

- Byte-level canonical-prompt equality + SHA-256 re-derivation per condition (independent
  recompute, not trusting recorded flags).
- Design-embedding equality vs live review record; version-1 preservation via snapshot bytes.
- Preregistration + protected-dataset byte-identity on every run.
- Blind packet: field whitelist, design-term leak scan, prompt↔dataset equality, batch sizes,
  sealed-key state, invalidated-session consistency, no-fabricated-statistics guard.
- Tool-order enforcement (context reveal refused before blind annotation; KEEP requires completed
  sections, structural pass, safety pass).
- Append-only history semantics; re-decision conflicts; reviewer-identity requirements;
  PENDING-hygiene (no approval residue).

## Properties NOT tested / gaps

1. No cross-artifact freshness check: `phase7g_quality_summary.json` staleness undetectable
   (F-03). The only related test pins the stale value (`annotations_submitted == 0`) rather than
   comparing against the blind packet — a tautology w.r.t. the real invariant.
2. Tests couple to **live progress state** (`assertEqual(len(annotated), 1)`): every new human
   annotation breaks the suite until someone edits tests (F-20) — friction that creates pressure
   to loosen assertions during the QC phase.
3. No test binds `evaluation_state`/negative-claim flags to physical absence of artifacts beyond
   the 7G file blob scan (acceptable for now; Phase 8 needs stronger run-manifest checks).
4. Validator cannot detect a real-world key-file reading (self-referential seal) — process limit.

## Mutation campaign (all on `/tmp/opencode/AI_Search_snapshot`; canonical untouched)

| ID | Target invariant | Mutation | Expected | Actual | Killed? | Implication |
|---|---|---|---|---|---|---|
| M-01 | prompt byte/hash integrity | one word changed in RI-DU-001 canonical prompt | fail | 2 tests failed (equality+hash) | KILLED | core integrity enforced |
| M-02 | protocol immutability | newline appended to prereg md | fail | 2 tests failed incl. composite check | KILLED | freeze active |
| M-03 | protected dataset immutability | TR exploratory json modified | fail | 2 tests failed (7E+7G layers) | KILLED | layered protection |
| M-04 | no fabricated κ/agreement | percent_agreement=0.92, kappa=0.87 while status not_available | validator error | INVALID — fabricated statistics | KILLED | anti-fabrication works |
| M-05 | no approval without reviews | qc item → KEEP+researcher_qc=true with nothing done | multiple errors | 7 violations incl. count drift | KILLED | approval path hardened |
| M-06 | gate needs adjudication | gate_result set on unadjudicated item | error | INVALID — gate before adjudication | KILLED | ordering enforced |
| M-07 | blind packet no category leak | inject "dual_use_nonnull" into a prompt | error | INVALID — leaks design information | KILLED | blinding scan effective |
| M-08 | declared counts = reality | counts.keep=3 | errors | INVALID — counts.keep mismatch | KILLED | no silent count drift |
| M-09 | roll-up freshness | summary annotations_submitted=49 | ideally caught by cross-check | caught only by the stale-value pinning test (fails because ≠0, not because inconsistent) | **SURVIVED as gap** | F-03 confirmed: no consistency invariant exists |
| M-10 | D-arm ⇔ strategy N | add D condition to T-strategy item | structural fail | 3 tests failed | KILLED | design fidelity enforced |
| M-11 | decision integrity | review_decision REJECT w/o reason, researcher_approved left true | errors | 3 violations (notes, keep/reject counts) | KILLED | 7E invariants hold |
| M-12 | append-only history | drop last history line | fail | history-vs-live-record test failed (+1) | KILLED | truncation visible |
| M-13 | key seal honesty | opened=true | ideally flagged | validator VALID; but 2 tests failed (seal assertions) | KILLED (repo-state), **process gap remains** | self-referential seal can't survive a read-and-restore |
| M-14 | packet↔dataset binding | swap prompts of BLIND-002/003 | fail | packet-equality test failed | KILLED | mapping integrity tested |

## Verdict

Validator/test layer is unusually strong: 13 of 14 mutation classes killed, several by multiple
independent layers. The two real gaps are freshness consistency (M-09→F-03) and progress-coupled
test brittleness (F-20); both are process-quality issues, not data-integrity holes.
