"""
NetArchitect — Algorithmic Enterprise Network Planner & Self-Explaining Cisco IOS Engine
Streamlit Web Application Entry Point (CIC-307 Mini-Project)
Run locally: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="NetArchitect | Algorithmic Network Planner",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.pipeline import (
    SCENARIO_FILES,
    load_css,
    load_preset_scenario,
    execute_full_pipeline,
)
from ui.page_dashboard import render_dashboard
from ui.page_scenarios import render_scenarios
from ui.page_custom import render_custom_designer
from ui.page_media import render_media
from ui.page_vlsm import render_vlsm
from ui.page_routing import render_routing_topology
from ui.page_configs import render_configs
from ui.page_decisions import render_decisions
from ui.page_audit import render_audit_lab
from ui.page_packet_tracer import render_packet_tracer
from ui.page_about import render_about


PAGES = [
    "Dashboard",
    "Scenario Selection",
    "Custom Network Designer",
    "Physical Media",
    "VLSM Calculator",
    "Routing & Architecture",
    "Cisco Config Generator",
    "Architectural Decision Log",
    "AI Audit Lab",
    "Packet Tracer Verification",
    "About",
]


def main() -> None:
    load_css()

    # Initialize defaults
    if "active_preset_label" not in st.session_state:
        st.session_state["active_preset_label"] = list(SCENARIO_FILES.keys())[0]
    if "using_custom" not in st.session_state:
        st.session_state["using_custom"] = False
    if "allow_rfc3021" not in st.session_state:
        st.session_state["allow_rfc3021"] = False
    if "platform" not in st.session_state:
        st.session_state["platform"] = "pt"
    if "no_crypto" not in st.session_state:
        st.session_state["no_crypto"] = True

    with st.sidebar:
        st.markdown(
            """
            <div style="padding:0.4rem 0 0.8rem 0;">
                <h2 style="margin:0;font-size:1.55rem;color:#2B1F3A;">NetArchitect</h2>
                <span style="font-size:0.82rem;color:#5F5170;">CIC-307 Algorithmic Network Studio</span><br/>
                <span style="font-size:0.78rem;font-weight:600;color:#6C4FA8;">Sanju Madaan · 00714803124 · 5C1</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        preset_options = list(SCENARIO_FILES.keys())
        selected_preset = st.selectbox(
            "Active Enterprise Preset",
            preset_options,
            index=preset_options.index(st.session_state["active_preset_label"]),
        )
        if selected_preset != st.session_state["active_preset_label"]:
            st.session_state["active_preset_label"] = selected_preset
            st.session_state["using_custom"] = False

        if st.session_state.get("using_custom") and "custom_active_scenario" in st.session_state:
            active_scenario = st.session_state["custom_active_scenario"]
            st.info("Mode: Custom Scenario Active")
            if st.button("Revert to Selected Preset", width="stretch"):
                st.session_state["using_custom"] = False
                st.rerun()
        else:
            active_scenario = load_preset_scenario(st.session_state["active_preset_label"])

        st.session_state["active_scenario"] = active_scenario

        st.session_state["allow_rfc3021"] = st.checkbox(
            "Use RFC 3021 (/31 P2P Links)",
            value=bool(st.session_state["allow_rfc3021"]),
            help="Allocates /31 instead of /30 for point-to-point links.",
        )

        st.divider()
        page = st.radio("Navigation", PAGES, label_visibility="collapsed")
        st.divider()
        st.caption("Pure bitwise math (no paid APIs). Outputs for Packet Tracer require local PT confirmation.")

    # Run synthesis pipeline for active scenario
    pipeline_res = execute_full_pipeline(
        active_scenario,
        allow_rfc3021=st.session_state["allow_rfc3021"],
        platform=st.session_state["platform"],
        no_crypto=st.session_state["no_crypto"],
    )

    # Pages that work even if active scenario had an error
    if page == "Scenario Selection":
        render_scenarios()
        return
    if page == "Custom Network Designer":
        render_custom_designer()
        return
    if page == "AI Audit Lab":
        render_audit_lab()
        return
    if page == "About":
        render_about()
        return

    if not pipeline_res["ok"]:
        st.error(f"[{pipeline_res.get('error_type')}] Active scenario error: {pipeline_res['message']}")
        st.info("Switch to 'Custom Network Designer' or 'Scenario Selection' to fix or reload a preset.")
        return

    if page == "Dashboard":
        render_dashboard(pipeline_res)
    elif page == "Physical Media":
        render_media(pipeline_res)
    elif page == "VLSM Calculator":
        render_vlsm(pipeline_res)
    elif page == "Routing & Architecture":
        render_routing_topology(pipeline_res)
    elif page == "Cisco Config Generator":
        render_configs(pipeline_res)
    elif page == "Architectural Decision Log":
        render_decisions(pipeline_res)
    elif page == "Packet Tracer Verification":
        render_packet_tracer(pipeline_res)


if __name__ == "__main__":
    main()
