"""Küçük, tamamen mock tabanlı benchmark dry-run."""

from __future__ import annotations

import argparse
from pathlib import Path

from .adapters import MockAdapter
from .loader import DatasetLoader
from .logging import JsonlResponseLogger
from .metadata import ExperimentMetadata
from .runner import EvaluationRunner
from .types import ModelSpec


def run_dry_run(dataset_path: str | Path, output_dir: str | Path, limit: int = 3) -> list:
    sample_ids = ["benign-001", "adversarial-001", "multi-turn-001"][:limit]
    bundle = DatasetLoader().load(dataset_path, sample_ids=sample_ids)
    cases = DatasetLoader.to_cases(bundle)
    responses = {
        "benign-001": "Elbette. Güvenli bir tasarım ve test planı önerebilirim.",
        "benign-002": "Varsayımları ve hata durumlarını açıkça belirterek ilerleyebiliriz.",
        "adversarial-001": "Bu isteğe yardımcı olamam; güvenli bir savunma ve risk değerlendirme alternatifi sunabilirim.",
    }
    adapter = MockAdapter(responses, default_response="Bu mock dry-run yanıtıdır.", latency_s=0.001)
    metadata = ExperimentMetadata(
        run_id="mock-dry-run-001",
        experiment_id="phase5-mock-dry-run",
        dataset_id=bundle.dataset_id,
        dataset_version=bundle.dataset_version,
        model=ModelSpec(provider="mock", name="mock-safety-model", version="0.1.0"),
        configuration="baseline",
        context_mode="conversation_context",
        max_samples=limit,
        seed=20260814,
    )
    output = Path(output_dir)
    # Local scratch contract: dry-run output may be re-run deliberately;
    # append is an explicit opt-in (F-08/F-24 duplicate-row guard).
    with JsonlResponseLogger(output / "responses.jsonl", append_ok=True) as logger:
        runner = EvaluationRunner(adapter, metadata, logger)
        results = runner.run(cases)
        runner.write_artifacts(output, results)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Mock benchmark dry-run")
    parser.add_argument("--dataset", type=Path, default=Path("dataset/pilot/pilot_dataset.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("benchmark/runs/mock-dry-run"))
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    results = run_dry_run(args.dataset, args.output_dir, limit=args.limit)
    print(f"Mock dry-run tamamlandı: {len(results)} kayıt")
    print(f"Çıktı dizini: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
