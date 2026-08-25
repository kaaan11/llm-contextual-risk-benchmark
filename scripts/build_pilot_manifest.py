"""Phase 6B reproducible public-benchmark manifest builder.

Güvenlik gereği final manifest üretimi audit approval olmadan reddedilir. Bu
script şu anda metadata/audit durumunu kontrol etmek için de kullanılabilir;
harici datasetleri kendiliğinden repository'ye kopyalamaz.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SAMPLING_REPORT = ROOT / "results" / "dataset_audit" / "sampling_report.json"
DEFAULT_OVERLAP_REPORT = ROOT / "results" / "dataset_audit" / "overlap_report.json"
DEFAULT_VALIDATION_REPORT = ROOT / "results" / "dataset_audit" / "validation_report.json"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ManifestBlockedError(RuntimeError):
    """Final manifest için metodolojik/lisans approval eksik."""


def load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    value = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON nesne olmalı: {source}")
    return value


def normalized_text(value: str) -> str:
    """Overlap audit için açıklanabilir, kayıpsız olmayan normalize edilmiş metin."""

    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(value.split())


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def audit_gate(
    *,
    sampling_report: Mapping[str, Any],
    overlap_report: Mapping[str, Any],
    validation_report: Mapping[str, Any],
    approve_manifest_build: bool,
) -> None:
    if sampling_report.get("status") != "approved_for_manifest":
        raise ManifestBlockedError(
            "Sampling raporu approved_for_manifest değil; final manifest oluşturulmadı."
        )
    if overlap_report.get("status") != "approved_for_manifest":
        raise ManifestBlockedError(
            "Overlap raporu approved_for_manifest değil; final manifest oluşturulmadı."
        )
    if validation_report.get("status") != "approved_for_manifest":
        raise ManifestBlockedError(
            "Validation raporu approved_for_manifest değil; final manifest oluşturulmadı."
        )
    if not approve_manifest_build:
        raise ManifestBlockedError(
            "Final manifest için ayrıca --approve-manifest-build açıkça verilmelidir."
        )


def _validate_candidate(candidate: Mapping[str, Any]) -> None:
    required = (
        "source_dataset",
        "source_sample_id",
        "source_version",
        "source_url",
        "original_label",
        "mapped_label",
        "taxonomy_category",
        "split",
        "selection_reason",
        "license",
        "redistribution_status",
    )
    missing = [field for field in required if not candidate.get(field)]
    if missing:
        raise ValueError(f"Candidate provenance eksik: {missing}")
    if not isinstance(candidate["source_sample_id"], str):
        raise ValueError("source_sample_id türetilmiş locator olsa bile açık string olmalı")


def _select_stratified(
    candidates: Iterable[Mapping[str, Any]],
    *,
    targets: Mapping[str, int],
    seed: int,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        _validate_candidate(candidate)
        source = str(candidate["source_dataset"])
        grouped[source].append(dict(candidate))
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    seen_source_ids: set[tuple[str, str]] = set()
    seen_exact: set[str] = set()
    seen_normalized: set[str] = set()
    for source in sorted(targets):
        pool = sorted(
            grouped.get(source, []),
            key=lambda item: (str(item.get("sampling_cell", "")), str(item["source_sample_id"])),
        )
        target = int(targets[source])
        if len(pool) < target:
            raise ValueError(f"{source}: hedef {target}, uygun aday {len(pool)}")
        rng.shuffle(pool)
        chosen = []
        for candidate in pool:
            source_id_key = (source, str(candidate["source_sample_id"]))
            text = str(candidate.get("text", candidate.get("prompt", candidate.get("goal", ""))))
            exact_hash = sha256_text(text)
            normalized_hash = sha256_text(normalized_text(text))
            if source_id_key in seen_source_ids or exact_hash in seen_exact or normalized_hash in seen_normalized:
                continue
            chosen.append(candidate)
            seen_source_ids.add(source_id_key)
            seen_exact.add(exact_hash)
            seen_normalized.add(normalized_hash)
            if len(chosen) == target:
                break
        if len(chosen) != target:
            raise ValueError(f"{source}: duplicate dışlama sonrası hedef karşılanamadı")
        selected.extend(chosen)
    return selected


def build_manifest(
    candidates: Iterable[Mapping[str, Any]],
    *,
    targets: Mapping[str, int],
    seed: int,
    sampling_report: Mapping[str, Any],
    overlap_report: Mapping[str, Any],
    validation_report: Mapping[str, Any],
    approve_manifest_build: bool,
) -> dict[str, Any]:
    audit_gate(
        sampling_report=sampling_report,
        overlap_report=overlap_report,
        validation_report=validation_report,
        approve_manifest_build=approve_manifest_build,
    )
    selected = _select_stratified(candidates, targets=targets, seed=seed)
    records = []
    for index, candidate in enumerate(selected, start=1):
        source = str(candidate["source_dataset"]).upper().replace("-", "_")
        records.append({
            "sample_id": f"PILOT-{source}-{index:03d}",
            **candidate,
        })
    return {
        "manifest_version": "0.1.0",
        "dataset_id": "llm-security-usability-public-pilot",
        "dataset_profile": "PILOT_EVALUATION",
        "sampling_seed": seed,
        "targets": dict(targets),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 6B public benchmark manifest builder")
    parser.add_argument("--audit-only", action="store_true", help="Yalnızca audit gate durumunu göster")
    parser.add_argument("--approve-manifest-build", action="store_true")
    parser.add_argument("--sampling-report", type=Path, default=DEFAULT_SAMPLING_REPORT)
    parser.add_argument("--overlap-report", type=Path, default=DEFAULT_OVERLAP_REPORT)
    parser.add_argument("--validation-report", type=Path, default=DEFAULT_VALIDATION_REPORT)
    args = parser.parse_args()
    sampling = load_json(args.sampling_report)
    overlap = load_json(args.overlap_report)
    validation = load_json(args.validation_report)
    status = {
        "sampling_status": sampling.get("status"),
        "overlap_status": overlap.get("status"),
        "validation_status": validation.get("status"),
        "final_manifest_created": False,
    }
    if args.audit_only:
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0
    audit_gate(
        sampling_report=sampling,
        overlap_report=overlap,
        validation_report=validation,
        approve_manifest_build=args.approve_manifest_build,
    )
    raise ManifestBlockedError("Aday kaynağı CLI ile verilmeden manifest oluşturulamaz.")


if __name__ == "__main__":
    raise SystemExit(main())
