#!/usr/bin/env python3
"""Phase 8 — End-to-End Mock Dry-Run Test Harness.

Executes all 50 research items (171 stimulus conditions) against a local MockAdapter,
verifying complete pipeline integrity, retry handling, refusal detection,
pure latency calculation, and assistant stance stratification before any live API call.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmark.adapters.mock import MockAdapter
from benchmark.logging import InMemoryResponseLogger, JsonlResponseLogger
from benchmark.metadata import ExperimentMetadata
from benchmark.metrics import calculate_metrics
from benchmark.refusal import RefusalDetector
from benchmark.retry import RetryPolicy
from benchmark.runner import EvaluationRunner
from benchmark.types import EvaluationCase, ModelSpec

STIMULI_FILE = ROOT / "dataset" / "pilot" / "multiturn" / "stimulus_dataset_v1.json"
CONFIG_FILE = ROOT / "configs" / "phase8_eval_plan.json"
DEFAULT_OUTPUT_DIR = ROOT / "benchmark" / "runs" / "phase8-mock-dryrun"


def build_cases_from_stimuli(stimuli_path: Path = STIMULI_FILE) -> list[EvaluationCase]:
    data = json.loads(stimuli_path.read_text(encoding="utf-8"))
    cases = []

    for r in data.get("records", []):
        rid = r["research_item_id"]
        cat = r.get("category", "dual_use_nonnull")

        for cond_name, cdata in r.get("conditions", {}).items():
            code = cdata.get("condition_code", "A")
            sample_id = f"{rid}_{code}"

            case = EvaluationCase(
                sample_id=sample_id,
                record_type="multi_turn",
                dataset_membership=(cat, f"condition_{code}"),
                turns=tuple(cdata.get("turns", [])),
                task_metadata={
                    "research_item_id": rid,
                    "condition_code": code,
                    "condition_name": cond_name,
                    "category": cat,
                },
            )
            cases.append(case)

    return cases


def build_synthetic_responses(cases: list[EvaluationCase]) -> dict[str, str]:
    responses = {}
    for c in cases:
        code = c.task_metadata.get("condition_code")
        cat = c.task_metadata.get("category")

        # Synthetic policy:
        # C (incriminating) in high-risk or dual-use produces refusal signals
        if code == "C" and (cat in {"null_highrisk", "dual_use_nonnull"}):
            responses[c.sample_id] = (
                "I cannot fulfill this request as I cannot assist with actions that "
                "could compromise security or violate policy."
            )
        elif code == "B":
            responses[c.sample_id] = (
                "Here is the detailed legitimate documentation and configuration guidance "
                "to address your compliance requirement."
            )
        else:
            responses[c.sample_id] = (
                "Here is general educational and architectural information regarding your prompt."
            )
    return responses


def run_phase8_dryrun(output_dir: Path = DEFAULT_OUTPUT_DIR, limit: int | None = None) -> dict:
    cases = build_cases_from_stimuli()
    if limit is not None:
        cases = cases[:limit]

    plan = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}
    gen_params = plan.get("generation_parameters", {"temperature": 0.0, "max_tokens": 1024, "seed": 42})

    responses_map = build_synthetic_responses(cases)
    adapter = MockAdapter(responses_map, default_response="Default mock response.")

    output_dir.mkdir(parents=True, exist_ok=True)
    logger = JsonlResponseLogger(output_dir / "responses.jsonl")

    metadata = ExperimentMetadata(
        run_id="phase8-mock-dryrun-001",
        experiment_id="phase8-dryrun",
        dataset_id="llm-ctx-pilot-stimuli-en",
        dataset_version="1.0.0",
        model=ModelSpec(provider="mock", name="synthetic-evaluator", version="1.0.0"),
        configuration="frozen-protocol-v1.0.2",
        context_mode="conversation_context",
        max_samples=limit,
        generation_parameters=gen_params,
    )

    runner = EvaluationRunner(
        adapter,
        metadata,
        logger,
        refusal_detector=RefusalDetector(),
        retry_policy=RetryPolicy(max_attempts=2, initial_backoff_s=0.01),
    )

    print(f"=== Phase 8 Mock Dry-Run Başlatılıyor ===")
    print(f"Toplam Test Koşulu: {len(cases)} (Hedef: 171 koşul)")
    print(f"Çıktı Dizini: {output_dir}\n")

    results = runner.run(cases)
    artifacts = runner.write_artifacts(output_dir, results)

    metrics = json.loads(artifacts["metrics"].read_text(encoding="utf-8"))

    print("=== Dry-Run Başarıyla Tamamlandı! ===")
    print(f"• Toplam Çağrı: {metrics['total_requests']}")
    print(f"• Başarılı Çağrı: {metrics['completed_requests']}")
    print(f"• Toplam Ret Sayısı: {metrics['refusal_count']} (Oran: %{metrics['refusal_rate'] * 100:.1f})")

    # Tabakalı analiz çıktısı
    strata = metrics.get("stratified_by_assistant_stance", {})
    print("\n--- ASİSTAN TURU TABAKALI ANALİZ ÇIKTISI (C3 STRATIFICATION) ---")
    for s_name, s_data in strata.items():
        print(f" • {s_name}: n={s_data['n']}, ret={s_data['refusals']}, oran=%{s_data['refusal_rate'] * 100:.1f}")

    print("\n--- GECİKME AYRIŞTIRMASI ---")
    print(f" • Saf Model Gecikmesi (Mean): {metrics['pure_inference_latency_ms']['mean']:.2f} ms")
    print(f" • Retry Gecikme Yükü (Total): {metrics['retry_overhead_ms']['total_ms']:.2f} ms")

    print(f"\nÜretilen Artefaktlar:\n - {artifacts['metadata']}\n - {artifacts['metrics']}\n - {output_dir / 'responses.jsonl'}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 8 Mock Dry-Run Harness")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of condition records")
    args = parser.parse_args()

    run_phase8_dryrun(args.output_dir, limit=args.limit)


if __name__ == "__main__":
    main()
