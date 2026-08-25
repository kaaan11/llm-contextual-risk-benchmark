# VCS Anchor Plan — first provenance commit set

F-04/F-23 remediation. The repository currently has **zero commits**; every integrity
claim is anchored only by self-recorded hashes in the working tree. This plan prepares
the **first provenance anchor** for the researcher to execute after reviewing this
campaign. Nothing has been committed, pushed, or tagged by the remediation.

## Ignore-rule changes made (narrow, provenance-driven)

`.gitignore` now additionally un-ignores:

- `results/dataset_audit/*.jsonl` — append-only review histories (7E + 7G)
- `results/dataset_audit/snapshots/` — pre-write state captures backing immutability claims
- `results/smoke_test/` — sanitized provider-preflight summaries (raw responses remain
  excluded by policy; none exist)

Deliberately still excluded: `benchmark/runs/` payloads are governed by their own nested
`benchmark/runs/.gitignore`, which re-includes only `mock-dry-run/**` (three small mock
artifacts documenting the dry-run contract) — kept as-is. `.env*`, `__pycache__`,
`.pytest_cache` remain ignored. No secrets were observed in any file that becomes
trackable (verified: histories contain reviewer roles only; summaries contain no keys).

## Proposed commit boundaries (researcher executes)

```bash
cd /home/kaan/AI_Search

# Commit 1 — frozen research base + code + tests (the reproducible instrument)
git add .gitignore README.md PROJECT_STATUS.md \
        docs/ dataset/ benchmark/ configs/ scripts/ tests/ audit/deep_research_audit/
git commit -m "LLM-CTX-PILOT-2026-01: frozen protocol v1.0.2, stimuli v1, frameworks, deep-audit artifacts"

# Commit 2 — live research state + provenance chain
git add results/
git commit -m "Phase 7E review state (50/50 KEEP), Phase 7G blind-review state (1 rater_a), histories + snapshots"

# Commit 3 — remediation campaign record
git add remediation/
git commit -m "pre-eval remediation: R1/R2 implemented, F-01..F-10 dispositions, mutation regression"

# Optional but recommended (F-23): external anchoring of the composite hash.
# Publish the value printed by:
python scripts/freeze_phase7e_preregistration.py   # read-only recompute; compare before pushing
```

## Post-anchor verification commands

```bash
git log --oneline                      # three commits expected
git status --porcelain -uall | wc -l   # should be small and intentional
/tmp/opencode/audit_venv/bin/python -m pytest -q   # 314+ tests from a clean clone
```

## Notes / limits

- This plan does NOT create remotes or tags. If a remote is added later, tag the anchor
  commit (e.g. `provenance-anchor-1`) and push.
- Even with VCS anchoring, the freeze remains verifiable independently via the composite
  hash (`47ae3fed…bcfc6f` at manifest v1.0.2); VCS adds tamper-*evidence* over time.
