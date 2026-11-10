"""
NetArchitect Network Topology & Graph Analysis Engine
Evaluates network tier architecture (collapsed-core vs three-tier),
calculates graph-theoretic propagation and hop latency, and verifies N-1 resiliency.
Formulae:
  - Latency: 5 us/km (optical propagation delay) + 50 us/hop (L2/L3 frame forwarding delay)
  - Resiliency: All device pairs must remain connected after removal of any single redundant link.
"""

from typing import Any
import networkx as nx
from engine.errors import (
    ResiliencyViolationError,
    LatencyBudgetError,
    InvalidParameterError,
)


def evaluate_tier_architecture(
    access_switch_count: int,
    total_endpoints: int,
    building_count: int = 1,
    access_ports_per_switch: int = 24,
    uplink_bandwidth_gbps: float = 10.0,
    downlink_bandwidth_gbps: float = 1.0,
) -> dict[str, Any]:
    """
    Determine whether Collapsed-Core (2-tier) or Three-Tier (Core + Distribution + Access)
    is architecturally recommended based on switch scale and oversubscription.
    """
    if access_switch_count < 1:
        raise InvalidParameterError(f"Access switch count must be >= 1, got {access_switch_count}")
    if total_endpoints < 1:
        raise InvalidParameterError(f"Total endpoints must be >= 1, got {total_endpoints}")

    # Calculate access layer oversubscription ratio
    # e.g., 24x 1G downlinks (24 Gbps) / 2x 10G uplinks (20 Gbps) = 1.2 : 1
    # Standard enterprise guideline: <= 20:1 for access layer, <= 4:1 for distribution
    total_downlink_cap = access_ports_per_switch * downlink_bandwidth_gbps
    # Dual 10G uplinks per access switch
    total_uplink_cap = 2 * uplink_bandwidth_gbps
    oversubscription_ratio = total_downlink_cap / total_uplink_cap if total_uplink_cap > 0 else 1.0

    # Decision rule
    if access_switch_count <= 4 and total_endpoints < 2500 and building_count <= 3:
        recommended_tier = "Two-Tier Collapsed Core (Core/Distribution combined)"
        tier_mode = "collapsed_core"
        rationale = (
            f"Selected Two-Tier Collapsed Core architecture. With {access_switch_count} access switches "
            f"and {total_endpoints} endpoints across {building_count} building(s), a dedicated distribution "
            f"layer is unnecessary. Collapsing Core and Distribution into high-throughput L3 switches eliminates "
            f"an active forwarding hop (saving ~50 us latency), lowers hardware Capex/Opex, and simplifies "
            f"STP root placement while maintaining access uplink oversubscription at {oversubscription_ratio:.1f}:1 "
            f"(well within the <=20:1 enterprise campus best-practice ceiling)."
        )
    else:
        recommended_tier = "Three-Tier Hierarchical (Core, Distribution, Access)"
        tier_mode = "three_tier"
        rationale = (
            f"Selected Three-Tier Hierarchical architecture. Large scale ({access_switch_count} access switches, "
            f"{total_endpoints} endpoints across {building_count} buildings) requires an independent Distribution layer. "
            f"Distribution switches aggregate building uplinks, perform L3 default gateway routing, enforce ACL security "
            f"policies, and prevent L2 Spanning-Tree broadcast domain propagation from reaching the ultra-fast campus core backbone."
        )

    decision_record = {
        "topic": "Topology Architecture Tier",
        "selected_solution": recommended_tier,
        "inputs_used": {
            "access_switches": access_switch_count,
            "total_endpoints": total_endpoints,
            "buildings": building_count,
            "oversubscription_ratio": f"{oversubscription_ratio:.1f}:1",
        },
        "condition_triggered": (
            "Access Switches <= 4 and Endpoints < 2500 -> Collapsed Core"
            if tier_mode == "collapsed_core"
            else "Access Switches > 4 or Endpoints >= 2500 -> Three Tier"
        ),
        "reasoning": rationale,
        "standard_or_math_basis": "Cisco Enterprise Campus 3.0 Hierarchical Design Principles",
        "warnings": [],
    }

    return {
        "recommended_tier": recommended_tier,
        "tier_mode": tier_mode,
        "oversubscription_ratio": oversubscription_ratio,
        "rationale": rationale,
        "decision_record": decision_record,
    }


