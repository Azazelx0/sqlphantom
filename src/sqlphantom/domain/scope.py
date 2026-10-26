"""
SQLPhantom target scope validation and network safety controls.
"""

import fnmatch
import ipaddress
import socket
from urllib.parse import urlsplit

from sqlphantom.domain.models import ScopeRule, Target


def is_private_ip(hostname: str) -> bool:
    """
    Determine if a hostname or IP address resolves to a private, loopback,
    link-local, or reserved network range.
    """
    if not hostname:
        return False

    # Check if the hostname is directly a numeric IP literal
    try:
        ip = ipaddress.ip_address(hostname.strip("[]"))
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_unspecified
        )
    except ValueError:
        pass

    # Resolve hostname to examine associated IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        for entry in addr_info:
            sockaddr = entry[4]
            ip_str = sockaddr[0]
            try:
                ip = ipaddress.ip_address(ip_str)
                if (
                    ip.is_private
                    or ip.is_loopback
                    or ip.is_link_local
                    or ip.is_reserved
                    or ip.is_unspecified
                ):
                    return True
            except ValueError:
                continue
    except (socket.gaierror, socket.herror, OSError):
        # In case of DNS resolution failure, do not automatically block;
        # domain validation rules handle accessibility during execution.
        return False

    return False


def validate_target_in_scope(target: Target, scope: ScopeRule) -> tuple[bool, str]:
    """
    Validate whether a target URL strictly complies with configured scope boundaries.

    Returns:
        tuple[bool, str]: (is_allowed, reason_if_rejected)
    """
    if not target.url or not target.url.strip():
        return False, "Target URL is empty"

    try:
        parsed = urlsplit(target.url)
    except Exception as exc:
        return False, f"Malformed URL: {exc}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported scheme '{parsed.scheme}'; only HTTP and HTTPS are permitted"

    hostname = parsed.hostname
    if not hostname:
        return False, "Target URL missing valid host component"

    # Private IP protection
    if scope.block_private_ips and is_private_ip(hostname):
        return (
            False,
            f"Host '{hostname}' resolves to a private, loopback, or reserved IP address",
        )

    # Domain allowlist matching
    if scope.allowed_domains:
        host_lower = hostname.lower()
        matched = False
        for domain in scope.allowed_domains:
            domain_lower = domain.strip().lower()
            if not domain_lower:
                continue
            if host_lower == domain_lower or host_lower.endswith("." + domain_lower):
                matched = True
                break
        if not matched:
            return (
                False,
                f"Host '{hostname}' does not match any allowed domain in scope: {scope.allowed_domains}",
            )

    # URL pattern matching
    if scope.allowed_url_patterns:
        matched_pattern = False
        for pattern in scope.allowed_url_patterns:
            if fnmatch.fnmatch(target.url, pattern):
                matched_pattern = True
                break
        if not matched_pattern:
            return (
                False,
                f"Target URL '{target.url}' does not match any permitted URL pattern",
            )

    return True, ""


def validate_scope_rules(scope: ScopeRule) -> list[str]:
    """
    Validate the configuration of a scope rule set itself, identifying ambiguities.
    """
    errors: list[str] = []

    if not scope.allowed_domains and not scope.allowed_url_patterns:
        errors.append(
            "Scope defines neither allowed domains nor allowed URL patterns; targets will only be constrained by private IP filters"
        )

    for domain in scope.allowed_domains:
        clean = domain.strip()
        if not clean:
            errors.append("Scope includes an empty allowed domain entry")
        elif "/" in clean or ":" in clean:
            errors.append(
                f"Allowed domain '{domain}' appears to contain path or port components; use domain names only"
            )

    return errors
