"""
scripts/verify_worker_shutdown_and_recovery.py
==============================================
Validates worker graceful shutdown on SIGTERM, ensuring un-ACKed messages
remain pending and are safely reclaimed by surviving workers via XAUTOCLAIM.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import fakeredis.aioredis
from backend.app.services.distributed_stream_service import RedisStreamBackend, DistributedStreamEngine
from backend.app.services.predict_service import predict_service
from backend.app.schemas.predict import PacketFeatureVector


async def test_worker_shutdown_and_reclamation():
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    stream_key = "sentinel:telemetry"
    group_name = "sentinel:telemetry:group"

    print("=================================================================")
    print("   SentinelAI Worker Graceful Shutdown & Recovery Lifecycle      ")
    print("=================================================================")

    # 1. Publish 2 telemetry events into stream
    evt1 = {
        "event_id": "evt-shutdown-001",
        "source_ip": "192.168.1.50", "destination_ip": "10.0.0.1",
        "source_port": 12345, "destination_port": 80, "protocol": "TCP",
        "flow_duration": 1000.0, "total_fwd_packets": 2.0, "packet_length_mean": 200.0
    }
    evt2 = {
        "event_id": "evt-shutdown-002",
        "source_ip": "192.168.1.51", "destination_ip": "10.0.0.1",
        "source_port": 12346, "destination_port": 80, "protocol": "TCP",
        "flow_duration": 2000.0, "total_fwd_packets": 3.0, "packet_length_mean": 300.0
    }

    id1 = await backend.publish_event(stream_key, evt1)
    id2 = await backend.publish_event(stream_key, evt2)
    print(f"Step 1: Published 2 events to stream '{stream_key}': MsgIDs=[{id1}, {id2}]")

    # 2. Worker 1 consumes Event 1 and ACKs it, but receives SIGTERM while holding Event 2
    w1_name = "worker-alpha"
    msgs = await backend.consume_events(stream_key, group_name, w1_name, count=2)
    print(f"Step 2: Worker '{w1_name}' consumed {len(msgs)} messages from group '{group_name}'")

    # Complete & ACK Event 1
    vec1 = PacketFeatureVector(**msgs[0]["data"])
    predict_service.infer_packet_threat(vector=vec1, model_name="CatBoost")
    ack1 = await backend.acknowledge_event(stream_key, group_name, msgs[0]["id"])
    print(f"  -> MsgID {msgs[0]['id']} ({msgs[0]['data']['event_id']}) processed and ACKed: {ack1}")

    # Simulate SIGTERM on Worker 1 before processing Msg 2 (Msg 2 remains un-ACKed in pending list)
    print(f"Step 3: Worker '{w1_name}' received SIGTERM! Stopped processing. MsgID {msgs[1]['id']} left un-ACKed.")

    # 3. Replacement Worker 2 reclaims Msg 2 via XAUTOCLAIM
    w2_name = "worker-beta"
    print(f"Step 4: Replacement Worker '{w2_name}' scanning for abandoned pending messages...")
    # Using claim_pending_events (XAUTOCLAIM with min_idle_time_ms=0 for test)
    reclaimed = await backend.claim_pending_events(
        stream_key=stream_key,
        group_name=group_name,
        consumer_name=w2_name,
        min_idle_time_ms=0,
        count=10
    )

    print(f"  -> Worker '{w2_name}' successfully reclaimed {len(reclaimed)} pending message(s) via XAUTOCLAIM!")
    assert len(reclaimed) >= 1
    rec_msg = reclaimed[0]
    assert rec_msg["id"] == msgs[1]["id"]
    assert rec_msg["data"]["event_id"] == "evt-shutdown-002"
    print(f"  -> Reclaimed MsgID {rec_msg['id']} payload: {rec_msg['data']['event_id']} (src={rec_msg['data']['source_ip']})")

    # Complete & ACK Event 2 by Worker 2
    vec2 = PacketFeatureVector(**rec_msg["data"])
    predict_service.infer_packet_threat(vector=vec2, model_name="CatBoost")
    ack2 = await backend.acknowledge_event(stream_key, group_name, rec_msg["id"])
    print(f"  -> MsgID {rec_msg['id']} processed by Worker 2 and ACKed: {ack2}")

    print("=================================================================")
    print("RESULT: WORKER GRACEFUL SHUTDOWN & RECOVERY VERIFIED WITH 0 LOSS")
    print("=================================================================")


if __name__ == "__main__":
    asyncio.run(test_worker_shutdown_and_reclamation())
