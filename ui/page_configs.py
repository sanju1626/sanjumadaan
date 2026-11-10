"""
Page 7: Cisco IOS Configuration Generator & Multi-Device Zip Exporter
"""

import io
import zipfile
import html
import streamlit as st
from ui.pipeline import render_hero, execute_full_pipeline


def render_configs(pipeline_result: dict) -> None:
    scen = pipeline_result["scenario"]
    scen_id = scen.get("scenario_id", "custom_network")

    render_hero(
        f"Cisco IOS Configuration Generator — {scen.get('name')}",
        "Copy-paste ready switch, router, SVI, ACL, OSPF, eBGP, NAT, QoS, and GRE configs with automated pre-export verification.",
        badges=[("Zero Duplicate IPs", "mint"), ("Explicit Trunk VLANs", "lavender"), ("Wildcard Verified", "butter")],
    )

    c_opt1, c_opt2 = st.columns(2)
    platform = c_opt1.selectbox(
        "Target CLI Platform Dialect",
        ["pt", "ios"],
        index=0 if st.session_state.get("platform", "pt") == "pt" else 1,
        help="'pt' targets Cisco Packet Tracer compatible Gigabit naming; 'ios' targets real hardware.",
    )
    no_crypto = c_opt2.checkbox(
        "Omit IPsec Crypto Profiles on GRE Tunnels (--no-crypto for Packet Tracer)",
        value=bool(st.session_state.get("no_crypto", True)),
    )

    if platform != st.session_state.get("platform", "pt") or no_crypto != st.session_state.get("no_crypto", True):
        st.session_state["platform"] = platform
        st.session_state["no_crypto"] = no_crypto
        pipeline_result = execute_full_pipeline(
            scen,
            allow_rfc3021=st.session_state.get("allow_rfc3021", False),
            platform=platform,
            no_crypto=no_crypto,
        )

    if not pipeline_result["ok"]:
        st.error(f"[{pipeline_result.get('error_type')}] {pipeline_result['message']}")
        return

    configs = pipeline_result["configs"]
    self_check = pipeline_result["self_check"]

    if self_check["passed"]:
        st.markdown(
            f"""
            <div class="na-card na-card-mint">
                <span class="na-pill na-pill-mint">Automated Pre-Export Self-Check PASSED</span>
                <p style="margin:0.4rem 0 0 0;font-size:0.9rem;">
                    Verified <strong>{self_check['checked_ip_count']}</strong> unique IPv4 interface addresses,
                    zero subnet overlaps, exact bitwise wildcards (<code>~mask &amp; 0xFFFFFFFF</code>),
                    explicit trunk allowed VLAN lists, OSPF-to-interface matching, and complete ACL definitions.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Combined exports & ZIP archive
    combined_cfg = "\n\n".join(f"! >>> DEVICE: {d} <<<\n{cfg}" for d, cfg in configs.items())
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for dname, cfg in configs.items():
            zf.writestr(f"{scen_id}/{dname}.cfg", cfg)
        zf.writestr(f"{scen_id}_config.cfg", combined_cfg)
        zf.writestr(f"rationale_{scen_id}.md", pipeline_result["rationale_md"])
    zip_buf.seek(0)

    dl1, dl2 = st.columns(2)
    dl1.download_button(
        f"Download Combined {scen_id}_config.cfg",
        data=combined_cfg,
        file_name=f"{scen_id}_config.cfg",
        mime="text/plain",
        width="stretch",
    )
    dl2.download_button(
        "Download All Device Configs + Rationale (.zip)",
        data=zip_buf.getvalue(),
        file_name=f"netarchitect_{scen_id}_configs.zip",
        mime="application/zip",
        type="primary",
        width="stretch",
    )

    st.divider()
    dev_names = list(configs.keys())
    tabs = st.tabs(dev_names)
    for tab, dname in zip(tabs, dev_names):
        with tab:
            dev_meta = next((d for d in scen.get("devices", []) if d["name"] == dname), {})
            col_info, col_dl = st.columns([3, 1])
            col_info.markdown(
                f"**Model (`{platform.upper()}`)**: `{dev_meta.get('model_pt', 'IOS')}` | **Role**: {dev_meta.get('role', 'Device')}"
            )
            col_dl.download_button(
                f"Download {dname}.cfg",
                data=configs[dname],
                file_name=f"{dname}.cfg",
                mime="text/plain",
                key=f"dl_{scen_id}_{dname}",
                width="stretch",
            )
            st.code(configs[dname], language="text")
