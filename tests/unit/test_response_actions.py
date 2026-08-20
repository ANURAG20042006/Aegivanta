"""
tests/unit/test_response_actions.py
===================================
Phase 3.7 Unit Tests: Modular Response Action Framework & Safe Adapters.
Verifies BlockIPAction, HostIsolationAction, QuarantineAssetAction,
RevokeSessionAction, DisableAccountAction, validation, verification, and rollback.
"""

import pytest
from backend.app.services.response_actions import (
    BlockIPAction, HostIsolationAction, QuarantineAssetAction,
    RevokeSessionAction, DisableAccountAction,
    NetworkEnforcementAdapter, HostIsolationAdapter,
    AssetQuarantineAdapter, AccountResponseAdapter
)


@pytest.fixture(autouse=True)
def reset_adapters():
    NetworkEnforcementAdapter.reset()
    HostIsolationAdapter.reset()
    AssetQuarantineAdapter.reset()
    AccountResponseAdapter.reset()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_block_ip_action_lifecycle():
    """Verify BlockIPAction validate, preview, execute, verify, rollback."""
    action = BlockIPAction()

    # 1. Validation: valid and invalid
    is_valid, _ = action.validate("198.51.100.5")
    assert is_valid is True

    is_loopback_valid, err = action.validate("127.0.0.1")
    assert is_loopback_valid is False
    assert "restricted" in err

    is_syntax_valid, _ = action.validate("invalid.ip.address")
    assert is_syntax_valid is False

    # 2. Preview
    preview = action.preview("198.51.100.5")
    assert preview["would_execute"] is True
    assert preview["action_type"] == "BLOCK_IP"

    # 3. Execution
    exec_res = await action.execute("198.51.100.5", {"duration_seconds": 1800})
    assert exec_res["status"] == "SUCCESS"
    assert NetworkEnforcementAdapter.is_blocked("198.51.100.5") is True

    # 4. Verification
    is_verified, v_msg = await action.verify("198.51.100.5", exec_res)
    assert is_verified is True
    assert "Verified" in v_msg

    # 5. Rollback
    rb_res = await action.rollback("198.51.100.5", exec_res["reversal_state"])
    assert rb_res["status"] == "ROLLED_BACK"
    assert NetworkEnforcementAdapter.is_blocked("198.51.100.5") is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_host_isolation_action_lifecycle():
    """Verify HostIsolationAction lifecycle and injection prevention."""
    action = HostIsolationAction()

    # Injection prevention
    is_bad, err = action.validate("host-1; rm -rf /")
    assert is_bad is False
    assert "invalid characters" in err

    # Valid execution
    is_ok, _ = action.validate("srv-prod-db01")
    assert is_ok is True

    exec_res = await action.execute("srv-prod-db01")
    assert exec_res["status"] == "SUCCESS"
    assert HostIsolationAdapter.is_isolated("srv-prod-db01") is True

    # Verification
    is_ver, _ = await action.verify("srv-prod-db01", exec_res)
    assert is_ver is True

    # Rollback
    rb = await action.rollback("srv-prod-db01", exec_res["reversal_state"])
    assert rb["status"] == "ROLLED_BACK"
    assert HostIsolationAdapter.is_isolated("srv-prod-db01") is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_quarantine_asset_action():
    """Verify QuarantineAssetAction execute and rollback."""
    action = QuarantineAssetAction()
    exec_res = await action.execute("asset-finance-01")
    assert exec_res["status"] == "SUCCESS"
    assert AssetQuarantineAdapter.is_quarantined("asset-finance-01") is True

    is_ver, _ = await action.verify("asset-finance-01", exec_res)
    assert is_ver is True

    await action.rollback("asset-finance-01", exec_res["reversal_state"])
    assert AssetQuarantineAdapter.is_quarantined("asset-finance-01") is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_revoke_session_and_disable_account_actions():
    """Verify RevokeSessionAction and DisableAccountAction."""
    act_session = RevokeSessionAction()
    act_disable = DisableAccountAction()

    # Revoke session
    res_s = await act_session.execute("user_victim")
    assert res_s["status"] == "SUCCESS"
    assert AccountResponseAdapter.is_session_revoked("user_victim") is True

    # Disable account
    res_d = await act_disable.execute("user_victim")
    assert res_d["status"] == "SUCCESS"
    assert AccountResponseAdapter.is_account_disabled("user_victim") is True

    # Rollback
    await act_disable.rollback("user_victim", res_d["reversal_state"])
    assert AccountResponseAdapter.is_account_disabled("user_victim") is False
