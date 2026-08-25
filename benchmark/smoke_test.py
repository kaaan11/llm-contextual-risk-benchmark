"""Phase 6A gerçek-model smoke test preflight ve sınırlı çalıştırıcısı.

Bu modül varsayılan olarak ağa çıkmaz. Gerçek sağlayıcı çağrısı yalnızca ``--live``
ile ve gerekli model sürümü/credential ortam değişkenleri mevcutsa yapılır.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping

from .adapters import AnthropicAdapter, OpenAIAdapter, OpenWeightAdapter
from .errors import AdapterConfigurationError, DatasetLoadError, sanitize_error_message
from .loader import DatasetLoader
from .logging import JsonlResponseLogger
from .metadata import ExperimentMetadata, utc_now
from .metrics import calculate_metrics
from .retry import RetryPolicy
from .runner import EvaluationRunner
from .types import ModelSpec


PROVIDER_ORDER = ("openai", "anthropic", "open_weight")
MAX_SMOKE_SAMPLES = 20


class SmokeConfigError(ValueError):
    """Smoke test yapılandırması veya manifesti geçersiz."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SmokeConfigError(f"JSON okunamadı: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SmokeConfigError(f"JSON nesne olmalı: {path}")
    return value


def _resolve_path(value: str, *, base_dir: Path) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else base_dir / candidate


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_smoke_config(path: str | Path) -> tuple[dict[str, Any], Path]:
    config_path = Path(path).resolve()
    config = _read_json(config_path)
    required = ("experiment_id", "dataset_path", "manifest_path", "output_root", "providers", "retry")
    missing = [key for key in required if key not in config]
    if missing:
        raise SmokeConfigError(f"Eksik config alanları: {', '.join(missing)}")
    max_samples = config.get("max_samples", MAX_SMOKE_SAMPLES)
    if not isinstance(max_samples, int) or max_samples < 1 or max_samples > MAX_SMOKE_SAMPLES:
        raise SmokeConfigError(f"max_samples 1 ile {MAX_SMOKE_SAMPLES} arasında olmalı")
    if not isinstance(config["providers"], Mapping):
        raise SmokeConfigError("providers nesne olmalı")
    try:
        retry = RetryPolicy(**dict(config["retry"]))
    except (TypeError, ValueError) as exc:
        raise SmokeConfigError(f"retry yapılandırması geçersiz: {exc}") from exc
    config["max_samples"] = max_samples
    config["retry"] = retry.to_dict()
    return config, config_path


