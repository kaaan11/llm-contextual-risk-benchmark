# 10 — Statistical Audit (Audit I)

Audits the frozen SAP (prereg §14 + annotation protocol) against the actual design. No plan
changes proposed.

## Unit / dependence

- Statistical unit = research item; A/B/C/D paired within item — stated, encoded in dataset
  metadata (`conditions_are_paired_not_independent: true`, `unit_of_analysis`), and protected by
  the 7D→7E amendment that removed the McNemar-across-groups misapplication. Pseudo-replication
  risk is therefore explicitly closed at plan level.
- Residual dependence: items sharing domain/mechanism could correlate (design §30.6 admits);
  SAP has no clustering handling — with 49/50 unique mechanisms and n=50 this is bounded but
  should be reported as a limitation (F-21, MEDIUM-): a few correlated domain pairs could swing
  a descriptive-existence claim's apparent robustness.

## Test-by-test

| Element | Assessment |
|---|---|
| Ordinal transition matrix primary | appropriate for ordinal paired data; immune to symmetry-assumption critique |
| McNemar exact restricted to within-item binaries | correct post-amendment scope |
| Fisher exact dual-use vs nulls | correct for independent unequal groups |
| Wilcoxon supporting-only + tie caveat (>50% ties → sign test carries) | honest about weak symmetry/ties at n=30 |
| Rank-biserial effect size accompanying Wilcoxon | present |
| Clopper–Pearson whole-stratum only | avoids small-cell CIs |
| Prohibitions (no per-cell p, no bootstrap n<20, no prevalence/cross-model claims) | enforceable and testable claims |
| Multiplicity: 3 comparisons, no adjustment, disclosed | acceptable given descriptive framing; must be reported verbatim |

## Missing-data / stochastic outputs

- Modal-over-3 with `unscorable_unstable` fallback: defined; exclusions tabulated; no imputation;
  API errors never scored as refusals; stopping rules forbid data-dependent early stop ✓.
- Seeds: none needed for inference (no resampling planned); bootstrap prohibition removes seed
  sensitivity from analysis.

## Power / sample size

No power analysis exists — acceptable for an existence/feasibility pilot whose pre-registered
claims are direction/existence only; F5/F6 operate as quality gates rather than power targets.
Any future prevalence language would be unsupported (already prohibited).

## Verdict

The SAP matches the design and its own prohibitions are auditable. Findings to carry forward:
F-21 (clustered-domain caveat unhandled, MEDIUM-), plus the annotation-side dependency that gate
outcomes feed inclusion rules (see F-06: one-rater mode would zero out the analysis base).
