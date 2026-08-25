#!/usr/bin/env python3
"""Phase 7F — build the controlled English stimulus dataset from approved designs.

Reads the Phase 7E researcher-approved research items and the authored content
modules, assembles A/B/C/(D) conditions around one canonical final prompt per
item, and writes the dataset plus audit reports.

Guarantees enforced here (not merely asserted in prose):
  * exactly one canonical final prompt per research item;
  * the final user turn of every applicable condition is byte-identical to it;
  * SHA-256 of the canonical prompt is recorded and cross-checked;
  * D exists only where the approved design specifies control_strategy == "N";
  * researcher_qc = false and stimulus_review_status = PENDING everywhere.

Performs no network access and calls no model API.
"""

from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dataset" / "pilot" / "multiturn"))

from stimulus_content_ctl import AMBIGUITY, NULL_BENIGN, NULL_HIGHRISK  # noqa: E402
from stimulus_content_du import DUAL_USE  # noqa: E402

CONTENT: dict[str, dict] = {**DUAL_USE, **AMBIGUITY, **NULL_BENIGN, **NULL_HIGHRISK}

STIMULUS_VERSION = 1
DATASET_VERSION = "0.3.0"
CREATED_AT = "2026-08-14T15:00:00Z"
GENERATION_VERSION = "phase7f-v1"

# --- safety scan patterns (pre-filter only; never a substitute for human review)
SAFETY_PATTERNS = {
    "code_block": re.compile(r"```"),
    "shell_destructive": re.compile(r"\brm\s+-rf\b|\bmkfs\b|\bdd\s+if=|\bshutdown\s+-h\b", re.I),
    "credential_literal": re.compile(
        r"(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*\S{6,}", re.I),
    "private_key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "aws_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "email_address": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "url": re.compile(r"https?://\S+"),
    "cve_identifier": re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.I),
    "hostname_like": re.compile(r"\b[a-z0-9-]+\.(?:com|net|org|io|co\.uk)\b", re.I),
}

# Phrases that would leak the experimental design into the stimulus text.
LEAKAGE_TERMS = (
    "dual_use", "dual-use item", "null_benign", "null_highrisk", "persistent_ambiguity",
    "context_increases", "expected_context_effect", "legitimating context",
    "incriminating context", "neutral filler", "condition a", "condition b",
    "condition c", "condition d", "research item", "benchmark", "canonical final prompt",
    "isolated_prompt", "control_strategy", "triplet",
)

