"""Host-root router: ingest (single+batch), query, tree, live stream."""

from __future__ import annotations

import pytest
import pytest_asyncio

from kestrel_feature_observability_fleet.endpoints import get_router
from kestrel_feature_observability_fleet.store import FleetObservabilityStore

from conftest import make_event


@pytest_asyncio.fixture
async def client(db_url, tenant_id):
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    store = await FleetObservabilityStore.open(db_url, tenant_id)
    app = fastapi.FastAPI()
    app.include_router(get_router(lambda: store))
    try:
        with TestClient(app) as c:
            yield c
    finally:
        await store.close()


def test_post_single_event(client):
    resp = client.post("/api/observability/events", json=make_event(session_id="s1"))
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 1
    assert len(body["ids"]) == 1


def test_post_batch_events(client):
    payload = {"events": [make_event(session_id="b") for _ in range(3)]}
    resp = client.post("/api/observability/events", json=payload)
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 3


def test_post_unknown_event_type_returns_422(client):
    resp = client.post(
        "/api/observability/events", json=make_event(event_type="nope")
    )
    assert resp.status_code == 422


def test_post_missing_required_returns_422(client):
    resp = client.post("/api/observability/events", json=make_event(agent_name=""))
    assert resp.status_code == 422


def test_post_metadata_redacted(client):
    client.post(
        "/api/observability/events",
        json=make_event(session_id="red", metadata={"token": "t", "ok": 1}),
    )
    resp = client.get("/api/observability/events", params={"session_id": "red"})
    ev = resp.json()["events"][0]
    assert ev["metadata"]["token"] == "[REDACTED]"
    assert ev["metadata"]["ok"] == 1


def test_get_events_filtered(client):
    client.post(
        "/api/observability/events",
        json={
            "events": [
                make_event(agent_name="a1", orchestrator="o", session_id="q"),
                make_event(agent_name="a2", orchestrator="o", session_id="q"),
            ]
        },
    )
    resp = client.get("/api/observability/events", params={"orchestrator": "o"})
    assert resp.status_code == 200
    assert resp.json()["count"] == 2


def test_get_events_subtree(client):
    client.post(
        "/api/observability/events",
        json={
            "events": [
                make_event(agent_name="root", session_id="t"),
                make_event(agent_name="child", orchestrator="root", session_id="t"),
            ]
        },
    )
    resp = client.get(
        "/api/observability/events",
        params={"agent_name": "root", "subtree": "true"},
    )
    assert resp.json()["count"] == 2


def test_get_tree_has_direct_node(client):
    client.post(
        "/api/observability/events",
        json={
            "events": [
                make_event(agent_name="root", session_id="t"),
                make_event(agent_name="child", orchestrator="root", session_id="t"),
            ]
        },
    )
    resp = client.get("/api/observability/tree")
    assert resp.status_code == 200
    tree = resp.json()["tree"]
    assert any(n["is_direct"] and n["label"] == "Direct" for n in tree)


def test_stream_returns_event_stream_with_preamble(client):
    with client.stream("GET", "/api/observability/stream") as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        assert "X-Stream-Session" in resp.headers
        # Read just the session preamble comment, then disconnect.
        for line in resp.iter_lines():
            assert line.startswith(": stream ")
            break


@pytest.mark.asyncio
async def test_stream_generator_delivers_live_event(store):
    from kestrel_feature_observability_fleet.endpoints import event_stream

    gen = event_stream(store, last_event_id=0, session_id="sess")
    # Preamble frames first.
    assert (await gen.__anext__()).startswith(": stream ")
    assert (await gen.__anext__()).startswith("retry:")
    # Ingest, then the next frame is the live SSE data frame.
    await store.ingest([make_event(session_id="live")])
    frame = await gen.__anext__()
    assert frame.startswith("id: ")
    assert '"session_id": "live"' in frame
    await gen.aclose()
