"""Store round-trip: ingest (bulk, redaction, validation), query, tree."""

from __future__ import annotations

import pytest

from kestrel_feature_observability_fleet.redaction import REDACTED
from kestrel_feature_observability_fleet.store import IngestError

from conftest import make_event

pytestmark = pytest.mark.asyncio


async def test_ingest_and_query_roundtrip(store):
    ids = await store.ingest([make_event(session_id="s1")])
    assert len(ids) == 1
    events = await store.query(session_id="s1")
    assert len(events) == 1
    assert events[0]["id"] == ids[0]
    assert events[0]["agent_name"] == "talon:acme/widgets#42"


async def test_bulk_insert(store):
    ids = await store.ingest(
        [make_event(session_id="s") for _ in range(5)]
    )
    assert len(ids) == 5
    assert len(await store.query(session_id="s")) == 5


async def test_metadata_redacted_on_ingest(store):
    await store.ingest(
        [
            make_event(
                session_id="sr",
                metadata={"api_key": "secret", "nested": {"password": "p", "ok": 1}},
            )
        ]
    )
    ev = (await store.query(session_id="sr"))[0]
    assert ev["metadata"]["api_key"] == REDACTED
    assert ev["metadata"]["nested"]["password"] == REDACTED
    assert ev["metadata"]["nested"]["ok"] == 1


async def test_unknown_event_type_rejected(store):
    with pytest.raises(IngestError):
        await store.ingest([make_event(event_type="not_a_type")])


async def test_missing_required_fields_rejected(store):
    with pytest.raises(IngestError):
        await store.ingest([make_event(agent_name="")])
    with pytest.raises(IngestError):
        await store.ingest([make_event(session_id="")])


async def test_ingest_is_all_or_nothing(store):
    with pytest.raises(IngestError):
        await store.ingest(
            [make_event(session_id="atomic"), make_event(event_type="bad")]
        )
    assert await store.query(session_id="atomic") == []


async def test_gate_event_accepted(store):
    ids = await store.ingest(
        [
            make_event(
                session_id="g",
                event_type="gate_started",
                metadata={"gate": "verify", "attempt": 1},
            )
        ]
    )
    assert len(ids) == 1


async def test_query_filters(store):
    await store.ingest(
        [
            make_event(agent_name="a1", orchestrator="orch", session_id="x"),
            make_event(agent_name="a2", orchestrator="orch", session_id="y"),
        ]
    )
    assert len(await store.query(orchestrator="orch")) == 2
    assert len(await store.query(agent_name="a1")) == 1
    assert len(await store.query(session_id="y")) == 1


async def test_subtree_includes_orchestrated_events(store):
    await store.ingest(
        [
            make_event(agent_name="root", orchestrator=None, session_id="s"),
            make_event(agent_name="child", orchestrator="root", session_id="s"),
        ]
    )
    own = await store.query(agent_name="root")
    assert len(own) == 1
    subtree = await store.query(agent_name="root", subtree=True)
    assert len(subtree) == 2


async def test_tree_direct_node_and_grouping(store):
    await store.ingest(
        [
            make_event(agent_name="root", orchestrator=None, session_id="s"),
            make_event(agent_name="child", orchestrator="root", session_id="s"),
        ]
    )
    tree = (await store.tree())["tree"]
    direct = [n for n in tree if n["is_direct"]]
    assert len(direct) == 1
    assert direct[0]["label"] == "Direct"
    orch = [n for n in tree if n["orchestrator"] == "root"]
    assert len(orch) == 1
    assert orch[0]["agents"][0]["agent_name"] == "child"


async def test_tree_shortens_did_shaped_values(store):
    await store.ingest(
        [make_event(agent_name="did:key:z6MkverylongidentifierABCDEF", session_id="s")]
    )
    tree = (await store.tree())["tree"]
    labels = [a["label"] for n in tree for a in n["agents"]]
    assert any(label.startswith("did:…") for label in labels)
