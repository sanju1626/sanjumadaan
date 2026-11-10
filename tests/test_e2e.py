"""
End-to-End Pipeline & Self-Check Regression Tests
Validates the complete execution flow from JSON ingestion to L1/L2 media,
L3 bitwise VLSM allocation, routing protocol selection, topology latency/resiliency,
explainable ADR generation, and Cisco IOS self-check validation across all 3 presets.
"""

import json
import pytest
from pathlib import Path
from engine.validation import validate_network_specification
from engine.vlsm_engine import allocate_vlsm
from engine.media_engine import evaluate_media
from engine.routing_engine import determine_routing_architecture
from engine.topology import evaluate_tier_architecture, analyze_topology
from engine.decision_engine import generate_decisions_for_scenario
from engine.config_generator import generate_all_configs, run_configuration_self_check
from engine.ptbuilder_gen import generate_ptbuilder_script


@pytest.mark.parametrize("preset_file", ["campus_lan", "metro_man", "global_wan"])
def test_full_pipeline_on_preset(preset_file):
    # 1. Ingestion
    path = Path(f"scenarios/{preset_file}.json")
    assert path.exists(), f"Preset file {path} not found"
    with open(path, "r", encoding="utf-8") as f:
        scen = json.load(f)

    # 2. Validation
    val_report = validate_network_specification(scen)
    assert val_report["is_valid"] is True, f"Validation errors on {preset_file}: {val_report['errors']}"

    # 3. VLSM Allocation (Pure bitwise math)
    vlsm_res = allocate_vlsm(scen["root_cidr"], scen["subnets"])
    assert len(vlsm_res["allocated_subnets"]) == len(scen["subnets"])
    assert vlsm_res["remaining_addresses"] >= 0

    # 4. Media Physics Evaluation
    media_evals = []
    for link in scen["links"]:
        m = evaluate_media(link["distance_m"], forced_media=link.get("forced_media"), link_name=link["link_id"])
        m["link_id"] = link["link_id"]
        media_evals.append(m)
    assert len(media_evals) == len(scen["links"])

    # 5. Routing Architecture
    routing_res = determine_routing_architecture(
        site_count=scen.get("site_count", 1),
        subnet_count=len(vlsm_res["allocated_subnets"]),
        has_cloud_vpc=scen.get("has_cloud_vpc", False),
        is_multi_as=scen.get("is_multi_as", False),
    )

    # 6. Topology Analysis & Resiliency
    leaf_nodes = {"CLOUD-EDGE", "BLDG-A-SW", "BLDG-B-SW", "BLDG-C-SW"}
    topo_res = analyze_topology(
        scen["devices"],
        scen["links"],
        latency_budget_ms=scen.get("latency_budget_ms", 10.0),
        enforce_resiliency=(preset_file == "metro_man"),  # Metro MAN is a full resilient ring
        single_homed_allowed=leaf_nodes,
    )
    assert topo_res["baseline_max_latency_ms"] <= scen.get("latency_budget_ms", 50.0)

    # 7. Tier Architecture
    tier_res = evaluate_tier_architecture(
        access_switch_count=3 if preset_file == "campus_lan" else 1,
        total_endpoints=sum(s["hosts"] for s in scen["subnets"]),
    )

    # 8. Explainable Decision Engine (ADRs)
    decision_engine = generate_decisions_for_scenario(
        scen, media_evals, vlsm_res, routing_res, topo_res, tier_res
    )
    records = decision_engine.get_all_records()
    assert len(records) >= 8  # Covers media, VLSM, VLAN, topology, routing, STP, redundancy, security
    rationale_md = decision_engine.export_rationale_markdown(scen["name"])
    assert len(rationale_md) > 500

    # 9. Cisco IOS Configuration Generation & Strict Self-Check
    configs = generate_all_configs(scen, vlsm_res, media_evals, routing_res, platform="pt", no_crypto=True)
    assert len(configs) == len(scen["devices"])

    self_check = run_configuration_self_check(configs, scen, vlsm_res)
    assert self_check["passed"] is True, f"Self-check failed on {preset_file}: {self_check['errors']}"

    # 10. PTBuilder JavaScript Script Generation
    ptbuilder_js = generate_ptbuilder_script(scen, vlsm_res, configs, media_evals)
    assert len(ptbuilder_js) > 500
    assert "runNetArchitectBuild" in ptbuilder_js
