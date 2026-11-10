"""
NetArchitect VLSM & IP Subnet Allocation Engine (L3)
Pure bitwise integer arithmetic (<<, >>, &, |, ~) with zero ipaddress module usage.
Features:
  - Exact prefix sizing: need = hosts + 2 -> 32 - ceil(log2(need))
  - Stable descending allocation with bitwise natural boundary alignment: (cursor + size - 1) & ~(size - 1)
  - Strict zero-overlap verification
  - AddressSpaceExhaustedError with capacity accounting
  - RFC 3021 /31 point-to-point support option & /32 loopback support
  - Contiguous Area/Domain grouped allocation with exact supernet summarization
  - Arithmetic trace generation for viva voce defense
"""

import math
from typing import Any
from engine.errors import AddressSpaceExhaustedError, InvalidParameterError
from engine.addr import (
    ip_to_int,
    int_to_ip,
    prefix_to_mask_int,
    prefix_to_wildcard_int,
    parse_cidr,
)


def compute_prefix_for_hosts(hosts: int, allow_rfc3021: bool = False, is_loopback: bool = False) -> tuple[int, int, str]:
    """
    Calculate prefix length and block size from host count.
    Returns (prefix, size, arithmetic_explanation).
    """
    if not isinstance(hosts, int) or hosts < 1:
        raise InvalidParameterError(f"Host count must be an integer >= 1, got {hosts}")

    if is_loopback or hosts == 1:
        # Loopback interface (/32)
        return 32, 1, "1 host (Loopback) -> 1 address -> 2^0 -> /32"

    if allow_rfc3021 and hosts == 2:
        # RFC 3021 /31 Subnet for Point-to-Point Links
        return 31, 2, "2 hosts (RFC 3021 P2P Link) -> 2 addresses -> 2^1 -> /31"

    # Standard subnet: Network ID + Broadcast require 2 overhead addresses
    need = hosts + 2
    power = math.ceil(math.log2(need))
    if power < 2:
        power = 2
    prefix = 32 - power
    if prefix < 0:
        raise AddressSpaceExhaustedError(
            f"Host requirement of {hosts} exceeds 32-bit IPv4 address space",
            remaining_hosts=0,
            requested_hosts=hosts,
        )
    size = 1 << power
    arithmetic_str = f"{hosts} hosts + 2 = {need} -> {size} = 2^{power} -> /{prefix}"
    return prefix, size, arithmetic_str


