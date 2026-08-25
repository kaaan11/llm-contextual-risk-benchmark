# 16 — Researcher Degrees of Freedom (Audit O)

Places where future choices could move conclusions after model outputs are seen. Distinguishes
legitimate operational flexibility from conclusion-capable flexibility.

## Already closed by freezing

Exclusions (prereg §6), metric definitions, thresholds + rationale, rubric boundaries,
aggregation (modal), stopping rules, reporting rules, prohibition list. These are the classic
garden-of-forking-paths levers and they are locked.

## Residual freedom points

1. **Disposition scoring is human, post-hoc, and not yet blinded-by-tooling** — the protocol
   requires raters "blind to condition label where operationally possible" but no scoring tool
   exists; whoever scores knows the condition from turn content anyway (contexts are visible in
   the transcript). Directional drift risk acknowledged in design §30.2. *Conclusion-capable* on
   n=50 where single ordinal steps flip flags. Mitigation available within frozen rules: shuffled,
   condition-stripped scoring of final turns only (final turns are identical across conditions by
   construction, so stripping context is mechanically possible).
2. **Utility rubric lacks a two-rater protocol** (09 §5) — single-rater utility calls are a
   quiet freedom point.
3. **Test-suite coupling to live progress** (F-20): each 7G batch currently breaks ~2 tests that
   hard-code progress counts; the researcher must edit tests mid-QC — an occasion where assertion
   loosening could pass unnoticed. Recommend decoupling progress assertions from invariants.
4. **Retry/timeout parameters** remain configurable per run; prereg §16 requires them fixed
   pre-run — enforcement is procedural, not technical.
5. **Subgroup reporting**: prereg fixes primary strata; no discretionary subgroups defined —
   good. Any post-hoc subgroup slicing would be visible as such under §18's reporting rules.
6. **Model/provider selection for Phase 8** is deliberately open (RQ1) but cross-model inference
   is prohibited in-pilot — freedom exists but its conclusions are capped by frozen rules.

## Verdict

No uncontrolled conclusion-changing lever was found inside the frozen analysis path; residual
freedom concentrates at human-scoring stage (1–2) and tooling friction (3). All are addressable
by procedure before evaluation without amending rules.
