"""Endpoint trust and scheme policy enforcement before credential handling."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit

from ..errors import AdapterConfigurationError


def is_loopback_host(hostname: str | None) -> bool:
    """Return True only if hostname is strictly localhost, any 127.0.0.0/8 address, or ::1."""
    if not hostname:
        return False
    host = hostname.strip().lower()
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]
    if host == "localhost":
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv4Address):
        return ip in ipaddress.IPv4Network("127.0.0.0/8")
    if isinstance(ip, ipaddress.IPv6Address):
        return ip == ipaddress.IPv6Address("::1")
    return False


def check_endpoint(url: str, *, allow_plaintext_loopback: bool = False) -> None:
    """Validate endpoint URL against owner-approved trust policy.

    1. https:// is allowed for any host.
    2. http:// is allowed only when host is loopback AND allow_plaintext_loopback is True.
    3. Any other scheme (ftp:, file:, empty, etc.) is refused.
    4. A URL containing userinfo (https://user:pw@host/...) is refused.
    5. Plaintext through a proxy is not supported. There is no opt-in for non-loopback http.
    6. Refusal raises AdapterConfigurationError naming scheme, host, and rule.
    """
    if not isinstance(url, str) or not url.strip():
        raise AdapterConfigurationError(
            "Endpoint URL must be a non-empty string; scheme='', host='' "
            "(rule: valid absolute URL with http or https scheme required)"
        )

    try:
        parsed = urlsplit(url)
    except Exception as exc:
        raise AdapterConfigurationError(
            f"Endpoint URL cannot be parsed: '{url}'; scheme='', host='' "
            f"(rule: valid URL required: {exc})"
        ) from exc

    scheme = (parsed.scheme or "").lower()
    host = parsed.hostname or ""

    # Rule 4: Userinfo is forbidden
    if parsed.username is not None or parsed.password is not None or "@" in parsed.netloc:
        raise AdapterConfigurationError(
            f"Endpoint URL contains userinfo: scheme='{scheme}', host='{host}' "
            "(rule: URLs containing userinfo are forbidden)"
        )

    if not scheme:
        raise AdapterConfigurationError(
            f"Endpoint URL missing scheme: scheme='', host='{host}' "
            "(rule: only https and opt-in loopback http are allowed)"
        )

    if not host:
        raise AdapterConfigurationError(
            f"Endpoint URL missing host: scheme='{scheme}', host='' "
            "(rule: endpoint URL must include a host)"
        )

    # Rule 1: https is allowed for any host
    if scheme == "https":
        return

    # Rule 2 & 5: http is allowed only for loopback with explicit opt-in
    if scheme == "http":
        if not is_loopback_host(host):
            raise AdapterConfigurationError(
                f"Plaintext HTTP endpoint is not loopback: scheme='{scheme}', host='{host}' "
                "(rule: plaintext HTTP is only allowed for loopback hosts; no opt-in for non-loopback http)"
            )
        if not allow_plaintext_loopback:
            raise AdapterConfigurationError(
                f"Plaintext HTTP loopback endpoint requires allow_plaintext_loopback opt-in: scheme='{scheme}', host='{host}' "
                "(rule: http loopback requires allow_plaintext_loopback: true)"
            )
        return

    # Rule 3: Any other scheme is refused
    raise AdapterConfigurationError(
        f"Endpoint scheme is not allowed: scheme='{scheme}', host='{host}' "
        "(rule: only https and opt-in loopback http are allowed)"
    )
