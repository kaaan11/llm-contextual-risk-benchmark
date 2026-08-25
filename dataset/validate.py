"""Dataset manifesti için bağımlılıksız temel doğrulama.

Bu modül JSON Schema’nın yerine geçmez. Şema belgesine ek olarak, birden fazla
kayıt veya alan arasındaki ilişkileri kontrol eder. Hassas veri üretmez ya da
değiştirmez.
"""

from __future__ import annotations

import json
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "dataset" / "schema.json"
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")
SCHEMA_VERSIONS = {"0.1.0", "0.2.0"}
MEMBERSHIPS = {"benign", "adversarial", "multi_turn"}
SENSITIVITIES = {"public_sanitized", "controlled", "private", "restricted"}
RISK_PROFILES = {"none", "low", "medium", "high", "critical", "unknown"}
SOURCES = {"original", "adapted_public_concept", "public_benchmark_derived"}
CONTEXT_EFFECTS = {
    "context_increases_legitimacy",
    "context_increases_risk",
    "context_reduces_ambiguity",
    "context_increases_ambiguity",
    "context_has_no_material_effect",
    "context_is_irrelevant",
}
CONTEXT_SIGNAL_TYPES = {
    "intent_clarification",
    "role_clarification",
    "task_clarification",
    "environmental_context",
    "defensive_context",
    "academic_context",
    "developer_context",
    "prior_technical_discussion",
    "ambiguity_reduction",
    "ambiguity_introduction",
    "risk_escalation",
    "risk_de_escalation",
    "irrelevant_context",
    "conflicting_context",
}
COMPOSITION_CELLS = {
    "context_changes_interpretation",
    "context_does_not_change_interpretation",
    "legitimate_technical_context",
    "ambiguous_borderline_context",
}
EXPECTED_INTERPRETATIONS = {
    "benign",
    "legitimate_technical",
    "adversarial_or_high_risk",
    "ambiguous_or_insufficient_information",
}
DESIGN_CONFIDENCES = {"low", "medium", "high"}
AUTHORING_METHODS = {
    "researcher_authored",
    "llm_assisted_draft",
    "adapted_public_concept",
    "researcher_specified_llm_assisted_draft",
}
GENERATION_ASSISTANCE = {
    "none",
    "drafting_only",
    "paraphrase_assistance",
    "mixed",
}
EXTERNAL_VALIDATION_STATUSES = {
    "not_reviewed",
    "researcher_reviewed",
    "expert_reviewed",
    "externally_validated",
}


def _is_object(value: Any) -> bool:
    return isinstance(value, dict)


def _required(obj: dict[str, Any], fields: tuple[str, ...], path: str, errors: list[str]) -> None:
    for field in fields:
        if field not in obj:
            errors.append(f"{path}: zorunlu alan eksik: {field}")


