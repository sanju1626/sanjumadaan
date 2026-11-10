"""
Page 10: Cisco Packet Tracer Verification Pack & PTBuilder Automation
"""

import html
import streamlit as st
from ui.pipeline import BASE_DIR, render_hero


def render_packet_tracer(pipeline_result: dict) -> None:
    scen = pipeline_result["scenario"]
    scen_id = scen.get("scenario_id", "custom_network")
    lab_guide = pipeline_result["lab_guide"]
    ptbuilder_js = pipeline_result["ptbuilder_js"]

    render_hero(
        f"Packet Tracer Verification & PTBuilder Lab — {scen.get('name')}",
        "Reproducible lab build manuals, cabling/IP verification checklists, and zero-hand-typed PTBuilder JavaScript automation generated directly from engine calculations.",
        badges=[("PTBuilder API Verified Syntax", "lavender"), ("Unverified Locally — Run in PT", "butter")],
    )

    st.markdown(
        """
        <div class="na-card na-card-butter">
            <span class="na-pill na-pill-butter">Honest Verification Policy</span>
            <p style="margin:0.4rem 0 0 0;font-size:0.9rem;">
                Configs and PTBuilder scripts have passed NetArchitect's automated self-check and unit test suite.
                <strong>They are NOT pre-verified inside Cisco Packet Tracer.</strong> Run the topology locally in Packet Tracer 8.2+
                and tick each verification step below as you capture your viva screenshots.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    dl1, dl2 = st.columns(2)
    dl1.download_button(
        f"Download ptbuilder_{scen_id}.js",
        data=ptbuilder_js,
        file_name=f"ptbuilder_{scen_id}.js",
        mime="application/javascript",
        type="primary",
        width="stretch",
    )
    dl2.download_button(
        f"Download lab_guide_{scen_id}.md",
        data=lab_guide,
        file_name=f"lab_guide_{scen_id}.md",
        mime="text/markdown",
        width="stretch",
    )

    t1, t2, t3, t4 = st.tabs([
        "PTBuilder Script (.js)",
        "Lab Guide (lab_guide.md)",
        "Interactive PT Checklist",
        "PTBuilder Setup (lab/README.md)",
    ])

    with t1:
        st.caption("Paste into Cisco Packet Tracer: Extensions -> Builder Code Editor -> Run.")
        st.code(ptbuilder_js, language="javascript")

    with t2:
        st.markdown(lab_guide)

    with t3:
        st.markdown("### Student Packet Tracer Sign-Off Checklist (Local Lab Execution)")
        checks = [
            ("c_psu", "3650-24PS AC-POWER-SUPPLY inserted in Physical View (if applicable) / all links green"),
            ("c_brief", "show ip interface brief -> All physical interfaces, subinterfaces & SVIs show UP/UP"),
            ("c_vlan", "show vlan brief -> All user/voice/server/mgmt VLANs + Parking VLAN 999 active"),
            ("c_trunk", "show interfaces trunk -> Mode ON (DTP off), Native VLAN 999, explicit allowed VLANs (never 1-4094)"),
            ("c_stp", "show spanning-tree -> Rapid-PVST active, Core Switch priority 4096 is Root Bridge"),
            ("c_ospf", "show ip route & show ip ospf neighbor -> FULL adjacencies and dynamic routes converged"),
            ("c_acl", "MUST FAIL ACL Test (Campus WiFi -> Server) blocked with ACL hit counter increment"),
            ("c_fail", "N-1 Link Shutdown Test -> Ping recovers over alternate path without manual route edits"),
        ]
        done = 0
        for key, label in checks:
            if st.checkbox(label, key=f"pt_chk_{scen_id}_{key}"):
                done += 1
        st.progress(done / len(checks), text=f"Local PT Verification Progress: {done} / {len(checks)} items verified by user")

    with t4:
        readme_path = BASE_DIR / "lab" / "README.md"
        if readme_path.exists():
            st.markdown(readme_path.read_text(encoding="utf-8"))
        else:
            st.info("See lab/README.md in repository root for PTBuilder installation steps.")
