"""
NetArchitect Command-Line Interface (CLI)
Automates enterprise network evaluation, bitwise VLSM allocation, routing synthesis,
Cisco IOS configuration generation, self-check validation, architectural rationale export,
and Packet Tracer / PTBuilder lab pack generation.

Usage Examples:
  python cli.py --preset campus --out exports/
  python cli.py --preset man --out exports/ --emit-ptbuilder
  python cli.py --preset wan --out exports/ --no-crypto --platform pt --emit-ptbuilder
  python cli.py --custom my_network.json --out exports/
"""

import argparse
import json
import sys
from pathlib import Path

from engine.errors import NetArchitectError
from engine.validation import validate_network_specification
from engine.media_engine import evaluate_media
from engine.vlsm_engine import allocate_vlsm
from engine.routing_engine import determine_routing_architecture
from engine.topology import evaluate_tier_architecture, analyze_topology
from engine.decision_engine import generate_decisions_for_scenario
from engine.config_generator import generate_all_configs, run_configuration_self_check
from engine.ptbuilder_gen import generate_ptbuilder_script
from engine.lab_pack import generate_lab_guide


PRESET_MAP = {
    "campus": "scenarios/campus_lan.json",
    "man": "scenarios/metro_man.json",
    "wan": "scenarios/global_wan.json",
}


