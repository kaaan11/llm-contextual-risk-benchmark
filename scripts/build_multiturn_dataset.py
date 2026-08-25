"""Phase 7B özgün multi-turn dataset construction pipeline'ı.

Bu script dış model API'si çağırmaz. Construction specification içindeki insan
tarafından incelenmemiş LLM-assisted taslakları deterministik dataset kayıtlarına
dönüştürür; canonical prompt ilişkilerini, provenance'ı, güvenlik sınırlarını,
duplicate'leri ve dağılım hedeflerini doğrular.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dataset.validate import validate_dataset  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "phase7b_multiturn_construction.json"
DEFAULT_OUTPUT_DIR = ROOT / "dataset" / "pilot" / "multiturn"
DEFAULT_RESULTS_DIR = ROOT / "results" / "dataset_audit"
ALLOWED_ROLES = {"system", "developer", "user", "assistant", "tool"}
ALLOWED_CATEGORIES = {
    "context_changes_interpretation",
    "context_has_no_material_effect",
    "legitimate_technical_context",
    "ambiguous_or_borderline",
}
FORBIDDEN_PATTERNS = (
    re.compile(r"(?i)\b(?:mimikatz|ransomware|keylogger|reverse shell|payload|botnet)\b"),
    re.compile(r"(?i)\b(?:powershell|cmd\.exe|bash)\s+[-/]"),
    re.compile(r"(?i)\b(?:curl|wget|nc|netcat)\s+https?://"),
    re.compile(r"(?i)-----BEGIN (?:RSA|OPENSSH|PRIVATE) KEY-----"),
    re.compile(r"(?i)\b(?:api[_ -]?key|access[_ -]?token|password)\s*[:=]\s*\S+"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
)


class ConstructionError(ValueError):
    """Construction specification veya aday kayıt güvenlik hatası."""


def load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConstructionError(f"JSON okunamadı: {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConstructionError(f"JSON kökü nesne olmalı: {source}")
    return value


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalized_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(value.split())


def _check_safe_text(text: str, location: str) -> None:
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            raise ConstructionError(f"{location}: güvenlik filtresi eşleşti: {pattern.pattern}")
    if "```" in text:
        raise ConstructionError(f"{location}: kod bloğu içeremez")
    if len(text) > 1200:
        raise ConstructionError(f"{location}: turn metni 1200 karakteri aşamaz")


def _require_string(entry: Mapping[str, Any], field: str, location: str) -> str:
    value = entry.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ConstructionError(f"{location}.{field}: boş olmayan metin gerekli")
    return value


def validate_construction_spec(spec: Mapping[str, Any]) -> None:
    required = (
        "construction_version",
        "schema_version",
        "dataset_id",
        "dataset_version",
        "created_at",
        "seed",
        "target_categories",
        "target_turn_counts",
        "authoring_defaults",
        "quality_gate",
        "candidate_plan",
    )
    missing = [field for field in required if field not in spec]
    if missing:
        raise ConstructionError(f"Construction specification eksik alanlar: {missing}")
    if spec["schema_version"] != "0.2.0":
        raise ConstructionError("Phase 7B yalnızca schema_version 0.2.0 destekler")
    if not isinstance(spec["candidate_plan"], list):
        raise ConstructionError("candidate_plan liste olmalı")

    targets = spec["target_categories"]
    length_targets = spec["target_turn_counts"]
    if not isinstance(targets, dict) or set(targets) != ALLOWED_CATEGORIES:
        raise ConstructionError("target_categories dört Phase 7B hücresini içermeli")
    if not isinstance(length_targets, dict):
        raise ConstructionError("target_turn_counts nesne olmalı")
    target_total = sum(int(value) for value in targets.values())
    if target_total != 50:
        raise ConstructionError(f"Kategori hedefleri 50 olmalı: {target_total}")
    if sum(int(value) for value in length_targets.values()) != 50:
        raise ConstructionError("Turn uzunluğu hedefleri 50 olmalı")

    if spec["authoring_defaults"].get("researcher_qc") is not False:
        raise ConstructionError("Bu construction aşamasında authoring_defaults.researcher_qc false olmalı")
    if spec["authoring_defaults"].get("external_validation_status") != "not_reviewed":
        raise ConstructionError("Bu construction aşamasında external_validation_status not_reviewed olmalı")
    if spec["authoring_defaults"].get("model_observed_effect") is not None:
        raise ConstructionError("Bu construction aşamasında model_observed_effect null olmalı")

    plan = spec["candidate_plan"]
    if len(plan) != 50:
        raise ConstructionError(f"candidate_plan tam olarak 50 kayıt içermeli: {len(plan)}")

    category_counts: Counter[str] = Counter()
    length_counts: Counter[str] = Counter()
    sample_ids: set[str] = set()
    for index, candidate in enumerate(plan):
        location = f"candidate_plan[{index}]"
        if not isinstance(candidate, dict):
            raise ConstructionError(f"{location}: nesne olmalı")
        for field in (
            "sample_id",
            "target_category",
            "composition_cell",
            "domain",
            "mechanism",
            "expected_context_effect",
            "expected_risk_profile",
            "design_confidence",
            "expected_interpretation",
            "expected_context_effect_rationale",
            "final_prompt",
        ):
            _require_string(candidate, field, location)
        sample_id = candidate["sample_id"]
        if sample_id in sample_ids:
            raise ConstructionError(f"{location}: duplicate sample_id: {sample_id}")
        sample_ids.add(sample_id)
        category = candidate["target_category"]
        if category not in ALLOWED_CATEGORIES:
            raise ConstructionError(f"{location}.target_category: bilinmeyen kategori: {category}")
        category_counts[category] += 1

        prior_turns = candidate.get("prior_turns")
        if not isinstance(prior_turns, list) or not prior_turns:
            raise ConstructionError(f"{location}.prior_turns: en az bir bağlam turn'ü gerekli")
        total_turns = len(prior_turns) + 1
        length_counts[str(total_turns)] += 1
        for turn_index, turn in enumerate(prior_turns):
            turn_location = f"{location}.prior_turns[{turn_index}]"
            if not isinstance(turn, dict):
                raise ConstructionError(f"{turn_location}: nesne olmalı")
            role = turn.get("role")
            if role not in ALLOWED_ROLES:
                raise ConstructionError(f"{turn_location}.role: geçersiz rol: {role}")
            text = _require_string(turn, "text", turn_location)
            _check_safe_text(text, turn_location)
        final_prompt = candidate["final_prompt"]
        _check_safe_text(final_prompt, f"{location}.final_prompt")
        if candidate["composition_cell"] == "ambiguous_borderline_context" and candidate["design_confidence"] == "high":
            raise ConstructionError(f"{location}: ambiguous kayıt high design_confidence taşıyamaz")

    if dict(category_counts) != {key: int(value) for key, value in targets.items()}:
        raise ConstructionError(f"Kategori dağılımı hedefle eşleşmiyor: {dict(category_counts)}")
    if dict(length_counts) != {str(key): int(value) for key, value in length_targets.items()}:
        raise ConstructionError(f"Uzunluk dağılımı hedefle eşleşmiyor: {dict(length_counts)}")


def _make_turn(turn_id: str, sequence: int, role: str, text: str) -> dict[str, Any]:
    return {
        "turn_id": turn_id,
        "sequence": sequence,
        "role": role,
        "content": {
            "text": text,
            "redaction_status": "not_redacted",
        },
    }


def build_dataset(spec: Mapping[str, Any]) -> dict[str, Any]:
    validate_construction_spec(spec)
    defaults = dict(spec["authoring_defaults"])
    records: list[dict[str, Any]] = []
    seen_conversation_ids: set[str] = set()
    seen_exact: set[str] = set()
    seen_normalized: set[str] = set()

    for candidate in spec["candidate_plan"]:
        sample_id = str(candidate["sample_id"])
        conversation_id = f"CONV-{sample_id}"
        if conversation_id in seen_conversation_ids:
            raise ConstructionError(f"duplicate conversation_id: {conversation_id}")
        seen_conversation_ids.add(conversation_id)
        prior_turns = candidate["prior_turns"]
        canonical_prompt = str(candidate["final_prompt"])
        exact_text_hash = sha256_text(canonical_prompt)
        normalized_hash = sha256_text(normalized_text(canonical_prompt))
        if exact_text_hash in seen_exact or normalized_hash in seen_normalized:
            raise ConstructionError(f"duplicate final prompt: {sample_id}")
        seen_exact.add(exact_text_hash)
        seen_normalized.add(normalized_hash)
        turns = [
            _make_turn(f"{sample_id}-turn-{index:02d}", index, str(turn["role"]), str(turn["text"]))
            for index, turn in enumerate(prior_turns)
        ]
        final_turn_id = f"{sample_id}-turn-{len(turns):02d}"
        turns.append(_make_turn(final_turn_id, len(turns), "user", canonical_prompt))
        prompt_hash = sha256_text(canonical_prompt)
        record = {
            "sample_id": sample_id,
            "record_version": "0.2.0",
            "dataset_membership": ["multi_turn"],
            "record_type": "multi_turn",
            "split": "none",
            "sensitivity": "private",
            "source": str(candidate.get("source", defaults["source"])),
            "dataset_version": str(spec["dataset_version"]),
            "conversation_id": conversation_id,
            "canonical_final_prompt": canonical_prompt,
            "canonical_final_prompt_sha256": prompt_hash,
            "evaluation_conditions": {
                "final_prompt_only": {
                    "condition": "final_prompt_only",
                    "prompt": canonical_prompt,
                    "prompt_sha256": prompt_hash,
                },
                "full_context": {
                    "condition": "full_context",
                    "turn_ids": [turn["turn_id"] for turn in turns],
                    "final_prompt_turn_id": final_turn_id,
                },
            },
            "expected_context_effect": candidate["expected_context_effect"],
            "model_observed_effect": None,
            "expected_risk_profile": candidate["expected_risk_profile"],
            "design_confidence": candidate["design_confidence"],
            "composition_cell": candidate["composition_cell"],
            "context_signal_types": list(candidate["context_signal_types"]),
            "expected_interpretation": candidate["expected_interpretation"],
            "expected_context_effect_rationale": candidate["expected_context_effect_rationale"],
            "authoring_method": str(candidate.get("authoring_method", defaults["authoring_method"])),
            "generation_assistance": str(candidate.get("generation_assistance", defaults["generation_assistance"])),
            "source_seed": candidate.get("source_seed", defaults["source_seed"]),
            "researcher_qc": bool(candidate.get("researcher_qc", defaults["researcher_qc"])),
            "external_validation_status": str(candidate.get("external_validation_status", defaults["external_validation_status"])),
            "created_at": str(candidate.get("created_at", spec["created_at"])),
            "provenance": {
                "source_type": "research_generated",
                "source_ref": "phase7b-original-multiturn",
                "collection_notes": "Özgün Phase 7B taslağı; insan araştırmacı QC'si bekliyor.",
            },
            "task_metadata": {
                "domain_code": str(candidate["domain"]),
                "language": "tr",
                "source_type": "research_generated",
                "sampling_cell": str(candidate["target_category"]),
                "template_id": "phase7b-original-multiturn-v1",
                "context_effect_description": str(candidate["mechanism"]),
            },
            "turns": turns,
            "annotations": [],
            "evaluations": [],
        }
        records.append(record)

    return {
        "schema_version": str(spec["schema_version"]),
        "dataset_id": str(spec["dataset_id"]),
        "dataset_version": str(spec["dataset_version"]),
        "created_at": str(spec["created_at"]),
        "purpose": "Original multi-turn context-aware risk interpretation pilot; evaluation yapılmamıştır.",
        "release_profile": "private",
        "provenance": {
            "source_type": "research_generated",
            "source_ref": "phase7b-original-multiturn",
            "collection_notes": "50 özgün, güvenli, LLM-assisted taslak; researcher QC ve external validation bekliyor.",
        },
        "records": records,
        "evaluation_runs": [],
        "analysis_runs": [],
    }


def calculate_statistics(dataset: Mapping[str, Any], spec: Mapping[str, Any], validation_errors: list[str]) -> dict[str, Any]:
    records = list(dataset.get("records", []))
    turn_counts = [len(record.get("turns", [])) for record in records]
    bool_counts = Counter(str(record.get("researcher_qc")).lower() for record in records)
    validation_status_counts = Counter(str(record.get("external_validation_status")) for record in records)
    duplicate_count = len(records) - len({record.get("sample_id") for record in records})
    stats: dict[str, Any] = {
        "phase": "7B",
        "statistics_version": "0.1.0",
        "dataset_id": dataset.get("dataset_id"),
        "dataset_version": dataset.get("dataset_version"),
        "total_conversations": len(records),
        "total_turns": sum(turn_counts),
        "turns_per_conversation": dict(sorted(Counter(str(value) for value in turn_counts).items(), key=lambda item: int(item[0]))),
        "minimum_turns": min(turn_counts) if turn_counts else 0,
        "maximum_turns": max(turn_counts) if turn_counts else 0,
        "mean_turns": round(statistics.mean(turn_counts), 4) if turn_counts else 0,
        "median_turns": statistics.median(turn_counts) if turn_counts else 0,
        "target_category_distribution": dict(Counter(
            str(record.get("task_metadata", {}).get("sampling_cell")) for record in records
        )),
        "composition_cell_distribution": dict(Counter(str(record.get("composition_cell")) for record in records)),
        "context_effect_distribution": dict(Counter(str(record.get("expected_context_effect")) for record in records)),
        "risk_profile_distribution": dict(Counter(str(record.get("expected_risk_profile")) for record in records)),
        "confidence_distribution": dict(Counter(str(record.get("design_confidence")) for record in records)),
        "authoring_method_distribution": dict(Counter(str(record.get("authoring_method")) for record in records)),
        "generation_assistance_distribution": dict(Counter(str(record.get("generation_assistance")) for record in records)),
        "researcher_qc_distribution": dict(bool_counts),
        "external_validation_status_distribution": dict(validation_status_counts),
        "duplicate_count": duplicate_count,
        "validation_failures": len(validation_errors),
        "evaluation_runs": 0,
        "model_observed_effect_non_null": sum(record.get("model_observed_effect") is not None for record in records),
        "construction_seed": spec.get("seed"),
    }
    return stats


def validate_built_dataset(dataset: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_dataset(dataset)
    records = list(dataset.get("records", []))
    sample_ids = [record.get("sample_id") for record in records]
    conversation_ids = [record.get("conversation_id") for record in records]
    duplicate_sample_ids = sorted(value for value, count in Counter(sample_ids).items() if count > 1)
    duplicate_conversation_ids = sorted(value for value, count in Counter(conversation_ids).items() if count > 1)
    for record in records:
        if record.get("model_observed_effect") is not None:
            errors.append(f"{record.get('sample_id')}: model_observed_effect null olmalı")
        if record.get("researcher_qc") is not False:
            errors.append(f"{record.get('sample_id')}: researcher_qc false olmalı; insan QC yapılmadı")
        if record.get("external_validation_status") != "not_reviewed":
            errors.append(f"{record.get('sample_id')}: external_validation_status not_reviewed olmalı")
        if record.get("source") != "original" or record.get("source_seed") is not None:
            errors.append(f"{record.get('sample_id')}: özgün source/source_seed tutarsız")
    status = "valid" if not errors and not duplicate_sample_ids and not duplicate_conversation_ids else "invalid"
    return {
        "phase": "7B",
        "validation_version": "0.1.0",
        "status": status,
        "schema_version": dataset.get("schema_version"),
        "records_checked": len(records),
        "errors": errors,
        "duplicate_sample_ids": duplicate_sample_ids,
        "duplicate_conversation_ids": duplicate_conversation_ids,
        "safety_checks": {
            "external_model_api_calls": 0,
            "model_evaluations": 0,
            "expert_annotations": 0,
            "personal_data_claims": 0,
            "operational_attack_payloads": 0,
        },
        "qc_summary": {
            "researcher_qc_true": sum(record.get("researcher_qc") is True for record in records),
            "researcher_qc_false": sum(record.get("researcher_qc") is False for record in records),
            "external_validation_claims": 0,
        },
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_outputs(
    dataset: Mapping[str, Any],
    spec: Mapping[str, Any],
    validation_report: Mapping[str, Any],
    statistics: Mapping[str, Any],
    *,
    output_dir: Path,
    results_dir: Path,
    config_path: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "multiturn_dataset.json", dataset)
    records_path = output_dir / "records.jsonl"
    records_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in dataset["records"]),
        encoding="utf-8",
    )
    _write_json(output_dir / "construction_plan_snapshot.json", spec)
    _write_json(results_dir / "multiturn_validation.json", validation_report)
    _write_json(results_dir / "multiturn_statistics.json", statistics)
    construction_report = {
        "phase": "7B",
        "report_version": "0.1.0",
        "status": "constructed_pending_researcher_qc" if validation_report["status"] == "valid" else "failed",
        "config_path": str(config_path.relative_to(ROOT)),
        "output_dataset": str((output_dir / "multiturn_dataset.json").relative_to(ROOT)),
        "plan_candidate_count": len(spec["candidate_plan"]),
        "records_created": len(dataset["records"]),
        "researcher_qc_true": validation_report["qc_summary"]["researcher_qc_true"],
        "researcher_qc_false": validation_report["qc_summary"]["researcher_qc_false"],
        "external_model_api_calls": validation_report["safety_checks"]["external_model_api_calls"],
        "model_evaluations": validation_report["safety_checks"]["model_evaluations"],
        "expert_annotations": validation_report["safety_checks"]["expert_annotations"],
        "validation_status": validation_report["status"],
        "next_gate": "Araştırmacı her kaydı inceleyip QC sonucunu explicit olarak güncellemeden model evaluation başlatılmamalı.",
    }
    _write_json(results_dir / "multiturn_construction_report.json", construction_report)


def build_and_write(
    config_path: str | Path = DEFAULT_CONFIG,
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    results_dir: str | Path = DEFAULT_RESULTS_DIR,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    config = Path(config_path)
    spec = load_json(config)
    validate_construction_spec(spec)
    dataset = build_dataset(spec)
    validation_report = validate_built_dataset(dataset)
    statistics = calculate_statistics(dataset, spec, list(validation_report["errors"]))
    write_outputs(
        dataset,
        spec,
        validation_report,
        statistics,
        output_dir=Path(output_dir),
        results_dir=Path(results_dir),
        config_path=config,
    )
    if validation_report["status"] != "valid":
        raise ConstructionError("Oluşturulan dataset geçersiz; çıktı raporu yazıldı")
    return dataset, validation_report, statistics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 7B özgün multi-turn dataset builder")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    args = parser.parse_args(argv)
    try:
        dataset, validation, statistics = build_and_write(
            args.config,
            output_dir=args.output_dir,
            results_dir=args.results_dir,
        )
    except (ConstructionError, OSError, TypeError, KeyError) as exc:
        print(f"Construction başarısız: {exc}")
        return 1
    print(json.dumps({
        "status": validation["status"],
        "records_created": len(dataset["records"]),
        "total_turns": statistics["total_turns"],
        "researcher_qc_true": validation["qc_summary"]["researcher_qc_true"],
        "model_evaluations": validation["safety_checks"]["model_evaluations"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
