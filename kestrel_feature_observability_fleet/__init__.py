"""Fleet-scoped observability HostFeature for Kestrel Sovereign.

This package ships a host-scoped ``HostFeature`` (discovered via the
``kestrel_sovereign.host_features`` entry-point group) that owns the fleet-wide
observability store, host-root ingest/query endpoints, a streamable live
stream, and the orchestrator swimlane panel. It is the fleet *consumer*; the
per-agent *producer* (the emitter hook) lives in ``kestrel-feature-observability``.
"""

from kestrel_feature_observability_fleet.feature import (
    FLEET_TENANT_ID,
    FleetObservabilityHostFeature,
)
from kestrel_feature_observability_fleet.models import (
    EVENT_TYPES,
    GATE_EVENT_TYPES,
    GATE_KINDS,
    ObservabilityEvent,
)
from kestrel_feature_observability_fleet.redaction import redact_metadata
from kestrel_feature_observability_fleet.store import FleetObservabilityStore, IngestError

__all__ = [
    "FleetObservabilityHostFeature",
    "FLEET_TENANT_ID",
    "FleetObservabilityStore",
    "IngestError",
    "ObservabilityEvent",
    "EVENT_TYPES",
    "GATE_EVENT_TYPES",
    "GATE_KINDS",
    "redact_metadata",
]
