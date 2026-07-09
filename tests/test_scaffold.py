"""Scaffold smoke test — replaced by real tests in Phase 2."""

from kestrel_feature_observability_fleet import FleetObservabilityHostFeature
from kestrel_sdk import HostFeature


def test_feature_is_a_host_feature():
    assert issubclass(FleetObservabilityHostFeature, HostFeature)
