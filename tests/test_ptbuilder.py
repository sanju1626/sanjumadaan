"""
Unit Tests for PTBuilder Automation Script Generator
Verifies that generated JavaScript files accurately reference every device, link,
interface name, and chunked configuration batch using documented PTBuilder APIs.
"""

import json
import re
from pathlib import Path
from engine.vlsm_engine import allocate_vlsm
from engine.media_engine import evaluate_media
from engine.routing_engine import determine_routing_architecture
from engine.config_generator import generate_all_configs
from engine.ptbuilder_gen import generate_ptbuilder_script, split_ios_into_safe_chunks


def _load_scenario(name: str):
    p = Path(f"scenarios/{name}.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def test_ptbuilder_campus_script_references():
    scen = _load_scenario("campus_lan")
    vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"])
    media_evals = [evaluate_media(l["distance_m"], link_name=l["link_id"]) for l in scen["links"]]
    for m, l in zip(media_evals, scen["links"]):
        m["link_id"] = l["link_id"]
    routing = determine_routing_architecture(scen["site_count"], len(vlsm["allocated_subnets"]))
    configs = generate_all_configs(scen, vlsm, media_evals, routing, platform="pt")

    script = generate_ptbuilder_script(scen, vlsm, configs, media_evals)

    # Check that all devices are added via addDevice
    for dev in scen["devices"]:
        assert f'addDevice("{dev["name"]}"' in script

    # Check that all links are cabled via addLink
    for link in scen["links"]:
        assert f'addLink("{link["endpoint_a"]}"' in script

    # Check Building B & C hosts cable to their OWN building switches (no 'B in BLDG' collision)
    assert 'addLink("BLDG-A-SW", "FastEthernet0/1", "HOST_BLDG_A_Data", "FastEthernet0", "straight");' in script
    assert 'addLink("BLDG-B-SW", "FastEthernet0/1", "HOST_BLDG_B_Data", "FastEthernet0", "straight");' in script
    assert 'addLink("BLDG-C-SW", "FastEthernet0/1", "HOST_BLDG_C_Data", "FastEthernet0", "straight");' in script
    assert 'addLink("BLDG-A-SW", "FastEthernet0/4", "HOST_Servers_Farm", "FastEthernet0", "straight");' in script
    assert 'addLink("BLDG-A-SW", "FastEthernet0/5", "HOST_HQ_Management", "FastEthernet0", "straight");' in script

    # Check that documented PTBuilder CLI push and IP functions are used
    assert "configureIosDevice" in script
    assert "configurePcIp" in script
    assert "Server-PT" in script or "PC-PT" in script


def test_ptbuilder_metro_script_references():
    scen = _load_scenario("metro_man")
    vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"])
    media_evals = [evaluate_media(l["distance_m"], link_name=l["link_id"]) for l in scen["links"]]
    for m, l in zip(media_evals, scen["links"]):
        m["link_id"] = l["link_id"]
    routing = determine_routing_architecture(scen["site_count"], len(vlsm["allocated_subnets"]))
    configs = generate_all_configs(scen, vlsm, media_evals, routing, platform="pt")

    script = generate_ptbuilder_script(scen, vlsm, configs, media_evals)

    for dev in scen["devices"]:
        assert f'addDevice("{dev["name"]}"' in script

    for link in scen["links"]:
        assert f'addLink("{link["endpoint_a"]}"' in script

    # Verify Metro MAN end-hosts attach to HQ-CORE spare ports and remote router LAN ports
    assert 'addLink("HQ-CORE", "GigabitEthernet1/0/3", "HOST_HQ_Users", "FastEthernet0", "straight");' in script
    assert 'addLink("REM1-R", "GigabitEthernet0/2", "HOST_REM1_Users", "FastEthernet0", "cross");' in script
    assert 'addLink("REM2-R", "GigabitEthernet0/2", "HOST_REM2_Users", "FastEthernet0", "cross");' in script


def test_ptbuilder_chunks_never_split_mid_block():
    for preset in ["campus_lan", "metro_man", "global_wan"]:
        scen = _load_scenario(preset)
        vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"], group_by="group" if preset == "global_wan" else None)
        media_evals = [evaluate_media(l["distance_m"], link_name=l["link_id"]) for l in scen["links"]]
        for m, l in zip(media_evals, scen["links"]):
            m["link_id"] = l["link_id"]
        routing = determine_routing_architecture(
            scen["site_count"], len(vlsm["allocated_subnets"]), scen.get("has_cloud_vpc", False), scen.get("is_multi_as", False)
        )
        configs = generate_all_configs(scen, vlsm, media_evals, routing, platform="pt", no_crypto=True)
        script = generate_ptbuilder_script(scen, vlsm, configs, media_evals)

        # Inspect every configureIosDevice batch generated
        matches = re.findall(r'configureIosDevice\("([^"]+)", "([^"]+)"\);', script)
        assert len(matches) > 0
        for dev_name, escaped_cmds in matches:
            cmds = escaped_cmds.split("\\n")
            assert len(cmds) <= 40, f"{dev_name} chunk exceeds 40 lines ({len(cmds)})"
            assert cmds[0] == "enable" and cmds[1] == "configure terminal"
            assert cmds[-1] == "end"
            # First real command after configure terminal must NEVER be an indented subcommand
            assert not cmds[2].startswith(" "), f"{dev_name} chunk started mid-block with '{cmds[2]}'"

        # Also directly test split helper
        chunks = split_ios_into_safe_chunks(next(iter(configs.values())), max_lines=38)
        for ch in chunks:
            assert len(ch) <= 38
