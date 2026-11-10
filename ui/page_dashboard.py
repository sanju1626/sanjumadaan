"""
Page 1: Dashboard Overview
"""

import html
import pandas as pd
import streamlit as st
from ui.pipeline import render_hero, render_metric_card


def render_dashboard(pipeline_result: dict) -> None:
    scen = pipeline_result["scenario"]
    vlsm = pipeline_result["vlsm"]
    routing = pipeline_result["routing"]
    topo = pipeline_result["topology"]
    tier = pipeline_result["tier"]
    media_evals = pipeline_result["media_evals"]
    self_check = pipeline_result["self_check"]

    render_hero(
        f"NetArchitect — {scen.get('name', 'Active Topology')}",
        scen.get("description", "Algorithmic enterprise network architecture, bitwise VLSM, and self-explaining Cisco IOS generator."),
        badges=[
            (f"Root: {vlsm['root_cidr']}", "lavender"),
            (f"Sites: {scen.get('site_count', 1)}", "mint"),
            (f"Routing: {routing['primary_protocol']}", "peach"),
            ("Pure Bitwise Math", "butter"),
        ],
    )

    total_hosts = sum(s["requested_hosts"] for s in vlsm["allocated_subnets"] if not s.get("is_p2p"))
    total_subnets = len(vlsm["allocated_subnets"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            "End-Host Demand",
            f"{total_hosts:,}",
            f"Across {total_subnets} subnets",
            tone="lavender",
        )
    with col2:
        render_metric_card(
            "Bitwise Efficiency",
            f"{vlsm['overall_efficiency_pct']}%",
            f"Space Used: {vlsm['overall_utilization_pct']}% of {vlsm['root_cidr']}",
            tone="mint",
        )
    with col3:
        n1_text = "N-1 Resilient" if topo.get("is_resilient_n_minus_1") else "Single-Homed Leaf/Star"
        render_metric_card(
            "Max Path Latency",
            f"{topo['baseline_max_latency_ms']} ms",
            f"Objective: {topo.get('latency_budget_ms', 'N/A')} ms ({n1_text})",
            tone="peach",
        )
    with col4:
        sc_status = "PASSED" if self_check["passed"] else "FAILED"
        render_metric_card(
            "IOS Self-Check",
            sc_status,
            f"{self_check['checked_ip_count']} unique IPs verified (0 overlaps)",
            tone="butter" if self_check["passed"] else "blush",
        )

    st.markdown("### Architecture Snapshot")
    left, right = st.columns(2)
    with left:
        st.markdown(
            f"""
            <div class="na-card na-card-lavender">
                <strong>Control & Switching Plane</strong><br/>
                <span class="na-pill na-pill-lavender">Topology Tier</span> {html.escape(tier['recommended_tier'])}<br/>
                <span class="na-pill na-pill-mint">IGP Routing</span> {html.escape(routing['primary_protocol'])}<br/>
                <span class="na-pill na-pill-peach">EGP / Cloud</span> {html.escape(routing['exterior_protocol'] or 'None (Single-AS Enterprise)')}<br/>
                <span class="na-pill na-pill-butter">Oversubscription</span> {tier['oversubscription_ratio']:.1f}:1 access ratio
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        devices = scen.get("devices", [])
        dev_summary = ", ".join(f"{d['name']} ({d.get('model_pt', 'IOS')})" for d in devices)
        st.markdown(
            f"""
            <div class="na-card na-card-mint">
                <strong>Hardware Inventory & Policy ({len(devices)} Devices)</strong><br/>
                <p style="margin:0.35rem 0;">{html.escape(dev_summary)}</p>
                <p style="margin:0.2rem 0;font-size:0.86rem;"><strong>Policy:</strong> {html.escape(scen.get('security_policy') or scen.get('qos_policy') or 'Standard OSPF + SSH v2')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    t1, t2 = st.tabs(["Physical Links Summary", "Allocated Subnets Summary"])
    with t1:
        media_df = pd.DataFrame([
            {
                "Link ID": m.get("link_id", m.get("link_name")),
                "Distance (m)": m["distance_m"],
                "Media Selected": m["media_type"],
                "Transceiver": m.get("transceiver", "RJ-45"),
                "Loss (dB)": f"{m['loss_db']:.2f}" if m.get("loss_db") is not None else "-",
                "Margin (dB)": f"{m['margin_db']:.2f}" if m.get("margin_db") is not None else "-",
            }
            for m in media_evals
        ])
        st.dataframe(media_df, width="stretch", hide_index=True)

    with t2:
        sub_df = pd.DataFrame([
            {
                "Subnet": s["name"],
                "VLAN": str(s["vlan"]) if s["vlan"] is not None else "P2P/Cloud",
                "CIDR": s["cidr"],
                "Gateway": s["gateway"],
                "Wildcard": s["wildcard"],
                "Req Hosts": s["requested_hosts"],
                "Usable": s["usable_hosts"],
                "Efficiency (%)": s["efficiency_pct"],
            }
            for s in vlsm["allocated_subnets"]
        ])
        st.dataframe(sub_df, width="stretch", hide_index=True)
