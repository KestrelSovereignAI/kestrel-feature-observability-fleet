"""Fleet observability ``HostFeature`` — scaffold.

The concrete data plane (entities ``ObservabilityEvent`` model, host-root
ingest/query endpoints), the streamable live stream, and the orchestrator
swimlane panel are implemented per the Phase 2 issue. This scaffold establishes
the package + entry point so the host-feature runtime can discover it.
"""

from __future__ import annotations

from kestrel_sdk import HostFeature


class FleetObservabilityHostFeature(HostFeature):
    """Host-scoped fleet observability feature.

    Owns a fleet-wide, tenant-scoped event store (via ``kestrel-feature-entities``)
    and serves host-root ingest/query + a streamable live stream, plus the
    orchestrator swimlane console panel. Discovered at host scope, not per-agent.
    """

    #: Stable slug used for mount path / capability gating.
    name = "observability-fleet"
