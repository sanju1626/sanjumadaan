"""
NetArchitect Routing Decision & Protocol Engine (L3)
Deterministic rule-based protocol selection based on site topology, subnet scale,
and administrative domain boundaries.
Rules:
  - Single site and <50 subnets: Single-Area OSPF (Area 0, RFC 2328, Link-State Dijkstra).
  - Multi-site or >=50 subnets: Multi-Area OSPF with ABR route summarization (RFC 4632 / RFC 2328).
  - Cloud / Multi-AS boundary: eBGP (RFC 4271) with private ASNs (RFC 6996) for route-domain isolation.
"""

from typing import Any
from engine.errors import InvalidParameterError


def determine_routing_architecture(
    site_count: int,
    subnet_count: int,
    has_cloud_vpc: bool = False,
    is_multi_as: bool = False,
    sites: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Select routing protocols and summarize routing architecture.
    Returns:
      {
        "primary_protocol": "OSPFv2 Single-Area" | "OSPFv2 Multi-Area",
        "exterior_protocol": "eBGP" | None,
        "ospf_mode": "single_area" | "multi_area",
        "areas": [{"area_id": 0, "name": "Backbone", "site": "HQ", "subnets": [...]}, ...],
        "ebgp_peers": [...],
        "rationale": str,
        "standards": list[str],
        "decision_record": dict,
      }
    """
    if site_count < 1:
        raise InvalidParameterError(f"Site count must be at least 1, got {site_count}")
    if subnet_count < 1:
        raise InvalidParameterError(f"Subnet count must be at least 1, got {subnet_count}")

    standards = []
    reasons = []

    # 1. Evaluate Interior Gateway Protocol (IGP)
    if site_count == 1 and subnet_count < 50:
        primary_protocol = "Single-Area OSPFv2 (Area 0)"
        ospf_mode = "single_area"
        standards.append("RFC 2328 (OSPF Version 2)")
        reasons.append(
            f"Network scale is single-site ({site_count} site) with {subnet_count} subnets (< 50 threshold). "
            f"A flat single-area design (Backbone Area 0) minimizes SPF CPU overhead, eliminates ABR inter-area route "
            f"propagation complexity, and provides sub-second Dijkstra SPF convergence without route summarization."
        )
    else:
        primary_protocol = "Multi-Area OSPFv2"
        ospf_mode = "multi_area"
        standards.extend(["RFC 2328 (OSPFv2)", "RFC 4632 (Classless Inter-domain Routing & Summarization)"])
        reasons.append(
            f"Network spans {site_count} site(s) with {subnet_count} subnets "
            f"({'multi-site topology' if site_count > 1 else '>=50 subnet scaling boundary'}). "
            f"Multi-Area OSPF is mandatory to constrain Link-State Advertisement (LSA) flooding within area boundaries. "
            f"Area Border Routers (ABRs) generate Type 3 Summary LSAs using 'area <id> range' summarization, protecting Area 0 "
            f"from remote link flap SPF recalculations and shrinking routing table size."
        )

    # 2. Evaluate Exterior Gateway Protocol (EGP / BGP)
    exterior_protocol = None
    ebgp_peers = []
    if has_cloud_vpc or is_multi_as:
        exterior_protocol = "eBGP (Exterior Border Gateway Protocol)"
        standards.extend(["RFC 4271 (BGP-4)", "RFC 6996 (Autonomous System Number Reservation for Private Use)"])
        reasons.append(
            f"Cloud VPC interconnect / Multi-AS boundary detected. Standard practice mandates eBGP peering "
            f"(RFC 4271) using private 16-bit Autonomous System Numbers (RFC 6996: AS 64512–65534). "
            f"eBGP enforces policy-based administrative route control, path-vector loop prevention (AS-Path), "
            f"and strict failure domain isolation between enterprise campus/WAN and public cloud provider infrastructure."
        )
        ebgp_peers.append({
            "local_asn": 65001,
            "remote_asn": 65010,
            "description": "Enterprise Core Edge to Cloud VPC Peering",
            "policy": "Advertise summarized enterprise prefix; receive default or VPC route.",
        })

    full_rationale = " ".join(reasons)

    decision_record = {
        "topic": "Routing Architecture & Protocol Selection",
        "selected_solution": f"{primary_protocol}{f' + {exterior_protocol}' if exterior_protocol else ''}",
        "inputs_used": {
            "site_count": site_count,
            "subnet_count": subnet_count,
            "has_cloud_vpc": has_cloud_vpc,
            "is_multi_as": is_multi_as,
        },
        "condition_triggered": (
            "Single-Site <50 Subnets -> Area 0"
            if (site_count == 1 and subnet_count < 50 and not has_cloud_vpc)
            else "Multi-Site / Scaling Threshold / Cloud Boundary -> Multi-Area OSPF + eBGP"
        ),
        "reasoning": full_rationale,
        "standard_or_math_basis": ", ".join(standards),
        "warnings": [],
    }

    return {
        "primary_protocol": primary_protocol,
        "exterior_protocol": exterior_protocol,
        "ospf_mode": ospf_mode,
        "ebgp_peers": ebgp_peers,
        "rationale": full_rationale,
        "standards": standards,
        "decision_record": decision_record,
    }
