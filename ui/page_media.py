"""
Page 4: Physical Media Calculator & Optical Budget Charts
"""

import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from engine.errors import NetArchitectError
from engine.media_engine import evaluate_media
from ui.pipeline import render_hero


def render_media(pipeline_result: dict) -> None:
    render_hero(
        "Physical Media & Optical Link Budget Engine (10 GbE)",
        "Physics-enforced media boundaries: Cat6a 10GBASE-T (<=100 m), OM4 MMF 10GBASE-SR (101–400 m), and OS2 SMF LR/ER/ZR (>400 m) with typical datasheet insertion losses.",
        badges=[("IEEE 802.3an", "lavender"), ("IEEE 802.3ae", "mint"), ("2 x 0.3 dB Connector Loss", "peach")],
    )

    st.markdown("### Interactive Single-Link Distance & Optical Budget Calculator")
    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        dist_unit = c1.radio("Unit", ["Metres (m)", "Kilometres (km)"], horizontal=True)
        raw_dist = c2.number_input(
            "Link Distance",
            min_value=0.0,
            max_value=5000000.0,
            value=15.0 if dist_unit.startswith("K") else 180.0,
            step=1.0,
        )
        distance_m = raw_dist * 1000.0 if dist_unit.startswith("K") else raw_dist
        forced = c3.selectbox("Forced Medium Constraint", ["Auto-Select", "copper", "mmf", "smf"])
        splice_db = c4.number_input("Extra Fusion Splice Loss (dB)", min_value=0.0, max_value=20.0, value=0.0, step=0.1)
        is_end = st.checkbox("Endpoint / PoE Access Point Horizontal Run (Copper-Only IEEE 802.3an Rule)", value=False)

        try:
            calc = evaluate_media(
                distance_m=distance_m,
                forced_media=None if forced == "Auto-Select" else forced,
                is_endpoint=is_end,
                splice_loss_db=splice_db,
                link_name="Interactive-Test-Link",
            )
            loss_txt = (
                f"<strong>Loss:</strong> {calc['loss_db']} dB | "
                f"<strong>Budget:</strong> {calc['budget_db']} dB | "
                f"<strong>Margin:</strong> {calc['margin_db']} dB (typical datasheet values)"
                if calc.get("loss_db") is not None
                else "Non-optical / Carrier DWDM range (standard optical transceiver budget N/A)"
            )
            st.markdown(
                f"""
                <div class="na-card na-card-mint">
                    <span class="na-pill na-pill-mint">{html.escape(calc['media_type'])}</span>
                    <span class="na-pill na-pill-lavender">{html.escape(calc.get('transceiver', 'RJ-45'))}</span>
                    <span class="na-pill na-pill-butter">{html.escape(calc.get('standard', 'IEEE'))}</span>
                    <p style="margin:0.45rem 0 0.25rem 0;">{html.escape(calc['rationale'])}</p>
                    <p style="margin:0;font-size:0.86rem;">{loss_txt}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except NetArchitectError as exc:
            st.markdown(
                f"""
                <div class="na-card na-card-blush">
                    <span class="na-pill na-pill-blush">{html.escape(type(exc).__name__)}</span>
                    <p style="margin:0.45rem 0 0 0;">{html.escape(str(exc))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown(f"### Active Scenario Links: `{pipeline_result['scenario'].get('name')}`")

    media_evals = pipeline_result["media_evals"]
    df = pd.DataFrame([
        {
            "Link": m.get("link_id", m.get("link_name")),
            "Distance (m)": m["distance_m"],
            "Distance (km)": round(m["distance_km"], 3),
            "Media Selected": m["media_type"],
            "Transceiver": m.get("transceiver", "RJ-45"),
            "Loss (dB)": m["loss_db"] if m.get("loss_db") is not None else None,
            "Budget (dB)": m["budget_db"] if m.get("budget_db") is not None else None,
            "Margin (dB)": m["margin_db"] if m.get("margin_db") is not None else None,
            "Engineering Rationale": m["rationale"],
        }
        for m in media_evals
    ])
    st.dataframe(df, width="stretch", hide_index=True)

    optical_links = [m for m in media_evals if m.get("loss_db") is not None and m.get("budget_db") is not None]
    if optical_links:
        st.markdown("### Optical Power Budget vs. Calculated Span Loss (Typical Datasheet Values)")
        fig = go.Figure()
        names = [f"{m.get('link_id', m.get('link_name'))} ({m['distance_km']:.1f} km)" for m in optical_links]
        fig.add_trace(go.Bar(
            name="Calculated Total Loss (dB)",
            x=names,
            y=[m["loss_db"] for m in optical_links],
            marker_color="#F28FB0",
            text=[f"{m['loss_db']} dB" for m in optical_links],
            textposition="auto",
        ))
        fig.add_trace(go.Bar(
            name="Remaining Power Margin (dB)",
            x=names,
            y=[m["margin_db"] for m in optical_links],
            marker_color="#7EC8A7",
            text=[f"{m['margin_db']} dB" for m in optical_links],
            textposition="auto",
        ))
        fig.add_trace(go.Scatter(
            name="Transceiver Optical Budget Ceiling (dB)",
            x=names,
            y=[m["budget_db"] for m in optical_links],
            mode="lines+markers+text",
            line=dict(color="#6C4FA8", width=3, dash="dot"),
            text=[f"{m['budget_db']} dB" for m in optical_links],
            textposition="top center",
        ))
        fig.update_layout(
            barmode="stack",
            paper_bgcolor="#FFF9FB",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#3B2F4A", family="DM Sans, sans-serif"),
            yaxis_title="Attenuation / Power Budget (dB)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=50, b=30, l=40, r=20),
            height=380,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Active scenario links are either short-reach Copper/MMF (<=400 m) or >80 km Carrier DWDM spans without direct unamplified LR/ER/ZR optical budgets.")
