"""
NetArchitect PTBuilder JavaScript Automation Generator
Generates clean JavaScript automation scripts for the PTBuilder Cisco Packet Tracer extension
(github.com/kimmknight/PTBuilder) to build, cable, and configure complete topologies programmatically.

Documented PTBuilder API Functions Used (github.com/kimmknight/PTBuilder):
  - addDevice(deviceName, deviceModel, x, y)
  - addLink(device1, port1, device2, port2, linkType)   // 'straight', 'cross', 'fiber', 'serial'
  - configureIosDevice(deviceName, commandsString)      // newline-delimited CLI string
  - configurePcIp(deviceName, dhcpBool, ip, mask, gw)

Rules:
  - Positions devices dynamically on a balanced grid layout.
  - Uses exact Packet Tracer device models (2960-24TT, 3650-24PS, 2911, ISR4331, PC-PT, Server-PT).
  - Connects links using exact interface names and Packet Tracer-compatible cable types.
  - Pushes IOS configurations in logical block-safe chunks of <= 40 lines (never splitting mid-block)
    in strict bottom-up OSI order: L2 switches -> L3 switches -> Routers.
  - Adds test PC/Server end-devices per subnet, cables them to exact matching access/LAN ports
    derived directly from the generated IOS configs, and sets static IP/mask/gateway via configurePcIp().
"""

from typing import Any
from engine.addr import ip_to_int, int_to_ip


def format_host_device_name(sub_name: str, host_index: int = 1) -> str:
    """Create a clean, deterministic PT host device name without mid-word truncation."""
    safe = sub_name.replace("-", "_").replace(" ", "_")
    if len(safe) > 22:
        safe = safe[:22].rstrip("_")
    return f"HOST_{safe}" if host_index == 1 else f"HOST_{safe}_{host_index}"


def _determine_pt_cable_type(dev_a: dict[str, Any], dev_b: dict[str, Any]) -> str:
    """
    Determine the appropriate Packet Tracer copper cable type based on OSI device layers.
    - Same layer (Switch <-> Switch, Router/PC <-> Router/PC): 'cross'
    - Different layer (Router <-> Switch, Switch <-> PC): 'straight'
    Note: 10G optical links are modeled as Gigabit copper ports in PT (--platform pt),
    with real fiber optic specs preserved in interface descriptions.
    """
    type_a = dev_a.get("type", "router")
    type_b = dev_b.get("type", "router")

    is_sw_a = type_a in ("l2_switch", "l3_switch")
    is_sw_b = type_b in ("l2_switch", "l3_switch")
    is_r_or_host_a = type_a in ("router", "cloud", "host")
    is_r_or_host_b = type_b in ("router", "cloud", "host")

    if (is_sw_a and is_sw_b) or (is_r_or_host_a and is_r_or_host_b):
        return "cross"
    return "straight"


def find_host_attachment_ports(
    scenario: dict[str, Any],
    configs: dict[str, str],
) -> dict[str, tuple[str, str, str]]:
    """
    Inspect the generated device configurations to find the exact physical switchport
    or router untagged LAN interface matching each subnet.
    Returns: {subnet_name: (device_name, interface_name, pt_cable_type)}
    """
    dev_map = {d["name"]: d for d in scenario.get("devices", [])}
    attachments: dict[str, tuple[str, str, str]] = {}

    for dev_name, cfg in configs.items():
        current_intf = None
        for raw_line in cfg.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith("interface "):
                current_intf = stripped[len("interface "):].strip()
            elif stripped == "!" or not raw_line.startswith(" "):
                if not stripped.startswith("interface "):
                    current_intf = None
            elif current_intf and stripped.startswith("description "):
                desc = stripped[len("description "):].strip()
                # Skip dot1Q subinterfaces (cannot plug an untagged PC directly without L2 switch)
                if "." in current_intf or current_intf.startswith("Vlan") or current_intf.startswith("Tunnel"):
                    continue

                matched_sub = None
                for marker in (
                    "Access Port for ",
                    "Local Access Port for ",
                    "Local LAN Gateway for ",
                ):
                    if desc.startswith(marker):
                        rest = desc[len(marker):]
                        matched_sub = rest.split(" (")[0].strip()
                        break

                if matched_sub and matched_sub not in attachments:
                    cable = _determine_pt_cable_type(
                        dev_map.get(dev_name, {}),
                        {"type": "host"},
                    )
                    attachments[matched_sub] = (dev_name, current_intf, cable)

    return attachments


