"""
NetArchitect Input & Topology Validation Engine
Comprehensive validation for custom network designs and preset integrity.
Checks:
  - Negative or zero distances
  - Zero or negative endpoint counts
  - Bad CIDR formats & root prefix ranges (1-30)
  - Host bits set in root network CIDRs
  - Bad host counts (hosts < 1)
  - VLAN IDs outside 2-4094 or inside Cisco reserved range 1002-1005
  - Duplicate device names, subnet names, or VLAN IDs
  - Unknown device references in links
  - Disconnected topologies (partitioned graphs)
  - Dual-homed sites configured with only one link
  - Cloud VPC edges without BGP peering parameters
"""

import math
from typing import Any
import networkx as nx
from engine.errors import (
    NetArchitectError,
    InvalidParameterError,
    PhysicalDistanceViolationError,
    AddressSpaceExhaustedError,
    ResiliencyViolationError,
)
from engine.addr import parse_cidr


def validate_network_specification(spec: dict[str, Any]) -> dict[str, Any]:
    """
    Validate a complete network specification dictionary.
    Returns:
      {
        "is_valid": bool,
        "errors": [{"field": str, "error_class": str, "message": str}],
        "warnings": [str],
        "sanitized_spec": dict | None,
      }
    """
    errors: list[dict[str, str]] = []
    warnings: list[str] = []

    if not isinstance(spec, dict):
        return {
            "is_valid": False,
            "errors": [{"field": "root", "error_class": "InvalidParameterError", "message": "Specification must be a JSON/dict object"}],
            "warnings": [],
            "sanitized_spec": None,
        }

    # 1. Root CIDR Validation
    root_cidr = spec.get("root_cidr")
    if not root_cidr:
        errors.append({"field": "root_cidr", "error_class": "InvalidParameterError", "message": "Root CIDR (e.g. '10.10.0.0/16') is required"})
    else:
        try:
            parse_cidr(root_cidr)
        except InvalidParameterError as e:
            errors.append({"field": "root_cidr", "error_class": "InvalidParameterError", "message": str(e)})

    # 2. Devices Validation
    devices = spec.get("devices", [])
    if not isinstance(devices, list) or len(devices) == 0:
        errors.append({"field": "devices", "error_class": "InvalidParameterError", "message": "At least one device must be defined"})

    device_names: set[str] = set()
    has_cloud_edge = False
    for idx, dev in enumerate(devices):
        if not isinstance(dev, dict):
            errors.append({"field": f"devices[{idx}]", "error_class": "InvalidParameterError", "message": "Device entry must be an object"})
            continue
        dname = dev.get("name")
        if not dname or not isinstance(dname, str):
            errors.append({"field": f"devices[{idx}].name", "error_class": "InvalidParameterError", "message": "Device missing a valid name"})
            continue
        if dname in device_names:
            errors.append({"field": f"devices[{idx}].name", "error_class": "InvalidParameterError", "message": f"Duplicate device name '{dname}'"})
        device_names.add(dname)

        dtype = str(dev.get("type", "")).lower()
        if dtype in ("cloud", "cloud-edge", "vpc"):
            has_cloud_edge = True
            # Cloud without BGP data
            bgp_data = dev.get("bgp")
            if isinstance(bgp_data, dict):
                remote_asn = bgp_data.get("remote_asn") or dev.get("remote_asn")
            elif bgp_data is None:
                remote_asn = dev.get("remote_asn")
            else:
                remote_asn = None
            if not remote_asn:
                errors.append({
                    "field": f"devices[{dname}].bgp",
                    "error_class": "InvalidParameterError",
                    "message": f"Cloud edge device '{dname}' requires BGP peering configuration (missing remote_asn).",
                })

    # 3. Subnets & Endpoints Validation
    subnets = spec.get("subnets", [])
    if not isinstance(subnets, list) or len(subnets) == 0:
        errors.append({"field": "subnets", "error_class": "InvalidParameterError", "message": "At least one subnet must be defined"})

    seen_subnets: set[str] = set()
    seen_vlans: set[int] = set()
    total_endpoints = 0

    for idx, s in enumerate(subnets):
        if not isinstance(s, dict):
            errors.append({"field": f"subnets[{idx}]", "error_class": "InvalidParameterError", "message": "Subnet entry must be an object"})
            continue
        sname = s.get("name")
        if not sname or not isinstance(sname, str):
            errors.append({"field": f"subnets[{idx}].name", "error_class": "InvalidParameterError", "message": "Subnet missing a valid name"})
            continue
        if sname in seen_subnets:
            errors.append({"field": f"subnets[{idx}].name", "error_class": "InvalidParameterError", "message": f"Duplicate subnet name '{sname}'"})
        seen_subnets.add(sname)

        hosts = s.get("hosts")
        if hosts is None or not isinstance(hosts, int) or hosts < 1:
            errors.append({
                "field": f"subnets[{sname}].hosts",
                "error_class": "InvalidParameterError",
                "message": f"Subnet '{sname}' has invalid host count: {hosts}. Must be integer >= 1.",
            })
        else:
            total_endpoints += hosts

        vlan = s.get("vlan")
        if vlan is not None:
            if not isinstance(vlan, int) or vlan < 2 or vlan > 4094:
                errors.append({
                    "field": f"subnets[{sname}].vlan",
                    "error_class": "InvalidParameterError",
                    "message": f"Subnet '{sname}' VLAN {vlan} is invalid. User VLANs must be between 2 and 4094 (VLAN 1 is default management).",
                })
            elif 1002 <= vlan <= 1005:
                errors.append({
                    "field": f"subnets[{sname}].vlan",
                    "error_class": "InvalidParameterError",
                    "message": f"Subnet '{sname}' uses reserved Cisco legacy VLAN ID {vlan} (1002-1005).",
                })
            elif vlan in seen_vlans:
                errors.append({
                    "field": f"subnets[{sname}].vlan",
                    "error_class": "InvalidParameterError",
                    "message": f"Duplicate VLAN ID {vlan} in subnet '{sname}'.",
                })
            else:
                seen_vlans.add(vlan)

    if total_endpoints == 0 and len(subnets) > 0:
        errors.append({
            "field": "subnets",
            "error_class": "InvalidParameterError",
            "message": "Total endpoints in network is 0. Network must support at least 1 host.",
        })

    # 4. Links Validation
    links = spec.get("links", [])
    if not isinstance(links, list):
        errors.append({"field": "links", "error_class": "InvalidParameterError", "message": "Links must be a list"})
        links = []

    G = nx.Graph()
    for d in device_names:
        G.add_node(d)

    for idx, l in enumerate(links):
        if not isinstance(l, dict):
            errors.append({"field": f"links[{idx}]", "error_class": "InvalidParameterError", "message": "Link entry must be an object"})
            continue
        u = l.get("endpoint_a")
        v = l.get("endpoint_b")
        dist = l.get("distance_m")

        if not u or u not in device_names:
            errors.append({
                "field": f"links[{idx}].endpoint_a",
                "error_class": "InvalidParameterError",
                "message": f"Unknown device '{u}' referenced in link {idx}",
            })
        if not v or v not in device_names:
            errors.append({
                "field": f"links[{idx}].endpoint_b",
                "error_class": "InvalidParameterError",
                "message": f"Unknown device '{v}' referenced in link {idx}",
            })
        if u and v and u == v:
            errors.append({
                "field": f"links[{idx}]",
                "error_class": "InvalidParameterError",
                "message": f"Self-loop link on device '{u}' is invalid",
            })

        if (
            dist is None
            or isinstance(dist, bool)
            or not isinstance(dist, (int, float))
            or math.isnan(dist)
            or math.isinf(dist)
            or dist <= 0
        ):
            errors.append({
                "field": f"links[{idx}].distance_m",
                "error_class": "InvalidParameterError",
                "message": f"Link '{u} <-> {v}' has invalid distance {dist}. Must be positive real number > 0.",
            })

        if u in device_names and v in device_names:
            G.add_edge(u, v)

    # 5. Graph Topology & Resiliency Checks
    if len(device_names) > 1:
        if not nx.is_connected(G):
            components = list(nx.connected_components(G))
            errors.append({
                "field": "topology",
                "error_class": "InvalidParameterError",
                "message": f"Topology is disconnected. Network has {len(components)} isolated partitions: {components}",
            })

    # Check dual-homed site constraints
    sites = spec.get("sites", [])
    for site in sites:
        if site.get("is_dual_homed", False):
            site_name = site.get("name")
            site_devs = site.get("devices", [])
            # Count external links connecting this site to others
            ext_links = 0
            for u, v in G.edges():
                if (u in site_devs and v not in site_devs) or (v in site_devs and u not in site_devs):
                    ext_links += 1
            if ext_links < 2:
                errors.append({
                    "field": f"sites[{site_name}]",
                    "error_class": "ResiliencyViolationError",
                    "message": (
                        f"Site '{site_name}' is declared dual-homed but has only {ext_links} external uplink. "
                        f"At least two distinct links are required for dual-homed resiliency."
                    ),
                })

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "sanitized_spec": spec if is_valid else None,
    }
