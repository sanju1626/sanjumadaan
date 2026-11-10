"""
NetArchitect Cisco IOS Configuration Generator & Self-Check Engine
Generates copy-paste ready, production-grade Cisco IOS configurations for:
  - L2 Access Switches (Cisco Catalyst 2960-24TT)
  - L3 Core/Distribution Switches (Cisco Catalyst 3650-24PS / 3560-24PS)
  - Perimeter / WAN Branch Routers (Cisco 2911 / ISR 4331)

Features:
  - Strict trunk encapsulation and explicit allowed VLAN lists (never unrestricted)
  - Native VLAN 999 and DTP negotiation disabled (switchport nonegotiate)
  - Rapid-PVST+ root priority and edge portfast/bpduguard
  - Bitwise-derived wildcard masks for OSPF
  - Passive-interface default on OSPF with explicit routed link activations
  - ABR route summarization ('area <id> range')
  - eBGP peering with Null0 aggregate routes
  - Named Extended ACLs with explicit permit-any fallback documentation
  - VTY line management restriction (access-class) and SSH v2 RSA 2048
  - NAT Overload (PAT) on perimeter edge
  - MQC QoS priority queuing for latency-critical traffic
  - GRE over IPsec WAN tunnels with '--no-crypto' Packet Tracer compatibility switch
  - Rigorous self-check validator ensuring zero duplicate IPs, matching masks, and interface parity
"""

from typing import Any
from engine.errors import InvalidParameterError
from engine.addr import (
    ip_to_int,
    int_to_ip,
    prefix_to_mask_str,
    prefix_to_wildcard_str,
)