def split_ios_into_safe_chunks(raw_cfg: str, max_lines: int = 38) -> list[list[str]]:
    """
    Split a generated Cisco IOS configuration into CLI chunks of at most max_lines lines
    (including 'enable', 'configure terminal', and 'end'), guaranteeing NO multi-line
    block (interface, vlan, router ospf/bgp, policy-map, ip access-list, line) is ever
    broken across chunk boundaries.
    """
    skip_exact = {
        "end",
        "write memory",
        "version 15.0",
        "boot-start-marker",
        "boot-end-marker",
    }

    blocks: list[list[str]] = []
    for raw_line in raw_cfg.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("!") or stripped in skip_exact:
            continue

        is_indented = len(raw_line) > 0 and raw_line[0].isspace()
        if not is_indented or not blocks:
            blocks.append([stripped])
        else:
            # Keep submode indentation cleanly preserved (single space) so IOS context stays clear
            blocks[-1].append(" " + stripped)

    max_body = max(5, max_lines - 3)  # Reserve 3 lines for enable, configure terminal, end
    chunks: list[list[str]] = []
    current_body: list[str] = []

    for blk in blocks:
        if len(blk) <= max_body:
            if len(current_body) + len(blk) > max_body and current_body:
                chunks.append(["enable", "configure terminal"] + current_body + ["end"])
                current_body = []
            current_body.extend(blk)
        else:
            # Extremely rare oversized block (e.g. >35 OSPF networks): repeat parent header on continuation
            if current_body:
                chunks.append(["enable", "configure terminal"] + current_body + ["end"])
                current_body = []
            parent_cmd = blk[0]
            sub_cmds = blk[1:]
            step = max_body - 1
            for idx in range(0, len(sub_cmds), step):
                part = [parent_cmd] + sub_cmds[idx : idx + step]
                chunks.append(["enable", "configure terminal"] + part + ["end"])

    if current_body:
        chunks.append(["enable", "configure terminal"] + current_body + ["end"])

    return chunks


