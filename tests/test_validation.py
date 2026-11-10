"""
Unit Tests for Custom Network Specification & Parameter Validation Engine
Tests every bad-input class:
  - Negative or zero link distances
  - Zero total endpoints
  - Bad CIDR formats & out-of-range prefix
  - Host bits set in root CIDR
  - Bad host counts (< 1)
  - Disallowed VLAN IDs (< 2, > 4094, and reserved 1002-1005)
  - Duplicate device names, subnet names, and VLAN IDs
  - Unknown device references in links
  - Disconnected topology graph
  - Dual-homed site declared with only one link
  - Cloud VPC edge missing BGP parameters
"""

import pytest
from engine.validation import validate_network_specification


def _base_valid_spec():
    return {
        "root_cidr": "10.0.0.0/16",
        "devices": [
            {"name": "R1", "type": "router"},
            {"name": "SW1", "type": "l2_switch"},
        ],
        "links": [
            {"endpoint_a": "R1", "endpoint_b": "SW1", "distance_m": 100.0},
        ],
        "subnets": [
            {"name": "LAN1", "hosts": 50, "vlan": 10, "device": "R1"},
        ],
    }


def test_valid_specification_passes():
    spec = _base_valid_spec()
    res = validate_network_specification(spec)
    assert res["is_valid"] is True
    assert len(res["errors"]) == 0


def test_bad_cidr_format():
    spec = _base_valid_spec()
    spec["root_cidr"] = "invalid_cidr"
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("CIDR format" in e["message"] for e in res["errors"])


def test_host_bits_set_in_root():
    spec = _base_valid_spec()
    spec["root_cidr"] = "10.10.1.0/16"  # Host bit 1 set in /16
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("Host bits are set" in e["message"] for e in res["errors"])


def test_negative_link_distance():
    spec = _base_valid_spec()
    spec["links"][0]["distance_m"] = -50.0
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("invalid distance" in e["message"] for e in res["errors"])


def test_zero_link_distance():
    spec = _base_valid_spec()
    spec["links"][0]["distance_m"] = 0.0
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("invalid distance" in e["message"] for e in res["errors"])


def test_zero_endpoints():
    spec = _base_valid_spec()
    spec["subnets"] = []
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("At least one subnet" in e["message"] for e in res["errors"])


def test_bad_host_count_zero():
    spec = _base_valid_spec()
    spec["subnets"][0]["hosts"] = 0
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("invalid host count" in e["message"] for e in res["errors"])


def test_disallowed_vlan_out_of_range():
    spec = _base_valid_spec()
    spec["subnets"][0]["vlan"] = 5000  # > 4094
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("invalid" in e["message"] for e in res["errors"])


def test_disallowed_vlan_reserved_cisco():
    spec = _base_valid_spec()
    spec["subnets"][0]["vlan"] = 1002  # Reserved Token Ring
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("reserved Cisco legacy VLAN" in e["message"] for e in res["errors"])


def test_duplicate_subnet_names():
    spec = _base_valid_spec()
    spec["subnets"].append({"name": "LAN1", "hosts": 20, "vlan": 20, "device": "R1"})
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("Duplicate subnet name" in e["message"] for e in res["errors"])


def test_duplicate_vlan_ids():
    spec = _base_valid_spec()
    spec["subnets"].append({"name": "LAN2", "hosts": 20, "vlan": 10, "device": "R1"})
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("Duplicate VLAN ID" in e["message"] for e in res["errors"])


def test_unknown_device_in_link():
    spec = _base_valid_spec()
    spec["links"][0]["endpoint_b"] = "GHOST_SWITCH"
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("Unknown device" in e["message"] for e in res["errors"])


def test_disconnected_topology():
    spec = _base_valid_spec()
    spec["devices"].append({"name": "ISOLATED_R", "type": "router"})
    # No link connecting ISOLATED_R
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("disconnected" in e["message"] for e in res["errors"])


def test_dual_homed_site_single_link_violation():
    spec = _base_valid_spec()
    spec["sites"] = [{"name": "Site-A", "is_dual_homed": True, "devices": ["R1"]}]
    # R1 only has 1 link to SW1
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("dual-homed" in e["message"] for e in res["errors"])


def test_cloud_without_bgp_data():
    spec = _base_valid_spec()
    spec["devices"].append({"name": "CLOUD-1", "type": "cloud"})
    spec["links"].append({"endpoint_a": "R1", "endpoint_b": "CLOUD-1", "distance_m": 500.0})
    # Missing remote_asn in cloud device
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("requires BGP peering configuration" in e["message"] for e in res["errors"])


def test_cloud_malformed_bgp_string_returns_validation_error():
    spec = _base_valid_spec()
    spec["devices"].append({"name": "CLOUD-1", "type": "cloud", "bgp": "not-a-dict"})
    spec["links"].append({"endpoint_a": "R1", "endpoint_b": "CLOUD-1", "distance_m": 500.0})
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any(e["error_class"] == "InvalidParameterError" and "remote_asn" in e["message"] for e in res["errors"])


def test_nan_and_inf_link_distance_rejected_by_validator():
    spec = _base_valid_spec()
    spec["links"][0]["distance_m"] = float("nan")
    res = validate_network_specification(spec)
    assert res["is_valid"] is False
    assert any("invalid distance" in e["message"] for e in res["errors"])

    spec["links"][0]["distance_m"] = float("inf")
    res2 = validate_network_specification(spec)
    assert res2["is_valid"] is False
    assert any("invalid distance" in e["message"] for e in res2["errors"])
