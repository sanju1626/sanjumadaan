"""
Unit Tests for Cisco IOS Configuration Generator across Presets
Tests:
  - VLAN, SVI, Trunk allowed lists, OSPF wildcards, and ACLs on Campus LAN
  - MQC QoS priority queues and OSPF costs on Metro MAN
  - eBGP peering and GRE tunnels on Global WAN
"""

import json
import pytest
from pathlib import Path
from engine.vlsm_engine import allocate_vlsm
from engine.media_engine import evaluate_media
from engine.routing_engine import determine_routing_architecture
from engine.config_generator import generate_all_configs, run_configuration_self_check


def _load_scenario(name: str):
    p = Path(f"scenarios/{name}.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def test_campus_lan_config_generation():
    scen = _load_scenario("campus_lan")
    vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"])
    media_evals = [evaluate_media(l["distance_m"], link_name=l["link_id"]) for l in scen["links"]]
    for m, l in zip(media_evals, scen["links"]):
        m["link_id"] = l["link_id"]
    routing = determine_routing_architecture(scen["site_count"], len(vlsm["allocated_subnets"]))

    configs = generate_all_configs(scen, vlsm, media_evals, routing, platform="pt")

    # Assert all 5 devices exist
    assert "EDGE-R1" in configs
    assert "CORE-SW" in configs
    assert "BLDG-A-SW" in configs
    assert "BLDG-B-SW" in configs
    assert "BLDG-C-SW" in configs

    core_cfg = configs["CORE-SW"]
    # Check VLANs and SVIs present on Core Switch
    assert "vlan 10" in core_cfg
    assert "vlan 100" in core_cfg
    assert "interface Vlan10" in core_cfg
    assert "interface Vlan100" in core_cfg
    # Check Rapid-PVST+ root priority
    assert "spanning-tree vlan 1-4094 priority 4096" in core_cfg
    # Check explicit trunk allowed vlan and native vlan 999
    assert "switchport trunk native vlan 999" in core_cfg
    assert "switchport trunk allowed vlan" in core_cfg
    # Check Named Extended ACL for WiFi restriction
    assert "ip access-list extended ACL_WIFI_SECURITY" in core_cfg
    assert "deny ip any" in core_cfg
    assert "permit ip any any" in core_cfg
    # Check NAT on EDGE-R1
    edge_cfg = configs["EDGE-R1"]
    assert "ip nat inside source list" in edge_cfg


def test_metro_man_config_generation():
    scen = _load_scenario("metro_man")
    vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"])
    media_evals = [evaluate_media(l["distance_m"], link_name=l["link_id"]) for l in scen["links"]]
    for m, l in zip(media_evals, scen["links"]):
        m["link_id"] = l["link_id"]
    routing = determine_routing_architecture(scen["site_count"], len(vlsm["allocated_subnets"]))

    configs = generate_all_configs(scen, vlsm, media_evals, routing, platform="pt")

    hq_cfg = configs["HQ-CORE"]
    # Check MQC QoS
    assert "class-map match-any CM_VOIP_FINTECH" in hq_cfg
    assert "policy-map PM_METRO_QOS_EGRESS" in hq_cfg
    assert "priority percent" in hq_cfg

    # Check OSPF cost on backup link
    rem1_cfg = configs["REM1-R"]
    assert "ip ospf cost 100" in rem1_cfg or "ip ospf cost 10" in rem1_cfg


def test_global_wan_config_generation():
    scen = _load_scenario("global_wan")
    vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"], group_by="group")
    media_evals = [evaluate_media(l["distance_m"], link_name=l["link_id"]) for l in scen["links"]]
    for m, l in zip(media_evals, scen["links"]):
        m["link_id"] = l["link_id"]
    routing = determine_routing_architecture(scen["site_count"], len(vlsm["allocated_subnets"]), has_cloud_vpc=True, is_multi_as=True)

    configs = generate_all_configs(scen, vlsm, media_evals, routing, platform="pt", no_crypto=True)

    del_cfg = configs["R-DEL"]
    cloud_cfg = configs["CLOUD-EDGE"]

    # Check dynamic eBGP peering IPs match P2P-DEL-CLOUD
    p2p_cloud = next(s for s in vlsm["allocated_subnets"] if s["name"] == "P2P-DEL-CLOUD")
    assert "router bgp 65001" in del_cfg
    assert f"neighbor {p2p_cloud['last_host']} remote-as 65010" in del_cfg
    assert "router bgp 65010" in cloud_cfg
    assert f"neighbor {p2p_cloud['first_host']} remote-as 65001" in cloud_cfg

    # Check dynamic ABR area ranges
    area1_sum = vlsm["group_summaries"]["Area 1 (Mumbai)"]
    assert f"area 1 range {area1_sum['summary_network']} {area1_sum['summary_mask']}" in del_cfg

    # Check GRE Tunnel
    assert "interface Tunnel0" in del_cfg


def test_self_check_detects_duplicate_ip():
    scen = _load_scenario("campus_lan")
    vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"])
    fake_configs = {
        "R1": "interface Gi0/0\n ip address 10.10.0.1 255.255.255.0\n",
        "R2": "interface Gi0/0\n ip address 10.10.0.1 255.255.255.0\n",
    }
    report = run_configuration_self_check(fake_configs, scen, vlsm)
    assert report["passed"] is False
    assert any("Duplicate IP 10.10.0.1" in e for e in report["errors"])


def test_no_unrestricted_trunks_across_presets():
    for preset in ["campus_lan", "metro_man", "global_wan"]:
        scen = _load_scenario(preset)
        vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"])
        media_evals = [evaluate_media(l["distance_m"], link_name=l["link_id"]) for l in scen["links"]]
        for m, l in zip(media_evals, scen["links"]):
            m["link_id"] = l["link_id"]
        routing = determine_routing_architecture(scen["site_count"], len(vlsm["allocated_subnets"]), scen.get("has_cloud_vpc", False))
        configs = generate_all_configs(scen, vlsm, media_evals, routing, platform="pt", no_crypto=True)
        for dev_name, cfg in configs.items():
            assert "Packet Tracer Verified" not in cfg, f"Unverified claim found in {dev_name}!"
            if "switchport mode trunk" in cfg:
                assert "switchport trunk allowed vlan" in cfg, f"Unrestricted trunk on {dev_name} in {preset}!"
                assert "switchport trunk native vlan 999" in cfg
                assert "switchport nonegotiate" in cfg


def test_self_check_detects_missing_acl_and_ospf_mismatch():
    scen = _load_scenario("campus_lan")
    vlsm = allocate_vlsm(scen["root_cidr"], scen["subnets"])

    bad_acl_configs = {
        "EDGE-R1": (
            "interface GigabitEthernet0/0\n"
            " ip address 10.10.9.129 255.255.255.252\n"
            "line vty 0 4\n"
            " access-class ACL_MGMT_VTY in\n"
        )
    }
    res_acl = run_configuration_self_check(bad_acl_configs, scen, vlsm)
    assert res_acl["passed"] is False
    assert any("undefined ACL" in e for e in res_acl["errors"])

    bad_ospf_configs = {
        "EDGE-R1": (
            "interface GigabitEthernet0/0\n"
            " ip address 10.10.9.129 255.255.255.252\n"
            "router ospf 1\n"
            " network 192.168.99.0 0.0.0.255 area 0\n"
        )
    }
    res_ospf = run_configuration_self_check(bad_ospf_configs, scen, vlsm)
    assert res_ospf["passed"] is False
    assert any("does not match any configured interface" in e for e in res_ospf["errors"])


def test_every_referenced_acl_defined_on_same_device():
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
        report = run_configuration_self_check(configs, scen, vlsm)
        assert report["passed"] is True, f"{preset} failed self-check: {report['errors']}"
