"""F-10 remediation — pre-evaluation frozen-configuration preflight.

The preregistration (§16) requires provider, exact model identifier and version,
sampling parameters, retry/timeout policy, repetition count and dataset identity
to be fixed and recorded BEFORE any canonical evaluation run. Until now that
requirement was procedural only: a runner constructed from an under-specified
metadata object silently fell back to provider defaults (e.g. Anthropic's hidden
``max_tokens=1024``) or sent requests with no sampling parameters at all.

This module makes the freeze list enforceable:

* ``assert_run_config_frozen(metadata)`` raises :class:`PreflightError` unless
  every contract-required field is present and sane, and returns a stable
  ``run_config_digest`` (sha256 over the canonical JSON of the frozen fields).
* ``EvaluationRunner(..., enforce_frozen_config=True)`` calls it before the first
  case and records the digest in the experiment metadata artifact.
* Adapters receive ``require_explicit_max_tokens`` from the runner in strict mode,
  so no adapter can substitute an undocumented default for a missing parameter.

Honesty note: ``ModelSpec.version`` is METADATA ONLY — none of the current
adapters transmit a model-version field to a provider. The preflight records
this explicitly rather than implying the provider received one.

Performs no network access and calls no model API.
"""

from __future__ import annotations

import hashlib
import json

from .errors import BenchmarkError
from .metadata import ExperimentMetadata


class PreflightError(BenchmarkError):
    """Kurallı değerlendirme öncesi donmuş-yapılandırma doğrulaması başarısız."""


REQUIRED_GENERATION_PARAMETERS = ("temperature", "top_p", "max_output_tokens")


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def assert_run_config_frozen(metadata: ExperimentMetadata) -> str:
    """Validate the freeze list; return the run-config digest.

    Raises PreflightError on any missing/invalid frozen field. Never mutates the
    metadata and never contacts any provider.
    """
    problems: list[str] = []
    model = metadata.model
    if not getattr(model, "provider", None):
        problems.append("model.provider is required")
    if not getattr(model, "name", None):
        problems.append("model.name (exact provider identifier) is required")
    if not getattr(model, "version", None):
        problems.append("model.version is required (recorded metadata; providers "
                        "receive only model.name)")

    params = dict(metadata.generation_parameters or {})
    for key in REQUIRED_GENERATION_PARAMETERS:
        if key not in params:
            problems.append(f"generation_parameters.{key} is required and must be "
                            f"frozen before evaluation")
        elif not _is_number(params[key]):
            problems.append(f"generation_parameters.{key} must be numeric")
    if "temperature" in params and _is_number(params["temperature"]) \
            and not 0 <= params["temperature"] <= 2:
        problems.append("generation_parameters.temperature outside [0, 2]")
    if "top_p" in params and _is_number(params["top_p"]) \
            and not 0 < params["top_p"] <= 1:
        problems.append("generation_parameters.top_p outside (0, 1]")
    if "max_output_tokens" in params:
        limit = params["max_output_tokens"]
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            problems.append("generation_parameters.max_output_tokens must be a positive integer")

    if not metadata.retry_policy:
        problems.append("retry_policy must be recorded before evaluation")
    timeout = getattr(metadata, "timeout_s", None)
    if not _is_number(timeout) or timeout <= 0:
        problems.append("timeout_s must be a positive number")
    if not getattr(metadata, "dataset_id", None):
        problems.append("dataset_id is required")
    if not getattr(metadata, "dataset_version", None):
        problems.append("dataset_version is required")

    if problems:
        raise PreflightError(
            "frozen run configuration incomplete — refusing to start evaluation:\n  - "
            + "\n  - ".join(problems))

    frozen_view = {
        "provider": model.provider,
        "model_name": model.name,
        "model_version_recorded": model.version,
        "model_version_transmitted_to_provider": False,
        "generation_parameters": {k: params[k] for k in sorted(params)},
        "retry_policy": metadata.retry_policy,
        "timeout_s": metadata.timeout_s,
        "dataset_id": metadata.dataset_id,
        "dataset_version": metadata.dataset_version,
        "context_mode": metadata.context_mode,
        "max_samples": metadata.max_samples,
    }
    encoded = json.dumps(frozen_view, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
