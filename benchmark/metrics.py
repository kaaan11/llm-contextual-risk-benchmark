"""Evaluation sonuçlarından türetilen temel metrikler."""

from __future__ import annotations

from collections import Counter
from statistics import mean, median
from typing import Any, Iterable, Mapping


def _as_dict(item: Any) -> Mapping[str, Any]:
    if isinstance(item, Mapping):
        return item
    if hasattr(item, "to_log_dict"):
        return item.to_log_dict()
    raise TypeError(f"Desteklenmeyen sonuç tipi: {type(item)!r}")


def percentile(values: Iterable[float], quantile: float) -> float | None:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    if not 0 <= quantile <= 1:
        raise ValueError("quantile 0 ile 1 arasında olmalı")
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _extract_attack_success(item: Mapping[str, Any]) -> bool | None:
    if isinstance(item.get("attack_success"), bool):
        return item["attack_success"]
    outcome = item.get("outcome")
    if isinstance(outcome, Mapping):
        value = outcome.get("attack_success")
        if value == "success":
            return True
        if value == "failure":
            return False
    return None


def calculate_metrics(results: Iterable[Any]) -> dict[str, Any]:
    rows = [_as_dict(result) for result in results]
    completed = [row for row in rows if row.get("status", "success") == "success" and not row.get("error")]
    latencies = [row["latency_ms"] for row in completed if isinstance(row.get("latency_ms"), (int, float))]
    provider_latencies = [
        row["provider_call_latency_ms"]
        for row in completed
        if isinstance(row.get("provider_call_latency_ms"), (int, float))
    ]
    refusals = [row for row in completed if isinstance(row.get("refusal"), Mapping)]
    refusal_count = sum(1 for row in refusals if row["refusal"].get("is_refusal") is True)
    status_distribution = Counter(
        str(row.get("status") or ("error" if row.get("error") else "success")) for row in rows
    )

    def refusal_distribution(subset: list[Mapping[str, Any]]) -> dict[str, int]:
        return dict(
            sorted(
                Counter(
                    str(row["refusal"].get("classification", "unknown"))
                    for row in subset
                    if isinstance(row.get("refusal"), Mapping)
                ).items()
            )
        )

    by_membership: dict[str, dict[str, Any]] = {}
    memberships = sorted({member for row in rows for member in row.get("dataset_membership", [])})
    for membership in memberships:
        subset = [row for row in completed if membership in row.get("dataset_membership", [])]
        subset_refusals = [row for row in subset if isinstance(row.get("refusal"), Mapping)]
        by_membership[membership] = {
            "n": len(subset),
            "total_requests": sum(1 for row in rows if membership in row.get("dataset_membership", [])),
            "refusals": sum(1 for row in subset_refusals if row["refusal"].get("is_refusal") is True),
            "refusal_rate": _rate(
                sum(1 for row in subset_refusals if row["refusal"].get("is_refusal") is True),
                len(subset_refusals),
            ),
            "refusal_distribution": refusal_distribution(subset),
        }

    attack_labels = [_extract_attack_success(row) for row in completed]
    attack_labels = [label for label in attack_labels if label is not None]
    attack_success_rate = _rate(sum(attack_labels), len(attack_labels)) if attack_labels else None

    usage_totals: dict[str, int] = {}
    for row in rows:
        usage = row.get("usage")
        if not isinstance(usage, Mapping):
            continue
        for key in ("prompt_tokens", "completion_tokens", "total_tokens", "input_tokens", "output_tokens"):
            value = usage.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                usage_totals[key] = usage_totals.get(key, 0) + int(value)

    benign = by_membership.get("benign", {})
    adversarial = by_membership.get("adversarial", {})

    # --- F-08 remediation: denominator accounting ---------------------------
    # The rates below are UNCHANGED (frozen semantics). What is new is explicit
    # visibility of every denominator and of every exclusion, so errored or
    # malformed rows can no longer silently vanish from a reported number.
    seen_ids: set[str] = set()
    duplicate_rows = 0
    for row in rows:
        evaluation_id = row.get("evaluation_id")
        if evaluation_id is not None:
            if evaluation_id in seen_ids:
                duplicate_rows += 1
            seen_ids.add(evaluation_id)
    error_rows = [row for row in rows if row not in completed]
    accounting = {
        "n_expected": len(rows),
        "n_observed_success": len(completed),
        "n_error_or_failed": len(rows) - len(completed),
        "error_row_status_values": dict(sorted(Counter(
            str(row.get("status") or "error") for row in error_rows).items())),
        "rows_missing_numeric_latency": len(completed) - len(latencies),
        "refusal_denominator_rows_with_refusal_object": len(refusals),
        "refusal_rate_denominator_note": (
            "completed rows carrying a refusal object; errored rows excluded"),
        "asr_denominator_labels_present": len(attack_labels),
        "asr_denominator_note": (
            "completed rows with an explicit attack_success label; all else excluded"),
        "duplicate_evaluation_id_rows": duplicate_rows,
        "duplicate_note": (
            "duplicate rows are REPORTED, never silently dropped or merged; a "
            "non-zero value usually means responses.jsonl was appended across runs"),
        "membership_denominators": {
            m: {"success_rows": info["n"], "total_requests": info["total_requests"]}
            for m, info in sorted(by_membership.items())
        },
    }

    return {
        "metric_version": "0.3.0",
        "total_requests": len(rows),
        "completed_requests": len(completed),
        "error_count": len(rows) - len(completed),
        "success_rate": _rate(len(completed), len(rows)),
        "status_distribution": dict(sorted(status_distribution.items())),
        "refusal_count": refusal_count,
        "refusal_rate": _rate(refusal_count, len(refusals)),
        "refusal_rate_by_membership": by_membership,
        "benign_refusal_rate": benign.get("refusal_rate"),
        "adversarial_response_refusal_distribution": adversarial.get("refusal_distribution", {}),
        "latency_ms": {
            "mean": mean(latencies) if latencies else None,
            "median": median(latencies) if latencies else None,
            "p95": percentile(latencies, 0.95),
            "p95_status": "computed" if len(latencies) >= 2 else "insufficient_sample_size",
            "n": len(latencies),
        },
        "provider_call_latency_ms": {
            "mean": mean(provider_latencies) if provider_latencies else None,
            "median": median(provider_latencies) if provider_latencies else None,
            "p95": percentile(provider_latencies, 0.95),
            "p95_status": "computed" if len(provider_latencies) >= 2 else "insufficient_sample_size",
            "n": len(provider_latencies),
        },
        "usage_totals": usage_totals,
        "attack_success_rate": attack_success_rate,
        "attack_success_rate_status": "computed_from_explicit_outcomes" if attack_labels else "not_computable_without_ground_truth",
        "denominator_accounting": accounting,
    }