def build_topology_graph(nodes: list[dict[str, Any]], links: list[dict[str, Any]]) -> nx.Graph:
    """Build a NetworkX undirected graph from topology nodes and links."""
    G = nx.Graph()
    for n in nodes:
        name = n["name"]
        G.add_node(name, **n)

    for l in links:
        u = l["endpoint_a"]
        v = l["endpoint_b"]
        dist_m = float(l.get("distance_m", 100.0))
        dist_km = dist_m / 1000.0
        # Latency of this single link: 5 us/km propagation delay + 50 us hop forwarding delay
        hop_latency_us = (dist_km * 5.0) + 50.0
        edge_data = dict(l)
        edge_data["distance_m"] = dist_m
        edge_data["distance_km"] = dist_km
        edge_data["latency_us"] = hop_latency_us
        G.add_edge(u, v, **edge_data)

    return G


def analyze_topology(
    nodes: list[dict[str, Any]],
    links: list[dict[str, Any]],
    latency_budget_ms: float | None = None,
    enforce_resiliency: bool = True,
    single_homed_allowed: set[str] | None = None,
) -> dict[str, Any]:
    """
    Perform graph analysis on network topology:
      1. Calculate all-pairs shortest paths and propagation + hop latencies.
      2. Check N-1 single link failure resiliency.
      3. Verify latency within design budget (e.g. 5 ms in Metro MAN).
    """
    G = build_topology_graph(nodes, links)
    allowed_leaves = single_homed_allowed or set()

    # Verify basic graph connectivity
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        raise InvalidParameterError(f"Network topology is disconnected. Found {len(components)} isolated segments: {components}")

    # Compute baseline all-pairs shortest path and latency
    node_list = list(G.nodes())
    pair_latencies: dict[str, float] = {}
    path_details: list[dict[str, Any]] = []

    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            u, v = node_list[i], node_list[j]
            try:
                path = nx.shortest_path(G, source=u, target=v, weight="latency_us")
                total_latency_us = 0.0
                total_distance_km = 0.0
                hop_count = len(path) - 1

                for step in range(len(path) - 1):
                    edge_data = G[path[step]][path[step + 1]]
                    total_distance_km += edge_data.get("distance_km", 0.0)
                    total_latency_us += edge_data.get("latency_us", 50.0)

                pair_key = f"{u} <-> {v}"
                pair_latencies[pair_key] = total_latency_us
                path_details.append({
                    "pair": pair_key,
                    "path": path,
                    "hops": hop_count,
                    "distance_km": round(total_distance_km, 3),
                    "latency_us": round(total_latency_us, 2),
                    "latency_ms": round(total_latency_us / 1000.0, 4),
                })
            except nx.NetworkXNoPath:
                pair_latencies[f"{u} <-> {v}"] = float("inf")

    max_latency_us = max(pair_latencies.values()) if pair_latencies else 0.0
    max_latency_ms = max_latency_us / 1000.0

    # Latency Budget Evaluation
    latency_violation = False
    if latency_budget_ms is not None:
        if max_latency_ms > latency_budget_ms:
            latency_violation = True
            raise LatencyBudgetError(
                f"Latency Budget Exceeded: Worst-case baseline latency of {max_latency_ms:.2f} ms "
                f"exceeds the design budget of {latency_budget_ms:.2f} ms.",
                measured_latency_us=max_latency_us,
                budget_latency_us=latency_budget_ms * 1000.0,
            )

    # N-1 Resiliency Verification (Remove each link one by one)
    resiliency_results = []
    edges = list(G.edges(data=True))

    for u, v, data in edges:
        G_temp = G.copy()
        G_temp.remove_edge(u, v)
        link_id = f"{u} <-> {v}"

        # If either u or v is an explicitly allowed single-homed leaf (like a cloud edge or leaf access switch),
        # then removing its only uplink will isolate it, which is expected and logged as a warning.
        is_leaf_link = (u in allowed_leaves and G.degree(u) == 1) or (v in allowed_leaves and G.degree(v) == 1)

        if not nx.is_connected(G_temp):
            if is_leaf_link:
                resiliency_results.append({
                    "failed_link": link_id,
                    "status": "Warning (Leaf Link)",
                    "message": f"Removal of link {link_id} isolates single-homed node. Architectural warning generated.",
                })
            elif enforce_resiliency:
                raise ResiliencyViolationError(
                    f"Topology Resiliency Violation (N-1 Failure): Removal of link '{link_id}' "
                    f"partitions the network into {nx.number_connected_components(G_temp)} disconnected segments! "
                    f"Redundant dual-homing is required for all backbone nodes."
                )
            else:
                resiliency_results.append({
                    "failed_link": link_id,
                    "status": "Partitioned",
                    "message": f"Link {link_id} failure partitions network.",
                })
        else:
            # Recheck latency under link failure
            failover_max_lat_us = 0.0
            for i in range(len(node_list)):
                for j in range(i + 1, len(node_list)):
                    src, dst = node_list[i], node_list[j]
                    try:
                        p = nx.shortest_path(G_temp, source=src, target=dst, weight="latency_us")
                        lat = sum(G_temp[p[k]][p[k + 1]]["latency_us"] for k in range(len(p) - 1))
                        failover_max_lat_us = max(failover_max_lat_us, lat)
                    except nx.NetworkXNoPath:
                        pass
            failover_max_ms = failover_max_lat_us / 1000.0

            if latency_budget_ms is not None and failover_max_ms > latency_budget_ms:
                if enforce_resiliency:
                    raise LatencyBudgetError(
                        f"Failover Latency Budget Exceeded: When link '{link_id}' fails, "
                        f"reconverged worst-case latency increases to {failover_max_ms:.2f} ms, "
                        f"which exceeds the {latency_budget_ms:.2f} ms budget.",
                        measured_latency_us=failover_max_lat_us,
                        budget_latency_us=latency_budget_ms * 1000.0,
                    )

            resiliency_results.append({
                "failed_link": link_id,
                "status": "Resilient (Reconverged)",
                "failover_max_latency_ms": round(failover_max_ms, 4),
            })

    is_resilient_n_minus_1 = bool(resiliency_results) and all(
        r["status"] == "Resilient (Reconverged)" for r in resiliency_results
    )
    core_backbone_resilient = bool(resiliency_results) and all(
        r["status"] != "Partitioned" for r in resiliency_results
    )

    return {
        "node_count": G.number_of_nodes(),
        "link_count": G.number_of_edges(),
        "baseline_max_latency_us": round(max_latency_us, 2),
        "baseline_max_latency_ms": round(max_latency_ms, 4),
        "latency_budget_ms": latency_budget_ms,
        "path_details": path_details,
        "resiliency_evaluations": resiliency_results,
        "is_resilient_n_minus_1": is_resilient_n_minus_1,
        "core_backbone_resilient": core_backbone_resilient,
        "latency_statement": (
            f"Calculated worst-case latency: {max_latency_ms:.2f} ms. "
            f"Note: Design latency targets are computed objectives based on standard 5 us/km optical propagation "
            f"delay and 50 us/hop switching latency under uncontended bandwidth assumptions — never guaranteed "
            f"under arbitrary queuing contention or carrier network congestion."
        ),
    }
