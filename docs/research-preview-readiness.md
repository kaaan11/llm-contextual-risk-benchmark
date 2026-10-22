# Research preview readiness — 2026-10-22

Source: `379fb88564ce884bbd1a1b3b38e88284e8189273`. This is a technical support boundary,
not a research approval, release authorization or claim of public readiness.
The [freeze record](reviews/llm-benchmark/PROJECT-FROZEN-2026-09-10.md) remains effective.
Historical reports, sealed data and review histories are preserved.

## Supported now

The checkout supports deterministic dataset validation, read-only integrity checks, negative
QC gate tests, and harmless mock/injected-transport exercises. The README example uses one
abstract prompt, produces no research annotation, writes no run artifact and calls no API.
CI tests Python 3.10, 3.12 and 3.14 after installing `requirements-dev.txt`; the offline profile
blocks Python socket connections during tests. Four legacy files containing invented rater
fixtures are excluded explicitly, rather than presenting their execution as human evidence.
The pre/post integrity check verifies six protocol documents and their composite, protected
datasets, stimulus v1, and the original 51/5-line audit prefixes. Valid future append-only
entries are permitted; existing history cannot be replaced.

The mock Phase 8 harness is legacy tooling, not the accepted E5/E6 pipeline: it lacks the
approved r=3 schedule, complete job/attempt/outcome provenance and versioned item-level
analysis. Generic response-row metrics and heuristic refusal signals are tooling diagnostics,
not the proposed primary analysis, human disposition scores, or a model leaderboard.

## Open issues and required human inputs

| Issue | Verified state and next requirement |
| --- | --- |
| [#1](https://github.com/kaaan11/llm-contextual-risk-benchmark/issues/1) | Current freeze is linked prominently; read-only checks, a harmless offline example and CI cover the supported preview. CI success does not close any scientific gate. |
| [#2](https://github.com/kaaan11/llm-contextual-risk-benchmark/issues/2) | E1a/E1b/E1c are technically accepted **drafts**, not effective scientific decisions. The researcher must record claim scope, nominal action/harm/utility rubric, applicability/contested choices, denominator, missingness, CI and prospective threshold decisions, then authorize the formal amendment/version chain. See the [E1a](reviews/llm-benchmark/E1a-acceptance.md), [E1b-R6](reviews/llm-benchmark/E1b-r6-acceptance.md) and [E1c-R3](reviews/llm-benchmark/E1c-r3-acceptance.md) acceptance boundaries. |
| [#3](https://github.com/kaaan11/llm-contextual-risk-benchmark/issues/3) | Phase 7G has 50 items, rater_a 1/50, rater_b 0/50, 0 adjudications and 0 KEEP. Two real independent raters, completed condition references/reviews, reasoned KEEP/REVISE/REJECT and recorded disagreement adjudication are required. E3a's 19 review candidates are candidates, not decided defects. v1 stays fixed; a revision requires explicit human authorization and a new version. |
| [#4](https://github.com/kaaan11/llm-contextual-risk-benchmark/issues/4) | Publishing stimuli, category/expected-effect fields or the blind mapping before recruiting raters may compromise future blinding. This is a prospective exposure risk, not evidence that a rater was exposed. The researcher must record each rater's prior exposure, eligibility, who can access the mapping, and public/restricted material scope before publication. Existing full-history copies and archives also need review. No exposure declaration has been invented. |
| [#5](https://github.com/kaaan11/llm-contextual-risk-benchmark/issues/5) | E5a–d wait for approved E1c and accepted E4b inputs. Deterministic r=3 logical jobs, translated provider parameters, request/response provenance, physical attempts, honest latency labels and a mandatory canonical preflight/completion/resume policy remain requirements. A local parameter or latency bug fix cannot accept E5 or enable evaluation. |
| [#6](https://github.com/kaaan11/llm-contextual-risk-benchmark/issues/6) | E6a/b/c and E7 wait for upstream approvals and contracts. No prospective sensitivity threshold, accepted denominator, scientific analysis or integrated full-success run is declared complete. An offline pre-QC rejection can be tested; full success needs real accepted human inputs. |
| [#7](https://github.com/kaaan11/llm-contextual-risk-benchmark/issues/7) | The owner must decide licensing/attribution and publication scope. Full history, all refs/archives and Actions logs/artifacts still need disclosure/secret review; this change performs no such complete audit. A reviewed release tag and authorization to publish remain outstanding. |

No real provider dispatch or model experiment is authorized by this preview. Publication and
research restart require the existing human decisions; agents cannot supply raters, reference
labels, adjudication, KEEP decisions, signed approvals or scientific endpoint choices.
