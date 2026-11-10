"""
Shared Pipeline Orchestrator & Pastel UI Helpers for Streamlit Pages
"""

import json
import html
from pathlib import Path
from typing import Any
import streamlit as st

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

BASE_DIR = Path(__file__).resolve().parent.parent
SCENARIO_FILES = {
    "Campus LAN (Enterprise Single-Site)": BASE_DIR / "scenarios" / "campus_lan.json",
    "Metro MAN (Tri-Site Optical Ring)": BASE_DIR / "scenarios" / "metro_man.json",
    "Global WAN (Multi-City & Cloud VPC)": BASE_DIR / "scenarios" / "global_wan.json",
}


def load_css() -> None:
    css_path = BASE_DIR / "ui" / "pastel.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_hero(title: str, subtitle: str, badges: list[tuple[str, str]] | None = None) -> None:
    badge_html = ""
    if badges:
        pills = "".join(
            f'<span class="na-pill na-pill-{html.escape(tone)}">{html.escape(label)}</span>'
            for label, tone in badges
        )
        badge_html = f'<div style="margin-top:0.55rem;">{pills}</div>'
    st.markdown(
        f"""
        <div class="na-hero">
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(subtitle)}</p>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, subtext: str = "", tone: str = "default") -> None:
    tone_cls = "" if tone == "default" else f" na-card-{tone}"
    sub_html = f'<div class="na-metric-sub">{html.escape(subtext)}</div>' if subtext else ""
    st.markdown(
        f"""
        <div class="na-metric{tone_cls}">
            <div class="na-metric-label">{html.escape(label)}</div>
            <div class="na-metric-value">{html.escape(value)}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_preset_scenario(label: str) -> dict[str, Any]:
    path = SCENARIO_FILES[label]
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def execute_full_pipeline(
    scenario: dict[str, Any],
    allow_rfc3021: bool = False,
    platform: str = "pt",
    no_crypto: bool = True,
) -> dict[str, Any]:
    """
    Execute the complete NetArchitect calculation pipeline without silent fallbacks.
    Returns structured dict with {'ok': True/False, ...}.
    """
    val_report = validate_network_specification(scenario)
    if not val_report["is_valid"]:
        return {
            "ok": False,
            "error_type": "ValidationFailed",
            "validation": val_report,
            "message": "; ".join(f"[{e['error_class']}] {e['message']}" for e in val_report["errors"]),
        }

    try:
        scen_id = scenario.get("scenario_id", "custom_network")

        # 1. Media Physics
        media_evals = []
        for link in scenario["links"]:
            lid = link.get("link_id", f"{link['endpoint_a']}-{link['endpoint_b']}")
            m = evaluate_media(
                distance_m=link["distance_m"],
                forced_media=link.get("forced_media"),
                splice_loss_db=float(link.get("splice_loss_db", 0.0)),
                is_endpoint=bool(link.get("is_endpoint", False)),
                link_name=lid,
            )
            m["link_id"] = lid
            media_evals.append(m)

        # 2. Bitwise VLSM Allocation
        use_grouping = "group" if (scenario.get("site_count", 1) > 1 and scen_id == "global_wan") else None
        vlsm_res = allocate_vlsm(
            scenario["root_cidr"],
            scenario["subnets"],
            allow_rfc3021=allow_rfc3021,
            group_by=use_grouping,
        )

        # 3. Routing Architecture
        routing_res = determine_routing_architecture(
            site_count=scenario.get("site_count", 1),
            subnet_count=len(vlsm_res["allocated_subnets"]),
            has_cloud_vpc=scenario.get("has_cloud_vpc", False),
            is_multi_as=scenario.get("is_multi_as", False),
        )

        # 4. Topology & Resiliency
        leaf_nodes = {
            d["name"] for d in scenario["devices"]
            if d.get("type") in ("l2_switch", "cloud")
        }
        enforce_res = (scen_id == "metro_man") or bool(scenario.get("enforce_resiliency", False))
        topo_res = analyze_topology(
            scenario["devices"],
            scenario["links"],
            latency_budget_ms=scenario.get("latency_budget_ms"),
            enforce_resiliency=enforce_res,
            single_homed_allowed=leaf_nodes,
        )

        # 5. Tier Architecture
        access_sw_cnt = sum(1 for d in scenario["devices"] if d.get("type") == "l2_switch") or 1
        total_endpoints = sum(s["hosts"] for s in scenario["subnets"])
        tier_res = evaluate_tier_architecture(
            access_switch_count=access_sw_cnt,
            total_endpoints=total_endpoints,
            building_count=max(1, scenario.get("site_count", 1)),
        )

        # 6. Decision Records
        decision_engine = generate_decisions_for_scenario(
            scenario, media_evals, vlsm_res, routing_res, topo_res, tier_res
        )
        rationale_md = decision_engine.export_rationale_markdown(scenario.get("name", scen_id))

        # 7. Cisco IOS Configs + Self-Check
        configs = generate_all_configs(
            scenario, vlsm_res, media_evals, routing_res, platform=platform, no_crypto=no_crypto
        )
        self_check = run_configuration_self_check(configs, scenario, vlsm_res)

        # 8. PTBuilder & Lab Guide
        ptbuilder_js = generate_ptbuilder_script(scenario, vlsm_res, configs, media_evals)
        lab_guide = generate_lab_guide(scenario, vlsm_res, media_evals, routing_res, configs, topo_res)

        return {
            "ok": True,
            "scenario": scenario,
            "validation": val_report,
            "media_evals": media_evals,
            "vlsm": vlsm_res,
            "routing": routing_res,
            "topology": topo_res,
            "tier": tier_res,
            "decisions": decision_engine.get_all_records(),
            "rationale_md": rationale_md,
            "configs": configs,
            "self_check": self_check,
            "ptbuilder_js": ptbuilder_js,
            "lab_guide": lab_guide,
        }
    except NetArchitectError as e:
        return {
            "ok": False,
            "error_type": type(e).__name__,
            "validation": val_report,
            "message": str(e),
        }
