# kestrel-feature-observability-fleet — Agent Instructions

This package is the host/fleet-scoped observability consumer. It is distinct
from `kestrel-feature-observability`, the per-agent event producer.

## Package structure

- `kestrel_feature_observability_fleet/feature.py` — `HostFeature` lifecycle,
  router, host store, and UI contribution.
- `kestrel_feature_observability_fleet/endpoints.py` — fleet ingest/query/tree/
  stream API under `/api/host/observability/*`.
- `kestrel_feature_observability_fleet/store.py` — tenant-scoped event store.
- `kestrel_feature_observability_fleet/pubsub.py` — resumable in-process event
  backplane.
- `kestrel_feature_observability_fleet/static/swimlane.js` — host UI panel.
- `tests/` — host contract, store, endpoint, stream, and UI tests.

## Entry point and ownership

`kestrel_sovereign.host_features` discovers
`FleetObservabilityHostFeature`. Its router is mounted once at the host root;
it must never claim `/api/observability/*`, which is selected-agent scope.
Machine ingest is API-key authenticated by Sovereign. Any future cookie-backed
state-changing route must also use host CSRF protection.

## Verification

```bash
uv run --extra test pytest tests/ -q
```

For host lifecycle or routing changes, also dogfood through the deployed
`kestrel_sovereign.server:app` with an isolated `Kite --test` agent, following
Sovereign's `docs/architecture/testing/LIVE_AGENT_DOGFOODING.md`.
