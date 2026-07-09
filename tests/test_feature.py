"""FleetObservabilityHostFeature lifecycle + discovery wiring."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from kestrel_feature_observability_fleet.feature import (
    FLEET_TENANT_ID,
    FleetObservabilityHostFeature,
)


def _ctx(db_url: str) -> SimpleNamespace:
    return SimpleNamespace(config={"observability_fleet_db_url": db_url})


@pytest.mark.asyncio
async def test_on_host_start_opens_store_and_stop_closes(db_url):
    feature = FleetObservabilityHostFeature()
    assert feature.store is None

    await feature.on_host_start(_ctx(db_url))
    assert feature.store is not None
    assert feature.store.tenant_id == FLEET_TENANT_ID

    # Round-trips through the live store.
    ids = await feature.store.ingest(
        [{"agent_name": "a", "session_id": "s", "event_type": "metric"}]
    )
    assert len(ids) == 1

    await feature.on_host_stop(_ctx(db_url))
    assert feature.store is None


@pytest.mark.asyncio
async def test_on_host_stop_is_idempotent(db_url):
    feature = FleetObservabilityHostFeature()
    # Safe to stop before ever starting.
    await feature.on_host_stop(_ctx(db_url))
    assert feature.store is None


async def test_router_503_before_start(db_url):
    pytest.importorskip("fastapi")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    feature = FleetObservabilityHostFeature()
    app = FastAPI()
    app.include_router(feature.get_router())
    with TestClient(app) as client:
        resp = client.get("/api/observability/tree")
        assert resp.status_code == 503


def test_get_ui_contributions_ships_swimlane():
    feature = FleetObservabilityHostFeature()
    contributions = feature.get_ui_contributions()
    assert contributions is not None
    assert any("swimlane.js" in m for m in contributions.modules)


def test_entry_point_registered():
    from importlib.metadata import entry_points

    eps = entry_points(group="kestrel_sovereign.host_features")
    names = {ep.name for ep in eps}
    assert "FleetObservabilityHostFeature" in names