def _check_id(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        errors.append(f"{path}: geçersiz kimlik biçimi")


def _check_version(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not VERSION_RE.fullmatch(value):
        errors.append(f"{path}: geçersiz sürüm biçimi")


def _check_datetime(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{path}: tarih metin olmalı")
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{path}: ISO-8601 tarih bekleniyor")


def _check_enum(value: Any, allowed: set[str], path: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{path}: geçersiz değer: {value}")


def _check_sha256(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        errors.append(f"{path}: 64 karakterlik SHA-256 hex değeri bekleniyor")
        return False
    return True


def _check_phase7_record(
    record: dict[str, Any],
    path: str,
    turns: list[Any],
    errors: list[str],
    *,
    root_dataset_version: str | None,
    allow_observed_effect: bool,
    allow_reviewed_status: bool,
) -> None:
    """Validate v0.2.0 paired multi-turn metadata and exact prompt identity."""

    _required(
        record,
        (
            "conversation_id",
            "canonical_final_prompt",
            "canonical_final_prompt_sha256",
            "evaluation_conditions",
            "expected_context_effect",
            "model_observed_effect",
            "expected_risk_profile",
            "design_confidence",
            "source",
            "dataset_version",
            "composition_cell",
            "context_signal_types",
            "expected_interpretation",
            "expected_context_effect_rationale",
            "authoring_method",
            "generation_assistance",
            "source_seed",
            "researcher_qc",
            "external_validation_status",
            "created_at",
        ),
        path,
        errors,
    )

    conversation_id = record.get("conversation_id")
    if conversation_id is not None:
        _check_id(conversation_id, f"{path}.conversation_id", errors)

    if "dataset_version" in record:
        _check_version(record["dataset_version"], f"{path}.dataset_version", errors)
        if record["dataset_version"] != root_dataset_version:
            errors.append(f"{path}.dataset_version: root dataset_version ile aynı olmalı")

    canonical_prompt = record.get("canonical_final_prompt")
    if not isinstance(canonical_prompt, str) or not canonical_prompt:
        errors.append(f"{path}.canonical_final_prompt: boş olmayan metin olmalı")

    canonical_hash = record.get("canonical_final_prompt_sha256")
    canonical_hash_valid = _check_sha256(canonical_hash, f"{path}.canonical_final_prompt_sha256", errors)
    if canonical_hash_valid and isinstance(canonical_prompt, str):
        expected_hash = hashlib.sha256(canonical_prompt.encode("utf-8")).hexdigest()
        if canonical_hash.lower() != expected_hash:
            errors.append(f"{path}.canonical_final_prompt_sha256: canonical prompt ile eşleşmiyor")

    conditions = record.get("evaluation_conditions")
    if not _is_object(conditions):
        errors.append(f"{path}.evaluation_conditions: nesne olmalı")
    else:
        expected_condition_keys = {"final_prompt_only", "full_context"}
        if set(conditions) != expected_condition_keys:
            errors.append(f"{path}.evaluation_conditions: yalnızca iki değerlendirme koşulu bekleniyor")

        final_only = conditions.get("final_prompt_only")
        if not _is_object(final_only):
            errors.append(f"{path}.evaluation_conditions.final_prompt_only: nesne olmalı")
        else:
            if final_only.get("condition") != "final_prompt_only":
                errors.append(f"{path}.evaluation_conditions.final_prompt_only.condition: sabit değer hatalı")
            if final_only.get("prompt") != canonical_prompt:
                errors.append(f"{path}.evaluation_conditions.final_prompt_only.prompt: canonical prompt ile aynı olmalı")
            prompt_hash = final_only.get("prompt_sha256")
            if _check_sha256(prompt_hash, f"{path}.evaluation_conditions.final_prompt_only.prompt_sha256", errors):
                if isinstance(canonical_prompt, str):
                    expected_hash = hashlib.sha256(canonical_prompt.encode("utf-8")).hexdigest()
                    if prompt_hash.lower() != expected_hash:
                        errors.append(f"{path}.evaluation_conditions.final_prompt_only.prompt_sha256: prompt ile eşleşmiyor")

        full_context = conditions.get("full_context")
        if not _is_object(full_context):
            errors.append(f"{path}.evaluation_conditions.full_context: nesne olmalı")
        else:
            if full_context.get("condition") != "full_context":
                errors.append(f"{path}.evaluation_conditions.full_context.condition: sabit değer hatalı")
            condition_turn_ids = full_context.get("turn_ids")
            if not isinstance(condition_turn_ids, list) or len(condition_turn_ids) < 2:
                errors.append(f"{path}.evaluation_conditions.full_context.turn_ids: en az iki turn bekleniyor")
            else:
                if all(isinstance(turn_id, str) for turn_id in condition_turn_ids) and len(condition_turn_ids) != len(set(condition_turn_ids)):
                    errors.append(f"{path}.evaluation_conditions.full_context.turn_ids: tekrar eden turn_id")
                actual_turn_ids = [turn.get("turn_id") for turn in turns if _is_object(turn)]
                if condition_turn_ids != actual_turn_ids:
                    errors.append(f"{path}.evaluation_conditions.full_context.turn_ids: turns ile aynı sırada olmalı")
            final_turn_id = full_context.get("final_prompt_turn_id")
            actual_turn_ids = [turn.get("turn_id") for turn in turns if _is_object(turn)]
            if not actual_turn_ids or final_turn_id != actual_turn_ids[-1]:
                errors.append(f"{path}.evaluation_conditions.full_context.final_prompt_turn_id: son turn olmalı")
            if turns and _is_object(turns[-1]):
                if turns[-1].get("role") != "user":
                    errors.append(f"{path}.turns[-1].role: final prompt turn user rolünde olmalı")
                final_turn_content = turns[-1].get("content")
                if not _is_object(final_turn_content) or final_turn_content.get("text") != canonical_prompt:
                    errors.append(f"{path}.turns[-1].content.text: canonical prompt ile tam olarak aynı olmalı")

    _check_enum(record.get("expected_context_effect"), CONTEXT_EFFECTS, f"{path}.expected_context_effect", errors)
    observed_effect = record.get("model_observed_effect")
    if observed_effect is not None:
        if not allow_observed_effect:
            errors.append(f"{path}.model_observed_effect: örnek üretimi aşamasında null olmalı")
        else:
            _check_enum(observed_effect, CONTEXT_EFFECTS, f"{path}.model_observed_effect", errors)
    _check_enum(record.get("expected_risk_profile"), RISK_PROFILES, f"{path}.expected_risk_profile", errors)
    _check_enum(record.get("design_confidence"), DESIGN_CONFIDENCES, f"{path}.design_confidence", errors)
    _check_enum(record.get("source"), SOURCES, f"{path}.source", errors)
    _check_enum(record.get("composition_cell"), COMPOSITION_CELLS, f"{path}.composition_cell", errors)
    signal_types = record.get("context_signal_types")
    if not isinstance(signal_types, list) or not signal_types:
        errors.append(f"{path}.context_signal_types: boş olmayan liste olmalı")
    else:
        if all(isinstance(signal_type, str) for signal_type in signal_types) and len(signal_types) != len(set(signal_types)):
            errors.append(f"{path}.context_signal_types: tekrar eden değer var")
        for signal_type in signal_types:
            _check_enum(signal_type, CONTEXT_SIGNAL_TYPES, f"{path}.context_signal_types", errors)
    _check_enum(record.get("expected_interpretation"), EXPECTED_INTERPRETATIONS, f"{path}.expected_interpretation", errors)
    if not isinstance(record.get("expected_context_effect_rationale"), str) or not record.get("expected_context_effect_rationale"):
        errors.append(f"{path}.expected_context_effect_rationale: boş olmayan metin olmalı")
    _check_enum(record.get("authoring_method"), AUTHORING_METHODS, f"{path}.authoring_method", errors)
    _check_enum(record.get("generation_assistance"), GENERATION_ASSISTANCE, f"{path}.generation_assistance", errors)

    source_seed = record.get("source_seed")
    if source_seed is not None:
        if not _is_object(source_seed):
            errors.append(f"{path}.source_seed: nesne veya null olmalı")
        else:
            _required(source_seed, ("source_dataset", "source_sample_id", "source_url", "transformation_summary"), f"{path}.source_seed", errors)
            for field in ("source_dataset", "source_sample_id", "source_url", "transformation_summary"):
                if field in source_seed and (not isinstance(source_seed[field], str) or not source_seed[field]):
                    errors.append(f"{path}.source_seed.{field}: boş olmayan metin olmalı")
    if record.get("authoring_method") == "adapted_public_concept" and source_seed is None:
        errors.append(f"{path}.source_seed: adapted_public_concept için kaynak bilgisi gerekli")

    researcher_qc = record.get("researcher_qc")
    if not isinstance(researcher_qc, bool):
        errors.append(f"{path}.researcher_qc: boolean olmalı")
    validation_status = record.get("external_validation_status")
    _check_enum(validation_status, EXTERNAL_VALIDATION_STATUSES, f"{path}.external_validation_status", errors)
    if not allow_reviewed_status and validation_status in {"expert_reviewed", "externally_validated"}:
        errors.append(f"{path}.external_validation_status: uzman veya dış doğrulama iddiası bu aşamada yasak")
    if researcher_qc is True and validation_status not in {"researcher_reviewed", "expert_reviewed", "externally_validated"}:
        errors.append(f"{path}.researcher_qc: true için en az researcher_reviewed durumu gerekli")
    if validation_status == "researcher_reviewed" and researcher_qc is not True:
        errors.append(f"{path}.external_validation_status: researcher_reviewed için researcher_qc=true gerekli")
    _check_datetime(record.get("created_at"), f"{path}.created_at", errors)


def _check_content(content: Any, path: str, errors: list[str]) -> None:
    if not _is_object(content):
        errors.append(f"{path}: içerik nesne olmalı")
        return
    _required(content, ("redaction_status",), path, errors)
    if not content.get("text") and not content.get("content_ref"):
        errors.append(f"{path}: text veya content_ref alanlarından biri gerekli")


def _check_turn(turn: Any, index: int, errors: list[str]) -> None:
    path = f"records[*].turns[{index}]"
    if not _is_object(turn):
        errors.append(f"{path}: nesne olmalı")
        return
    _required(turn, ("turn_id", "sequence", "role", "content"), path, errors)
    if "turn_id" in turn:
        _check_id(turn["turn_id"], f"{path}.turn_id", errors)
    if not isinstance(turn.get("sequence"), int) or turn.get("sequence", -1) < 0:
        errors.append(f"{path}.sequence: sıfır veya daha büyük tamsayı olmalı")
    _check_content(turn.get("content"), f"{path}.content", errors)


def _check_record(
    record: Any,
    index: int,
    run_ids: set[str],
    errors: list[str],
    *,
    schema_version: str,
    root_dataset_version: str | None,
    allow_observed_effect: bool,
    allow_reviewed_status: bool,
) -> None:
    path = f"records[{index}]"
    if not _is_object(record):
        errors.append(f"{path}: nesne olmalı")
        return
    _required(
        record,
        (
            "sample_id",
            "record_version",
            "dataset_membership",
            "record_type",
            "split",
            "sensitivity",
            "turns",
            "annotations",
            "evaluations",
        ),
        path,
        errors,
    )
    if "sample_id" in record:
        _check_id(record["sample_id"], f"{path}.sample_id", errors)
    if "record_version" in record:
        _check_version(record["record_version"], f"{path}.record_version", errors)

    memberships = record.get("dataset_membership", [])
    if not isinstance(memberships, list) or not memberships:
        errors.append(f"{path}.dataset_membership: boş olmayan liste olmalı")
        memberships = []
    if len(memberships) != len(set(memberships)):
        errors.append(f"{path}.dataset_membership: tekrar eden üyelik var")
    if any(item not in MEMBERSHIPS for item in memberships):
        errors.append(f"{path}.dataset_membership: bilinmeyen üyelik var")

    record_type = record.get("record_type")
    turns = record.get("turns", [])
    if not isinstance(turns, list):
        errors.append(f"{path}.turns: liste olmalı")
        turns = []
    if record_type == "single_turn" and len(turns) != 1:
        errors.append(f"{path}: single_turn tam olarak bir turn içermeli")
    if record_type == "multi_turn" and len(turns) < 2:
        errors.append(f"{path}: multi_turn en az iki turn içermeli")
    if (record_type == "multi_turn") != ("multi_turn" in memberships):
        errors.append(f"{path}: multi_turn membership ve record_type uyumsuz")
    if record_type == "single_turn" and "multi_turn" in memberships:
        errors.append(f"{path}: single_turn kaydı multi_turn üyeliği taşıyamaz")
    sequences = []
    turn_ids = set()
    for turn_index, turn in enumerate(turns):
        _check_turn(turn, turn_index, errors)
        if _is_object(turn):
            if turn.get("turn_id") in turn_ids:
                errors.append(f"{path}.turns: tekrar eden turn_id")
            turn_ids.add(turn.get("turn_id"))
            sequences.append(turn.get("sequence"))
    if sequences and sequences != list(range(len(sequences))):
        errors.append(f"{path}.turns.sequence: 0’dan başlayan ardışık sıra bekleniyor")

    if record.get("sensitivity") not in SENSITIVITIES:
        errors.append(f"{path}.sensitivity: bilinmeyen hassasiyet profili")

    if schema_version == "0.2.0" and record_type == "multi_turn":
        _check_phase7_record(
            record,
            path,
            turns,
            errors,
            root_dataset_version=root_dataset_version,
            allow_observed_effect=allow_observed_effect,
            allow_reviewed_status=allow_reviewed_status,
        )

    annotations = record.get("annotations", [])
    if not isinstance(annotations, list):
        errors.append(f"{path}.annotations: liste olmalı")
    else:
        annotation_ids = set()
        for annotation in annotations:
            if not _is_object(annotation):
                errors.append(f"{path}.annotations: her kayıt nesne olmalı")
                continue
            annotation_id = annotation.get("annotation_id")
            if annotation_id in annotation_ids:
                errors.append(f"{path}.annotations: tekrar eden annotation_id")
            annotation_ids.add(annotation_id)
            if annotation_id is not None:
                _check_id(annotation_id, f"{path}.annotation_id", errors)
            if "guideline_version" in annotation:
                _check_version(annotation["guideline_version"], f"{path}.guideline_version", errors)
            if "annotated_at" in annotation:
                _check_datetime(annotation["annotated_at"], f"{path}.annotated_at", errors)

    evaluations = record.get("evaluations", [])
    if not isinstance(evaluations, list):
        errors.append(f"{path}.evaluations: liste olmalı")
    else:
        evaluation_ids = set()
        for evaluation in evaluations:
            if not _is_object(evaluation):
                errors.append(f"{path}.evaluations: her kayıt nesne olmalı")
                continue
            evaluation_id = evaluation.get("evaluation_id")
            if evaluation_id in evaluation_ids:
                errors.append(f"{path}.evaluations: tekrar eden evaluation_id")
            evaluation_ids.add(evaluation_id)
            if evaluation_id is not None:
                _check_id(evaluation_id, f"{path}.evaluation_id", errors)
            run_id = evaluation.get("run_id")
            if run_id not in run_ids:
                errors.append(f"{path}.evaluations: tanımsız run_id: {run_id}")
            if "evaluated_at" in evaluation:
                _check_datetime(evaluation["evaluated_at"], f"{path}.evaluated_at", errors)
            _check_content(evaluation.get("response"), f"{path}.response", errors)
            latency = evaluation.get("latency")
            if not _is_object(latency) or not isinstance(latency.get("total_ms"), (int, float)):
                errors.append(f"{path}.latency: total_ms içeren nesne olmalı")


def validate_dataset(
    dataset: Any,
    *,
    allow_observed_effect: bool = False,
    allow_reviewed_status: bool = False,
) -> list[str]:
    """Dataset için hata listesini döndürür; boş liste geçerli veri demektir."""

    errors: list[str] = []
    if not _is_object(dataset):
        return ["kök değer nesne olmalı"]
    _required(dataset, ("schema_version", "dataset_id", "dataset_version", "release_profile", "records"), "root", errors)
    schema_version = dataset.get("schema_version")
    if schema_version not in SCHEMA_VERSIONS:
        errors.append("root.schema_version: 0.1.0 veya 0.2.0 bekleniyor")
    if "dataset_id" in dataset:
        _check_id(dataset["dataset_id"], "root.dataset_id", errors)
    if "dataset_version" in dataset:
        _check_version(dataset["dataset_version"], "root.dataset_version", errors)
    if "created_at" in dataset:
        _check_datetime(dataset["created_at"], "root.created_at", errors)

    runs = dataset.get("evaluation_runs", [])
    if not isinstance(runs, list):
        errors.append("root.evaluation_runs: liste olmalı")
        runs = []
    run_ids: set[str] = set()
    for run in runs:
        if not _is_object(run):
            errors.append("root.evaluation_runs: her kayıt nesne olmalı")
            continue
        run_id = run.get("run_id")
        if run_id in run_ids:
            errors.append(f"root.evaluation_runs: tekrar eden run_id: {run_id}")
        run_ids.add(run_id)
        if run_id is not None:
            _check_id(run_id, "root.evaluation_runs.run_id", errors)
        if "run_version" in run:
            _check_version(run["run_version"], "root.evaluation_runs.run_version", errors)
        if "dataset_version" in run and run["dataset_version"] != dataset.get("dataset_version"):
            errors.append(f"root.evaluation_runs[{run_id}]: dataset_version ile root sürümü farklı")

    records = dataset.get("records", [])
    if not isinstance(records, list):
        errors.append("root.records: liste olmalı")
        records = []
    sample_ids: set[str] = set()
    conversation_ids: set[str] = set()
    for index, record in enumerate(records):
        if _is_object(record):
            sample_id = record.get("sample_id")
            if sample_id in sample_ids:
                errors.append(f"root.records: tekrar eden sample_id: {sample_id}")
            sample_ids.add(sample_id)
            conversation_id = record.get("conversation_id")
            if conversation_id is not None:
                if conversation_id in conversation_ids:
                    errors.append(f"root.records: tekrar eden conversation_id: {conversation_id}")
                conversation_ids.add(conversation_id)
        _check_record(
            record,
            index,
            run_ids,
            errors,
            schema_version=schema_version,
            root_dataset_version=dataset.get("dataset_version"),
            allow_observed_effect=allow_observed_effect,
            allow_reviewed_status=allow_reviewed_status,
        )

    analyses = dataset.get("analysis_runs", [])
    if not isinstance(analyses, list):
        errors.append("root.analysis_runs: liste olmalı")
    else:
        analysis_ids: set[str] = set()
        for analysis in analyses:
            if not _is_object(analysis):
                errors.append("root.analysis_runs: her kayıt nesne olmalı")
                continue
            analysis_id = analysis.get("analysis_id")
            if analysis_id in analysis_ids:
                errors.append(f"root.analysis_runs: tekrar eden analysis_id: {analysis_id}")
            analysis_ids.add(analysis_id)
            if analysis_id is not None:
                _check_id(analysis_id, "root.analysis_runs.analysis_id", errors)
            if analysis.get("input_dataset_version") != dataset.get("dataset_version"):
                errors.append(f"root.analysis_runs[{analysis_id}]: input_dataset_version ile root sürümü farklı")

    return errors


def validate_file(
    path: str | Path,
    *,
    allow_observed_effect: bool = False,
    allow_reviewed_status: bool = False,
) -> list[str]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return validate_dataset(
            json.load(handle),
            allow_observed_effect=allow_observed_effect,
            allow_reviewed_status=allow_reviewed_status,
        )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("Kullanım: validate.py <dataset.json>")
        return 2
    try:
        errors = validate_file(argv[0])
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Dosya okunamadı: {exc}")
        return 2
    if errors:
        print("Geçersiz dataset:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Dataset geçerli.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