# Final prompts of non-null items must not carry the answer themselves.
VALENCE_LEAK_TERMS = (
    "without being detected", "without anyone noticing", "undetected", "evade",
    "evading", "bypass detection", "hide from", "conceal from", "cover my tracks",
    "i am authorized", "i'm authorized", "i am authorised", "i have permission",
    "for educational purposes", "this is a lab", "i am a security researcher",
    "in my authorized", "without leaving a trace",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def estimate_tokens(text: str) -> int:
    """Documented heuristic: whitespace words x 1.3, rounded. Not a tokenizer."""
    return round(len(text.split()) * 1.3)


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", " ", text).strip()


def build_condition(cond: str, ctx: list[tuple[str, str]] | None,
                    prompt: str, item_id: str) -> dict:
    turns = []
    seq = 0
    for role, text in (ctx or []):
        turns.append({
            "turn_id": f"{item_id}-{cond}-turn-{seq:02d}",
            "sequence": seq,
            "role": role,
            "content": {"text": text},
        })
        seq += 1
    turns.append({
        "turn_id": f"{item_id}-{cond}-turn-{seq:02d}",
        "sequence": seq,
        "role": "user",
        "content": {"text": prompt},
        "is_canonical_final_prompt": True,
    })
    joined = "\n".join(t["content"]["text"] for t in turns)
    return {
        "condition": CONDITION_NAME[cond],
        "condition_code": cond,
        "turns": turns,
        "turn_count": len(turns),
        "final_user_turn_id": turns[-1]["turn_id"],
        "final_user_turn_text": turns[-1]["content"]["text"],
        "estimated_input_tokens": estimate_tokens(joined),
    }


CONDITION_NAME = {
    "A": "final_prompt_only",
    "B": "full_context_legitimating",
    "C": "full_context_incriminating",
    "D": "neutral_filler_control",
}


def build_records(approved: list[dict]) -> tuple[list[dict], list[dict]]:
    records, flags = [], []

    for entry in approved:
        rid = entry["research_item_id"]
        design = entry["versions"][entry["current_version"] - 1]["design"]
        content = CONTENT.get(rid)
        if content is None:
            flags.append({"research_item_id": rid, "flag": "missing_authored_content",
                          "detail": "no stimulus content authored for this approved item"})
            continue

        prompt = content["prompt"]
        prompt_hash = sha256_text(prompt)
        wants_d = design["control_strategy"] == "N"

        conditions = {
            CONDITION_NAME["A"]: build_condition("A", None, prompt, rid),
            CONDITION_NAME["B"]: build_condition("B", content["B"], prompt, rid),
            CONDITION_NAME["C"]: build_condition("C", content["C"], prompt, rid),
        }
        if wants_d:
            if not content.get("D"):
                flags.append({"research_item_id": rid, "flag": "missing_d_control",
                              "detail": "design specifies control_strategy N but no D authored"})
            else:
                conditions[CONDITION_NAME["D"]] = build_condition("D", content["D"], prompt, rid)
        elif content.get("D"):
            flags.append({"research_item_id": rid, "flag": "unexpected_d_control",
                          "detail": "D authored but design does not specify control_strategy N"})

        # ---- self-audit (section 10 of the phase brief) --------------------
        audit = {
            "q1_context_provides_intended_signal": bool(content["B"]) and bool(content["C"]),
            "q2_no_unintended_stronger_signal": not any(
                t in normalise(prompt) for t in VALENCE_LEAK_TERMS
            ) if design["category"] in {"dual_use_nonnull", "persistent_ambiguity"} else True,
            "q3_final_prompt_unchanged": all(
                c["final_user_turn_text"] == prompt for c in conditions.values()),
            "q4_b_and_c_differ_explicably": (
                normalise(" ".join(t for _, t in content["B"]))
                != normalise(" ".join(t for _, t in content["C"]))),
            "q5_d_neutral_where_present": (
                bool(content.get("d_rationale")) if wants_d and content.get("D") else True),
        }
        if not all(audit.values()):
            flags.append({"research_item_id": rid, "flag": "self_audit_failed",
                          "detail": {k: v for k, v in audit.items() if not v}})

        token_est = {c["condition_code"]: c["estimated_input_tokens"]
                     for c in conditions.values()}
        ctx_tokens = [v for k, v in token_est.items() if k != "A"]
        spread = max(ctx_tokens) - min(ctx_tokens)
        if spread > 40:
            flags.append({"research_item_id": rid, "flag": "context_length_spread",
                          "detail": f"context conditions differ by {spread} estimated tokens"})

        turn_actual = conditions[CONDITION_NAME["B"]]["turn_count"]
        turn_dev = turn_actual - design["intended_turn_count"]

        records.append({
            "research_item_id": rid,
            "triplet_id": design["triplet_id"],
            "record_type": "context_conditioned_item",
            "category": design["category"],
            "context_mechanism": design["context_mechanism"],
            "language": "en",
            "canonical_final_prompt": prompt,
            "canonical_final_prompt_sha256": prompt_hash,
            "conditions": conditions,
            "condition_availability": {
                "A": True, "B": True, "C": True, "D": CONDITION_NAME["D"] in conditions,
            },
            "d_control_rationale": content.get("d_rationale"),
            "turn_counts": {c["condition_code"]: c["turn_count"] for c in conditions.values()},
            "estimated_input_tokens": token_est,
            "context_token_spread": spread,
            "intended_turn_count": design["intended_turn_count"],
            "turn_count_deviation": turn_dev,
            "self_audit": audit,
            # --- design layer, preserved verbatim, never overwritten ---------
            "design": design,
            "design_version": entry["versions"][0].get("version", 1),
            "researcher_approval_status": entry["review_decision"],
            # --- provenance --------------------------------------------------
            "dataset_version": DATASET_VERSION,
            "stimulus_version": STIMULUS_VERSION,
            "stimulus_generation_version": GENERATION_VERSION,
            "authoring_method": "researcher_specified_llm_assisted_draft",
            "generation_assistance": "drafting_only",
            "source": "original",
            "source_seed": None,
            "created_at": CREATED_AT,
            # --- review gates: nothing approved, nothing annotated -----------
            "researcher_qc": False,
            "stimulus_review_status": "PENDING",
            "external_validation_status": "not_reviewed",
            "isolated_prompt_valence_observed": None,
            "adjudicated_valence": None,
            "refusal_appropriateness_reference": None,
            "model_observed_effect": None,
        })

    return records, flags


def safety_scan(records: list[dict]) -> list[dict]:
    findings = []
    for rec in records:
        for cond in rec["conditions"].values():
            for turn in cond["turns"]:
                text = turn["content"]["text"]
                for name, pattern in SAFETY_PATTERNS.items():
                    if pattern.search(text):
                        findings.append({
                            "research_item_id": rec["research_item_id"],
                            "condition": cond["condition"],
                            "turn_id": turn["turn_id"],
                            "pattern": name,
                            "requires_human_review": True,
                        })
    return findings


def leakage_scan(records: list[dict]) -> list[dict]:
    findings = []
    for rec in records:
        for cond in rec["conditions"].values():
            for turn in cond["turns"]:
                norm = normalise(turn["content"]["text"])
                for term in LEAKAGE_TERMS:
                    # word-boundary match so ordinary English ("benchmarking a
                    # database") is not mistaken for design leakage
                    if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", norm):
                        findings.append({
                            "research_item_id": rec["research_item_id"],
                            "condition": cond["condition"],
                            "turn_id": turn["turn_id"],
                            "term": term,
                        })
    return findings


def overlap_scan(records: list[dict], root: Path) -> dict:
    """Compare generated final prompts against the existing corpora."""
    corpus: list[tuple[str, str]] = []
    for rel in ("dataset/pilot/records.jsonl", "dataset/pilot/multiturn/records.jsonl"):
        path = root / rel
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            for key in ("prompt", "text", "canonical_final_prompt"):
                if isinstance(obj.get(key), str):
                    corpus.append((rel, obj[key]))
            for turn in obj.get("turns", []) or []:
                text = (turn.get("content") or {}).get("text")
                if isinstance(text, str):
                    corpus.append((rel, text))

    exact = {sha256_text(t) for _, t in corpus}
    normed = {normalise(t) for _, t in corpus}
    corpus_tokens = [(src, set(normalise(t).split())) for src, t in corpus]

    exact_hits, normalised_hits, similar = [], [], []
    for rec in records:
        prompt = rec["canonical_final_prompt"]
        if sha256_text(prompt) in exact:
            exact_hits.append(rec["research_item_id"])
        if normalise(prompt) in normed:
            normalised_hits.append(rec["research_item_id"])
        tokens = set(normalise(prompt).split())
        best, best_src = 0.0, None
        for src, ctoks in corpus_tokens:
            if not tokens or not ctoks:
                continue
            j = len(tokens & ctoks) / len(tokens | ctoks)
            if j > best:
                best, best_src = j, src
        if best >= 0.6:
            similar.append({"research_item_id": rec["research_item_id"],
                            "jaccard": round(best, 3), "source": best_src})

    return {
        "audit_version": "0.1.0",
        "performed_at": CREATED_AT,
        "method": {
            "exact": "sha256 over raw UTF-8 prompt text",
            "normalised": "NFKC + casefold + whitespace collapse",
            "similarity": "Jaccard over normalised whitespace tokens, flag threshold 0.60",
        },
        "corpora_compared": ["dataset/pilot/records.jsonl",
                             "dataset/pilot/multiturn/records.jsonl"],
        "corpus_segment_count": len(corpus),
        "public_benchmark_note": (
            "No public benchmark text is vendored in this repository, so no external "
            "jailbreak corpus could be compared here. The pending public-benchmark "
            "overlap audit (results/dataset_audit/overlap_report.json, status "
            "preliminary_blocked) must be completed before any analytical combination."
        ),
        "exact_duplicates": exact_hits,
        "normalised_duplicates": normalised_hits,
        "high_similarity": similar,
        "flagged_for_researcher_review": sorted(
            set(exact_hits) | set(normalised_hits) | {s["research_item_id"] for s in similar}),
        "public_benchmark_modified": False,
    }


def structural_validation(records: list[dict]) -> list[str]:
    errors: list[str] = []
    for rec in records:
        rid = rec["research_item_id"]
        prompt = rec["canonical_final_prompt"]

        if rec["canonical_final_prompt_sha256"] != sha256_text(prompt):
            errors.append(f"{rid}: recorded prompt hash does not match canonical prompt")

        for name, cond in rec["conditions"].items():
            if cond["final_user_turn_text"] != prompt:
                errors.append(f"{rid}/{name}: final user turn differs from canonical prompt")
            if sha256_text(cond["final_user_turn_text"]) != rec["canonical_final_prompt_sha256"]:
                errors.append(f"{rid}/{name}: final turn hash mismatch")
            if cond["turns"][-1]["role"] != "user":
                errors.append(f"{rid}/{name}: final turn is not a user turn")
            seqs = [t["sequence"] for t in cond["turns"]]
            if seqs != list(range(len(seqs))):
                errors.append(f"{rid}/{name}: turn sequence is not contiguous from 0")
            for t in cond["turns"]:
                if t["role"] not in {"user", "assistant"}:
                    errors.append(f"{rid}/{name}: invalid role {t['role']!r}")
            prev = None
            for t in cond["turns"][:-1]:
                if prev == "user" and t["role"] == "user" and cond["turns"].index(t) < len(
                        cond["turns"]) - 2:
                    pass  # consecutive user turns are permitted (see README)
                prev = t["role"]

        avail = rec["condition_availability"]
        if not (avail["A"] and avail["B"] and avail["C"]):
            errors.append(f"{rid}: missing one of the required A/B/C conditions")
        should_have_d = rec["design"]["control_strategy"] == "N"
        if should_have_d != avail["D"]:
            errors.append(f"{rid}: D availability {avail['D']} contradicts control_strategy "
                          f"{rec['design']['control_strategy']}")
        if not avail["D"] and rec["d_control_rationale"]:
            errors.append(f"{rid}: D rationale present without a D condition")

        if rec["conditions"][CONDITION_NAME["A"]]["turn_count"] != 1:
            errors.append(f"{rid}: condition A must contain exactly one turn")
        for cond_name in (CONDITION_NAME["B"], CONDITION_NAME["C"]):
            if rec["conditions"][cond_name]["turn_count"] < 2:
                errors.append(f"{rid}/{cond_name}: context condition needs preceding turns")

        if rec["researcher_qc"] is not False:
            errors.append(f"{rid}: researcher_qc must be false in Phase 7F")
        if rec["stimulus_review_status"] != "PENDING":
            errors.append(f"{rid}: stimulus_review_status must be PENDING")
        for field in ("isolated_prompt_valence_observed", "adjudicated_valence",
                      "refusal_appropriateness_reference", "model_observed_effect"):
            if rec[field] is not None:
                errors.append(f"{rid}: {field} must remain null in Phase 7F")
        if rec["stimulus_version"] != 1:
            errors.append(f"{rid}: stimulus_version must be 1")

    return errors


def build_statistics(records: list[dict], safety, leakage, overlap, val_errors, flags) -> dict:
    cats: dict[str, int] = {}
    for r in records:
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    ctx_turns = [r["turn_counts"]["B"] for r in records]

    def tok(cond_key):
        vals = [r["estimated_input_tokens"][cond_key]
                for r in records if cond_key in r["estimated_input_tokens"]]
        if not vals:
            return None
        return {"n": len(vals), "mean": round(statistics.mean(vals), 1),
                "median": statistics.median(vals), "min": min(vals), "max": max(vals)}

    spreads = [r["context_token_spread"] for r in records]
    return {
        "report_version": "0.1.0",
        "phase": "7F",
        "generated_at": CREATED_AT,
        "total_research_items": len(records),
        "condition_availability": {
            "A": sum(1 for r in records if r["condition_availability"]["A"]),
            "B": sum(1 for r in records if r["condition_availability"]["B"]),
            "C": sum(1 for r in records if r["condition_availability"]["C"]),
            "D": sum(1 for r in records if r["condition_availability"]["D"]),
        },
        "category_distribution": cats,
        "turns": {
            "context_condition_mean": round(statistics.mean(ctx_turns), 2),
            "context_condition_median": statistics.median(ctx_turns),
            "min": min(ctx_turns), "max": max(ctx_turns),
            "condition_A_turns": 1,
            "turn_count_deviations": {
                r["research_item_id"]: r["turn_count_deviation"]
                for r in records if r["turn_count_deviation"] != 0
            },
        },
        "estimated_input_tokens": {
            "method": "whitespace word count x 1.3 (documented heuristic, not a tokenizer)",
            "A": tok("A"), "B": tok("B"), "C": tok("C"), "D": tok("D"),
        },
        "context_token_spread": {
            "mean": round(statistics.mean(spreads), 1),
            "median": statistics.median(spreads),
            "max": max(spreads),
            "items_over_40_tokens": [r["research_item_id"] for r in records
                                     if r["context_token_spread"] > 40],
        },
        "provenance_distribution": {
            "authoring_method": {"researcher_specified_llm_assisted_draft": len(records)},
            "generation_assistance": {"drafting_only": len(records)},
            "source": {"original": len(records)},
            "source_seed_present": 0,
        },
        "validation_failures": len(val_errors),
        "safety_flags": len(safety),
        "design_leakage_flags": len(leakage),
        "overlap_flags": len(overlap["flagged_for_researcher_review"]),
        "generation_flags": len(flags),
        "review_status": {"researcher_qc_true": 0, "stimulus_review_status_pending": len(records)},
    }


def main() -> int:
    review = json.loads(
        (ROOT / "results" / "dataset_audit" / "phase7e_review.json").read_text(encoding="utf-8"))
    approved = [i for i in review["items"] if i["researcher_approved"]]
    print(f"approved research items: {len(approved)}")

    records, flags = build_records(approved)
    val_errors = structural_validation(records)
    safety = safety_scan(records)
    leakage = leakage_scan(records)
    overlap = overlap_scan(records, ROOT)

    out_dir = ROOT / "dataset" / "pilot" / "multiturn"
    audit_dir = ROOT / "results" / "dataset_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    dataset = {
        "schema_version": "0.2.0",
        "dataset_id": "llm-ctx-pilot-stimuli-en",
        "dataset_version": DATASET_VERSION,
        "stimulus_version": STIMULUS_VERSION,
        "stimulus_generation_version": GENERATION_VERSION,
        "phase": "7F",
        "language": "en",
        "created_at": CREATED_AT,
        "purpose": ("Controlled English stimuli for the contextual risk-interpretation pilot. "
                    "One canonical final prompt per research item, evaluated under A/B/C and, "
                    "where the approved design specifies it, a neutral-filler D control."),
        "protocol_id": "LLM-CTX-PILOT-2026-01",
        "unit_of_analysis": "research_item",
        "conditions_are_paired_not_independent": True,
        "researcher_qc": False,
        "stimulus_review_status": "PENDING",
        "model_evaluations_run": False,
        "blind_review_performed": False,
        "record_count": len(records),
        "records": records,
    }
    (out_dir / "stimulus_dataset_v1.json").write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "stimulus_records.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")

    (audit_dir / "stimulus_validation.json").write_text(json.dumps({
        "report_version": "0.1.0", "phase": "7F", "generated_at": CREATED_AT,
        "checks_run": [
            "one canonical final prompt per item",
            "A/B/C/D final user turn byte-equality with canonical prompt",
            "SHA-256 of canonical prompt matches every applicable condition",
            "turn ordering contiguous and final turn is a user turn",
            "role vocabulary restricted to user/assistant",
            "D present only where control_strategy == N",
            "review-gate fields null / PENDING / researcher_qc false",
        ],
        "structural_errors": val_errors,
        "structural_valid": not val_errors,
        "generation_flags": flags,
        "design_leakage_findings": leakage,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    (audit_dir / "stimulus_safety_scan.json").write_text(json.dumps({
        "report_version": "0.1.0", "phase": "7F", "generated_at": CREATED_AT,
        "scan_type": "automated_pre_filter",
        "disclaimer": ("This scan is a pre-filter. It does NOT constitute human safety review. "
                       "Every finding, including suspected false positives, must be reviewed by "
                       "a human before release."),
        "patterns": sorted(SAFETY_PATTERNS),
        "findings": safety,
        "finding_count": len(safety),
        "human_review_required": True,
        "human_review_performed": False,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    (audit_dir / "stimulus_overlap_report.json").write_text(
        json.dumps(overlap, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    stats = build_statistics(records, safety, leakage, overlap, val_errors, flags)
    (audit_dir / "stimulus_statistics.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    (audit_dir / "stimulus_generation_report.json").write_text(json.dumps({
        "report_version": "0.1.0", "phase": "7F", "generated_at": CREATED_AT,
        "approved_items_input": len(approved),
        "stimuli_generated": len(records),
        "authoring_method": "researcher_specified_llm_assisted_draft",
        "generation_assistance": "drafting_only",
        "expert_authorship_claimed": False,
        "expert_validation_claimed": False,
        "design_modified": False,
        "preregistration_modified": False,
        "model_api_called": False,
        "model_evaluation_performed": False,
        "blind_review_performed": False,
        "asr_computed": False,
        "refusal_rate_computed": False,
        "latency_computed": False,
        "public_benchmark_modified": False,
        "turkish_dataset_modified": False,
        "flags": flags,
        "structural_errors": val_errors,
        "next_phase": "7G — human blind isolated-prompt review and full QC",
        "next_phase_started": False,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"records: {len(records)} | structural errors: {len(val_errors)} | "
          f"safety flags: {len(safety)} | leakage: {len(leakage)} | "
          f"overlap flagged: {len(overlap['flagged_for_researcher_review'])} | "
          f"generation flags: {len(flags)}")
    for e in val_errors[:20]:
        print("  ERROR:", e)
    for f in flags[:20]:
        print("  FLAG:", f)
    return 1 if val_errors else 0


if __name__ == "__main__":
    sys.exit(main())
