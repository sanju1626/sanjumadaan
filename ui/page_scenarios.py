"""
Page 2: Scenario Selection & Preset Explorer
"""

import json
import html
import pandas as pd
import streamlit as st
from ui.pipeline import (
    SCENARIO_FILES,
    load_preset_scenario,
    execute_full_pipeline,
    render_hero,
)


def render_scenarios() -> None:
    render_hero(
        "Enterprise Scenario Selection",
        "Inspect and switch among the three built-in CIC-307 architecture profiles. Every metric below is calculated dynamically by running the live engine.",
        badges=[("Campus LAN", "lavender"), ("Metro MAN", "mint"), ("Global WAN", "peach")],
    )

    cols = st.columns(3)
    for idx, (label, path) in enumerate(SCENARIO_FILES.items()):
        scen = load_preset_scenario(label)
        res = execute_full_pipeline(
            scen,
            allow_rfc3021=st.session_state.get("allow_rfc3021", False),
            platform=st.session_state.get("platform", "pt"),
            no_crypto=st.session_state.get("no_crypto", True),
        )
        with cols[idx]:
            is_active = st.session_state.get("active_preset_label") == label and not st.session_state.get("using_custom")
            tone = "lavender" if is_active else "default"
            badge = "ACTIVE SCENARIO" if is_active else f"{scen.get('site_count', 1)} Site(s)"
            if res["ok"]:
                v = res["vlsm"]
                r = res["routing"]
                t = res["topology"]
                hosts = sum(s["hosts"] for s in scen["subnets"] if not s.get("is_p2p"))
                st.markdown(
                    f"""
                    <div class="na-card na-card-{tone}">
                        <span class="na-pill na-pill-lavender">{html.escape(badge)}</span>
                        <h3 style="margin:0.4rem 0 0.35rem 0;font-size:1.15rem;">{html.escape(label)}</h3>
                        <p style="font-size:0.86rem;margin-bottom:0.65rem;">{html.escape(scen['description'])}</p>
                        <div style="font-size:0.84rem;">
                            <strong>Root CIDR:</strong> <code>{html.escape(scen['root_cidr'])}</code><br/>
                            <strong>Endpoints:</strong> {hosts:,} across {len(v['allocated_subnets'])} subnets<br/>
                            <strong>Routing:</strong> {html.escape(r['primary_protocol'])}<br/>
                            <strong>Max Latency:</strong> {t['baseline_max_latency_ms']} ms (Eff: {v['overall_efficiency_pct']}%)
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if st.button(f"Activate {label.split(' (')[0]}", key=f"btn_scen_{idx}", width="stretch", type="primary" if is_active else "secondary"):
                st.session_state["active_preset_label"] = label
                st.session_state["using_custom"] = False
                st.rerun()

    st.divider()
    active_scen = st.session_state["active_scenario"]
    st.markdown(f"### Specification Details: `{active_scen.get('name', 'Active')}`")
    t1, t2, t3, t4 = st.tabs(["Devices", "Links", "Subnet Requests", "Raw JSON Spec"])
    with t1:
        st.dataframe(pd.DataFrame(active_scen.get("devices", [])), width="stretch", hide_index=True)
    with t2:
        st.dataframe(pd.DataFrame(active_scen.get("links", [])), width="stretch", hide_index=True)
    with t3:
        st.dataframe(pd.DataFrame(active_scen.get("subnets", [])), width="stretch", hide_index=True)
    with t4:
        st.json(active_scen)
