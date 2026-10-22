"""The CI offline profile must never contact a provider or other network service."""
import os
import socket

import pytest


@pytest.fixture(autouse=True)
def offline_network_guard(monkeypatch):
    if os.environ.get("BENCHMARK_TEST_OFFLINE") == "1":
        def blocked(*args, **kwargs):
            raise AssertionError("Network access is disabled in the offline test profile")
        monkeypatch.setattr(socket.socket, "connect", blocked)
        monkeypatch.setattr(socket.socket, "connect_ex", blocked)
        monkeypatch.setattr(socket, "create_connection", blocked)
