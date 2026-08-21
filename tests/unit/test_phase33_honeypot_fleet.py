"""
tests/unit/test_phase33_honeypot_fleet.py
=========================================
Phase 33 Honeypot Fleet & Decoy Orchestration Unit Tests.
"""

import pytest
from backend.app.models.deception import HoneypotNode


class TestHoneypotFleet:
    """Unit tests for Honeypot Decoy node data models."""

    def test_honeypot_node_model_initialization(self):
        """HoneypotNode must initialize with decoy type, IP, and emulation profile."""
        node = HoneypotNode(
            tenant_id="tenant-123",
            node_name="decoy-ssh-bastion-01",
            decoy_type="SSH_COWRIE",
            internal_ip="10.0.12.50",
            vlan_segment="DMZ-DECEPTION-VLAN",
            emulation_profile="Ubuntu 22.04 LTS OpenSSH 8.9p1",
            interaction_level="MEDIUM",
            total_hits_count=12,
            is_active=True,
            status="LISTENING"
        )
        assert node.node_name == "decoy-ssh-bastion-01"
        assert node.decoy_type == "SSH_COWRIE"
        assert node.internal_ip == "10.0.12.50"
        assert node.total_hits_count == 12
