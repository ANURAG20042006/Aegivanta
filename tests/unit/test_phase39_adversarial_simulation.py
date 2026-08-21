"""
tests/unit/test_phase39_adversarial_simulation.py
=================================================
Phase 39 Adversarial Attack Simulation Unit Tests.
"""

import pytest
from backend.app.models.predictive_intel import AdversarialVectorSimulation


class TestAdversarialSimulation:
    """Unit tests for AdversarialVectorSimulation model."""

    def test_adversarial_simulation_model(self):
        """AdversarialVectorSimulation must store title, initial vector, escalation path, blast radius, and mitigation."""
        sim = AdversarialVectorSimulation(
            tenant_id="tenant-pred",
            threat_scenario_title="Phishing -> Token Theft",
            initial_access_vector="Session Token Theft",
            predicted_escalation_pathway="Initial Access -> IAM FullAccess -> S3 Sync",
            estimated_blast_radius_nodes=18,
            mitigation_directive="Enforce FIDO2 hardware passkeys."
        )
        assert sim.threat_scenario_title == "Phishing -> Token Theft"
        assert sim.estimated_blast_radius_nodes == 18
