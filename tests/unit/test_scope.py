"""
Unit tests for target scope validation and network boundary safeguards.
"""

from sqlphantom.domain.models import ScopeRule, Target
from sqlphantom.domain.scope import is_private_ip, validate_scope_rules, validate_target_in_scope


def test_is_private_ip_literals():
    assert is_private_ip("127.0.0.1") is True
    assert is_private_ip("10.0.0.5") is True
    assert is_private_ip("192.168.1.100") is True
    assert is_private_ip("172.16.0.1") is True
    assert is_private_ip("169.254.1.1") is True
    assert is_private_ip("::1") is True
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("1.1.1.1") is False


def test_validate_target_in_scope_allowed_domain():
    scope = ScopeRule(allowed_domains=["vulnweb.com"], block_private_ips=True)
    target_ok = Target(url="http://testphp.vulnweb.com/artists.php?artist=1")
    allowed, reason = validate_target_in_scope(target_ok, scope)
    assert allowed is True
    assert reason == ""

    target_rejected = Target(url="http://evil.com/artists.php?artist=1")
    allowed, reason = validate_target_in_scope(target_rejected, scope)
    assert allowed is False
    assert "evil.com" in reason


def test_validate_target_in_scope_private_ip_rejection():
    scope = ScopeRule(allowed_domains=[], block_private_ips=True)
    target_local = Target(url="http://127.0.0.1:8080/vulnerable.php?id=1")
    allowed, reason = validate_target_in_scope(target_local, scope)
    assert allowed is False
    assert "private" in reason.lower() or "loopback" in reason.lower()


def test_validate_target_in_scope_private_ip_allowed_when_unblocked():
    scope = ScopeRule(allowed_domains=["127.0.0.1"], block_private_ips=False)
    target_local = Target(url="http://127.0.0.1:8080/vulnerable.php?id=1")
    allowed, reason = validate_target_in_scope(target_local, scope)
    assert allowed is True


def test_validate_target_url_pattern_filtering():
    scope = ScopeRule(
        allowed_domains=["example.com"],
        allowed_url_patterns=["*/api/*", "*/v1/*"],
        block_private_ips=False,
    )
    t1 = Target(url="https://example.com/api/users?id=1")
    t2 = Target(url="https://example.com/admin/settings")

    ok1, _ = validate_target_in_scope(t1, scope)
    ok2, r2 = validate_target_in_scope(t2, scope)
    assert ok1 is True
    assert ok2 is False
    assert "pattern" in r2.lower()


def test_validate_scope_rules_warnings():
    scope = ScopeRule(allowed_domains=["example.com:8080/path"])
    errors = validate_scope_rules(scope)
    assert len(errors) > 0
