"""
Page 3: Custom Network Designer & Live Error-Handling Lab
"""

import copy
import json
import html
import pandas as pd
import streamlit as st
from engine.errors import (
    NetArchitectError,
    PhysicalDistanceViolationError,
    AddressSpaceExhaustedError,
    OpticalBudgetError,
)
from engine.media_engine import evaluate_media
from engine.vlsm_engine import allocate_vlsm
from ui.pipeline import render_hero, execute_full_pipeline


def render_custom_designer() -> None:
    render_hero(
        "Custom Network Designer & Validation Lab",
        "Design custom topologies with live validation catching every physical, addressing, VLAN, and graph error safely — plus one-click adversarial fault triggers.",
        badges=[("Zero Crash Guarantee", "mint"), ("Explicit Error Classes", "blush")],
    )

    # Interactive Viva Demo Buttons (Requirement 6 / UI Custom Designer)
    st.markdown("### Adversarial Engine Constraint Triggers")
    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        if st.button("Test Distance Violation", width="stretch", type="secondary"):
            try:
                evaluate_media(250.0, forced_media="copper", link_name="DEMO-COPPER-250M")
            except PhysicalDistanceViolationError as exc:
                st.session_state["demo_fault"] = (
                    "PhysicalDistanceViolationError",
                    "blush",
                    str(exc),
                )

    with btn_col2:
        if st.button("Test Address Exhaustion", width="stretch", type="secondary"):
            try:
                allocate_vlsm(
                    "192.168.10.0/24",
                    [
                        {"name": "Building-East-Users", "hosts": 200},
                        {"name": "Building-West-Users", "hosts": 100},
                    ],
                )
            except AddressSpaceExhaustedError as exc:
                st.session_state["demo_fault"] = (
                    "AddressSpaceExhaustedError",
                    "peach",
                    str(exc),
                )

    with btn_col3:
        if st.button("Test Optical Budget Exceeded", width="stretch", type="secondary"):
            try:
                evaluate_media(40000.0, splice_loss_db=1.0, link_name="DEMO-ER-OVERBUDGET")
            except OpticalBudgetError as exc:
                st.session_state["demo_fault"] = (
                    "OpticalBudgetError",
                    "butter",
                    str(exc),
                )

    if "demo_fault" in st.session_state:
        err_cls, tone, msg = st.session_state["demo_fault"]
        st.markdown(
            f"""
            <div class="na-card na-card-{tone}">
                <span class="na-pill na-pill-{tone}">Caught Exception: {html.escape(err_cls)}</span>
                <p style="margin:0.45rem 0 0 0;font-family:'JetBrains Mono',monospace;font-size:0.86rem;">
                    {html.escape(msg)}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("### Interactive Topology Builder")

    if "custom_draft" not in st.session_state:
        st.session_state["custom_draft"] = copy.deepcopy(st.session_state["active_scenario"])

    draft = st.session_state["custom_draft"]

    c_top1, c_top2 = st.columns([2, 1])
    with c_top1:
        if st.button("Load Current Active Scenario as Template", width="stretch"):
            st.session_state["custom_draft"] = copy.deepcopy(st.session_state["active_scenario"])
            st.rerun()
    with c_top2:
        mode = st.radio("Edit Mode", ["Form & Tables", "Raw JSON"], horizontal=True)

    candidate_spec = copy.deepcopy(draft)

    if mode == "Form & Tables":
        m1, m2, m3, m4 = st.columns(4)
        candidate_spec["name"] = m1.text_input("Scenario Name", value=draft.get("name", "Custom Topology"))
        candidate_spec["root_cidr"] = m2.text_input("Root CIDR Block", value=draft.get("root_cidr", "10.20.0.0/16"))
        candidate_spec["site_count"] = int(m3.number_input("Site Count", min_value=1, max_value=100, value=int(draft.get("site_count", 1))))
        candidate_spec["latency_budget_ms"] = float(m4.number_input("Latency Budget (ms)", min_value=0.05, max_value=500.0, value=float(draft.get("latency_budget_ms") or 10.0), step=0.5))

        c_chk1, c_chk2, c_chk3 = st.columns(3)
        candidate_spec["has_cloud_vpc"] = c_chk1.checkbox("Has Cloud VPC", value=bool(draft.get("has_cloud_vpc", False)))
        candidate_spec["is_multi_as"] = c_chk2.checkbox("Multi-AS (eBGP)", value=bool(draft.get("is_multi_as", False)))
        enforce_res = c_chk3.checkbox("Enforce N-1 Link Resiliency", value=bool(draft.get("enforce_resiliency", False)))
        candidate_spec["enforce_resiliency"] = enforce_res

        t_dev, t_link, t_sub = st.tabs(["Devices", "Links", "Subnets"])
        with t_dev:
            flat_devs = []
            for d in draft.get("devices", []):
                fd = {k: v for k, v in d.items() if k != "bgp"}
                if isinstance(d.get("bgp"), dict) and d["bgp"].get("remote_asn") is not None:
                    fd["remote_asn"] = d["bgp"]["remote_asn"]
                flat_devs.append(fd)
            dev_df = pd.DataFrame(flat_devs)
            edited_devs = st.data_editor(dev_df, num_rows="dynamic", width="stretch", key="edit_devs")
            cleaned_devs = []
            for row in edited_devs.to_dict(orient="records"):
                clean = {}
                remote_asn_val = None
                for k, v in row.items():
                    if pd.isna(v) or v == "":
                        continue
                    if k == "remote_asn":
                        remote_asn_val = int(v) if isinstance(v, (int, float)) else v
                    elif k == "ospf_area" and isinstance(v, (int, float)):
                        clean[k] = int(v)
                    else:
                        clean[k] = v
                if remote_asn_val is not None:
                    clean["bgp"] = {"remote_asn": remote_asn_val}
                if clean:
                    cleaned_devs.append(clean)
            candidate_spec["devices"] = cleaned_devs
        with t_link:
            link_df = pd.DataFrame(draft.get("links", []))
            edited_links = st.data_editor(link_df, num_rows="dynamic", width="stretch", key="edit_links")
            cleaned_links = []
            for row in edited_links.to_dict(orient="records"):
                clean = {}
                for k, v in row.items():
                    if pd.isna(v) or v == "":
                        continue
                    if k == "ospf_cost" and isinstance(v, (int, float)):
                        clean[k] = int(v)
                    elif k == "is_endpoint" and isinstance(v, (bool, float, int)):
                        clean[k] = bool(v)
                    else:
                        clean[k] = v
                if "forced_media" not in clean:
                    clean["forced_media"] = None
                if clean:
                    cleaned_links.append(clean)
            candidate_spec["links"] = cleaned_links
        with t_sub:
            sub_df = pd.DataFrame(draft.get("subnets", []))
            edited_subs = st.data_editor(sub_df, num_rows="dynamic", width="stretch", key="edit_subs")
            cleaned_subs = []
            for row in edited_subs.to_dict(orient="records"):
                clean = {}
                for k, v in row.items():
                    if pd.isna(v) or v == "":
                        continue
                    if k in ("hosts", "vlan") and isinstance(v, (int, float)):
                        clean[k] = int(v)
                    elif k in ("is_p2p", "is_priority_queue", "is_loopback") and isinstance(v, (bool, float, int)):
                        clean[k] = bool(v)
                    else:
                        clean[k] = v
                if "vlan" not in clean:
                    clean["vlan"] = None
                if clean:
                    cleaned_subs.append(clean)
            candidate_spec["subnets"] = cleaned_subs
    else:
        raw_text = st.text_area(
            "Custom Scenario JSON",
            value=json.dumps(draft, indent=2),
            height=380,
        )
        try:
            candidate_spec = json.loads(raw_text)
        except json.JSONDecodeError as je:
            st.error(f"[InvalidParameterError / JSONDecodeError] Malformed JSON at line {je.lineno}: {je.msg}")
            return

    st.session_state["custom_draft"] = candidate_spec

    # Live Validation & Execution
    result = execute_full_pipeline(
        candidate_spec,
        allow_rfc3021=st.session_state.get("allow_rfc3021", False),
        platform=st.session_state.get("platform", "pt"),
        no_crypto=st.session_state.get("no_crypto", True),
    )

    if not result["ok"]:
        err_type = result.get("error_type", "NetArchitectError")
        val = result.get("validation", {})
        if val.get("errors"):
            lines_html = "".join(
                f"<li><strong>[{html.escape(e['error_class'])}]</strong> <code>{html.escape(str(e['field']))}</code>: {html.escape(e['message'])}</li>"
                for e in val["errors"]
            )
            st.markdown(
                f"""
                <div class="na-card na-card-blush">
                    <span class="na-pill na-pill-blush">Validation Failed ({len(val['errors'])} issue(s))</span>
                    <ul style="margin:0.5rem 0 0 1.2rem;">{lines_html}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="na-card na-card-blush">
                    <span class="na-pill na-pill-blush">Engine Exception: {html.escape(err_type)}</span>
                    <p style="margin:0.45rem 0 0 0;">{html.escape(result['message'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"""
            <div class="na-card na-card-mint">
                <span class="na-pill na-pill-mint">Specification Valid & Synthesized</span>
                <p style="margin:0.4rem 0 0 0;">
                    Allocated <strong>{len(result['vlsm']['allocated_subnets'])}</strong> non-overlapping subnets
                    ({result['vlsm']['overall_efficiency_pct']}% efficiency) |
                    Routing: <strong>{html.escape(result['routing']['primary_protocol'])}</strong> |
                    Max Latency: <strong>{result['topology']['baseline_max_latency_ms']} ms</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Apply Custom Network to Entire Dashboard", type="primary", width="stretch"):
                st.session_state["custom_active_scenario"] = copy.deepcopy(candidate_spec)
                st.session_state["using_custom"] = True
                st.success("Custom scenario activated! Switch to any tab in the sidebar to inspect VLSM, Topology, Configs & PTBuilder.")
                st.rerun()
        with col_b:
            st.download_button(
                "Download Custom Scenario JSON",
                data=json.dumps(candidate_spec, indent=2),
                file_name="custom_scenario.json",
                mime="application/json",
                width="stretch",
            )
