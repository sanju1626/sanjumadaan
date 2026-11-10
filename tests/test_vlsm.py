"""
Unit Tests for Bitwise VLSM Subnet Allocation Engine
Strict requirement: Pure bitwise integer math is validated against the standard
ipaddress module as an independent reference test oracle.
Tests:
  - Exact fit in /24 passes; +1 host raises AddressSpaceExhaustedError
  - Root prefix /30 boundary allocation
  - Specific host counts: 1, 2, 254, 255
  - Stable descending order allocation
  - Bitwise natural boundary alignment: (network_int % size == 0)
  - Broadcast and gateway calculation correctness
  - 300-case seeded fuzzing oracle validation against ipaddress module
  - Exact contiguous wildcard masks for /0, /1, /8, /16, /23, /24, /25, /30, /31, /32
"""

import pytest
import random
import ipaddress
from engine.vlsm_engine import allocate_vlsm, compute_prefix_for_hosts, summarize_subnets
from engine.addr import (
    ip_to_int,
    int_to_ip,
    prefix_to_mask_int,
    prefix_to_wildcard_int,
    prefix_to_mask_str,
    prefix_to_wildcard_str,
)
from engine.errors import AddressSpaceExhaustedError, InvalidParameterError


def test_wildcard_mask_arithmetic_contiguous():
    # Wildcard masks for /0, /1, /8, /16, /23, /24, /25, /30, /31, /32
    # Verify: mask + wildcard == 0xFFFFFFFF (4294967295)
    prefixes = [0, 1, 8, 16, 23, 24, 25, 30, 31, 32]
    for p in prefixes:
        mask = prefix_to_mask_int(p)
        wc = prefix_to_wildcard_int(p)
        assert (mask + wc) == 0xFFFFFFFF, f"Failed for prefix /{p}: mask={mask}, wc={wc}"
        assert (mask & wc) == 0, f"Mask and wildcard overlap for /{p}"
        # Validate against ipaddress oracle
        if p > 0:
            oracle_net = ipaddress.IPv4Network(f"0.0.0.0/{p}")
            assert prefix_to_mask_str(p) == str(oracle_net.netmask)
            assert prefix_to_wildcard_str(p) == str(oracle_net.hostmask)


def test_exact_fit_in_slash_24_passes():
    # A /24 has 256 addresses (254 usable).
    # Requesting 254 hosts fits exactly in a /24 (254 + 2 = 256 -> /24).
    req = [{"name": "Subnet-Full", "hosts": 254}]
    res = allocate_vlsm("192.168.1.0/24", req)
    assert len(res["allocated_subnets"]) == 1
    sub = res["allocated_subnets"][0]
    assert sub["prefix"] == 24
    assert sub["size"] == 256
    assert sub["network"] == "192.168.1.0"
    assert sub["broadcast"] == "192.168.1.255"
    assert sub["usable_hosts"] == 254


def test_plus_one_host_exhausts_slash_24():
    # Requesting 255 hosts requires 255 + 2 = 257 -> next power of 2 is 512 (/23).
    # Since root is /24 (size 256), allocating 512 must raise AddressSpaceExhaustedError!
    req = [{"name": "Subnet-Overflow", "hosts": 255}]
    with pytest.raises(AddressSpaceExhaustedError) as exc_info:
        allocate_vlsm("192.168.1.0/24", req)
    assert exc_info.value.requested_hosts == 255


def test_root_prefix_slash_30():
    # Smallest valid multi-host root is /30 (size 4, 2 usable hosts)
    req = [{"name": "P2P-Link", "hosts": 2}]
    res = allocate_vlsm("10.0.0.0/30", req)
    assert len(res["allocated_subnets"]) == 1
    sub = res["allocated_subnets"][0]
    assert sub["prefix"] == 30
    assert sub["network"] == "10.0.0.0"
    assert sub["first_host"] == "10.0.0.1"
    assert sub["last_host"] == "10.0.0.2"
    assert sub["broadcast"] == "10.0.0.3"


def test_host_count_boundary_values():
    # Test specific host boundaries: 1, 2, 254, 255
    p1, s1, _ = compute_prefix_for_hosts(1, is_loopback=True)
    assert p1 == 32 and s1 == 1

    p2, s2, _ = compute_prefix_for_hosts(2, allow_rfc3021=True)
    assert p2 == 31 and s2 == 2

    p2_std, s2_std, _ = compute_prefix_for_hosts(2, allow_rfc3021=False)
    assert p2_std == 30 and s2_std == 4

    p254, s254, _ = compute_prefix_for_hosts(254)
    assert p254 == 24 and s254 == 256

    p255, s255, _ = compute_prefix_for_hosts(255)
    assert p255 == 23 and s255 == 512


