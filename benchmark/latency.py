"""Duvar saati latency ölçümü."""

from __future__ import annotations

from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


def measure_call(function: Callable[[], T]) -> tuple[T, float]:
    started = perf_counter()
    value = function()
    elapsed_ms = (perf_counter() - started) * 1000.0
    return value, elapsed_ms
