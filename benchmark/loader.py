"""Canonical dataset ve JSONL kayıt yükleyicisi."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from dataset.validate import validate_dataset

from .errors import DatasetLoadError
from .types import EvaluationCase


@dataclass(frozen=True)
class DatasetBundle:
    manifest: dict[str, Any]
    records: tuple[dict[str, Any], ...]

    @property
    def dataset_id(self) -> str:
        return str(self.manifest["dataset_id"])

    @property
    def dataset_version(self) -> str:
        return str(self.manifest["dataset_version"])


class DatasetLoader:
    """Dataset manifesti yükler ve runner için EvaluationCase üretir."""

    def load(
        self,
        path: str | Path,
        *,
        limit: int | None = None,
        sample_ids: Iterable[str] | None = None,
        memberships: Iterable[str] | None = None,
    ) -> DatasetBundle:
        source = Path(path)
        try:
            with source.open("r", encoding="utf-8") as handle:
                if source.suffix.lower() == ".jsonl":
                    records = [json.loads(line) for line in handle if line.strip()]
                    manifest: dict[str, Any] = {
                        "schema_version": "0.1.0",
                        "dataset_id": source.stem,
                        "dataset_version": "0.0.0",
                        "release_profile": "private",
                        "records": records,
                        "evaluation_runs": [],
                        "analysis_runs": [],
                    }
                else:
                    manifest = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise DatasetLoadError(f"Dataset okunamadı: {source}: {exc}") from exc

        errors = validate_dataset(manifest)
        if errors:
            raise DatasetLoadError("Dataset doğrulaması başarısız:\n" + "\n".join(errors[:20]))

        records = list(manifest["records"])
        requested_ids = set(sample_ids or ())
        requested_memberships = set(memberships or ())
        if requested_ids:
            records = [record for record in records if record["sample_id"] in requested_ids]
        if requested_memberships:
            records = [
                record
                for record in records
                if requested_memberships.intersection(record["dataset_membership"])
            ]
        if limit is not None:
            if limit < 0:
                raise DatasetLoadError("limit negatif olamaz")
            records = records[:limit]

        filtered_manifest = dict(manifest)
        filtered_manifest["records"] = records
        return DatasetBundle(filtered_manifest, tuple(records))

    @staticmethod
    def to_cases(bundle: DatasetBundle) -> tuple[EvaluationCase, ...]:
        return tuple(
            EvaluationCase(
                sample_id=record["sample_id"],
                record_type=record["record_type"],
                dataset_membership=tuple(record["dataset_membership"]),
                turns=tuple(record["turns"]),
                task_metadata=record.get("task_metadata", {}),
            )
            for record in bundle.records
        )
