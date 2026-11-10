"""
Page 11: About NetArchitect & CIC-307 Rubric Architecture
"""

import pandas as pd
import streamlit as st
from ui.pipeline import render_hero


def render_about() -> None:
    render_hero(
        "About NetArchitect (CIC-307 Computer Networks Mini-Project)",
        "Deterministic, pure-bitwise network planning, physics-validated media budgeting, explainable engineering rationales, and Cisco IOS / PTBuilder synthesis. Submitted by Sanju Madaan (00714803124 · Batch 5C1).",
        badges=[("Sanju Madaan · 00714803124 · 5C1", "butter"), ("Python 3.11+", "lavender"), ("Streamlit + Plotly + NetworkX", "mint"), ("Pure Bitwise VLSM", "peach")],
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="na-card na-card-lavender">
                <h3 style="margin-top:0;">Core Engineering Guarantees</h3>
                <ul>
                    <li><strong>Zero Black-Box LLMs or Paid APIs</strong>: Every media, prefix, OSPF/BGP, QoS, and ACL decision executes deterministically on your CPU.</li>
                    <li><strong>Pure Bitwise Integer VLSM</strong>: Subnet masks, wildcards (<code>~mask &amp; 0xFFFFFFFF</code>), natural block alignment, and overlap checks run using pure bitwise integer operators; Python's <code>ipaddress</code> is restricted strictly to unit test oracles.</li>
                    <li><strong>Strict Pre-Export Self-Check</strong>: Blocks invalid exports on duplicate IPs, overlapping blocks, wildcard drift, undefined ACL references, or mismatched OSPF network statements.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="na-card na-card-mint">
                <h3 style="margin-top:0;">CLI & Deployment Commands</h3>
                <p>Reproduce every export or run tests cleanly from terminal / VS Code:</p>
                <pre style="background:#FFFFFF;padding:0.75rem;border-radius:12px;border:1px solid #BEEBD7;font-size:0.82rem;">pip install -r requirements.txt
pytest -v
streamlit run app.py
python cli.py --preset campus --out exports/ --emit-ptbuilder
python cli.py --preset man    --out exports/ --emit-ptbuilder
python cli.py --preset wan    --out exports/ --no-crypto --platform pt --emit-ptbuilder</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Evaluation Rubric Traceability Matrix")
    rubric_rows = [
        {"Weight": "15 pts", "Rubric Component": "Parameter Engine + 3 Presets + Custom Validation", "NetArchitect Module": "scenarios/*.json, engine/validation.py, engine/errors.py, ui/page_custom.py"},
        {"Weight": "25 pts", "Rubric Component": "Explainable Decision Engine", "NetArchitect Module": "engine/media_engine.py, engine/routing_engine.py, engine/topology.py, engine/decision_engine.py"},
        {"Weight": "25 pts", "Rubric Component": "Bitwise VLSM (Zero Overlap) + Cisco IOS Configs", "NetArchitect Module": "engine/addr.py, engine/vlsm_engine.py, engine/config_generator.py, engine/ptbuilder_gen.py"},
        {"Weight": "15 pts", "Rubric Component": "Unit Tests (Distance, Exhaustion, Edge Wildcards)", "NetArchitect Module": "tests/test_*.py (70+ pytest cases + 300-case seeded fuzz vs ipaddress oracle)"},
        {"Weight": "20 pts", "Rubric Component": "AI Audit Log (Two Real Flaws + Packet-Flow Trace)", "NetArchitect Module": "ai_audit_log.md, audit/raw/*, git commit 8faf5ed, ui/page_audit.py"},
    ]
    st.dataframe(pd.DataFrame(rubric_rows), width="stretch", hide_index=True)