def load_and_validate_manifest(
    config: Mapping[str, Any],
    config_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    dataset_path = _resolve_path(str(config["dataset_path"]), base_dir=config_path.parent.parent)
    manifest_path = _resolve_path(str(config["manifest_path"]), base_dir=config_path.parent.parent)
    manifest = _read_json(manifest_path)
    sample_ids = manifest.get("sample_ids")
    if not isinstance(sample_ids, list) or not all(isinstance(item, str) and item for item in sample_ids):
        raise SmokeConfigError("manifest.sample_ids benzersiz olmayan/boş olmayan string listesi olmalı")
    if len(sample_ids) != len(set(sample_ids)):
        raise SmokeConfigError("Smoke manifestinde duplicate sample_id var")
    if len(sample_ids) > MAX_SMOKE_SAMPLES:
        raise SmokeConfigError(f"Smoke manifesti en fazla {MAX_SMOKE_SAMPLES} kayıt içerebilir")
    if manifest.get("sample_count") != len(sample_ids):
        raise SmokeConfigError("manifest.sample_count sample_ids uzunluğuyla eşleşmiyor")
    if manifest.get("dataset_id") != config.get("expected_dataset_id", "llm-security-usability-pilot"):
        raise SmokeConfigError("Smoke manifest dataset_id beklenen dataset ile eşleşmiyor")
    if manifest.get("dataset_version") != config.get("expected_dataset_version", "0.1.0"):
        raise SmokeConfigError("Smoke manifest dataset_version beklenen dataset ile eşleşmiyor")
    strata = manifest.get("strata")
    if not isinstance(strata, Mapping) or not strata:
        raise SmokeConfigError("Smoke manifestinde strata bulunmalı")
    stratum_ids: list[str] = []
    for name, value in strata.items():
        if not isinstance(value, Mapping):
            raise SmokeConfigError(f"strata.{name} nesne olmalı")
        ids = value.get("sample_ids")
        if not isinstance(ids, list) or value.get("count") != len(ids):
            raise SmokeConfigError(f"strata.{name} count/sample_ids eşleşmiyor")
        if stratum_ids and set(stratum_ids).intersection(ids):
            raise SmokeConfigError("Strata'lar arasında duplicate sample_id var")
        stratum_ids.extend(ids)
    if stratum_ids != sample_ids:
        raise SmokeConfigError("Manifest sample_ids strata sırasıyla birebir eşleşmeli")

    bundle = DatasetLoader().load(dataset_path, sample_ids=sample_ids)
    records_by_id = {record["sample_id"]: record for record in bundle.records}
    if set(records_by_id) != set(sample_ids):
        missing = sorted(set(sample_ids) - set(records_by_id))
        raise SmokeConfigError(f"Smoke manifestindeki kayıtlar dataset içinde yok: {missing}")
    if bundle.dataset_id != manifest["dataset_id"] or bundle.dataset_version != manifest["dataset_version"]:
        raise SmokeConfigError("Dataset kimliği/sürümü smoke manifestiyle eşleşmiyor")
    for name, value in strata.items():
        membership = value.get("membership", name)
        for sample_id in value["sample_ids"]:
            if membership not in records_by_id[sample_id].get("dataset_membership", []):
                raise SmokeConfigError(f"{sample_id}: {membership} stratum üyeliği yok")
    return manifest, records_by_id, dataset_path, manifest_path


def estimate_cost(config: Mapping[str, Any], records_by_id: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    estimate_config = config.get("cost_estimate", {})
    divisor = estimate_config.get("input_token_divisor", 4)
    output_per_sample = estimate_config.get("estimated_output_tokens_per_sample", config.get("max_output_tokens", 0))
    if not isinstance(divisor, (int, float)) or divisor <= 0:
        raise SmokeConfigError("cost_estimate.input_token_divisor pozitif olmalı")
    if not isinstance(output_per_sample, int) or output_per_sample < 0:
        raise SmokeConfigError("Tahmini output token sayısı negatif olamaz")
    input_characters = 0
    for record in records_by_id.values():
        for turn in record.get("turns", []):
            content = turn.get("content", {})
            if isinstance(content, Mapping) and isinstance(content.get("text"), str):
                input_characters += len(content["text"])
    estimated_input_tokens = math.ceil(input_characters / divisor)
    estimated_output_tokens = len(records_by_id) * output_per_sample
    input_price = estimate_config.get("input_price_usd_per_million_tokens")
    output_price = estimate_config.get("output_price_usd_per_million_tokens")
    cost = None
    pricing_status = "pricing_not_configured"
    if isinstance(input_price, (int, float)) and isinstance(output_price, (int, float)):
        cost = (estimated_input_tokens * input_price + estimated_output_tokens * output_price) / 1_000_000
        pricing_status = "estimated_from_configured_prices"
    return {
        "input_characters": input_characters,
        "estimated_input_tokens": estimated_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "estimated_total_tokens": estimated_input_tokens + estimated_output_tokens,
        "estimated_cost_usd": cost,
        "status": pricing_status,
        "note": "Bu üst sınır/tahmindir; gerçek sağlayıcı token kullanımı değildir.",
    }


def provider_preflight(name: str, provider_config: Mapping[str, Any], environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = environ or os.environ
    enabled = provider_config.get("enabled", True) is True
    credential_env = str(provider_config.get("credential_env", ""))
    model_env = str(provider_config.get("model_env", ""))
    version_env = str(provider_config.get("model_version_env", ""))
    endpoint_env = str(provider_config.get("endpoint_env", provider_config.get("base_url_env", "")))
    missing: list[str] = []
    if enabled and not model_env:
        missing.append("model_env config")
    if enabled and not version_env:
        missing.append("model_version_env config")
    if enabled and not env.get(model_env):
        missing.append(model_env)
    if enabled and not env.get(version_env):
        missing.append(version_env)
    if enabled and not provider_config.get("credential_optional", False) and not env.get(credential_env):
        missing.append(credential_env)
    if enabled and name == "open_weight" and not env.get(endpoint_env):
        missing.append(endpoint_env)
    return {
        "provider": name,
        "enabled": enabled,
        "credential_env": credential_env,
        "model_env": model_env,
        "model_version_env": version_env,
        "endpoint_env": endpoint_env or None,
        "missing_environment": sorted(set(missing)),
        "configured": enabled and not missing,
        "model": env.get(model_env) if env.get(model_env) else None,
        "model_version": env.get(version_env) if env.get(version_env) else None,
    }


def _make_adapter(name: str, provider_config: Mapping[str, Any], timeout_s: float):
    credential_env = str(provider_config["credential_env"])
    base_url_env = str(provider_config.get("base_url_env", ""))
    endpoint_env = str(provider_config.get("endpoint_env", base_url_env))
    if name == "openai":
        return OpenAIAdapter(
            api_key_env=credential_env,
            endpoint=os.environ.get(base_url_env) if base_url_env else None,
            timeout_s=timeout_s,
        )
    if name == "anthropic":
        return AnthropicAdapter(
            api_key_env=credential_env,
            endpoint=os.environ.get(base_url_env) if base_url_env else None,
            timeout_s=timeout_s,
        )
    if name == "open_weight":
        return OpenWeightAdapter(
            api_key_env=credential_env,
            endpoint=os.environ.get(endpoint_env),
            timeout_s=timeout_s,
        )
    raise SmokeConfigError(f"Desteklenmeyen provider: {name}")


def run_smoke(config_path: str | Path, *, live: bool = False) -> dict[str, Any]:
    config, resolved_config_path = load_smoke_config(config_path)
    manifest, records_by_id, dataset_path, manifest_path = load_and_validate_manifest(config, resolved_config_path)
    dataset_sha256_before = _sha256(dataset_path)
    manifest_sha256 = _sha256(manifest_path)
    if len(records_by_id) > config["max_samples"]:
        raise SmokeConfigError("Smoke manifesti config.max_samples sınırını aşıyor")
    source_root = resolved_config_path.parent.parent
    output_root = _resolve_path(str(config["output_root"]), base_dir=source_root) / str(config["experiment_id"])
    output_root.mkdir(parents=True, exist_ok=True)
    cases_bundle = DatasetLoader().load(dataset_path, sample_ids=manifest["sample_ids"])
    cases_by_id = {case.sample_id: case for case in DatasetLoader.to_cases(cases_bundle)}
    cases = tuple(cases_by_id[sample_id] for sample_id in manifest["sample_ids"])
    preflights = [
        provider_preflight(name, config["providers"].get(name, {"enabled": False}))
        for name in PROVIDER_ORDER
    ]
    cost = estimate_cost(config, records_by_id)
    provider_results: list[dict[str, Any]] = []
    retry_policy = RetryPolicy(**dict(config["retry"]))
    generation_parameters = {
        "temperature": config.get("temperature", 0.0),
        "max_output_tokens": config.get("max_output_tokens", 256),
    }
    for preflight in preflights:
        name = preflight["provider"]
        if not preflight["enabled"]:
            provider_results.append({**preflight, "status": "disabled", "sample_count": 0})
            continue
        if not preflight["configured"]:
            provider_results.append({
                **preflight,
                "status": "not_evaluated",
                "reason": "required model/version/credential/endpoint environment variable is missing",
                "sample_count": 0,
            })
            continue
        if not live:
            provider_results.append({
                **preflight,
                "status": "not_evaluated",
                "reason": "live execution requires explicit --live",
                "sample_count": 0,
            })
            continue
        model = ModelSpec(provider=name, name=preflight["model"], version=preflight["model_version"])
        provider_dir = output_root / name
        metadata = ExperimentMetadata(
            run_id=f"{config['experiment_id']}-{name}-001",
            experiment_id=str(config["experiment_id"]),
            dataset_id=cases_bundle.dataset_id,
            dataset_version=cases_bundle.dataset_version,
            model=model,
            configuration=str(config.get("configuration", "phase6a_baseline")),
            context_mode=str(config.get("context_mode", "conversation_context")),
            generation_parameters=generation_parameters,
            system_instruction_ref=config.get("system_instruction_ref"),
            max_samples=len(cases),
            seed=config.get("seed"),
            temperature=config.get("temperature"),
            max_output_tokens=config.get("max_output_tokens"),
            timeout_s=config.get("timeout_s"),
            retry_policy=retry_policy.to_dict(),
        )
        logger = JsonlResponseLogger(
            provider_dir / "responses.jsonl",
            include_response_text=bool(config.get("response_logging", {}).get("include_response_text", True)),
            append_ok=True,  # local scratch; explicit opt-in (F-08/F-24 guard)
        )
        started = perf_counter()
        try:
            runner = EvaluationRunner(
                _make_adapter(name, config["providers"][name], float(config.get("timeout_s", 30.0))),
                metadata,
                logger,
                retry_policy=retry_policy,
                enforce_frozen_config=live,  # F-10: canonical (live) runs validate the freeze list
            )
            results = runner.run(cases)
            artifacts = runner.write_artifacts(provider_dir, results)
            provider_results.append({
                **preflight,
                "status": "completed",
                "sample_count": len(results),
                "completed_requests": sum(result.status == "success" for result in results),
                "error_count": sum(result.status != "success" for result in results),
                "wall_clock_ms": (perf_counter() - started) * 1000.0,
                "artifacts": {key: str(value.relative_to(output_root)) for key, value in artifacts.items()},
                "metrics": calculate_metrics(results),
            })
        except (AdapterConfigurationError, DatasetLoadError, OSError, ValueError) as exc:
            provider_results.append({
                **preflight,
                "status": "error",
                "sample_count": 0,
                "wall_clock_ms": (perf_counter() - started) * 1000.0,
                "error_type": type(exc).__name__,
                "error": sanitize_error_message(str(exc), limit=300),
            })
        finally:
            logger.close()

    summary = {
        "phase": "6A",
        "summary_version": "0.1.0",
        "created_at": utc_now(),
        "config_path": str(resolved_config_path),
        "experiment_id": config["experiment_id"],
        "live_execution_requested": live,
        "dataset": {
            "dataset_id": manifest["dataset_id"],
            "dataset_version": manifest["dataset_version"],
            "sample_count": len(manifest["sample_ids"]),
            "sample_ids": manifest["sample_ids"],
            "strata_counts": {name: value["count"] for name, value in manifest["strata"].items()},
            "source_sha256_before": dataset_sha256_before,
            "source_sha256_after": _sha256(dataset_path),
            "manifest_sha256": manifest_sha256,
            "source_mutated_by_runner": dataset_sha256_before != _sha256(dataset_path),
        },
        "cost_estimate": cost,
        "providers": provider_results,
        "safety": {
            "full_dataset_evaluation_performed": False,
            "real_model_evaluation_performed": any(item["status"] == "completed" for item in provider_results),
            "raw_responses_are_local_only": True,
            "api_keys_written_to_artifacts": False,
        },
    }
    summary_path = output_root / "summary.json"
    summary["summary_path"] = str(summary_path)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 6A bounded real-model smoke test")
    parser.add_argument("--config", type=Path, default=Path("configs/phase6a_smoke.json"))
    parser.add_argument("--live", action="store_true", help="Configured providers için ağ çağrısını etkinleştir")
    args = parser.parse_args()
    summary = run_smoke(args.config, live=args.live)
    print(json.dumps({
        "phase": summary["phase"],
        "sample_count": summary["dataset"]["sample_count"],
        "live_execution_requested": summary["live_execution_requested"],
        "providers": [
            {"provider": item["provider"], "status": item["status"], "missing_environment": item.get("missing_environment", [])}
            for item in summary["providers"]
        ],
        "summary_path": summary["summary_path"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
