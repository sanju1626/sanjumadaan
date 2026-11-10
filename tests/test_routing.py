"""
Unit Tests for Routing Decision & Route Summarization Engine
Tests:
  - 49 vs 50 subnets scaling threshold (Area 0 vs Multi-Area OSPF)
  - Multi-site routing protocol selection (Multi-Area OSPF)
  - Multi-cloud / Multi-AS boundary (eBGP peering)
  - Route summarization exact vs covering summary flags
"""

import pytest
from engine.routing_engine import determine_routing_architecture
from engine.vlsm_engine import summarize_subnets
from engine.addr import ip_to_int


def test_routing_under_50_subnets_single_site():
    # 49 subnets, single site -> Single-Area OSPF (Area 0)
    res = determine_routing_architecture(site_count=1, subnet_count=49)
    assert "Single-Area OSPF" in res["primary_protocol"]
    assert res["ospf_mode"] == "single_area"
    assert res["exterior_protocol"] is None
    assert "Area 0" in res["rationale"]


def test_routing_at_50_subnets_scaling_boundary():
    # 50 subnets, single site -> Multi-Area OSPF (scaling boundary reached)
    res = determine_routing_architecture(site_count=1, subnet_count=50)
    assert "Multi-Area OSPF" in res["primary_protocol"]
    assert res["ospf_mode"] == "multi_area"
    assert "ABR" in res["rationale"]


def test_routing_multi_site():
    # Multi-site (3 sites, e.g. Metro MAN) -> Multi-Area OSPF
    res = determine_routing_architecture(site_count=3, subnet_count=10)
    assert "Multi-Area OSPF" in res["primary_protocol"]
    assert res["ospf_mode"] == "multi_area"


def test_routing_multi_cloud_and_as():
    # Cloud VPC presence or Multi-AS -> eBGP enabled with private ASN
    res = determine_routing_architecture(site_count=4, subnet_count=20, has_cloud_vpc=True, is_multi_as=True)
    assert "eBGP" in res["exterior_protocol"]
    assert len(res["ebgp_peers"]) > 0
    assert "RFC 4271" in res["decision_record"]["standard_or_math_basis"]
    assert "RFC 6996" in res["decision_record"]["standard_or_math_basis"]


def test_summarization_exact_match():
    # Two adjacent /24s (10.0.0.0/24 and 10.0.1.0/24) form an exact /23
    sub1 = {
        "network": "10.0.0.0",
        "network_int": ip_to_int("10.0.0.0"),
        "end_int": ip_to_int("10.0.0.0") + 256,
        "size": 256,
        "prefix": 24,
    }
    sub2 = {
        "network": "10.0.1.0",
        "network_int": ip_to_int("10.0.1.0"),
        "end_int": ip_to_int("10.0.1.0") + 256,
        "size": 256,
        "prefix": 24,
    }
    summary = summarize_subnets([sub1, sub2])
    assert summary["summary_cidr"] == "10.0.0.0/23"
    assert summary["exact"] is True


def test_summarization_covering_with_holes():
    # Subnets with a hole: 10.0.0.0/24 and 10.0.3.0/24
    # Covering summary is 10.0.0.0/22 (size 1024), but allocated is 512, so exact is False
    sub1 = {
        "network": "10.0.0.0",
        "network_int": ip_to_int("10.0.0.0"),
        "end_int": ip_to_int("10.0.0.0") + 256,
        "size": 256,
        "prefix": 24,
    }
    sub2 = {
        "network": "10.0.3.0",
        "network_int": ip_to_int("10.0.3.0"),
        "end_int": ip_to_int("10.0.3.0") + 256,
        "size": 256,
        "prefix": 24,
    }
    summary = summarize_subnets([sub1, sub2])
    assert summary["summary_cidr"] == "10.0.0.0/22"
    assert summary["exact"] is False
