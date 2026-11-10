"""
NetArchitect Packet Tracer Lab Pack & Verification Guide Generator
Dynamically builds comprehensive lab_guide.md manuals directly from calculated engine state:
  (a) Devices, Packet Tracer models, interface-count table, and required hardware modules
  (b) Physical cabling table (device:interface <-> device:interface, cable type, distance, real medium)
  (c) Full IP addressing plan (every router/switch interface + 1-2 test PCs/Servers per subnet)
  (d) Ordered paste-ready device configurations (L2 switches first, L3 switches second, Routers third)
  (e) Manual build steps & 3650 power-supply / module notes
  (f) Verification command checklist with dynamically derived EXPECTED outputs + ACL deny test + failover test
  (g) Screenshot capture checklist slots
  (h) Troubleshooting guide
"""

from typing import Any
from engine.addr import ip_to_int, int_to_ip
from engine.ptbuilder_gen import format_host_device_name, find_host_attachment_ports


def generate_lab_guide(
    scenario: dict[str, Any],
    vlsm_result: dict[str, Any],
    media_evals: list[dict[str, Any]],
    routing_result: dict[str, Any],
    configs: dict[str, str],
    topology_result: dict[str, Any] | None = None,
) -> str:
    """Generate full Markdown Packet Tracer Lab Guide for a scenario."""
    scenario_id = scenario.get("scenario_id", "network")
    scen_name = scenario.get("name", "Network Scenario")
    devices = scenario.get("devices", [])
    links = scenario.get("links", [])
    subnets = vlsm_result.get("allocated_subnets", [])
    media_by_link = {m.get("link_id", ""): m for m in media_evals}

    lines = [
        f"# Cisco Packet Tracer Lab Guide: {scen_name}",
        "",
        "> [!NOTE]",
        "> All IP plans, subnet masks, wildcard masks, interface descriptions, and verification expectations in this guide are **computed directly by the NetArchitect Engine**.",
        "> **Never assume verified in Packet Tracer until you run the topology and confirm every checklist item below.**",
        "",
        "---",
        "",
        "## (a) Device Inventory, PT Models & Interface-Count Table",
        "",
        "| Device Name | OSI Role | Packet Tracer Model | Links Used | Required Hardware / Power Modules (Verify in PT) |",
        "| :--- | :--- | :--- | :---: | :--- |",
    ]

    # Count links per device
    link_counts: dict[str, int] = {d["name"]: 0 for d in devices}
    for l in links:
        link_counts[l["endpoint_a"]] = link_counts.get(l["endpoint_a"], 0) + 1
        link_counts[l["endpoint_b"]] = link_counts.get(l["endpoint_b"], 0) + 1

    for d in devices:
        dname = d["name"]
        model = d.get("model_pt", "2911")
        role = d.get("role", "Infrastructure")
        used = link_counts.get(dname, 0)
        # Check if device also hosts local LAN interfaces
        local_subs = [s for s in subnets if s.get("device") == dname and not s.get("is_p2p")]
        extra_ports = 1 if (local_subs and d.get("type") in ("router", "cloud")) else 0
        total_ports_needed = used + extra_ports

        if "3650" in model:
            module_note = "Insert `AC-POWER-SUPPLY` in PSU slot to power on (24x Gi built-in)."
        elif "2960" in model:
            module_note = "Built-in 24x Fa + 2x Gi (no extra module needed)."
        elif "2911" in model:
            if total_ports_needed > 3:
                module_note = (
                    f"Built-in 3x Gi (`Gi0/0-0/2`); needs {total_ports_needed} Gi ports -> "
                    f"add `HWIC-1GE-SFP` or `EHWIC-4ESG` (or use `Router-PT` with `PT-ROUTER-NM-1CGE`). *Verify exact slot naming in your PT version.*"
                )
            else:
                module_note = "Built-in 3x Gi (`Gi0/0`, `Gi0/1`, `Gi0/2`)."
        elif "4331" in model:
            module_note = "Built-in 3x Gi (`Gi0/0/0-0/0/2`); verify interface prefix (`Gi0/0/x` vs `Gi0/x`) in your PT version."
        else:
            module_note = "Standard built-in ports (*verify in your PT version*)."

        lines.append(f"| `{dname}` | {role} | `{model}` | {total_ports_needed} | {module_note} |")

    lines.extend([
        "",
        "---",
        "",
        "## (b) Physical Cabling & Optical Media Table",
        "",
        "*Note on `--platform pt`: 10 GbE optical trunks/WAN links are modeled using GigabitEthernet copper interfaces in Packet Tracer, with the true calculated L1 medium and optical power budget recorded in each interface `description`.*",
        "",
        "| Link ID | Endpoint A (`Port`) | Endpoint B (`Port`) | PT Cable Type | Physical Distance | Engineered Medium & Optic | Optical Margin |",
        "| :--- | :--- | :--- | :--- | :---: | :--- | :---: |",
    ])

    dev_map = {d["name"]: d for d in devices}
    for l in links:
        u, v = l["endpoint_a"], l["endpoint_b"]
        ia, ib = l["interface_a"], l["interface_b"]
        lid = l.get("link_id", f"{u}-{v}")
        med = media_by_link.get(lid, {})
        dist_m = med.get("distance_m", l.get("distance_m", 0))
        dist_str = f"{dist_m/1000.0:.1f} km" if dist_m >= 1000 else f"{dist_m:.0f} m"
        med_str = f"{med.get('media_type', 'Cat6a')} ({med.get('transceiver', 'RJ-45')})"
        margin = f"{med['margin_db']} dB" if med.get("margin_db") is not None else "N/A"

        type_a = dev_map.get(u, {}).get("type", "router")
        type_b = dev_map.get(v, {}).get("type", "router")
        same_layer = (type_a in ("l2_switch", "l3_switch") and type_b in ("l2_switch", "l3_switch")) or (
            type_a in ("router", "cloud") and type_b in ("router", "cloud")
        )
        pt_cable = "Copper Cross-Over" if same_layer else "Copper Straight-Through"

        lines.append(
            f"| `{lid}` | `{u}` (`{ia}`) | `{v}` (`{ib}`) | {pt_cable} | {dist_str} | {med_str} | {margin} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## (c) Bitwise-Allocated IP Addressing Plan & Test Hosts",
        "",
        f"- **Root Prefix**: `{vlsm_result['root_cidr']}`",
        f"- **Overall Allocation Efficiency**: `{vlsm_result['overall_efficiency_pct']}%`",
        "",
        "### Subnet & Gateway Plan",
        "",
        "| Subnet / VLAN Name | VLAN | CIDR Block | Subnet Mask | Wildcard Mask | Default Gateway | Broadcast |",
        "| :--- | :---: | :--- | :--- | :--- | :--- | :--- |",
    ])

    for s in subnets:
        vlan_str = str(s["vlan"]) if s.get("vlan") else "Routed P2P"
        lines.append(
            f"| `{s['name']}` | {vlan_str} | `{s['cidr']}` | `{s['mask']}` | `{s['wildcard']}` | `{s['gateway']}` | `{s['broadcast']}` |"
        )

    lines.extend([
        "",
        "### End-Device (PC-PT / Server-PT) Static Test Plan (1–2 Hosts per Subnet)",
        "",
        "| End-Device Hostname | Type | Target Subnet / VLAN | Static IP Address | Subnet Mask | Default Gateway | Attachment Port (Host 1) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    attachments = find_host_attachment_ports(scenario, configs)
    test_hosts = []
    for s in subnets:
        if s.get("is_p2p") or s.get("is_loopback"):
            continue
        gw_int = ip_to_int(s["gateway"])
        h1_ip = int_to_ip(gw_int + 1)
        h2_ip = int_to_ip(gw_int + 2) if s["usable_hosts"] >= 3 else None
        is_srv = ("Server" in s["name"] or "Colo" in s["name"] or "Cloud" in s["name"])
        dtype = "Server-PT" if is_srv else "PC-PT"
        hname = format_host_device_name(s["name"], 1)
        if s["name"] in attachments:
            att_dev, att_intf, att_cable = attachments[s["name"]]
            att_str = f"`{att_dev}` (`{att_intf}`, {att_cable})"
        else:
            att_str = f"`{s.get('device', 'Router')}` (802.1Q trunk — add optional 2960 switch)"
        test_hosts.append({"name": hname, "subnet": s["name"], "vlan": s.get("vlan"), "ip": h1_ip, "gw": s["gateway"]})
        lines.append(f"| `{hname}` | {dtype} | `{s['name']}` (VLAN {s.get('vlan') or 'LAN'}) | `{h1_ip}` | `{s['mask']}` | `{s['gateway']}` | {att_str} |")
        if h2_ip:
            hname2 = format_host_device_name(s["name"], 2)
            lines.append(f"| `{hname2}` | {dtype} | `{s['name']}` (VLAN {s.get('vlan') or 'LAN'}) | `{h2_ip}` | `{s['mask']}` | `{s['gateway']}` | Optional extra host (switch default access port) |")

    lines.extend([
        "",
        "---",
        "",
        "## (d) Per-Device Configurations in Paste Order",
        "",
        "> [!IMPORTANT]",
        "> Paste configurations strictly in **bottom-up OSI order**: **L2 Access Switches first -> L3 Core Switches second -> Perimeter / WAN Routers third**.",
        "> Always verify RSA key generation (`crypto key generate rsa modulus 2048`) if SSH fails to initialize in Packet Tracer.",
        "",
    ])

    sorted_devs = sorted(
        devices,
        key=lambda d: 0 if d.get("type") == "l2_switch" else 1 if d.get("type") == "l3_switch" else 2,
    )

    for idx, d in enumerate(sorted_devs, 1):
        dname = d["name"]
        model = d.get("model_pt", "2911")
        cfg = configs.get(dname, "")
        lines.extend([
            f"### Step {idx}: `{dname}` (`{model}` — {d.get('type', 'device').upper()})",
            "",
            "```ios",
            cfg.strip(),
            "```",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## (e) Manual Build Steps (If Not Using PTBuilder)",
        "",
        "1. Open **Cisco Packet Tracer** (v8.2+ recommended).",
        "2. Drag devices onto the logical workspace matching Section (a).",
        "   - For `3650-24PS` L3 switches: open the **Physical** tab and drag an `AC-POWER-SUPPLY` into the empty power bay until the green link lights activate.",
        "   - For `2911` routers requiring >3 Gigabit ports: power off the router, insert an `EHWIC-4ESG` or `HWIC-1GE-SFP` module, and power back on (*verify slot numbers in your PT version*).",
        "3. Connect all physical cables strictly per the interface mapping in Section (b).",
        "4. Place 1–2 `PC-PT` / `Server-PT` devices per subnet and assign the static IP/Mask/Gateway from Section (c).",
        "5. Open each device's **CLI** tab, enter `enable` -> `configure terminal`, and paste the configurations from Section (d) in the exact order shown.",
        "6. Wait ~30 seconds (or click **Fast Forward Time** in PT) for Rapid-PVST+ and OSPF/BGP neighbor adjacencies to converge.",
        "",
        "---",
        "",
        "## (f) Verification Checklist & Expected Outputs",
        "",
        "Run these exact commands on the specified devices and verify your output matches:",
        "",
        "### 1. Interface Status (`show ip interface brief`)",
        "- Run on **all L3 switches and routers**.",
        "- **Expected**: Every configured GigabitEthernet interface, subinterface, and SVI (`Vlan10`, etc.) shows Status = `up`, Protocol = `up`.",
        "",
        "### 2. VLAN Database (`show vlan brief`)",
        "- Run on **all L2 and L3 switches**.",
        f"- **Expected**: All active VLANs (`{', '.join(str(s['vlan']) for s in subnets if s.get('vlan'))}`) and parking VLAN `999` (`Parking_Native_Blackhole`) appear as `active`.",
        "",
        "### 3. 802.1Q Trunk Security (`show interfaces trunk`)",
        "- Run on **CORE-SW** and **Access Switches**.",
        "- **Expected**: Mode = `on` (with DTP disabled), Encapsulation = `802.1q`, Native VLAN = `999`, Status = `trunking`, and **Vlans allowed on trunk** shows ONLY the explicit allowed list (never `1-4094`).",
        "",
        "### 4. Spanning Tree Root (`show spanning-tree`)",
        "- Run on **CORE-SW / HQ-CORE**.",
        "- **Expected**: Protocol displays `rstp` (`rapid-pvst`), and the Core Switch displays **\"This bridge is the root\"** with Priority `4096` (plus SysID extension).",
        "",
        "### 5. Dynamic Routing Table (`show ip route`)",
        "- Run on **all L3 devices**.",
        "- **Expected**: Connected (`C`), Local (`L`), and OSPF (`O` / `O IA`) routes exist for all remote subnets.",
    ])

    if scenario_id == "global_wan":
        lines.extend([
            "",
            "### 6. Multi-Area OSPF & eBGP Neighbors (`show ip ospf neighbor` & `show ip bgp summary`)",
            "- Run `show ip ospf neighbor` on **R-DEL**: Expected state `FULL/DR` or `FULL/BDR` for `R-MUM`, `R-BLR`, and `R-CHE`.",
            "- Run `show ip bgp summary` on **R-DEL**: Expected neighbor `AS 65010` (`CLOUD-EDGE`) in state `Established` (or numeric PfxRcd >= 1).",
        ])
    else:
        lines.extend([
            "",
            "### 6. OSPF Neighbor Adjacencies (`show ip ospf neighbor`)",
            "- Run on **EDGE-R1 / CORE-SW / HQ-CORE / REM1-R / REM2-R**.",
            "- **Expected**: Neighbor states show `FULL`.",
        ])

    if scenario_id == "campus_lan":
        wifi_host = next((h for h in test_hosts if "WiFi" in h["subnet"]), None)
        srv_host = next((h for h in test_hosts if "Server" in h["subnet"]), None)
        data_host = next((h for h in test_hosts if "Data" in h["subnet"]), None)
        lines.extend([
            "",
            "### 7. Security ACL & NAT Verification (`show access-lists` & `show ip nat translations`)",
            "- Run `show access-lists` on **CORE-SW**: Inspect `ACL_WIFI_SECURITY` hit counters.",
            "- **MUST PASS Ping Test**: Ping from Data host (`" + (data_host['ip'] if data_host else '10.10.0.2') + "`) to Server (`" + (srv_host['ip'] if srv_host else '10.10.x.x') + "`) -> **Reply received (0% loss)**.",
            "- **MUST FAIL Security ACL Test**: Ping from WiFi host (`" + (wifi_host['ip'] if wifi_host else '10.10.x.x') + "`) to Server (`" + (srv_host['ip'] if srv_host else '10.10.x.x') + "`) -> **Destination host unreachable / Administratively prohibited (100% blocked by `ACL_WIFI_SECURITY`)**.",
            "- Run `show ip nat translations` on **EDGE-R1** after pinging the WAN ISP IP (`203.0.113.1`) -> Verify Inside Global `203.0.113.2:<port>` PAT mapping.",
        ])

    lines.extend([
        "",
        "### 8. Link Failover & Convergence Test",
        "- On a redundant link (e.g., `HQ-CORE` <-> `REM1-R` in Metro MAN, or `R-DEL` <-> `R-MUM` in Global WAN):",
        "  1. Start continuous `ping -t` from branch host to HQ/Delhi server.",
        "  2. Enter `interface <uplink>` -> `shutdown` on the primary link.",
        "  3. Observe OSPF reconverge via the alternate ring/mesh path (`show ip route` updates automatically).",
        "  4. Verify connectivity resumes after ~1–3 ping timeouts.",
        "  5. Restore link with `no shutdown`.",
        "",
        "---",
        "",
        "## (g) Viva & Submission Screenshot Slots",
        "",
        "Capture and save the following screenshots in your lab submission report:",
        "- [ ] **Screenshot 1**: Full Packet Tracer logical topology showing green link triangles.",
        "- [ ] **Screenshot 2**: `show ip interface brief` & `show vlan brief` on Core Switch.",
        "- [ ] **Screenshot 3**: `show interfaces trunk` confirming Native VLAN 999 and explicit allowed VLANs.",
        "- [ ] **Screenshot 4**: `show ip route` & `show ip ospf neighbor` (plus `show ip bgp summary` for WAN).",
        "- [ ] **Screenshot 5**: Successful end-to-end `ping`/`traceroute` AND blocked ACL test (`Destination unreachable` + incremented ACL hit counters).",
        "- [ ] **Screenshot 6**: Failover reconvergence proof after shutting down a primary ring/backbone link.",
        "",
        "---",
        "",
        "## (h) Troubleshooting Common Packet Tracer Issues",
        "",
        "| Symptom | Root Cause | Resolution |",
        "| :--- | :--- | :--- |",
        "| Interfaces remain red (`administratively down`) | `3650-24PS` lacks power supply OR `no shutdown` missed | Insert `AC-POWER-SUPPLY` in Physical view; issue `no shutdown` on physical interface and SVIs. |",
        "| OSPF stuck in `EXSTART` / `INIT` | Link mismatched subnet mask or passive-interface active | Verify both sides of `/30` match `255.255.255.252` and `no passive-interface <intf>` is applied. |",
        "| Trunk drops VLAN traffic | VLAN missing from `switchport trunk allowed vlan` or VLAN not created | Run `show vlan brief` on both switches and ensure VLAN IDs exist in `vlan.dat`. |",
        "| SSH commands rejected by PT | Hostname/domain-name or RSA key missing | Ensure `ip domain-name netarchitect.lab` and `crypto key generate rsa modulus 2048` are executed. |",
        "| Trunk command rejected (`encapsulation dot1q`) | `3650-24PS` runs IOS-XE (dot1q-only) whereas `3560-24PS` requires explicit encap | Ignore `% Invalid input` on `3650-24PS` (`switchport mode trunk` still applies), or verify on `3560-24PS`. |",
        "| GRE/IPsec commands fail in PT | Basic PT router image lacks crypto IPsec profile support | Re-generate configs using `--no-crypto` flag to run clean GRE over Packet Tracer. |",
        "",
    ])

    return "\n".join(lines)