def run_pipeline_for_scenario(
    spec_path: Path,
    out_dir: Path,
    lab_dir: Path,
    platform: str = "pt",
    no_crypto: bool = False,
    emit_ptbuilder: bool = False,
    allow_rfc3021: bool = False,
) -> None:
    """Execute complete NetArchitect architectural pipeline for a given scenario JSON."""
    if not spec_path.exists():
        print(f"[ERROR] Specification file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    with open(spec_path, "r", encoding="utf-8") as f:
        scen = json.load(f)

    scen_id = scen.get("scenario_id", spec_path.stem)
    print(f"\n=== NetArchitect Synthesis Engine: {scen.get('name', scen_id)} ===")

    # 1. Validation
    val = validate_network_specification(scen)
    if not val["is_valid"]:
        print("[ERROR] Validation Failed:", file=sys.stderr)
        for err in val["errors"]:
            print(f"  - [{err['error_class']}] {err['field']}: {err['message']}", file=sys.stderr)
        sys.exit(1)
    print("  [OK] Parameter & Topology Validation passed.")

    # 2. Media Physics Engine
    media_evals = []
    for link in scen["links"]:
        m = evaluate_media(
            distance_m=link["distance_m"],
            forced_media=link.get("forced_media"),
            splice_loss_db=float(link.get("splice_loss_db", 0.0)),
            is_endpoint=bool(link.get("is_endpoint", False)),
            link_name=link.get("link_id", f"{link['endpoint_a']}-{link['endpoint_b']}"),
        )
        m["link_id"] = link.get("link_id", f"{link['endpoint_a']}-{link['endpoint_b']}")
        media_evals.append(m)
    print(f"  [OK] Evaluated physical media & optical budgets for {len(media_evals)} link(s).")

    # 3. Bitwise VLSM Allocator
    use_grouping = "group" if scen.get("site_count", 1) > 1 and scen_id == "global_wan" else None
    vlsm_res = allocate_vlsm(
        scen["root_cidr"],
        scen["subnets"],
        allow_rfc3021=allow_rfc3021,
        group_by=use_grouping,
    )
    print(
        f"  [OK] Allocated {len(vlsm_res['allocated_subnets'])} non-overlapping subnets "
        f"(Efficiency: {vlsm_res['overall_efficiency_pct']}%, Util: {vlsm_res['overall_utilization_pct']}%)."
    )

    # 4. Routing & Topology Engines
    routing_res = determine_routing_architecture(
        site_count=scen.get("site_count", 1),
        subnet_count=len(vlsm_res["allocated_subnets"]),
        has_cloud_vpc=scen.get("has_cloud_vpc", False),
        is_multi_as=scen.get("is_multi_as", False),
    )

    leaf_nodes = {
        d["name"] for d in scen["devices"]
        if d.get("type") in ("l2_switch", "cloud")
    }
    enforce_res = (scen_id == "metro_man") or bool(scen.get("enforce_resiliency", False))
    topo_res = analyze_topology(
        scen["devices"],
        scen["links"],
        latency_budget_ms=scen.get("latency_budget_ms", 50.0),
        enforce_resiliency=enforce_res,
        single_homed_allowed=leaf_nodes,
    )

    access_sw_cnt = sum(1 for d in scen["devices"] if d.get("type") == "l2_switch") or 1
    total_endpoints = sum(s["hosts"] for s in scen["subnets"])
    tier_res = evaluate_tier_architecture(
        access_switch_count=access_sw_cnt,
        total_endpoints=total_endpoints,
    )
    print(
        f"  [OK] Routing: {routing_res['primary_protocol']}"
        f"{' + ' + routing_res['exterior_protocol'] if routing_res['exterior_protocol'] else ''} "
        f"| Max Latency: {topo_res['baseline_max_latency_ms']} ms"
    )

    # 5. Explainable Decision Engine
    decision_engine = generate_decisions_for_scenario(
        scen, media_evals, vlsm_res, routing_res, topo_res, tier_res
    )
    rationale_md = decision_engine.export_rationale_markdown(scen.get("name", scen_id))

    # 6. Cisco IOS Config Generation & Automated Self-Check
    configs = generate_all_configs(
        scen, vlsm_res, media_evals, routing_res, platform=platform, no_crypto=no_crypto
    )
    self_check = run_configuration_self_check(configs, scen, vlsm_res)
    if not self_check["passed"]:
        print(f"[ERROR] Self-check failed: {self_check['errors']}", file=sys.stderr)
        sys.exit(1)
    print(f"  [OK] Generated {len(configs)} device config(s) & passed self-check ({self_check['checked_ip_count']} unique IPs verified).")

    # 7. Write Exports
    out_dir.mkdir(parents=True, exist_ok=True)
    device_dir = out_dir / scen_id
    device_dir.mkdir(parents=True, exist_ok=True)

    # Combined preset config file (e.g. exports/campus_lan_config.cfg)
    combined_path = out_dir / f"{scen_id}_config.cfg"
    combined_content = []
    for dname, cfg in configs.items():
        device_file = device_dir / f"{dname}.cfg"
        device_file.write_text(cfg, encoding="utf-8")
        combined_content.append(f"! >>> DEVICE: {dname} <<<\n{cfg}")

    combined_path.write_text("\n\n".join(combined_content), encoding="utf-8")

    # Rationale Markdown export
    rationale_path = out_dir / f"rationale_{scen_id}.md"
    rationale_path.write_text(rationale_md, encoding="utf-8")

    print(f"  [SAVED] Combined config: {combined_path}")
    print(f"  [SAVED] Per-device configs: {device_dir}/ ({len(configs)} files)")
    print(f"  [SAVED] Architectural rationale: {rationale_path}")

    # 8. Optional Lab Pack & PTBuilder Automation Export
    if emit_ptbuilder:
        preset_lab_dir = lab_dir / scen_id
        preset_lab_dir.mkdir(parents=True, exist_ok=True)

        ptbuilder_js = generate_ptbuilder_script(scen, vlsm_res, configs, media_evals)
        ptb_path = preset_lab_dir / f"ptbuilder_{scen_id}.js"
        ptb_path.write_text(ptbuilder_js, encoding="utf-8")

        lab_guide = generate_lab_guide(scen, vlsm_res, media_evals, routing_res, configs, topo_res)
        guide_path = preset_lab_dir / "lab_guide.md"
        guide_path.write_text(lab_guide, encoding="utf-8")

        print(f"  [SAVED] PTBuilder script: {ptb_path}")
        print(f"  [SAVED] Lab Verification Guide: {guide_path}")


def main():
    parser = argparse.ArgumentParser(
        description="NetArchitect: Algorithmic Network Planning & Self-Explaining Config Engine CLI"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--preset",
        choices=["campus", "man", "wan", "all"],
        help="Built-in enterprise network preset to synthesize.",
    )
    group.add_argument(
        "--custom",
        type=str,
        help="Path to custom scenario JSON file.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="exports/",
        help="Output directory for Cisco .cfg and rationale .md exports (default: exports/).",
    )
    parser.add_argument(
        "--lab-out",
        type=str,
        default="lab/",
        help="Output directory for Packet Tracer lab pack and PTBuilder scripts (default: lab/).",
    )
    parser.add_argument(
        "--platform",
        choices=["pt", "ios"],
        default="pt",
        help="Target CLI syntax dialect ('pt' for Packet Tracer compatible Gigabit naming, 'ios' for real hardware).",
    )
    parser.add_argument(
        "--no-crypto",
        action="store_true",
        help="Omit IPsec crypto profiles on WAN GRE tunnels for Packet Tracer compatibility.",
    )
    parser.add_argument(
        "--emit-ptbuilder",
        action="store_true",
        help="Generate Packet Tracer lab guide and PTBuilder .js automation script.",
    )
    parser.add_argument(
        "--rfc3021",
        action="store_true",
        help="Use RFC 3021 /31 addressing for point-to-point links instead of /30.",
    )

    args = parser.parse_args()
    out_dir = Path(args.out)
    lab_dir = Path(args.lab_out)

    try:
        if args.custom:
            run_pipeline_for_scenario(
                Path(args.custom),
                out_dir,
                lab_dir,
                platform=args.platform,
                no_crypto=args.no_crypto,
                emit_ptbuilder=args.emit_ptbuilder,
                allow_rfc3021=args.rfc3021,
            )
        elif args.preset == "all":
            for p_key, p_path in PRESET_MAP.items():
                run_pipeline_for_scenario(
                    Path(p_path),
                    out_dir,
                    lab_dir,
                    platform=args.platform,
                    no_crypto=(args.no_crypto or p_key == "wan"),
                    emit_ptbuilder=args.emit_ptbuilder,
                    allow_rfc3021=args.rfc3021,
                )
        else:
            run_pipeline_for_scenario(
                Path(PRESET_MAP[args.preset]),
                out_dir,
                lab_dir,
                platform=args.platform,
                no_crypto=args.no_crypto,
                emit_ptbuilder=args.emit_ptbuilder,
                allow_rfc3021=args.rfc3021,
            )
    except NetArchitectError as e:
        print(f"\n[NETARCHITECT ERROR: {type(e).__name__}] {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
