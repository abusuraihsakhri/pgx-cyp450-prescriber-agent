"""
Security-focused tests for pgx-cyp450-prescriber-agent.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import AuditTrail, PHIGuard, SecurityException, assert_no_phi


def test_audit_trail_with_custom_key():
    """AuditTrail should accept a custom secret key."""
    trail = AuditTrail(secret_key="test-secret-key-12345")
    entry = trail.log("test_actor", "test_tier", "TEST_EVENT", {"key": "value"})
    assert entry["current_hash"] != ""
    assert entry["prev_hash"] == "GENESIS_BLOCK_0000000000000000"
    assert trail.verify_integrity() is True


def test_audit_trail_chained_integrity():
    """Multiple audit entries should form a valid chain."""
    trail = AuditTrail(secret_key="chain-test-key")
    for i in range(5):
        trail.log("actor", "tier", "EVENT", {"index": i})
    assert len(trail.get_trail()) == 5
    assert trail.verify_integrity() is True


def test_audit_trail_tamper_detection():
    """Tampered audit entries should fail integrity check."""
    trail = AuditTrail(secret_key="tamper-test-key")
    trail.log("actor", "tier", "EVENT", {"data": "original"})
    # Tamper with the entry
    trail.logs[0]["payload_hash"] = "tampered_hash"
    assert trail.verify_integrity() is False


def test_phi_guard_ssn():
    """PHI guard should detect SSN patterns."""
    with pytest.raises(SecurityException):
        assert_no_phi("Patient SSN: 123-45-6789")


def test_phi_guard_mrn():
    """PHI guard should detect MRN patterns."""
    with pytest.raises(SecurityException):
        assert_no_phi("MRN-12345678 sample analysis")


def test_phi_guard_phone():
    """PHI guard should detect phone number patterns."""
    with pytest.raises(SecurityException):
        assert_no_phi("Contact patient at 555-123-4567")


def test_phi_guard_email():
    """PHI guard should detect email patterns."""
    with pytest.raises(SecurityException):
        assert_no_phi("Send results to patient@hospital.com")


def test_phi_guard_clean_text():
    """PHI guard should allow clean analytical text."""
    assert_no_phi("Analytical assay specimen KEY-001 optimal")
    assert_no_phi("Metric value 24.5 within normal range")


def test_phi_guard_empty_string():
    """PHI guard should handle empty strings."""
    assert_no_phi("")


def test_phi_redaction():
    """PHIGuard should redact PHI from text."""
    redacted = PHIGuard.redact_phi("Patient MRN-12345678 has SSN 123-45-6789")
    assert "MRN" not in redacted or "12345678" not in redacted
    assert "123-45-6789" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_batch_input_validation_missing_file():
    """Batch command should handle missing input file gracefully."""
    from cli import _validate_input_path
    with pytest.raises(FileNotFoundError):
        _validate_input_path("/nonexistent/path/file.csv")


def test_batch_input_validation_wrong_extension(tmp_path):
    """Batch command should reject unsupported file types."""
    from cli import _validate_input_path
    # Create a temporary file with wrong extension
    wrong_ext_file = tmp_path / "test.txt"
    wrong_ext_file.write_text("some content")
    with pytest.raises(ValueError, match="Unsupported file type"):
        _validate_input_path(str(wrong_ext_file))