def _match_p2p_subnet(link: dict[str, Any], all_subnets: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    Strictly match a P2P /30 subnet to a link using exact link_id or both endpoint names.
    Avoids substring collisions (e.g. 'R-CHE' falsely matching 'BLR-CHE').
    """
    link_id = link.get("link_id", "")
    u = link["endpoint_a"]
    v = link["endpoint_b"]

    # 1. Exact P2P-<link_id> match
    exact = next((s for s in all_subnets if s.get("is_p2p") and s["name"] == f"P2P-{link_id}"), None)
    if exact:
        return exact

    # 2. Link ID substring match (e.g. 'DEL-CHE' in 'P2P-DEL-CHE')
    if link_id:
        by_id = next((s for s in all_subnets if s.get("is_p2p") and link_id in s["name"]), None)
        if by_id:
            return by_id

    # 3. Match where both endpoint identifiers appear
    return next(
        (s for s in all_subnets if s.get("is_p2p") and u in s["name"] and v in s["name"]),
        None,
    )


def generate_all_configs(
    scenario: dict[str, Any],
    vlsm_result: dict[str, Any],
    media_evals: list[dict[str, Any]],
    routing_result: dict[str, Any],
    platform: str = "pt",
    no_crypto: bool = False,
) -> dict[str, str]:
    """
    Generate complete Cisco IOS configuration files for all devices in a scenario.
    Returns: {device_name: config_text, ...}
    """
    devices = scenario.get("devices", [])
    subnets = vlsm_result.get("allocated_subnets", [])
    links = scenario.get("links", [])

    # Build lookup tables
    subnets_by_device: dict[str, list[dict[str, Any]]] = {}
    for s in subnets:
        d = s.get("device")
        if d:
            subnets_by_device.setdefault(d, []).append(s)

    links_by_device: dict[str, list[dict[str, Any]]] = {}
    for l in links:
        u = l["endpoint_a"]
        v = l["endpoint_b"]
        links_by_device.setdefault(u, []).append(l)
        links_by_device.setdefault(v, []).append(l)

    media_by_link: dict[str, dict[str, Any]] = {}
    for m in media_evals:
        media_by_link[m.get("link_id", "")] = m

    configs: dict[str, str] = {}
    l2_counter = 0
    router_counter = 0

    for dev in devices:
        name = dev["name"]
        dtype = dev.get("type", "router")

        dev_subnets = subnets_by_device.get(name, [])
        dev_links = links_by_device.get(name, [])

        if dtype == "l2_switch":
            l2_counter += 1
            cfg = _generate_l2_switch_config(
                dev, dev_subnets, dev_links, scenario, subnets, media_by_link, platform, l2_counter
            )
        elif dtype == "l3_switch":
            cfg = _generate_l3_switch_config(
                dev, dev_subnets, dev_links, scenario, subnets, media_by_link, routing_result, platform
            )
        else:
            router_counter += 1
            cfg = _generate_router_config(
                dev, dev_subnets, dev_links, scenario, subnets, media_by_link, routing_result, platform, no_crypto, router_counter, vlsm_result
            )

        configs[name] = cfg

    # Run self-check before returning
    self_check_report = run_configuration_self_check(configs, scenario, vlsm_result)
    if not self_check_report["passed"]:
        raise InvalidParameterError(f"Cisco Config Self-Check Failed: {self_check_report['errors']}")

    return configs


def _build_header(dev: dict[str, Any], scenario: dict[str, Any], platform: str) -> list[str]:
    name = dev["name"]
    model = dev.get("model_pt", "Generic")
    role = dev.get("role", "Network Infrastructure")
    return [
        f"! ===========================================================================",
        f"! NetArchitect Cisco IOS Configuration File",
        f"! Device: {name} (Model: {model}, Role: {role})",
        f"! Scenario: {scenario.get('name', 'Enterprise Network')}",
        f"! Target Platform: {platform.upper()} (Packet Tracer Compatible Syntax - Verify in PT)",
        f"! Generated algorithmically with bitwise-verified address structures",
        f"! ===========================================================================",
        f"version 15.0",
        f"service timestamps debug datetime msec",
        f"service timestamps log datetime msec",
        f"service password-encryption",
        f"!",
        f"hostname {name}",
        f"!",
        f"boot-start-marker",
        f"boot-end-marker",
        f"!",
        f"no ip domain-lookup",
        f"ip domain-name netarchitect.lab",
        f"!",
        f"! AAA & Local Administrative Security",
        f"username admin privilege 15 secret CHANGE_ME",
        f"enable secret CHANGE_ME",
        f"!",
        f"! Generate RSA 2048 key for SSH v2: (crypto key generate rsa modulus 2048)",
        f"ip ssh version 2",
        f"!",
    ]


def _build_footer(mgmt_subnet: dict[str, Any] | None) -> list[str]:
    lines = ["!"]
    if mgmt_subnet:
        lines.extend([
            f"! Management Access Control List (VTY Protection)",
            f"ip access-list standard ACL_MGMT_VTY",
            f" permit {mgmt_subnet['network']} {mgmt_subnet['wildcard']}",
            f" deny any log",
            f"!",
        ])
    lines.extend([
        f"! Line Console & VTY Control Plane Protection",
        f"line con 0",
        f" exec-timeout 10 0",
        f" logging synchronous",
        f" login local",
        f"line aux 0",
        f"line vty 0 4",
        f" exec-timeout 10 0",
        f" logging synchronous",
        f" login local",
        f" transport input ssh",
    ])
    if mgmt_subnet:
        lines.append(f" access-class ACL_MGMT_VTY in")
    lines.extend([
        f"line vty 5 15",
        f" transport input none",
        f"!",
        f"end",
        f"write memory",
        f"",
    ])
    return lines


def _generate_l2_switch_config(
    dev: dict[str, Any],
    dev_subnets: list[dict[str, Any]],
    dev_links: list[dict[str, Any]],
    scenario: dict[str, Any],
    all_subnets: list[dict[str, Any]],
    media_by_link: dict[str, dict[str, Any]],
    platform: str,
    l2_idx: int,
) -> str:
    name = dev["name"]
    lines = _build_header(dev, scenario, platform)

    # 1. Spanning-tree mode
    lines.extend([
        f"! Layer 2 Spanning-Tree Optimization",
        f"spanning-tree mode rapid-pvst",
        f"spanning-tree extend system-id",
        f"spanning-tree portfast default",
        f"spanning-tree portfast bpduguard default",
        f"!",
    ])

    # 2. VLANs definition
    vlan_subnets = [s for s in all_subnets if s.get("vlan") is not None]
    lines.append("! VLAN Database Definition")
    for s in vlan_subnets:
        lines.extend([
            f"vlan {s['vlan']}",
            f" name {s['name']}",
        ])
    lines.extend([
        f"vlan 999",
        f" name Parking_Native_Blackhole",
        f"!",
    ])

    # 3. Interfaces (Trunk and Access)
    lines.append("! Interface Allocations & Cabling")
    for link in dev_links:
        is_endpoint_a = (link["endpoint_a"] == name)
        intf = link["interface_a"] if is_endpoint_a else link["interface_b"]
        peer = link["endpoint_b"] if is_endpoint_a else link["endpoint_a"]
        link_id = link.get("link_id", "")
        med = media_by_link.get(link_id, {})
        med_type = med.get("media_type", "Cat6a")
        dist = med.get("distance_m", link.get("distance_m", 100))

        allowed_vlan_ids = sorted({s["vlan"] for s in all_subnets if s.get("vlan") is not None})
        vlan_str = ",".join(map(str, allowed_vlan_ids)) if allowed_vlan_ids else "1"

        lines.extend([
            f"interface {intf}",
            f" description Uplink Trunk to {peer} [Media: {med_type}, Distance: {dist:.0f}m]",
            f" switchport mode trunk",
            f" switchport trunk native vlan 999",
            f" switchport trunk allowed vlan {vlan_str}",
            f" switchport nonegotiate",
            f" no shutdown",
            f"!",
        ])

    # Access edge ports mapped to building VLANs (and Servers/Mgmt on first access switch)
    site_tag = dev.get("site", "Building A")
    local_vlans = [
        s for s in vlan_subnets
        if s.get("device") == name or (s.get("group") == site_tag and site_tag)
    ]
    if l2_idx == 1:
        assigned_groups = {d.get("site") for d in scenario.get("devices", []) if d.get("type") == "l2_switch"}
        assigned_devs = {d["name"] for d in scenario.get("devices", []) if d.get("type") == "l2_switch"}
        for s in vlan_subnets:
            if s not in local_vlans and s.get("device") not in assigned_devs and s.get("group") not in assigned_groups:
                local_vlans.append(s)
    if local_vlans:
        lines.append("! Access Edge Ports (Host-facing PortFast & BPDU Guard)")
        port_idx = 1
        for s in local_vlans:
            lines.extend([
                f"interface FastEthernet0/{port_idx}",
                f" description Access Port for {s['name']} (VLAN {s['vlan']})",
                f" switchport mode access",
                f" switchport access vlan {s['vlan']}",
                f" spanning-tree portfast",
                f" spanning-tree bpduguard enable",
                f" no shutdown",
                f"!",
            ])
            port_idx += 1
        data_vlan = local_vlans[0]["vlan"]
        lines.extend([
            f"interface range FastEthernet0/{port_idx} - 24",
            f" description Default Access Edge Ports ({site_tag})",
            f" switchport mode access",
            f" switchport access vlan {data_vlan}",
            f" spanning-tree portfast",
            f" spanning-tree bpduguard enable",
            f" no shutdown",
            f"!",
        ])

    # Management SVI on L2 switch (VLAN 99)
    mgmt_sub = next((s for s in all_subnets if s.get("vlan") == 99), None)
    if mgmt_sub:
        mgmt_gw_int = ip_to_int(mgmt_sub["gateway"])
        # Deterministic unique management IP using l2_idx (10 + 1, 10 + 2, ...)
        sw_mgmt_ip = int_to_ip(mgmt_gw_int + 10 + l2_idx)
        lines.extend([
            f"! Out-of-Band Management SVI",
            f"interface Vlan99",
            f" description Management Interface for {name}",
            f" ip address {sw_mgmt_ip} {mgmt_sub['mask']}",
            f" no shutdown",
            f"!",
            f"ip default-gateway {mgmt_sub['gateway']}",
            f"!",
        ])

    lines.extend(_build_footer(mgmt_sub))
    return "\n".join(lines)


def _generate_l3_switch_config(
    dev: dict[str, Any],
    dev_subnets: list[dict[str, Any]],
    dev_links: list[dict[str, Any]],
    scenario: dict[str, Any],
    all_subnets: list[dict[str, Any]],
    media_by_link: dict[str, dict[str, Any]],
    routing_result: dict[str, Any],
    platform: str,
) -> str:
    name = dev["name"]
    model = dev.get("model_pt", "3650-24PS")
    scenario_id = scenario.get("scenario_id", "")
    lines = _build_header(dev, scenario, platform)

    # L3 routing enable
    lines.extend([
        f"! Layer 3 Switching Architecture",
        f"ip routing",
        f"ip cef",
        f"!",
        f"! Spanning-Tree Root Determinism",
        f"spanning-tree mode rapid-pvst",
        f"spanning-tree extend system-id",
        f"spanning-tree vlan 1-4094 priority 4096",
        f"!",
    ])

    # QoS for Metro MAN HQ-CORE
    if scenario_id == "metro_man":
        lines.extend([
            f"! Modular QoS CLI (MQC) Low-Latency Queuing Architecture",
            f"class-map match-any CM_VOIP_FINTECH",
            f" match ip dscp ef",
            f" match ip dscp cs5",
            f"!",
            f"policy-map PM_METRO_QOS_EGRESS",
            f" class CM_VOIP_FINTECH",
            f"  priority percent 35",
            f" class class-default",
            f"  fair-queue",
            f"!",
        ])

    # Only define VLANs and SVIs owned by this L3 switch (or connected L2 switches)
    local_vlan_subnets = [s for s in dev_subnets if s.get("vlan") is not None]

    lines.append("! VLAN Database Definition")
    for s in local_vlan_subnets:
        lines.extend([
            f"vlan {s['vlan']}",
            f" name {s['name']}",
        ])
    lines.extend([
        f"vlan 999",
        f" name Parking_Native_Blackhole",
        f"!",
    ])

    # Trunk and Routed Interfaces
    lines.append("! Physical Interfaces (Trunks & Routed P2P)")
    routed_links: list[dict[str, Any]] = []

    for link in dev_links:
        is_endpoint_a = (link["endpoint_a"] == name)
        intf = link["interface_a"] if is_endpoint_a else link["interface_b"]
        peer = link["endpoint_b"] if is_endpoint_a else link["endpoint_a"]
        link_id = link.get("link_id", "")
        med = media_by_link.get(link_id, {})
        med_type = med.get("media_type", "Cat6a")
        dist = med.get("distance_m", link.get("distance_m", 100))
        dist_km = dist / 1000.0
        dist_label = f"{dist_km:.1f} km" if dist >= 1000.0 else f"{dist:.0f} m"

        # Determine if peer is an L2 switch or L3 peer (router/core)
        peer_dev = next((d for d in scenario.get("devices", []) if d["name"] == peer), {})
        is_routed_peer = peer_dev.get("type", "router") != "l2_switch"

        if is_routed_peer:
            p2p_sub = _match_p2p_subnet(link, all_subnets)
            if p2p_sub:
                ip_addr = p2p_sub["first_host"] if is_endpoint_a else p2p_sub["last_host"]
                mask = p2p_sub["mask"]
                routed_links.append({"interface": intf, "subnet": p2p_sub})
            else:
                ip_addr = "10.255.255.1" if is_endpoint_a else "10.255.255.2"
                mask = "255.255.255.252"

            lines.extend([
                f"interface {intf}",
                f" description Routed Point-to-Point Uplink to {peer} [Media: {med_type}, Distance: {dist_label}]",
                f" no switchport",
                f" ip address {ip_addr} {mask}",
            ])
            if "ospf_cost" in link:
                lines.append(f" ip ospf cost {link['ospf_cost']}")
            if scenario_id == "metro_man":
                lines.append(" service-policy output PM_METRO_QOS_EGRESS")
            lines.extend([
                f" no shutdown",
                f"!",
            ])
        else:
            # L2 Trunk to access switch (L3 switch 3560/3650 includes encapsulation dot1q per spec; verify in PT version)
            allowed_vlan_ids = sorted({s["vlan"] for s in local_vlan_subnets if s.get("vlan") is not None})
            vlan_str = ",".join(map(str, allowed_vlan_ids)) if allowed_vlan_ids else "1"

            lines.extend([
                f"interface {intf}",
                f" description Downlink Trunk to Access Switch {peer} [Media: {med_type}, Distance: {dist_label}]",
                f" switchport trunk encapsulation dot1q",
                f" switchport mode trunk",
                f" switchport trunk native vlan 999",
                f" switchport trunk allowed vlan {vlan_str}",
                f" switchport nonegotiate",
                f" no shutdown",
                f"!",
            ])

    # If no L2 access switches exist in the scenario, map spare GigabitEthernet ports as local access ports
    # so SVIs enter UP/UP state when Packet Tracer end-hosts connect directly (e.g. Metro MAN HQ-CORE).
    has_l2_switches = any(d.get("type") == "l2_switch" for d in scenario.get("devices", []))
    used_l3_intfs = {
        (l["interface_a"] if l["endpoint_a"] == name else l["interface_b"])
        for l in dev_links
    }
    if not has_l2_switches and local_vlan_subnets:
        lines.append("! Local Direct-Attach Access Ports (SVI Activation for End-Hosts)")
        next_gi_port = 1
        for s in local_vlan_subnets:
            while f"GigabitEthernet1/0/{next_gi_port}" in used_l3_intfs and next_gi_port <= 24:
                next_gi_port += 1
            if next_gi_port <= 24:
                lines.extend([
                    f"interface GigabitEthernet1/0/{next_gi_port}",
                    f" description Local Access Port for {s['name']} (VLAN {s['vlan']})",
                    f" switchport mode access",
                    f" switchport access vlan {s['vlan']}",
                    f" spanning-tree portfast",
                    f" spanning-tree bpduguard enable",
                    f" no shutdown",
                    f"!",
                ])
                used_l3_intfs.add(f"GigabitEthernet1/0/{next_gi_port}")
                next_gi_port += 1

    # SVIs for local VLAN gateways
    lines.append("! Switch Virtual Interfaces (SVI Layer 3 Default Gateways)")
    for s in local_vlan_subnets:
        vlan_id = s["vlan"]
        gw_ip = s["gateway"]
        mask = s["mask"]
        lines.extend([
            f"interface Vlan{vlan_id}",
            f" description SVI Default Gateway for {s['name']}",
            f" ip address {gw_ip} {mask}",
        ])
        if scenario_id == "campus_lan" and "WiFi" in s["name"]:
            lines.append(" ip access-group ACL_WIFI_SECURITY in")
        lines.extend([
            f" no shutdown",
            f"!",
        ])

    # Named Extended ACL for WiFi security
    if scenario_id == "campus_lan":
        lines.extend([
            f"! Named Extended ACL: WiFi Traffic Restriction",
            f"! Denies wireless clients access to Server Farm (VLAN 100) and Management (VLAN 99)",
            f"! Explicit permit any any retained for general campus/Internet traffic",
            f"ip access-list extended ACL_WIFI_SECURITY",
            f" remark Deny WiFi access to Production Server Farm",
        ])
        server_sub = next((s for s in all_subnets if s.get("vlan") == 100), None)
        mgmt_sub = next((s for s in all_subnets if s.get("vlan") == 99), None)
        if server_sub:
            lines.append(f" deny ip any {server_sub['network']} {server_sub['wildcard']}")
        if mgmt_sub:
            lines.append(f" deny ip any {mgmt_sub['network']} {mgmt_sub['wildcard']}")
        lines.extend([
            f" remark Explicit permit for remaining campus and Internet destinations",
            f" permit ip any any",
            f"!",
        ])

    # Routing Configuration: OSPF
    lines.extend([
        f"! Interior Gateway Protocol: OSPFv2 (RFC 2328)",
        f"router ospf 1",
        f" router-id 10.255.255.1",
        f" passive-interface default",
    ])
    for rl in routed_links:
        lines.append(f" no passive-interface {rl['interface']}")

    # OSPF network statements for local SVIs and local routed links only
    ospf_nets_seen = set()
    for s in local_vlan_subnets:
        net_key = (s["network"], s["wildcard"])
        if net_key not in ospf_nets_seen:
            lines.append(f" network {s['network']} {s['wildcard']} area 0")
            ospf_nets_seen.add(net_key)
    for rl in routed_links:
        s = rl["subnet"]
        if s:
            net_key = (s["network"], s["wildcard"])
            if net_key not in ospf_nets_seen:
                lines.append(f" network {s['network']} {s['wildcard']} area 0")
                ospf_nets_seen.add(net_key)

    lines.append("!")

    mgmt_sub = next((s for s in all_subnets if s.get("vlan") == 99), None)
    lines.extend(_build_footer(mgmt_sub))
    return "\n".join(lines)


def _generate_router_config(
    dev: dict[str, Any],
    dev_subnets: list[dict[str, Any]],
    dev_links: list[dict[str, Any]],
    scenario: dict[str, Any],
    all_subnets: list[dict[str, Any]],
    media_by_link: dict[str, dict[str, Any]],
    routing_result: dict[str, Any],
    platform: str,
    no_crypto: bool,
    router_idx: int,
    vlsm_result: dict[str, Any],
) -> str:
    name = dev["name"]
    scenario_id = scenario.get("scenario_id", "")
    lines = _build_header(dev, scenario, platform)

    lines.extend([
        f"! Layer 3 Routing & Forwarding",
        f"ip cef",
        f"!",
    ])

    # QoS / MQC configuration for Metro MAN
    if scenario_id == "metro_man":
        lines.extend([
            f"! Modular QoS CLI (MQC) Low-Latency Queuing Architecture",
            f"class-map match-any CM_VOIP_FINTECH",
            f" match ip dscp ef",
            f" match ip dscp cs5",
            f"!",
            f"policy-map PM_METRO_QOS_EGRESS",
            f" class CM_VOIP_FINTECH",
            f"  priority percent 35",
            f" class class-default",
            f"  fair-queue",
            f"!",
        ])

    # Track used interfaces so LAN subinterfaces never collide with WAN links
    used_interfaces = set()
    routed_subnets_for_ospf: list[dict[str, Any]] = []
    bgp_p2p_ip_for_cloud: dict[str, str] = {}

    lines.append("! Physical Routed Interfaces")
    for link in dev_links:
        is_endpoint_a = (link["endpoint_a"] == name)
        intf = link["interface_a"] if is_endpoint_a else link["interface_b"]
        peer = link["endpoint_b"] if is_endpoint_a else link["endpoint_a"]
        used_interfaces.add(intf)

        link_id = link.get("link_id", "")
        med = media_by_link.get(link_id, {})
        med_type = med.get("media_type", "OS2 SMF")
        dist = med.get("distance_m", link.get("distance_m", 1000))
        dist_km = dist / 1000.0
        dist_label = f"{dist_km:.1f} km" if dist >= 1000.0 else f"{dist:.0f} m"

        p2p_sub = _match_p2p_subnet(link, all_subnets)
        if p2p_sub:
            ip_addr = p2p_sub["first_host"] if is_endpoint_a else p2p_sub["last_host"]
            mask = p2p_sub["mask"]
            if peer != "CLOUD-EDGE" and name != "CLOUD-EDGE":
                routed_subnets_for_ospf.append(p2p_sub)
            else:
                bgp_p2p_ip_for_cloud["local"] = ip_addr
                bgp_p2p_ip_for_cloud["peer"] = p2p_sub["last_host"] if is_endpoint_a else p2p_sub["first_host"]
        else:
            ip_addr = f"10.253.{router_idx}.1" if is_endpoint_a else f"10.253.{router_idx}.2"
            mask = "255.255.255.252"

        lines.extend([
            f"interface {intf}",
            f" description Routed Link to {peer} [Media: {med_type}, Distance: {dist_label}]",
            f" ip address {ip_addr} {mask}",
        ])

        if "ospf_cost" in link:
            lines.append(f" ip ospf cost {link['ospf_cost']}")

        if scenario_id == "metro_man":
            lines.append(" service-policy output PM_METRO_QOS_EGRESS")

        if scenario_id == "campus_lan" and name == "EDGE-R1":
            lines.append(" ip nat inside")

        lines.extend([
            f" no shutdown",
            f"!",
        ])

    # Campus Edge Outside WAN Interface
    if scenario_id == "campus_lan" and name == "EDGE-R1":
        pub_cidr = scenario.get("public_nat_ip", "203.0.113.2/30")
        pub_ip = pub_cidr.split("/")[0]
        used_interfaces.add("GigabitEthernet0/1")
        lines.extend([
            f"interface GigabitEthernet0/1",
            f" description WAN Internet Uplink (RFC 5737 Documentation IP)",
            f" ip address {pub_ip} 255.255.255.252",
            f" ip nat outside",
            f" no shutdown",
            f"!",
        ])

    # Local LAN Subnets attached directly to this router
    local_lan_subs = [s for s in dev_subnets if not s.get("is_p2p")]
    if local_lan_subs:
        # Select first unused physical interface for LAN gateway / Router-on-a-Stick
        lan_intf = next(
            (cand for cand in ["GigabitEthernet0/2", "GigabitEthernet0/3", "GigabitEthernet0/1"] if cand not in used_interfaces),
            "GigabitEthernet0/4"
        )
        if len(local_lan_subs) == 1:
            s = local_lan_subs[0]
            routed_subnets_for_ospf.append(s)
            vlan_note = f" (VLAN {s['vlan']} Untagged Access)" if s.get("vlan") is not None else ""
            lines.extend([
                f"interface {lan_intf}",
                f" description Local LAN Gateway for {s['name']}{vlan_note}",
                f" ip address {s['gateway']} {s['mask']}",
                f" no shutdown",
                f"!",
            ])
        else:
            # Enable physical interface and create 802.1Q subinterfaces
            lines.extend([
                f"interface {lan_intf}",
                f" description Trunk to Local Site LAN Distribution",
                f" no ip address",
                f" no shutdown",
                f"!",
            ])
            for idx, s in enumerate(local_lan_subs):
                routed_subnets_for_ospf.append(s)
                vlan_id = s.get("vlan") or (100 + idx)
                lines.extend([
                    f"interface {lan_intf}.{vlan_id}",
                    f" description Subinterface Gateway for {s['name']} (VLAN {vlan_id})",
                    f" encapsulation dot1Q {vlan_id}",
                    f" ip address {s['gateway']} {s['mask']}",
                    f" no shutdown",
                    f"!",
                ])

    # WAN GRE / IPsec Tunnels (Global WAN: Hub R-DEL <-> Spoke Routers)
    if scenario_id == "global_wan" and name != "CLOUD-EDGE":
        # Build deterministic P2P hub-and-spoke tunnel list rooted at R-DEL
        del_wan_links = [
            l for l in scenario.get("links", [])
            if "R-DEL" in (l["endpoint_a"], l["endpoint_b"])
            and "CLOUD-EDGE" not in (l["endpoint_a"], l["endpoint_b"])
        ]
        tunnel_defs: list[tuple[int, str, str, str, str]] = []
        for idx, wl in enumerate(del_wan_links):
            p2p_sub = _match_p2p_subnet(wl, all_subnets)
            if not p2p_sub:
                continue
            del_is_a = (wl["endpoint_a"] == "R-DEL")
            del_ip = p2p_sub["first_host"] if del_is_a else p2p_sub["last_host"]
            spoke_ip = p2p_sub["last_host"] if del_is_a else p2p_sub["first_host"]
            del_intf = wl["interface_a"] if del_is_a else wl["interface_b"]
            spoke_intf = wl["interface_b"] if del_is_a else wl["interface_a"]
            spoke_name = wl["endpoint_b"] if del_is_a else wl["endpoint_a"]

            hub_tun_ip = f"10.254.0.{idx * 4 + 1}"
            spoke_tun_ip = f"10.254.0.{idx * 4 + 2}"

            if name == "R-DEL":
                tunnel_defs.append((idx, spoke_name, hub_tun_ip, del_intf, spoke_ip))
            elif name == spoke_name:
                tunnel_defs.append((0, "R-DEL", spoke_tun_ip, spoke_intf, del_ip))

        if tunnel_defs and not no_crypto:
            lines.extend([
                f"! IPsec Crypto Profile (IETF RFC 4301 / RFC 2409)",
                f"crypto isakmp policy 10",
                f" encr aes 256",
                f" authentication pre-share",
                f" group 14",
                f"crypto isakmp key CHANGE_ME address 0.0.0.0 0.0.0.0",
                f"crypto ipsec transform-set TS_AES_SHA esp-aes 256 esp-sha-hmac",
                f" mode transport",
                f"crypto ipsec profile IPSEC_WAN_PROFILE",
                f" set transform-set TS_AES_SHA",
                f"!",
            ])

        for tun_id, peer_rtr, tun_ip, src_intf, dst_ip in tunnel_defs:
            lines.extend([
                f"! Point-to-Point Secure WAN Encapsulation -> {peer_rtr}",
                f"interface Tunnel{tun_id}",
                f" description GRE Overlay Span to {peer_rtr} ({'Encrypted IPsec' if not no_crypto else 'No-Crypto PT Mode'})",
                f" ip address {tun_ip} 255.255.255.252",
                f" tunnel source {src_intf}",
                f" tunnel destination {dst_ip}",
            ])
            if not no_crypto:
                lines.append(" tunnel protection ipsec profile IPSEC_WAN_PROFILE")
            lines.extend([
                f" no shutdown",
                f"!",
            ])

    # Routing Protocols: OSPF (Skip on CLOUD-EDGE which only runs eBGP)
    if name != "CLOUD-EDGE":
        ospf_area = dev.get("ospf_area", 0)
        lines.extend([
            f"! Interior Gateway Protocol: OSPFv2 (RFC 2328)",
            f"router ospf 1",
            f" router-id 10.255.255.{router_idx + 1}",
            f" passive-interface default",
        ])
        for l in dev_links:
            peer_name = l["endpoint_b"] if l["endpoint_a"] == name else l["endpoint_a"]
            if peer_name != "CLOUD-EDGE":
                intf = l["interface_a"] if l["endpoint_a"] == name else l["interface_b"]
                lines.append(f" no passive-interface {intf}")

        seen_ospf_nets = set()
        for s in routed_subnets_for_ospf:
            k = (s["network"], s["wildcard"])
            if k not in seen_ospf_nets:
                lines.append(f" network {s['network']} {s['wildcard']} area {ospf_area}")
                seen_ospf_nets.add(k)

        if name == "R-DEL" and scenario_id == "global_wan":
            grp_sums = vlsm_result.get("group_summaries", {})
            lines.append("! ABR Inter-Area Route Summarization (RFC 4632 Classless Summary)")
            for area_num, grp_key in [(1, "Area 1 (Mumbai)"), (2, "Area 2 (Bangalore)"), (3, "Area 3 (Chennai)")]:
                if grp_key in grp_sums:
                    gs = grp_sums[grp_key]
                    lines.append(f" area {area_num} range {gs['summary_network']} {gs['summary_mask']}")
        lines.append("!")

    # eBGP Configuration
    bgp_data = scenario.get("bgp_peering")
    if bgp_data and (name == "R-DEL" or name == "CLOUD-EDGE"):
        local_asn = bgp_data["enterprise_asn"] if name == "R-DEL" else bgp_data["cloud_asn"]
        remote_asn = bgp_data["cloud_asn"] if name == "R-DEL" else bgp_data["enterprise_asn"]
        peer_ip = bgp_p2p_ip_for_cloud.get("peer", "10.0.13.150" if name == "R-DEL" else "10.0.13.149")
        root_net = vlsm_result.get("root_network", "10.0.0.0")
        root_mask = prefix_to_mask_str(vlsm_result.get("root_prefix", 16))
        summary_net = root_net if name == "R-DEL" else (local_lan_subs[0]["network"] if local_lan_subs else root_net)
        summary_mask = root_mask if name == "R-DEL" else (local_lan_subs[0]["mask"] if local_lan_subs else root_mask)

        lines.extend([
            f"! Exterior Border Gateway Protocol: eBGP (RFC 4271 / RFC 6996 Private ASN)",
            f"router bgp {local_asn}",
            f" bgp router-id 192.168.255.{router_idx}",
            f" bgp log-neighbor-changes",
            f" neighbor {peer_ip} remote-as {remote_asn}",
            f" neighbor {peer_ip} description eBGP Peering to {'Cloud VPC' if name == 'R-DEL' else 'Enterprise Delhi Hub'}",
            f" network {summary_net} mask {summary_mask}",
            f"!",
            f"! Discard Route to Null0 to satisfy BGP network synchronization",
            f"ip route {summary_net} {summary_mask} Null0 250",
            f"!",
        ])

    # NAT Overload on Campus Edge Router
    if scenario_id == "campus_lan" and name == "EDGE-R1":
        root_net = vlsm_result.get("root_network", "10.10.0.0")
        root_wc = prefix_to_wildcard_str(vlsm_result.get("root_prefix", 16))
        lines.extend([
            f"! Network Address Translation: NAT Overload / PAT (RFC 3022 & RFC 5737)",
            f"ip access-list standard ACL_NAT_PERMIT",
            f" permit {root_net} {root_wc}",
            f"!",
            f"ip nat inside source list ACL_NAT_PERMIT interface GigabitEthernet0/1 overload",
            f"ip route 0.0.0.0 0.0.0.0 203.0.113.1",
            f"!",
        ])

    mgmt_sub = next((s for s in all_subnets if s.get("vlan") == 99), None)
    lines.extend(_build_footer(mgmt_sub))
    return "\n".join(lines)


def run_configuration_self_check(
    configs: dict[str, str],
    scenario: dict[str, Any],
    vlsm_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Automated self-check before export:
      1. Zero duplicate IP addresses across devices.
      2. Zero overlapping subnets + exact bitwise wildcard (~mask & 0xFFFFFFFF).
      3. Trunk allowed VLAN lists match VLANs present in scenario (never unrestricted).
      4. Every OSPF 'network' statement matches a configured interface subnet on that device.
      5. Every referenced ACL ('access-class', 'ip access-group', 'nat source list') is defined on that device.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Collect all assigned IPs across all devices + per-device interface subnets
    seen_ips: dict[str, str] = {}
    for dev_name, cfg in configs.items():
        dev_intfs: list[tuple[int, int]] = []
        ospf_nets: list[tuple[str, str, int, int]] = []
        defined_acls: set[str] = set()
        referenced_acls: set[str] = set()

        for raw_line in cfg.splitlines():
            line = raw_line.strip()
            if line.startswith("ip address ") and not line.startswith("ip address dhcp"):
                parts = line.split()
                if len(parts) >= 4:
                    ip_str, mask_str = parts[2], parts[3]
                    if ip_str in ("dhcp", "negotiated"):
                        continue
                    if ip_str in seen_ips:
                        errors.append(f"Duplicate IP {ip_str} detected! Used on {seen_ips[ip_str]} and {dev_name}")
                    seen_ips[ip_str] = dev_name
                    dev_intfs.append((ip_to_int(ip_str), ip_to_int(mask_str)))

            elif line.startswith("network ") and " area " in line:
                parts = line.split()
                if len(parts) >= 5:
                    net_str, wc_str = parts[1], parts[2]
                    net_int = ip_to_int(net_str)
                    wc_int = ip_to_int(wc_str)
                    mask_from_wc = (~wc_int) & 0xFFFFFFFF
                    ospf_nets.append((net_str, wc_str, net_int, mask_from_wc))

            elif line.startswith("ip access-list standard ") or line.startswith("ip access-list extended "):
                parts = line.split()
                if len(parts) >= 4:
                    defined_acls.add(parts[3])

            elif line.startswith("access-class "):
                parts = line.split()
                if len(parts) >= 2:
                    referenced_acls.add(parts[1])

            elif line.startswith("ip access-group "):
                parts = line.split()
                if len(parts) >= 3:
                    referenced_acls.add(parts[2])

            elif line.startswith("ip nat inside source list "):
                parts = line.split()
                if len(parts) >= 6:
                    referenced_acls.add(parts[5])

        # Verify every OSPF network statement matches an interface IP/subnet on this device
        for net_str, wc_str, ospf_net_int, ospf_mask_int in ospf_nets:
            matched = any(
                (intf_ip & ospf_mask_int) == (ospf_net_int & ospf_mask_int)
                and intf_mask == ospf_mask_int
                for intf_ip, intf_mask in dev_intfs
            )
            if not matched:
                errors.append(
                    f"OSPF network {net_str} {wc_str} on {dev_name} does not match any configured interface subnet!"
                )

        # Verify every referenced ACL is defined on this device
        missing_acls = referenced_acls - defined_acls
        if missing_acls:
            errors.append(
                f"Device {dev_name} references undefined ACL(s): {sorted(missing_acls)}"
            )

    # 2. Check VLSM subnets for zero overlap & wildcard = ~mask & 0xFFFFFFFF
    allocs = vlsm_result.get("allocated_subnets", [])
    for idx, s in enumerate(allocs):
        mask_int = s["mask_int"]
        wildcard_int = s["wildcard_int"]
        expected_wildcard = (~mask_int) & 0xFFFFFFFF
        if wildcard_int != expected_wildcard:
            errors.append(f"Wildcard mismatch on subnet {s['name']}: {wildcard_int} != {expected_wildcard}")
        for other in allocs[idx + 1:]:
            if not (s["end_int"] <= other["network_int"] or other["end_int"] <= s["network_int"]):
                errors.append(f"Overlapping subnets detected: {s['name']} ({s['cidr']}) and {other['name']} ({other['cidr']})")

    # 3. Check trunk allowed lists
    all_vlans = {s["vlan"] for s in allocs if s.get("vlan") is not None}
    for dev_name, cfg in configs.items():
        for raw_line in cfg.splitlines():
            line = raw_line.strip()
            if "switchport trunk allowed vlan" in line:
                vlan_str = line.split("switchport trunk allowed vlan")[-1].strip()
                configured_vlans = set(map(int, vlan_str.split(",")))
                if not configured_vlans.issubset(all_vlans):
                    errors.append(f"Trunk on {dev_name} allows undeclared VLANs: {configured_vlans - all_vlans}")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "checked_ip_count": len(seen_ips),
    }
