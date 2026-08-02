"""Release metadata contracts for the deprecated fleet package."""

from __future__ import annotations

import pathlib
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SDK_REQUIREMENT = "kestrel-sovereign-sdk>=0.34,<0.35"


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _package_from_lock(name: str) -> dict:
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    return next(package for package in lock["package"] if package["name"] == name)


def test_release_version_is_0_4_1_in_project_and_lock() -> None:
    assert _pyproject()["project"]["version"] == "0.4.1"
    assert (
        _package_from_lock("kestrel-feature-observability-fleet")["version"]
        == "0.4.1"
    )


def test_base_and_test_extra_require_exact_sdk_line() -> None:
    project = _pyproject()["project"]
    assert SDK_REQUIREMENT in project["dependencies"]
    assert SDK_REQUIREMENT in project["optional-dependencies"]["test"]


def test_lock_records_public_sdk_contract_and_version() -> None:
    package = _package_from_lock("kestrel-feature-observability-fleet")
    requirements = package["metadata"]["requires-dist"]
    assert {
        "name": "kestrel-sovereign-sdk",
        "specifier": ">=0.34,<0.35",
    } in requirements
    assert {
        "name": "kestrel-sovereign-sdk",
        "marker": "extra == 'test'",
        "specifier": ">=0.34,<0.35",
    } in requirements

    sdk = _package_from_lock("kestrel-sovereign-sdk")
    assert sdk["version"] == "0.34.0"
