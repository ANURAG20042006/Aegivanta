"""
tests/unit/test_phase311_horizontal_scaling.py
==============================================
Phase 3.11 Unit Tests: Horizontal Scaling Infrastructure.
Tests worker registry, consumer base configuration, retry policies, DLQ routing,
and backpressure thresholds without requiring a live Redis connection.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestWorkerRegistry:

    def test_all_roles_have_stream_assignments(self):
        """Every WorkerRole must have at least one stream assigned."""
        from backend.app.services.worker_registry import WorkerRole, WORKER_STREAM_ASSIGNMENTS

        for role in WorkerRole:
            assert role in WORKER_STREAM_ASSIGNMENTS, f"No stream assignment for role {role}"
            assert len(WORKER_STREAM_ASSIGNMENTS[role]) >= 1, f"Empty stream list for role {role}"

    def test_all_roles_have_retry_policies(self):
        """Every WorkerRole must have a retry policy with required keys."""
        from backend.app.services.worker_registry import WorkerRole, WORKER_RETRY_POLICY

        required_keys = {"max_retries", "retry_backoff_s", "dlq_threshold"}
        for role in WorkerRole:
            assert role in WORKER_RETRY_POLICY, f"No retry policy for role {role}"
            policy = WORKER_RETRY_POLICY[role]
            for key in required_keys:
                assert key in policy, f"Missing '{key}' in retry policy for role {role}"
            assert policy["max_retries"] >= 1
            assert policy["retry_backoff_s"] >= 1
            assert policy["dlq_threshold"] >= 1

    def test_all_roles_have_backpressure_thresholds(self):
        """Every WorkerRole must have a positive backpressure threshold."""
        from backend.app.services.worker_registry import WorkerRole, BACKPRESSURE_THRESHOLDS

        for role in WorkerRole:
            assert role in BACKPRESSURE_THRESHOLDS, f"No backpressure threshold for role {role}"
            assert BACKPRESSURE_THRESHOLDS[role] > 0

    def test_consumer_group_name_is_role_prefixed(self):
        """Consumer group names must include the role name."""
        from backend.app.services.worker_registry import WorkerRole, get_consumer_group

        for role in WorkerRole:
            cg = get_consumer_group(role)
            assert role.value in cg, f"Role not in consumer group name: '{cg}'"

    def test_current_worker_role_defaults_to_detection_on_unknown_env(self):
        """Unknown SENTINELAI_WORKER_ROLE env must fall back to DETECTION."""
        import os
        from backend.app.services.worker_registry import current_worker_role, WorkerRole

        with patch.dict(os.environ, {"SENTINELAI_WORKER_ROLE": "banana"}):
            role = current_worker_role()
        assert role == WorkerRole.DETECTION

    def test_current_worker_role_reads_env_correctly(self):
        """SENTINELAI_WORKER_ROLE=response must return WorkerRole.RESPONSE."""
        import os
        from backend.app.services.worker_registry import current_worker_role, WorkerRole

        with patch.dict(os.environ, {"SENTINELAI_WORKER_ROLE": "response"}):
            role = current_worker_role()
        assert role == WorkerRole.RESPONSE

    def test_no_main_stream_key_collision_between_roles(self):
        """Primary stream keys (non-DLQ) must not be shared between different roles."""
        from backend.app.services.worker_registry import WorkerRole, WORKER_STREAM_ASSIGNMENTS

        primary_streams: dict[str, str] = {}  # stream_key → first role
        for role, streams in WORKER_STREAM_ASSIGNMENTS.items():
            for s in streams:
                if "dl_queue" not in s:
                    if s in primary_streams:
                        pytest.fail(
                            f"Stream '{s}' is shared between '{primary_streams[s]}' and '{role}' — "
                            "each primary stream must be owned by exactly one role"
                        )
                    primary_streams[s] = role.value


class TestStreamConsumerBase:

    def _make_consumer(self, role_value="detection"):
        """Factory: create a StreamConsumerBase subclass with a mock Redis client."""
        from backend.app.services.worker_registry import WorkerRole
        from backend.app.services.stream_consumer_base import StreamConsumerBase

        class _TestConsumer(StreamConsumerBase):
            async def process_event(self, stream_key, event_data):
                return True

        mock_redis = AsyncMock()
        mock_redis.xgroup_create = AsyncMock(return_value=True)
        mock_redis.xack = AsyncMock(return_value=1)
        mock_redis.xadd = AsyncMock(return_value=b"1-0")
        mock_redis.xpending = AsyncMock(return_value={"pending": 0})

        role = WorkerRole(role_value)
        return _TestConsumer(role=role, redis_client=mock_redis), mock_redis

    @pytest.mark.asyncio
    async def test_ensure_consumer_groups_creates_group_per_stream(self):
        """_ensure_consumer_groups must call xgroup_create for each primary stream."""
        consumer, mock_redis = self._make_consumer("detection")
        primary_streams = [s for s in consumer.streams if "dl_queue" not in s]

        await consumer._ensure_consumer_groups()

        assert mock_redis.xgroup_create.call_count == len(primary_streams)

    @pytest.mark.asyncio
    async def test_ensure_consumer_groups_handles_busygroup_gracefully(self):
        """BUSYGROUP error from Redis must not propagate."""
        consumer, mock_redis = self._make_consumer("detection")
        mock_redis.xgroup_create = AsyncMock(side_effect=Exception("BUSYGROUP Consumer Group name already exists"))

        # Should not raise
        await consumer._ensure_consumer_groups()

    @pytest.mark.asyncio
    async def test_send_to_dlq_publishes_to_dlq_stream(self):
        """_send_to_dlq must call redis.xadd on the DLQ stream."""
        consumer, mock_redis = self._make_consumer("detection")
        await consumer._send_to_dlq("sentinelai:detection", "1-0", {"foo": "bar"}, "test error")

        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args
        dlq_key = call_args[0][0]
        assert "dl_queue" in dlq_key

    @pytest.mark.asyncio
    async def test_process_message_acks_on_success(self):
        """On success, process_event must ACK the message."""
        consumer, mock_redis = self._make_consumer("detection")
        await consumer._process_message("sentinelai:detection", "1-0", {b"key": b"val"})

        mock_redis.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_retries_and_dlqs_on_repeated_failure(self):
        """After max_retries, message must be moved to DLQ and ACKed."""
        from backend.app.services.worker_registry import WorkerRole
        from backend.app.services.stream_consumer_base import StreamConsumerBase

        class _AlwaysFailConsumer(StreamConsumerBase):
            async def process_event(self, stream_key, event_data):
                raise RuntimeError("deliberate failure")

        mock_redis = AsyncMock()
        mock_redis.xack = AsyncMock(return_value=1)
        mock_redis.xadd = AsyncMock(return_value=b"1-0")

        consumer = _AlwaysFailConsumer(role=WorkerRole.DETECTION, redis_client=mock_redis)
        max_retries = consumer.retry_policy["max_retries"]

        # Simulate max_retries - 1 prior failures so next call triggers DLQ
        consumer._retry_counts["99-0"] = max_retries - 1

        with patch("asyncio.sleep", new_callable=AsyncMock):
            await consumer._process_message("sentinelai:detection", "99-0", {})

        # Should have been ACKed (moved to DLQ, message not stuck in PEL)
        mock_redis.xack.assert_called()
        # DLQ write should have occurred
        mock_redis.xadd.assert_called()

    @pytest.mark.asyncio
    async def test_backpressure_check_returns_true_when_pending_exceeds_threshold(self):
        """_is_backpressured must return True when PEL exceeds configured threshold."""
        consumer, mock_redis = self._make_consumer("detection")
        # Set pending well above threshold
        threshold = consumer.backpressure_threshold
        mock_redis.xpending = AsyncMock(return_value={"pending": threshold + 1000})

        result = await consumer._is_backpressured("sentinelai:detection")
        assert result is True

    @pytest.mark.asyncio
    async def test_backpressure_check_returns_false_when_below_threshold(self):
        """_is_backpressured must return False when PEL is below threshold."""
        consumer, mock_redis = self._make_consumer("detection")
        mock_redis.xpending = AsyncMock(return_value={"pending": 0})

        result = await consumer._is_backpressured("sentinelai:detection")
        assert result is False

    def test_consumer_name_contains_role(self):
        """Consumer name must identify the worker role for observability."""
        consumer, _ = self._make_consumer("response")
        assert "response" in consumer.consumer_name


class TestKubernetesWorkerManifests:

    def _load_k8s_yaml(self, filename: str):
        """Load and parse a k8s YAML file."""
        import yaml
        from pathlib import Path

        path = Path(__file__).parents[2] / "k8s" / filename
        with open(path, "r", encoding="utf-8") as f:
            return list(yaml.safe_load_all(f))

    def test_hpa_yaml_has_entries_for_all_worker_roles(self):
        """hpa.yaml must define HPAs for API, detection, response, threat-intel, and hunting."""
        docs = self._load_k8s_yaml("hpa.yaml")
        hpa_names = {d["metadata"]["name"] for d in docs if d and d.get("kind") == "HorizontalPodAutoscaler"}

        required_hpas = {
            "sentinelai-api-hpa",
            "sentinelai-detection-worker-hpa",
            "sentinelai-response-worker-hpa",
            "sentinelai-threat-intel-worker-hpa",
            "sentinelai-hunting-worker-hpa",
        }
        missing = required_hpas - hpa_names
        assert not missing, f"Missing HPAs: {missing}"

    def test_hpa_max_replicas_are_reasonable(self):
        """All HPAs must have maxReplicas >= 2."""
        docs = self._load_k8s_yaml("hpa.yaml")
        for doc in docs:
            if doc and doc.get("kind") == "HorizontalPodAutoscaler":
                max_rep = doc["spec"]["maxReplicas"]
                assert max_rep >= 2, f"HPA '{doc['metadata']['name']}' maxReplicas={max_rep} too low"

    def test_worker_deployments_yaml_sets_worker_role_env(self):
        """Each worker deployment must set SENTINELAI_WORKER_ROLE environment variable."""
        docs = self._load_k8s_yaml("deployment-workers.yaml")
        for doc in docs:
            if not doc or doc.get("kind") != "Deployment":
                continue
            containers = doc["spec"]["template"]["spec"]["containers"]
            for container in containers:
                env_names = [e["name"] for e in (container.get("env") or [])]
                assert "SENTINELAI_WORKER_ROLE" in env_names, \
                    f"Deployment '{doc['metadata']['name']}' container '{container['name']}' missing SENTINELAI_WORKER_ROLE"
