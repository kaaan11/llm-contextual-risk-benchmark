"""Deney metadata modeli."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from . import __version__
from .types import ModelSpec


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ExperimentMetadata:
    run_id: str
    experiment_id: str
    dataset_id: str
    dataset_version: str
    model: ModelSpec
    configuration: str
    context_mode: str
    created_at: str = field(default_factory=utc_now)
    runner_version: str = __version__
    generation_parameters: Mapping[str, Any] = field(default_factory=dict)
    system_instruction_ref: str | None = None
    max_samples: int | None = None
    seed: int | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    timeout_s: float | None = None
    retry_policy: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["model"] = self.model.to_dict()
        value["generation_parameters"] = dict(self.generation_parameters)
        return value


def write_metadata(metadata: ExperimentMetadata, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(metadata.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
