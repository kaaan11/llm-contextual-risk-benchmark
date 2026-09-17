#!/usr/bin/env python3
"""E3a-R2 read-only stimulus scans (persistent delivery helper).

Reads a stimulus v1 JSON (read-only) and writes the machine-readable inventory
to an explicit output path ONLY. Never writes to the input file or to any
other repository path.

Usage:
    python3 helpers/e3a_scan.py --stimulus <in.json> --output <out.json>

Output gate (fail-closed, evaluated BEFORE any write, on resolve()d paths):
  - output resolving to the input path is refused without writing;
  - in-repo outputs are refused EXCEPT this delivery's own
    docs/reviews/llm-benchmark/E3a-r2/stimulus-issues.json;
  - outside-repo caller-owned temp paths are allowed.
Symlink and ".." escapes are evaluated via resolve().

Deterministic: stdlib only, fixed rule constants below, stable sort orders.
Two runs on the same input bytes produce byte-identical output bytes.

Method (kept 1:1 with docs/reviews/llm-benchmark/E3a-r2/stimulus-issues.md):
  - Normalization: regex [a-z0-9]+ over lowercased text; keep len>=5; drop
    STOPWORDS. No stemming, no unicode folding beyond lowercasing.
  - STOPWORDS: fixed set below.
  - DF universe: document frequency over pre-final turn texts, counted once
    per research item across the 50-item corpus.
  - assistant_shared_bc: EXACT equality of the B/C assistant-turn sequences —
    ordered (role, UTF-8 text bytes) pairs. Token sets, order, case and
    punctuation all count. This is NOT token-set equality.
  - assistant_jaccard_bc: separate DESCRIPTIVE lexical measure (Jaccard
    distance over content-token sets). It must not be read as the shared
    boolean; on this corpus both happen to give 7/43, which is coincidence,
    not equivalence (see the divergence unit case in the evidence log).
  - R-REF1 / R-REF2 / R-DHINT / R-STANCE / R-LEN: unchanged from E3a-R1
    (detector hits only; top-5 queue with no-verdict caveat; descriptive
    measurements; token-tolerance verdict OPEN).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

STOPWORDS = frozenset(
    "a an the and or but to of in on for with is are was were be been "
    "it its this that these those i you he she we they me him her us them "
    "my your his our their as at by from into over after before about "
    "against between through during such so than too very can will just "
    "should now not no do does did would could may might must shall there "
    "here what which who whom whose when where why how all any both each "
    "few more most other some own same s t d ll m re ve y".split()
)

COND_ORDER = ["final_prompt_only", "full_context_legitimating",
              "full_context_incriminating", "neutral_filler_control"]

# In-repo write allowlist: this delivery's inventory file ONLY.
IN_REPO_ALLOWLIST = (
    "docs/reviews/llm-benchmark/E3a-r2/stimulus-issues.json",
)


def toks(t: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", t.lower())
            if len(w) >= 5 and w not in STOPWORDS]


def prefinal(cond: dict) -> list[dict]:
    return [t for t in cond["turns"] if not t.get("is_canonical_final_prompt")]


def assistant_seq(cond: dict) -> list[tuple[str, bytes]]:
    """Ordered (role, UTF-8 text bytes) of assistant pre-final turns."""
    return [(t["role"], t["content"]["text"].encode("utf-8"))
            for t in prefinal(cond) if t["role"] == "assistant"]


def assistant_shared_exact(cond_b: dict, cond_c: dict) -> bool:
    """True iff B/C assistant sequences match in order and bytes."""
    return assistant_seq(cond_b) == assistant_seq(cond_c)


def assistant_jaccard(cond_b: dict, cond_c: dict) -> float:
    """Descriptive Jaccard distance over content-token sets (NOT equality)."""
    sa = set(w for t in prefinal(cond_b) if t["role"] == "assistant"
             for w in toks(t["content"]["text"]))
    sc = set(w for t in prefinal(cond_c) if t["role"] == "assistant"
             for w in toks(t["content"]["text"]))
    return round(1 - len(sa & sc) / len(sa | sc), 3) if (sa | sc) else 0.0


def h(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def resolve_output(out_arg: str, in_arg: str, root: Path) -> Path:
    """Fail-closed output resolution. Raises SystemExit on refusal."""
    out_r = Path(out_arg).resolve()
    in_r = Path(in_arg).resolve()
    if out_r == in_r:
        raise SystemExit(f"refusing to write: output == input ({out_r})")
    try:
        rel = out_r.relative_to(root.resolve()).as_posix()
    except ValueError:
        return Path(out_arg)  # outside repo: caller-owned, allowed
    if rel in IN_REPO_ALLOWLIST:
        return Path(out_arg)
    raise SystemExit(f"refusing to write into the repository: {rel} "
                     f"(allowlist: {list(IN_REPO_ALLOWLIST)})")


def scan(stimulus_path: Path) -> dict:
    d = json.loads(stimulus_path.read_text(encoding="utf-8"))
    recs = d["records"]
    assert len(recs) == 50, len(recs)
    total_conds = sum(len(r["conditions"]) for r in recs)
    assert total_conds == 171, total_conds

    structural, measurements, findings = [], [], []

    # S1: structural integrity per item.
    for r in recs:
        conds = r["conditions"]
        final_eq = len({cond["final_user_turn_text"].encode()
                        for cond in conds.values()}) == 1
        has_d = "neutral_filler_control" in conds
        strat_ok = (has_d == (r["design"]["control_strategy"] == "N"))
        structural.append({
            "research_item_id": r["research_item_id"],
            "category": r["category"],
            "conditions": sorted(conds),
            "turn_counts": {c: len(cond["turns"])
                            for c, cond in conds.items()},
            "turn_ids": {c: [t["turn_id"] for t in cond["turns"]]
                         for c, cond in conds.items()},
            "final_byte_equal": final_eq,
            "has_d": has_d,
            "control_strategy": r["design"]["control_strategy"],
            "d_matches_strategy": strat_ok})
        assert final_eq and strat_ok

    # Document frequency over pre-final texts (R-REF2 rarity universe).
    df: Counter = Counter()
    for r in recs:
        seen = set()
        for cond in r["conditions"].values():
            for t in prefinal(cond):
                seen.update(toks(t["content"]["text"]))
        for w in seen:
            df[w] += 1

    def text_of(record: dict, cond_name: str, turn_id: str) -> str:
        for t in record["conditions"][cond_name]["turns"]:
            if t["turn_id"] == turn_id:
                return t["content"]["text"]
        raise KeyError(turn_id)

    # R-REF1: detector hit only (no discourse judgment).
    for r in recs:
        for det, word in re.findall(r"\b(this|these)\s+([a-z][a-z\-]{3,})",
                                    r["canonical_final_prompt"], re.I):
            aturn = r["conditions"]["final_prompt_only"]["turns"][0]
            findings.append({
                "rule_id": "R-REF1",
                "research_item_id": r["research_item_id"],
                "condition": "final_prompt_only",
                "location": {
                    "turn_ids": [aturn["turn_id"]],
                    "text_sha256": {aturn["turn_id"]: h(aturn["content"]["text"])}},
                "issue_type": "T-REF",
                "evidence": (
                    "detector R-REF1 fired (determiner + token, len>=4); "
                    "match location above"),
                "human_decisions_open": {
                    "is_noun_phrase": "undecided",
                    "has_referent": "undecided",
                    "needs_context": "undecided",
                    "risk_ambiguity_relation": "undecided"},
                "alternative": "ordinary anaphora, verb/adverb use, or no defect",
                "auto_check": "regex hit only; noun-hood and discourse status need human reading",
                "human_decision_needed": "noun-phrasehood, referent existence, context need, risk relation, naturalness",
                "proposed_status": "REVIEW",
                "scanned_population": "50 canonical A-prompts"})

    # R-REF2: cross-condition rare-token reuse candidates.
    for r in recs:
        conds = r["conditions"]
        prompt_toks = set(toks(r["canonical_final_prompt"]))
        pre = {c: prefinal(cond) for c, cond in conds.items()}
        user_toks = {c: set(w for t in turns if t["role"] == "user"
                            for w in toks(t["content"]["text"]))
                     for c, turns in pre.items()}
        asst = {c: [(t["turn_id"], set(toks(t["content"]["text"])))
                    for t in turns if t["role"] == "assistant"]
                for c, turns in pre.items()}
        for y in pre:
            for tid, aset in asst[y]:
                for w in sorted(aset - user_toks[y] - prompt_toks):
                    if df[w] > 2:
                        continue
                    srcs = sorted(x for x in pre
                                  if x != y and w in user_toks[x])
                    if not srcs:
                        continue
                    src_turns = []
                    for x in srcs:
                        for t in pre[x]:
                            if (t["role"] == "user"
                                    and w in toks(t["content"]["text"])):
                                src_turns.append(t["turn_id"])
                    findings.append({
                        "rule_id": "R-REF2",
                        "research_item_id": r["research_item_id"],
                        "condition": y,
                        "location": {
                            "turn_ids": [tid],
                            "text_sha256": {tid: h(text_of(r, y, tid))},
                            "source_turn_ids": src_turns,
                            "source_text_sha256": {
                                s: h(text_of(r, x, s))
                                for x in srcs for s in src_turns
                                if s in [t["turn_id"] for t in pre[x]]}},
                        "issue_type": "T-XCOND",
                        "evidence": (
                            f"detector R-REF2 fired: rare token (df={df[w]}) "
                            f"in {y} assistant turn, absent from same-condition "
                            f"user turns and prompt, present in {srcs} user "
                            f"turns; match locations above"),
                        "alternative": "independent benign word choice in both places; no defect",
                        "auto_check": "rule fired (len>=5, df<=2, user-source only)",
                        "human_decision_needed": "coherence/naturalness judgment: does the turn depend on information the reader of this condition never received?",
                        "proposed_status": "REVIEW",
                        "scanned_population": "50 items x ordered condition pairs, assistant turns"})

    # R-DHINT: lexical adjacency, descriptive + top-5 queue (no verdict).
    def ov(a, b) -> float:
        a, b = set(a), set(b)
        denom = min(len(a), len(b))
        return len(a & b) / denom if denom else 0.0

    drows = []
    for r in recs:
        c = r["conditions"]
        if "neutral_filler_control" not in c:
            continue
        da = toks(" ".join(t["content"]["text"]
                           for t in c["neutral_filler_control"]["turns"]
                           if t["role"] == "assistant"))
        p = toks(r["canonical_final_prompt"])
        ba = toks(" ".join(t["content"]["text"]
                           for t in c["full_context_legitimating"]["turns"]
                           if t["role"] == "assistant"))
        ca = toks(" ".join(t["content"]["text"]
                           for t in c["full_context_incriminating"]["turns"]
                           if t["role"] == "assistant"))
        drows.append({"research_item_id": r["research_item_id"],
                      "ov_prompt": round(ov(da, p), 3),
                      "ov_b": round(ov(da, ba), 3),
                      "ov_c": round(ov(da, ca), 3)})
    drows.sort(key=lambda x: -max(x["ov_prompt"], x["ov_b"], x["ov_c"]))
    for rank, row in enumerate(drows[:5], start=1):
        rid = row["research_item_id"]
        r = next(x for x in recs if x["research_item_id"] == rid)
        dturns = [t["turn_id"]
                  for t in r["conditions"]["neutral_filler_control"]["turns"]
                  if t["role"] == "assistant"]
        findings.append({
            "rule_id": "R-DHINT",
            "research_item_id": rid,
            "condition": "neutral_filler_control",
            "location": {
                "turn_ids": dturns,
                "text_sha256": {
                    t: h(text_of(r, "neutral_filler_control", t))
                    for t in dturns}},
            "issue_type": "T-DHINT-LEX",
            "evidence": (
                f"lexical-adjacency rank #{rank}/21 "
                f"(ov_prompt={row['ov_prompt']}, ov_b={row['ov_b']}, "
                f"ov_c={row['ov_c']}); RANKING IS NOT A DEFECT VERDICT"),
            "alternative": "topic-adjacent filler with no task-solving content",
            "auto_check": "ranked by overlap coefficient; semantic task-priming needs human reading",
            "human_decision_needed": "neutrality judgment + d_rationale sufficiency",
            "proposed_status": "REVIEW",
            "scanned_population": "21 D arms"})

    # Human-sourced DU004 (lexical screen outcome recorded, not a firing).
    du004 = next(x for x in drows if x["research_item_id"] == "RI-DU-004")
    r = next(x for x in recs if x["research_item_id"] == "RI-DU-004")
    dturns = [t["turn_id"]
              for t in r["conditions"]["neutral_filler_control"]["turns"]
              if t["role"] == "assistant"]
    findings.append({
        "rule_id": "HUMAN-SRC",
        "research_item_id": "RI-DU-004",
        "condition": "neutral_filler_control",
        "location": {
            "turn_ids": dturns,
            "text_sha256": {
                t: h(text_of(r, "neutral_filler_control", t))
                for t in dturns}},
        "issue_type": "T-DHINT-HUMAN",
        "evidence": (
            "report-sourced D method-hint candidate; lexical screen values "
            f"(ov_prompt={du004['ov_prompt']}, ov_b={du004['ov_b']}, "
            f"ov_c={du004['ov_c']}) bound — not validate — the automated screen"),
        "alternative": "adjacent-but-inert filler per d_rationale",
        "auto_check": "not fired by automation; listed from report P13",
        "human_decision_needed": "neutrality judgment + d_rationale sufficiency",
        "proposed_status": "REVIEW",
        "scanned_population": "report P13 item note"})

    # R-STANCE / R-LEN measurements (descriptive, no verdicts).
    measurements = []
    for r in recs:
        c = r["conditions"]
        cond_b = c["full_context_legitimating"]
        cond_c = c["full_context_incriminating"]
        shared = assistant_shared_exact(cond_b, cond_c)
        jac = assistant_jaccard(cond_b, cond_c)
        ctx = {}
        for name, cond in c.items():
            pre = [t for t in cond["turns"]
                   if not t.get("is_canonical_final_prompt")]
            blob = " ".join(t["content"]["text"] for t in pre)
            words = len(blob.split())
            ctx[name] = {"pre_turns": len(pre),
                         "bytes": len(blob.encode()),
                         "words": words,
                         "heuristic_tokens": round(words * 1.3)}
        measurements.append({"research_item_id": r["research_item_id"],
                             "category": r["category"],
                             "assistant_shared_bc": shared,
                             "assistant_jaccard_bc": jac,
                             "context": ctx})

    n_shared = sum(1 for m in measurements if m["assistant_shared_bc"])
    return {
        "meta": {
            "helper": "helpers/e3a_scan.py (this file)",
            "population": "50 items / 171 condition records (full corpus, no sampling)",
            "rules": {
                "normalization": "regex [a-z0-9]+ over lowercased text; keep len>=5; drop STOPWORDS; no stemming",
                "stopwords": "fixed set in helper source (function words + single letters + contraction fragments)",
                "df_universe": "presence across items in pre-final turn texts, 50-item universe",
                "ordered_pairs": "X!=Y ordered; target Y-assistant only; source X-USER turns only",
                "overlap": "|A&B|/min(|A|,|B|), rounded to 3 decimals",
                "tie_ordering": "stable sort keeps corpus order on ties",
                "top5": "first 5 after descending max-overlap ordering, REVIEW queue with no-verdict caveat",
                "exact_shared": "ordered (role, UTF-8 text bytes) equality of B/C assistant sequences; order, case, punctuation and stopwords all count",
                "jaccard": "descriptive Jaccard distance over content-token sets; NOT the shared boolean",
                "R-REF1": "this/these + token(len>=4) in A; that/those excluded (relative-pronoun dominant)",
                "R-REF2": "rare token (len>=5, df<=2) in Y-assistant, absent Y-user + prompt, present X-user",
                "R-DHINT": "overlap D-assistant vs prompt/B-assistant/C-assistant",
                "R-STANCE/R-LEN": "descriptive only; token-tolerance verdict OPEN (no tokenizer profile)"},
            "limits": [
                "automation finds candidates, never verdicts",
                "lexical screens miss semantic adjacency (DU004 screen values bound the screen, not the item)",
                "no extrapolation from examples to corpus totals",
                "no KEEP/REVISE/REJECT decisions; proposed REVIEW = human-queue only"],
            "counts": {"items": 50, "conditions": total_conds,
                       "assistant_shared": n_shared,
                       "assistant_differing": 50 - n_shared}},
        "structural": structural,
        "measurements": measurements,
        "findings": findings}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stimulus", required=True,
                    help="input stimulus v1 JSON (read-only)")
    ap.add_argument("--output", required=True,
                    help="output inventory JSON (only path written)")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[5]  # repo root
    out_path = resolve_output(args.output, args.stimulus, root)
    out = scan(Path(args.stimulus))
    out["meta"]["stimulus_input"] = str(Path(args.stimulus))
    # The output gate above runs before ANY write in this process.
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    from collections import Counter as _C
    print(f"items=50 conditions=171 findings={len(out['findings'])} "
          f"shared={out['meta']['counts']['assistant_shared']}")
    print(" finding types:",
          _C(f["issue_type"] for f in out["findings"]))
    print(" wrote", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
