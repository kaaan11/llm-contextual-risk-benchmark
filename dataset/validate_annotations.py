"""Annotation sidecar doğrulayıcısı.

JSON Schema temel yapı ve değer kısıtlarını tanımlar. Bu modül, puanlayıcı
rolleri, sentetik örneklerin ayrıştırılması ve record_type ile
context_dependence arasındaki ilişkiler gibi çapraz kuralları kontrol eder.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ANNOTATOR_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
ORDINAL_DIMS = (
    "adversariality",
    "maliciousness",
    "legitimate_plausibility",
    "context_dependence",
    "expected_risk",
)
ALL_DIMS = ORDINAL_DIMS + ("refusal_appropriateness",)
STATUSES = {"scored", "not_applicable", "insufficient_information"}
CONFIDENCE = {"low", "medium", "high"}
REFUSAL_VALUES = {
    "allow_safe_completion",
    "allow_with_boundaries",
    "partial_or_redirect",
    "refusal_appropriate",
    "uncertain",
    "not_applicable",
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


def _check_rationale_codes(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{path}: en az bir rationale code gerekli")
        return
    if len(value) != len(set(value)):
        errors.append(f"{path}: tekrar eden rationale code var")


def _check_ordinal_label(label: Any, path: str, errors: list[str]) -> None:
    if not _is_object(label):
        errors.append(f"{path}: nesne olmalı")
        return
    _required(label, ("status", "confidence", "rationale_codes"), path, errors)
    status = label.get("status")
    if status not in STATUSES:
        errors.append(f"{path}.status: geçersiz durum")
    if label.get("confidence") not in CONFIDENCE:
        errors.append(f"{path}.confidence: low/medium/high olmalı")
    _check_rationale_codes(label.get("rationale_codes"), f"{path}.rationale_codes", errors)
    if status == "scored":
        score = label.get("score")
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 4:
            errors.append(f"{path}.score: scored durumunda 0–4 tamsayı olmalı")
    elif "score" in label:
        errors.append(f"{path}.score: scored olmayan durumda bulunmamalı")


def _check_refusal_label(label: Any, path: str, errors: list[str]) -> None:
    if not _is_object(label):
        errors.append(f"{path}: nesne olmalı")
        return
    _required(label, ("value", "confidence", "rationale_codes"), path, errors)
    if label.get("value") not in REFUSAL_VALUES:
        errors.append(f"{path}.value: geçersiz refusal_appropriateness değeri")
    if label.get("confidence") not in CONFIDENCE:
        errors.append(f"{path}.confidence: low/medium/high olmalı")
    _check_rationale_codes(label.get("rationale_codes"), f"{path}.rationale_codes", errors)


def _check_record(record: Any, index: int, bundle_type: str, annotation_ids: set[str], errors: list[str]) -> None:
    path = f"annotations[{index}]"
    if not _is_object(record):
        errors.append(f"{path}: nesne olmalı")
        return
    _required(
        record,
        (
            "annotation_id",
            "sample_id",
            "record_type",
            "annotator_id",
            "annotator_role",
            "review_state",
            "guideline_version",
            "annotated_at",
            "is_synthetic_example",
            "labels",
            "confidence",
        ),
        path,
        errors,
    )

    annotation_id = record.get("annotation_id")
    if annotation_id in annotation_ids:
        errors.append(f"{path}: tekrar eden annotation_id: {annotation_id}")
    annotation_ids.add(annotation_id)
    _check_id(annotation_id, f"{path}.annotation_id", errors)
    _check_id(record.get("sample_id"), f"{path}.sample_id", errors)
    if record.get("record_type") not in {"single_turn", "multi_turn"}:
        errors.append(f"{path}.record_type: geçersiz kayıt türü")
    annotator_id = record.get("annotator_id")
    if not isinstance(annotator_id, str) or not ANNOTATOR_ID_RE.fullmatch(annotator_id):
        errors.append(f"{path}.annotator_id: güvenli kod biçimi bekleniyor")
    annotator_role = record.get("annotator_role")
    roles = {"researcher", "expert", "adjudicator", "model_assisted", "synthetic_example"}
    if annotator_role not in roles:
        errors.append(f"{path}.annotator_role: geçersiz rol")
    review_state = record.get("review_state")
    if review_state not in {"independent", "adjudicated", "synthetic_example"}:
        errors.append(f"{path}.review_state: geçersiz durum")
    _check_version(record.get("guideline_version"), f"{path}.guideline_version", errors)
    _check_datetime(record.get("annotated_at"), f"{path}.annotated_at", errors)

    is_synthetic = record.get("is_synthetic_example")
    if not isinstance(is_synthetic, bool):
        errors.append(f"{path}.is_synthetic_example: boolean olmalı")
    if is_synthetic and (annotator_role != "synthetic_example" or review_state != "synthetic_example"):
        errors.append(f"{path}: sentetik örnek role ve review_state ile açıkça işaretlenmeli")
    if annotator_role == "synthetic_example" and not is_synthetic:
        errors.append(f"{path}: synthetic_example rolü gerçek anotasyonda kullanılamaz")
    if annotator_role == "expert" and is_synthetic:
        errors.append(f"{path}: sentetik kayıt expert anotasyonu olarak işaretlenemez")
    if bundle_type == "synthetic_examples" and not is_synthetic:
        errors.append(f"{path}: synthetic_examples bundle içinde gerçek anotasyon bulunamaz")
    if bundle_type == "annotation_set" and is_synthetic:
        errors.append(f"{path}: gerçek annotation_set içinde sentetik örnek bulunamaz")
    if review_state == "adjudicated" and annotator_role != "adjudicator":
        errors.append(f"{path}: adjudicated kayıt adjudicator rolü taşımalı")
    if is_synthetic and not str(record.get("sample_id", "")).startswith("synthetic-"):
        errors.append(f"{path}: sentetik sample_id 'synthetic-' ile başlamalı")

    labels = record.get("labels")
    if not _is_object(labels):
        errors.append(f"{path}.labels: nesne olmalı")
        labels = {}
    for dimension in ORDINAL_DIMS:
        if dimension not in labels:
            errors.append(f"{path}.labels: eksik boyut: {dimension}")
        else:
            _check_ordinal_label(labels[dimension], f"{path}.labels.{dimension}", errors)
    if "refusal_appropriateness" not in labels:
        errors.append(f"{path}.labels: eksik boyut: refusal_appropriateness")
    else:
        _check_refusal_label(labels["refusal_appropriateness"], f"{path}.labels.refusal_appropriateness", errors)

    context_label = labels.get("context_dependence", {}) if _is_object(labels) else {}
    context_status = context_label.get("status")
    if record.get("record_type") == "single_turn" and context_status != "not_applicable":
        errors.append(f"{path}: single_turn için context_dependence not_applicable olmalı")
    if record.get("record_type") == "multi_turn" and context_status == "not_applicable":
        errors.append(f"{path}: multi_turn için context_dependence not_applicable olamaz")

    overall_confidence = record.get("confidence")
    if not _is_object(overall_confidence):
        errors.append(f"{path}.confidence: nesne olmalı")
    else:
        _required(overall_confidence, ("level", "rationale_codes"), f"{path}.confidence", errors)
        if overall_confidence.get("level") not in CONFIDENCE:
            errors.append(f"{path}.confidence.level: low/medium/high olmalı")
        _check_rationale_codes(overall_confidence.get("rationale_codes"), f"{path}.confidence.rationale_codes", errors)


def validate_annotation_bundle(data: Any) -> list[str]:
    errors: list[str] = []
    if not _is_object(data):
        return ["kök değer nesne olmalı"]
    _required(data, ("annotation_schema_version", "guideline_version", "bundle_type", "annotations"), "root", errors)
    if data.get("annotation_schema_version") != "0.1.0":
        errors.append("root.annotation_schema_version: 0.1.0 bekleniyor")
    _check_version(data.get("guideline_version"), "root.guideline_version", errors)
    bundle_type = data.get("bundle_type")
    if bundle_type not in {"annotation_set", "synthetic_examples"}:
        errors.append("root.bundle_type: geçersiz bundle türü")
    annotations = data.get("annotations", [])
    if not isinstance(annotations, list):
        return errors + ["root.annotations: liste olmalı"]
    annotation_ids: set[str] = set()
    for index, record in enumerate(annotations):
        _check_record(record, index, bundle_type, annotation_ids, errors)
    return errors


def validate_file(path: str | Path) -> list[str]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return validate_annotation_bundle(json.load(handle))


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("Kullanım: validate_annotations.py <annotation-bundle.json>")
        return 2
    try:
        errors = validate_file(argv[0])
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Dosya okunamadı: {exc}")
        return 2
    if errors:
        print("Annotation bundle geçersiz:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Annotation bundle geçerli.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