def summarize_subnets(subnets: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute minimal covering supernet (CIDR summary) for a list of subnets.
    Returns:
      {
        "summary_cidr": "10.10.0.0/19",
        "exact": True/False,  # True if the summary exactly spans the subnets without holes
        "start_ip": str,
        "end_ip": str,
        "total_allocated_size": int,
        "summary_size": int
      }
    """
    if not subnets:
        return {"summary_cidr": None, "exact": True, "summary_size": 0, "total_allocated_size": 0}

    min_ip = min(s["network_int"] for s in subnets)
    max_end = max(s["end_int"] for s in subnets)
    total_allocated = sum(s["size"] for s in subnets)

    span = max_end - min_ip
    # Find minimal power-of-2 block covering span starting at aligned boundary
    power = math.ceil(math.log2(span)) if span > 0 else 0
    size = 1 << power
    aligned_start = min_ip & ~(size - 1)

    # Ensure covering
    while aligned_start + size < max_end:
        power += 1
        size = 1 << power
        aligned_start = min_ip & ~(size - 1)

    summary_prefix = 32 - power
    summary_cidr = f"{int_to_ip(aligned_start)}/{summary_prefix}"
    is_exact = (aligned_start == min_ip) and (aligned_start + size == max_end) and (total_allocated == size)

    return {
        "summary_cidr": summary_cidr,
        "summary_network": int_to_ip(aligned_start),
        "summary_prefix": summary_prefix,
        "summary_mask": int_to_ip(prefix_to_mask_int(summary_prefix)),
        "summary_wildcard": int_to_ip(prefix_to_wildcard_int(summary_prefix)),
        "exact": is_exact,
        "start_ip": int_to_ip(aligned_start),
        "end_ip": int_to_ip(aligned_start + size - 1),
        "total_allocated_size": total_allocated,
        "summary_size": size,
    }


def allocate_vlsm(
    root_cidr: str,
    subnets_req: list[dict[str, Any]],
    allow_rfc3021: bool = False,
    group_by: str | None = None,
) -> dict[str, Any]:
    """
    Perform Bitwise VLSM allocation within a root CIDR block.

    Parameters:
      - root_cidr: IPv4 CIDR string (e.g. '10.10.0.0/16')
      - subnets_req: list of dicts:
          [{"name": "Data-A", "hosts": 300, "vlan": 10, "group": "Area 0", ...}]
      - allow_rfc3021: allow /31 for 2-host point-to-point links (RFC 3021)
      - group_by: optional key to group contiguous allocations (e.g. 'area' or 'site')

    Returns:
      Comprehensive allocation dict including:
        - allocated_subnets: list of detailed subnet dicts
        - root_cidr, root_prefix, root_size, total_used_size, remaining_size
        - overall_utilization_pct, overall_efficiency_pct
        - group_summaries: dict of summaries per group
    """
    # 1. Parse and validate root CIDR
    root_ip, root_prefix, original_root = parse_cidr(root_cidr)
    root_size = 1 << (32 - root_prefix)
    root_end = root_ip + root_size

    # 2. Validate input subnets
    if not subnets_req:
        raise InvalidParameterError("Subnet request list cannot be empty")

    seen_names = set()
    seen_vlans = set()
    validated_req = []

    for idx, s in enumerate(subnets_req):
        if not isinstance(s, dict):
            raise InvalidParameterError(f"Subnet specification at index {idx} must be a dict")
        name = s.get("name")
        if not name or not isinstance(name, str):
            raise InvalidParameterError(f"Subnet at index {idx} has missing or invalid name: {name}")
        if name in seen_names:
            raise InvalidParameterError(f"Duplicate subnet name '{name}' detected. Subnet names must be unique.")
        seen_names.add(name)

        hosts = s.get("hosts")
        if hosts is None or not isinstance(hosts, int) or hosts < 1:
            raise InvalidParameterError(f"Subnet '{name}' has invalid host count: {hosts}. Must be integer >= 1.")

        vlan = s.get("vlan")
        if vlan is not None:
            if not isinstance(vlan, int) or vlan < 1 or vlan > 4094:
                raise InvalidParameterError(f"Subnet '{name}' has invalid VLAN ID {vlan}. Must be 1-4094.")
            # Disallow Cisco reserved range 1002-1005
            if 1002 <= vlan <= 1005:
                raise InvalidParameterError(f"Subnet '{name}' uses reserved Cisco VLAN ID {vlan} (1002-1005).")
            if vlan in seen_vlans:
                raise InvalidParameterError(f"Duplicate VLAN ID {vlan} in subnet '{name}'. VLAN IDs must be unique.")
            seen_vlans.add(vlan)

        item = dict(s)
        # Sizing calculation
        is_loop = bool(item.get("is_loopback", False))
        is_p2p = bool(item.get("is_p2p", False)) or (hosts == 2)
        prefix, size, arith_str = compute_prefix_for_hosts(
            hosts,
            allow_rfc3021=allow_rfc3021 and is_p2p,
            is_loopback=is_loop,
        )
        item["prefix"] = prefix
        item["size"] = size
        item["arithmetic_trace"] = arith_str
        validated_req.append(item)

    # 3. Handle Grouped vs Flat Allocation
    # If group_by is requested, sort within each group descending, and sort groups
    cursor = root_ip
    allocated_subnets: list[dict[str, Any]] = []

    if group_by:
        # Group items and sort groups descending by aligned summary block size (stable)
        groups: dict[str, list[dict[str, Any]]] = {}
        for item in validated_req:
            grp = item.get(group_by, "Default")
            groups.setdefault(grp, []).append(item)

        group_batches = []
        for grp_name, group_items in groups.items():
            group_items.sort(key=lambda x: (x["size"], x["hosts"]), reverse=True)
            grp_total_req = sum(item["size"] for item in group_items)
            grp_power = math.ceil(math.log2(grp_total_req)) if grp_total_req > 0 else 0
            grp_aligned_size = 1 << grp_power
            group_batches.append((grp_name, group_items, grp_aligned_size))

        group_batches.sort(key=lambda b: b[2], reverse=True)

        # Process each group into its own isolated summary supernet block
        for grp_name, group_items, grp_aligned_size in group_batches:
            # Align cursor to group boundary so the entire group block can be summarized cleanly
            grp_start = (cursor + grp_aligned_size - 1) & ~(grp_aligned_size - 1)
            cursor = grp_start

            for item in group_items:
                size = item["size"]
                prefix = item["prefix"]
                hosts = item["hosts"]

                # Bitwise boundary alignment: start = (cursor + size - 1) & ~(size - 1)
                start = (cursor + size - 1) & ~(size - 1)
                end = start + size

                if end > root_end:
                    remaining_cap = max(0, root_end - cursor)
                    raise AddressSpaceExhaustedError(
                        f"Root address space '{root_cidr}' exhausted while allocating subnet '{item['name']}' "
                        f"(requested /{prefix}, size {size}). Current cursor: {int_to_ip(cursor)}, "
                        f"Root end: {int_to_ip(root_end)}. Remaining capacity: {remaining_cap} addresses.",
                        remaining_hosts=remaining_cap,
                        requested_hosts=hosts,
                    )

                alloc_info = _build_subnet_record(item, start, prefix, size)
                allocated_subnets.append(alloc_info)
                cursor = end

            # Advance cursor past the entire group summary block so no subsequent group leaks into slack space
            cursor = max(cursor, grp_start + grp_aligned_size)
    else:
        # Flat allocation: Stable sort all descending by size
        validated_req.sort(key=lambda x: (x["size"], x["hosts"]), reverse=True)

        for item in validated_req:
            size = item["size"]
            prefix = item["prefix"]
            hosts = item["hosts"]

            # Bitwise boundary alignment
            start = (cursor + size - 1) & ~(size - 1)
            end = start + size

            if end > root_end:
                remaining_cap = max(0, root_end - cursor)
                raise AddressSpaceExhaustedError(
                    f"Root address space '{root_cidr}' exhausted while allocating subnet '{item['name']}' "
                    f"(requested /{prefix}, size {size}). Current cursor: {int_to_ip(cursor)}, "
                    f"Root end: {int_to_ip(root_end)}. Remaining capacity: {remaining_cap} addresses.",
                    remaining_hosts=remaining_cap,
                    requested_hosts=hosts,
                )

            alloc_info = _build_subnet_record(item, start, prefix, size)
            allocated_subnets.append(alloc_info)
            cursor = end

    # 4. Strict Zero-Overlap Verification
    _verify_zero_overlap(allocated_subnets)

    # 5. Global Metrics & Group Summaries
    total_allocated_size = sum(s["size"] for s in allocated_subnets)
    total_requested_hosts = sum(s["requested_hosts"] for s in allocated_subnets)
    total_usable_hosts = sum(s["usable_hosts"] for s in allocated_subnets)
    remaining_space = root_size - total_allocated_size

    # Utilization = total allocated block addresses / root address capacity
    overall_utilization_pct = (total_allocated_size / root_size) * 100.0 if root_size > 0 else 0.0
    # Efficiency = total requested hosts / total allocated block addresses
    overall_efficiency_pct = (total_requested_hosts / total_allocated_size) * 100.0 if total_allocated_size > 0 else 0.0

    # Group summaries if applicable
    group_summaries = {}
    distinct_groups = {s.get("group") for s in allocated_subnets if s.get("group") is not None}
    for g in distinct_groups:
        grp_subs = [s for s in allocated_subnets if s.get("group") == g]
        group_summaries[g] = summarize_subnets(grp_subs)

    return {
        "root_cidr": root_cidr,
        "root_network": int_to_ip(root_ip),
        "root_prefix": root_prefix,
        "root_size": root_size,
        "allocated_subnets": allocated_subnets,
        "total_requested_hosts": total_requested_hosts,
        "total_allocated_size": total_allocated_size,
        "total_usable_hosts": total_usable_hosts,
        "remaining_addresses": remaining_space,
        "overall_utilization_pct": round(overall_utilization_pct, 2),
        "overall_efficiency_pct": round(overall_efficiency_pct, 2),
        "group_summaries": group_summaries,
    }


def _build_subnet_record(item: dict[str, Any], start: int, prefix: int, size: int) -> dict[str, Any]:
    """Format and compute all address boundaries for an allocated block using bitwise integer math."""
    mask_int = prefix_to_mask_int(prefix)
    wildcard_int = prefix_to_wildcard_int(prefix)

    network_int = start
    end_int = start + size
    broadcast_int = end_int - 1

    # Host assignment according to prefix semantics
    if prefix == 32:
        # Single IP host/loopback
        first_host_int = network_int
        last_host_int = network_int
        gateway_int = network_int
        broadcast_str = "N/A (/32 Host)"
        usable_hosts = 1
    elif prefix == 31:
        # RFC 3021 Point-to-Point
        first_host_int = network_int
        last_host_int = network_int + 1
        gateway_int = network_int
        broadcast_str = "N/A (RFC 3021 /31)"
        usable_hosts = 2
    else:
        # Standard subnet
        first_host_int = network_int + 1
        last_host_int = broadcast_int - 1
        gateway_int = first_host_int  # Default first usable host as default gateway
        broadcast_str = int_to_ip(broadcast_int)
        usable_hosts = max(0, size - 2)

    requested_hosts = item["hosts"]
    util_pct = (requested_hosts / usable_hosts) * 100.0 if usable_hosts > 0 else 100.0
    eff_pct = (requested_hosts / size) * 100.0 if size > 0 else 100.0

    return {
        "name": item["name"],
        "requested_hosts": requested_hosts,
        "prefix": prefix,
        "size": size,
        "usable_hosts": usable_hosts,
        "network": int_to_ip(network_int),
        "cidr": f"{int_to_ip(network_int)}/{prefix}",
        "mask": int_to_ip(mask_int),
        "wildcard": int_to_ip(wildcard_int),
        "first_host": int_to_ip(first_host_int),
        "last_host": int_to_ip(last_host_int),
        "broadcast": broadcast_str,
        "gateway": int_to_ip(gateway_int),
        "is_p2p": item.get("is_p2p", False),
        "is_loopback": item.get("is_loopback", False),
        "vlan": item.get("vlan"),
        "group": item.get("group"),
        "device": item.get("device"),
        "description": item.get("description", item["name"]),
        "utilization_pct": round(util_pct, 1),
        "efficiency_pct": round(eff_pct, 1),
        "arithmetic_trace": item.get("arithmetic_trace", ""),
        "network_int": network_int,
        "end_int": end_int,
        "mask_int": mask_int,
        "wildcard_int": wildcard_int,
    }


def _verify_zero_overlap(subnets: list[dict[str, Any]]) -> None:
    """
    Formally verify zero address space overlap across all allocated subnets.
    O(N log N) interval overlap check.
    """
    sorted_by_start = sorted(subnets, key=lambda s: s["network_int"])
    for i in range(len(sorted_by_start) - 1):
        curr = sorted_by_start[i]
        nxt = sorted_by_start[i + 1]
        if curr["end_int"] > nxt["network_int"]:
            raise AddressSpaceExhaustedError(
                f"Bitwise Overlap Detected between '{curr['name']}' ({curr['cidr']}) "
                f"and '{nxt['name']}' ({nxt['cidr']})! Integrity check failed."
            )
        # Also verify alignment
        if curr["network_int"] % curr["size"] != 0:
            raise InvalidParameterError(
                f"Subnet '{curr['name']}' network {curr['network']} is not aligned to boundary {curr['size']}"
            )
