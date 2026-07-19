# ⚠️ DEPRECATED & ARCHIVED

This package is superseded. Kestrel observability is now **OpenTelemetry-native**:
emission lives in [`kestrel-feature-observability`](https://github.com/KestrelSovereignAI/kestrel-feature-observability)
(+ `kestrel_sdk.tracing` in the SDK), and the UI is a host-supervised, embedded
**Arize Phoenix** (see `kestrel-sovereign`'s `phoenix_supervisor`). The custom
fleet store/routes/panels this package provided were retired in
kestrel-feature-observability#39 (epic #32). Do not install; last release: 0.4.0.

---

# kestrel-feature-observability-fleet

Fleet-scoped observability **HostFeature** for Kestrel Sovereign.

This is the fleet *consumer/aggregator*: a host-scoped feature (discovered via the
`kestrel_sovereign.host_features` entry-point group) that owns a **fleet-wide,
tenant-scoped event store** (via `kestrel-feature-entities`), serves **host-root**
ingest/query endpoints and a **streamable live stream**, and ships the
**orchestrator swimlane** console panel.

The per-agent *producer* (the emitter hook) lives separately in
[`kestrel-feature-observability`](https://github.com/KestrelSovereignAI/kestrel-feature-observability) —
producer and consumer are deliberately split by scope so the per-agent emitter
stays lightweight (no DB/ORM stack) while the DB layer is confined to the host.

Part of the fleet-host-features epic: `KestrelSovereignAI/kestrel-claws#27`.

## Install

```bash
uv pip install kestrel-feature-observability-fleet
```

Auto-discovered by the Kestrel Sovereign host at host scope; enable via the host
feature manifest. Requires a host running the host-feature runtime
(kestrel-sovereign `HostFeature` support, SDK ≥ 0.29.2).

## Status

Scaffold — the entities model, host-root ingest/query endpoints, streamable
stream, and swimlane panel are implemented per the Phase 2 issue.