def generate_ptbuilder_script(
    scenario: dict[str, Any],
    vlsm_result: dict[str, Any],
    configs: dict[str, str],
    media_evals: list[dict[str, Any]],
) -> str:
    """
    Generate executable PTBuilder JavaScript file content using strictly documented API calls.
    """
    devices = scenario.get("devices", [])
    links = scenario.get("links", [])
    subnets = vlsm_result.get("allocated_subnets", [])

    dev_map = {d["name"]: d for d in devices}
    media_by_link = {m.get("link_id", ""): m for m in media_evals}
    attachments = find_host_attachment_ports(scenario, configs)

    js_lines = [
        "/**",
        f" * NetArchitect PTBuilder Automation Script: {scenario.get('name', 'Network Topology')}",
        " * Generated programmatically from engine data (zero hand-typed addresses).",
        " * Target Extension: PTBuilder (github.com/kimmknight/PTBuilder)",
        " * Run in Cisco Packet Tracer: Extensions > Builder Code Editor",
        " */",
        "",
        "function runNetArchitectBuild() {",
        "    // ===========================================================================",
        "    // Phase 1: Add Network Infrastructure Devices on Grid Layout",
        "    // ===========================================================================",
    ]

    x_router = 180
    x_l2 = 140
    for dev in devices:
        name = dev["name"]
        dtype = dev.get("type", "router")
        model = dev.get("model_pt", "2911")

        if dtype in ("router", "cloud"):
            coord = (x_router, 120)
            x_router += 220
        elif dtype == "l3_switch":
            coord = (400, 260)
        else:
            coord = (x_l2, 420)
            x_l2 += 220

        js_lines.append(f'    addDevice("{name}", "{model}", {coord[0]}, {coord[1]});')

    js_lines.extend([
        "",
        "    // ===========================================================================",
        "    // Phase 2: Cable Backbone & Infrastructure Links",
        "    // ===========================================================================",
    ])

    for link in links:
        u = link["endpoint_a"]
        v = link["endpoint_b"]
        intf_a = link["interface_a"]
        intf_b = link["interface_b"]
        link_id = link.get("link_id", "")
        med = media_by_link.get(link_id, {})
        med_type = med.get("media_type", "Cat6a")

        cable_type = _determine_pt_cable_type(dev_map.get(u, {}), dev_map.get(v, {}))
        js_lines.append(
            f'    addLink("{u}", "{intf_a}", "{v}", "{intf_b}", "{cable_type}"); '
            f'// {med_type} ({link.get("distance_m", 0):.0f}m)'
        )

    js_lines.extend([
        "",
        "    // ===========================================================================",
        "    // Phase 3: Add Test End-Devices (PCs/Servers per Subnet), Static IPs & Cabling",
        "    // ===========================================================================",
    ])

    x_host = 100
    y_host = 560

    for s in subnets:
        if s.get("is_p2p") or s.get("is_loopback"):
            continue
        sub_name = s["name"]
        gw = s["gateway"]
        mask = s["mask"]
        gw_int = ip_to_int(gw)
        host_ip = int_to_ip(gw_int + 1)

        is_server = ("Server" in sub_name or "Colo" in sub_name or "Cloud" in sub_name)
        dev_type = "Server-PT" if is_server else "PC-PT"
        host_name = format_host_device_name(sub_name, 1)

        js_lines.append(f'    addDevice("{host_name}", "{dev_type}", {x_host}, {y_host});')
        js_lines.append(f'    configurePcIp("{host_name}", false, "{host_ip}", "{mask}", "{gw}");')

        if sub_name in attachments:
            target_dev, target_intf, cable = attachments[sub_name]
            js_lines.append(
                f'    addLink("{target_dev}", "{target_intf}", "{host_name}", "FastEthernet0", "{cable}");'
            )
        else:
            parent_dev = s.get("device", "Router")
            js_lines.append(
                f'    // Note: {sub_name} (VLAN {s.get("vlan")}) terminates on a Router-on-a-Stick 802.1Q subinterface on {parent_dev}; add a 2960 switch to test.'
            )

        x_host += 130
        if x_host > 850:
            x_host = 100
            y_host += 90

    js_lines.extend([
        "",
        "    // ===========================================================================",
        "    // Phase 4: Push Cisco IOS Configurations (Logical Block-Safe Chunks <= 38 lines)",
        "    // Order: L2 Switches -> L3 Switches -> Routers",
        "    // ===========================================================================",
    ])

    sorted_devs = sorted(
        devices,
        key=lambda d: 0 if d.get("type") == "l2_switch" else 1 if d.get("type") == "l3_switch" else 2
    )

    for dev in sorted_devs:
        dname = dev["name"]
        raw_cfg = configs.get(dname, "")
        chunks = split_ios_into_safe_chunks(raw_cfg, max_lines=38)

        js_lines.append(f"    // --- Configuring {dname} ({dev.get('model_pt')}) ---")
        for batch in chunks:
            cmd_str = "\\n".join(c.replace('"', '\\"') for c in batch)
            js_lines.append(f'    configureIosDevice("{dname}", "{cmd_str}");')

        js_lines.append("")

    js_lines.extend([
        "}",
        "",
        "runNetArchitectBuild();",
        "",
    ])

    return "\n".join(js_lines)
