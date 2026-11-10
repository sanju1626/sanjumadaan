"""
Unit Tests for Topology Graph Analysis & Resiliency Engine
Tests:
  - Collapsed-core vs Three-tier selection based on scale and oversubscription
  - Latency calculation: 5 us/km propagation + 50 us/hop switching
  - Single-link failure keeps connectivity and reconverges within latency budget (N-1 criterion)
  - ResiliencyViolationError on topology partition
  - LatencyBudgetError when path latency exceeds design budget
"""

import pytest
from engine.topology import evaluate_tier_architecture, analyze_topology
from engine.errors import ResiliencyViolationError, LatencyBudgetError, InvalidParameterError


def test_tier_architecture_collapsed_core():
    # 3 access switches, 1600 endpoints -> Collapsed Core
    res = evaluate_tier_architecture(access_switch_count=3, total_endpoints=1600, building_count=3)
    assert res["tier_mode"] == "collapsed_core"
    assert "Two-Tier" in res["recommended_tier"]


def test_tier_architecture_three_tier():
    # 8 access switches, 3500 endpoints -> Three-Tier
    res = evaluate_tier_architecture(access_switch_count=8, total_endpoints=3500, building_count=6)
    assert res["tier_mode"] == "three_tier"
    assert "Three-Tier" in res["recommended_tier"]


def test_topology_latency_formula():
    # Link of 10 km (10,000 m):
    # Latency = 10 km * 5 us/km + 50 us/hop = 50 us + 50 us = 100 us (0.1 ms)
    nodes = [{"name": "A"}, {"name": "B"}]
    links = [{"endpoint_a": "A", "endpoint_b": "B", "distance_m": 10000.0}]
    res = analyze_topology(nodes, links, latency_budget_ms=1.0, enforce_resiliency=False)
    assert res["baseline_max_latency_us"] == 100.0
    assert res["baseline_max_latency_ms"] == 0.1


def test_topology_ring_n_minus_1_resiliency():
    # 3-node ring: A-B (15km), B-C (22km), C-A (35km)
    nodes = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    links = [
        {"endpoint_a": "A", "endpoint_b": "B", "distance_m": 15000.0},
        {"endpoint_a": "B", "endpoint_b": "C", "distance_m": 22000.0},
        {"endpoint_a": "C", "endpoint_b": "A", "distance_m": 35000.0},
    ]
    # Ring remains connected upon removing any single link
    res = analyze_topology(nodes, links, latency_budget_ms=5.0, enforce_resiliency=True)
    assert res["is_resilient_n_minus_1"] is True
    assert len(res["resiliency_evaluations"]) == 3
    for eval_item in res["resiliency_evaluations"]:
        assert eval_item["status"] == "Resilient (Reconverged)"
        assert eval_item["failover_max_latency_ms"] <= 5.0


def test_topology_resiliency_violation_error():
    # Linear topology: A - B - C. Removing A-B partitions A!
    nodes = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    links = [
        {"endpoint_a": "A", "endpoint_b": "B", "distance_m": 1000.0},
        {"endpoint_a": "B", "endpoint_b": "C", "distance_m": 1000.0},
    ]
    with pytest.raises(ResiliencyViolationError) as exc_info:
        analyze_topology(nodes, links, enforce_resiliency=True)
    assert "Topology Resiliency Violation" in str(exc_info.value)


def test_topology_latency_budget_error():
    # Long distance link exceeding tight budget
    nodes = [{"name": "A"}, {"name": "B"}]
    links = [{"endpoint_a": "A", "endpoint_b": "B", "distance_m": 1000000.0}]  # 1000 km = 5000 us = 5 ms
    with pytest.raises(LatencyBudgetError):
        analyze_topology(nodes, links, latency_budget_ms=2.0, enforce_resiliency=False)