def test_descending_order_and_natural_alignment():
    # Request subnets in mixed order; engine must allocate descending by size
    # and guarantee natural bitwise alignment: (network_int % size == 0).
    req = [
        {"name": "Small-1", "hosts": 10},
        {"name": "Large", "hosts": 600},
        {"name": "Medium", "hosts": 100},
        {"name": "Small-2", "hosts": 20},
    ]
    res = allocate_vlsm("172.16.0.0/16", req)
    allocated = res["allocated_subnets"]

    # Order must be Large (/22, 1024), Medium (/25, 128), Small-2 (/27, 32), Small-1 (/28, 16)
    assert allocated[0]["name"] == "Large"
    assert allocated[0]["size"] == 1024
    assert allocated[1]["name"] == "Medium"
    assert allocated[1]["size"] == 128

    # Check natural boundary alignment
    for s in allocated:
        net_int = s["network_int"]
        size = s["size"]
        assert net_int % size == 0, f"Subnet {s['name']} not aligned to boundary {size}"


def test_broadcast_and_gateways():
    req = [{"name": "Dept-A", "hosts": 50}]  # 50 + 2 = 52 -> /26 (size 64)
    res = allocate_vlsm("10.0.0.0/24", req)
    sub = res["allocated_subnets"][0]
    assert sub["network"] == "10.0.0.0"
    assert sub["first_host"] == "10.0.0.1"
    assert sub["last_host"] == "10.0.0.62"
    assert sub["broadcast"] == "10.0.0.63"
    assert sub["gateway"] == "10.0.0.1"


def test_300_case_seeded_fuzzing_vs_ipaddress_oracle():
    """
    300-case seeded fuzzing test comparing pure bitwise math against
    the independent standard library ipaddress oracle.
    """
    rng = random.Random(42)  # Deterministic seed for reproducible testing

    for case_idx in range(300):
        # Pick random root network
        o0 = rng.choice([10, 172, 192])
        o1 = rng.randint(0, 255) if o0 != 172 else rng.randint(16, 31)
        root_prefix = rng.randint(16, 24)
        root_mask = (0xFFFFFFFF << (32 - root_prefix)) & 0xFFFFFFFF
        raw_ip = (o0 << 24) | (o1 << 16) | (rng.randint(0, 255) << 8) | rng.randint(0, 255)
        root_net_int = raw_ip & root_mask
        root_cidr = f"{int_to_ip(root_net_int)}/{root_prefix}"

        # Generate 2 to 6 random subnet requests
        num_subnets = rng.randint(2, 6)
        subnets_req = []
        for i in range(num_subnets):
            hosts = rng.randint(2, 200)
            subnets_req.append({"name": f"Sub-{case_idx}-{i}", "hosts": hosts})

        try:
            res = allocate_vlsm(root_cidr, subnets_req)
            # Verify against ipaddress oracle
            oracle_root = ipaddress.IPv4Network(root_cidr)
            for sub in res["allocated_subnets"]:
                oracle_sub = ipaddress.IPv4Network(sub["cidr"])
                assert oracle_sub.subnet_of(oracle_root)
                assert str(oracle_sub.network_address) == sub["network"]
                assert str(oracle_sub.netmask) == sub["mask"]
                assert str(oracle_sub.hostmask) == sub["wildcard"]
                if sub["prefix"] < 31:
                    assert str(oracle_sub.broadcast_address) == sub["broadcast"]
                    assert str(list(oracle_sub.hosts())[0]) == sub["first_host"]
                    assert str(list(oracle_sub.hosts())[-1]) == sub["last_host"]
        except AddressSpaceExhaustedError:
            # Sizing exceeded root; valid outcome under fuzzing
            pass


def test_rfc3021_slash_31_point_to_point():
    req = [{"name": "P2P-RFC3021", "hosts": 2, "is_p2p": True}]
    res = allocate_vlsm("10.0.0.0/24", req, allow_rfc3021=True)
    sub = res["allocated_subnets"][0]
    assert sub["prefix"] == 31
    assert sub["size"] == 2
    assert sub["first_host"] == "10.0.0.0"
    assert sub["last_host"] == "10.0.0.1"
    assert "RFC 3021" in sub["broadcast"]


def test_grouped_allocation_disjoint_summaries():
    req = [
        {"name": "A1-Sub1", "hosts": 300, "group": "Area 1"},
        {"name": "A1-Sub2", "hosts": 200, "group": "Area 1"},
        {"name": "Cloud", "hosts": 250, "group": "Cloud VPC"},
    ]
    res = allocate_vlsm("10.0.0.0/16", req, group_by="group")
    a1 = ipaddress.IPv4Network(res["group_summaries"]["Area 1"]["summary_cidr"])
    cld = ipaddress.IPv4Network(res["group_summaries"]["Cloud VPC"]["summary_cidr"])
    assert not a1.overlaps(cld), "Grouped summaries must be strictly non-overlapping!"
    assert res["group_summaries"]["Cloud VPC"]["exact"] is True


def test_duplicate_subnet_name_raises():
    req = [{"name": "Dup", "hosts": 10}, {"name": "Dup", "hosts": 20}]
    with pytest.raises(InvalidParameterError):
        allocate_vlsm("10.0.0.0/24", req)


def test_host_bits_set_raises():
    req = [{"name": "Sub", "hosts": 10}]
    with pytest.raises(InvalidParameterError):
        allocate_vlsm("10.0.0.5/24", req)
