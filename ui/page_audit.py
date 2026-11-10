"""
Page 9: AI Adversarial Audit Lab & Packet-Flow Analysis Viewer
"""

from pathlib import Path
import html
import pandas as pd
import streamlit as st
from ui.pipeline import BASE_DIR, render_hero


def render_audit_lab() -> None:
    render_hero(
        "AI Adversarial Audit Lab (Commit 8faf5ed -> Audited Engine)",
        "Side-by-side comparison of real unreviewed AI draft bugs, executed detection failures, fixed bitwise/physics/IOS logic, and Layer 1–3 packet-flow traces.",
        badges=[("Commit 8faf5ed Audited", "blush"), ("3 Deep-Dive Defect Audits", "lavender"), ("Packet-Flow Trace", "mint")],
    )

    audit_md_path = BASE_DIR / "ai_audit_log.md"
    audit_text = audit_md_path.read_text(encoding="utf-8") if audit_md_path.exists() else "ai_audit_log.md not found."

    st.download_button(
        "Download Full ai_audit_log.md",
        data=audit_text,
        file_name="ai_audit_log.md",
        mime="text/markdown",
        type="primary",
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "Flaw #1: Bitwise Sign & 40-bit Mask",
        "Flaw #2: Media & Optical Budget",
        "Flaw #3: Trunks, OSPF & Packet Flow",
        "Full ai_audit_log.md Document",
    ])

    with tab1:
        st.markdown(
            """
            <div class="na-card na-card-blush">
                <span class="na-pill na-pill-blush">Root Cause</span>
                Python integers are arbitrary-precision signed objects. In commit <code>8faf5ed:engine/vlsm_engine.py</code>,
                <code>(0xFFFFFFFF &lt;&lt; (32 - prefix))</code> overflowed 32 bits (<code>0xFFFFFFFF00</code> for <code>/24</code>),
                and <code>~mask</code> produced negative integer <code>-1099511627521</code> instead of <code>255</code> (<code>0.0.0.255</code>).
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Before (`8faf5ed` Raw Draft)**")
            raw_vlsm = (BASE_DIR / "audit" / "raw" / "raw_vlsm.py")
            st.code(raw_vlsm.read_text(encoding="utf-8") if raw_vlsm.exists() else "", language="python")
        with c2:
            st.markdown("**After (`engine/addr.py` Fixed)**")
            st.code(
                "def prefix_to_mask_int(prefix: int) -> int:\n"
                "    if prefix == 0:\n"
                "        return 0\n"
                "    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF\n\n"
                "def prefix_to_wildcard_int(prefix: int) -> int:\n"
                "    mask = prefix_to_mask_int(prefix)\n"
                "    return (~mask) & 0xFFFFFFFF",
                language="python",
            )

    with tab2:
        st.markdown(
            """
            <div class="na-card na-card-peach">
                <span class="na-pill na-pill-peach">Root Cause</span>
                Commit <code>8faf5ed:engine/media_engine.py</code> returned <code>Cat6a 10GBASE-T</code> for forced copper at
                <code>180 m</code> without raising <code>PhysicalDistanceViolationError</code>, let IEEE 754 <code>NaN</code> fall through
                to Carrier DWDM, and omitted <code>2 x 0.3 dB = 0.6 dB</code> LC connector losses.
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Before (`8faf5ed` Raw Draft)**")
            raw_med = BASE_DIR / "audit" / "raw" / "raw_media.py"
            st.code(raw_med.read_text(encoding="utf-8") if raw_med.exists() else "", language="python")
        with c2:
            st.markdown("**After (`engine/media_engine.py` Fixed)**")
            st.code(
                "if not isinstance(distance_m, (int, float)) or math.isnan(distance_m) or math.isinf(distance_m):\n"
                "    raise InvalidParameterError(...)\n"
                "if forced in ('copper', 'cat6a', '10gbase-t') and distance_m > 100.0:\n"
                "    raise PhysicalDistanceViolationError('... NEXT/ANEXT ...')\n"
                "total_loss = (distance_km * atten_rate) + 0.6 + splice_loss_db\n"
                "margin = power_budget - total_loss\n"
                "if margin < 0:\n"
                "    raise OpticalBudgetError(...)",
                language="python",
            )

    with tab3:
        st.markdown(
            """
            <div class="na-card na-card-lavender">
                <span class="na-pill na-pill-lavender">L2/L3 Control & Security Flaws</span>
                <code>8faf5ed:engine/config_generator.py</code> left switch trunks unrestricted (VLANs 1–4094, Native VLAN 1, DTP active)
                and passed subnet mask <code>255.255.254.0</code> into OSPF instead of wildcard <code>0.0.1.255</code>.
            </div>
            """,
            unsafe_allow_html=True,
        )
        flow_rows = [
            {"Step": "1. WiFi Frame (10.10.5.2 -> 10.10.9.2)", "Before Fix (8faf5ed)": "Unrestricted VLAN 1-4094 + Native VLAN 1 allows double-tag hopping.", "After Fix (Audited)": "Fa0/2 tags 802.1Q VID=12; trunk restricts allowed VLANs, Native=999, nonegotiate."},
            {"Step": "2. SVI & ACL Inspection (CORE-SW Vlan12)", "Before Fix (8faf5ed)": "No inbound ACL; frame routed directly to Vlan100 Server Farm.", "After Fix (Audited)": "ip access-group ACL_WIFI_SECURITY in hits 'deny ip any 10.10.9.0 0.0.0.63' -> DROPPED."},
            {"Step": "3. Data Client Allowed Path (10.10.2.2 -> 10.10.9.2)", "Before Fix (8faf5ed)": "OSPF network 10.10.0.0 255.255.254.0 matches wrong octets + leaks Hellos.", "After Fix (Audited)": "Vlan20 routes across CEF FIB (TTL 128->127) -> Vlan100 -> Host 10.10.9.2; passive-interface default active."},
        ]
        st.dataframe(pd.DataFrame(flow_rows), width="stretch", hide_index=True)

    with tab4:
        st.markdown(audit_text)
