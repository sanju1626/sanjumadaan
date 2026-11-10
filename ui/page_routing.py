"""
Page 6: Routing Protocols, Tier Selection, Interactive Topology Graph & N-1 Resiliency
"""

import html
import math
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st
from engine.topology import build_topology_graph
from ui.pipeline import render_hero, render_metric_card


def _medium_color(media_type: str) -> str:
    m = media_type.lower()
    if "cat6a" in m or "copper" in m:
        return "#4EB58C"
    if "om4" in m or "mmf" in m:
        return "#E8984C"
    if "dwdm" in m:
        return "#D96592"
    return "#8D6BE0"


def render_routing_topology(pipeline_result: dict) -> None:
    scen = pipeline_result["scenario"]
    routing = pipeline_result["routing"]
    topo = pipeline_result["topology"]
    tier = pipeline_result["tier"]
    media_evals = pipeline_result["media_evals"]
    media_by_link = {m.get("link_id", ""): m for m in media_evals}

    render_hero(
        "Routing Architecture, Topology Graph & Resiliency",
        "Deterministic OSPF / eBGP routing synthesis, hierarchical tier selection, propagation latency analysis (5 us/km + 50 us/hop), and single-link N-1 survivability.",
        badges=[
            (routing["primary_protocol"], "lavender"),
            (routing["exterior_protocol"] or "Internal IGP Only", "peach"),
            ("N-1 Graph Check", "mint"),
        ],
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Topology Tier", "Collapsed Core" if tier["tier_mode"] == "collapsed_core" else "Three-Tier", f"{tier['oversubscription_ratio']:.1f}:1 access ratio", tone="lavender")
    with c2:
        render_metric_card("IGP Selection", routing["primary_protocol"], f"{scen.get('site_count', 1)} site(s), {len(pipeline_result['vlsm']['allocated_subnets'])} subnets", tone="mint")
    with c3:
        render_metric_card("Baseline Max Latency", f"{topo['baseline_max_latency_ms']} ms", f"{topo['baseline_max_latency_us']} us worst pair", tone="peach")
    with c4:
        n1_val = "PASS (Full N-1)" if topo.get("is_resilient_n_minus_1") else "Partial / Leaf"
        render_metric_card("N-1 Link Resiliency", n1_val, f"{topo['link_count']} links tested", tone="butter")

    # Interactive Topology Graph
    st.markdown("### Interactive Network Topology (Links Colored by Physical Medium)")
    G = build_topology_graph(scen["devices"], scen["links"])
    pos = nx.kamada_kawai_layout(G) if len(G.nodes) >= 3 else nx.spring_layout(G, seed=42)

    fig = go.Figure()
    legend_seen = set()

    for u, v, data in G.edges(data=True):
        lid = data.get("link_id", f"{u}-{v}")
        med = media_by_link.get(lid, {})
        mtype = med.get("media_type", "Cat6a")
        color = _medium_color(mtype)
        dist_m = data.get("distance_m", 0.0)
        dist_str = f"{dist_m / 1000.0:.1f} km" if dist_m >= 1000 else f"{dist_m:.0f} m"

        x0, y0 = pos[u]
        x1, y1 = pos[v]
        show_leg = mtype not in legend_seen
        legend_seen.add(mtype)

        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode="lines",
            line=dict(width=4, color=color),
            name=mtype,
            legendgroup=mtype,
            showlegend=show_leg,
            hoverinfo="skip",
        ))

        # Edge midpoint label + hover telemetry
        fig.add_trace(go.Scatter(
            x=[(x0 + x1) / 2.0],
            y=[(y0 + y1) / 2.0],
            mode="text",
            text=[f"{dist_str}"],
            textfont=dict(size=10, color="#3B2F4A", family="DM Sans, sans-serif"),
            showlegend=False,
            hovertemplate=(
                f"<b>{lid} ({u} <-> {v})</b><br>"
                f"Medium: {mtype}<br>"
                f"Transceiver: {med.get('transceiver', 'RJ-45')}<br>"
                f"Distance: {dist_str}<br>"
                f"Link Latency: {data.get('latency_us', 0):.1f} us<extra></extra>"
            ),
        ))

    # Nodes
    node_colors = {
        "router": "#B79CED",
        "l3_switch": "#F28FB0",
        "l2_switch": "#7EC8A7",
        "cloud": "#F6B26B",
    }
    node_sizes = {
        "router": 34,
        "l3_switch": 38,
        "l2_switch": 30,
        "cloud": 36,
    }
    node_x, node_y, node_txt, node_hover, n_cols, n_szs = [], [], [], [], [], []
    for n_name, attrs in G.nodes(data=True):
        x, y = pos[n_name]
        dtype = attrs.get("type", "router")
        node_x.append(x)
        node_y.append(y)
        node_txt.append(f"<b>{n_name}</b><br>({attrs.get('model_pt', '')})")
        node_hover.append(
            f"<b>{n_name}</b><br>Model: {attrs.get('model_pt', 'IOS')}<br>"
            f"Role: {attrs.get('role', 'Node')}<br>Site: {attrs.get('site', '-')}"
        )
        n_cols.append(node_colors.get(dtype, "#B79CED"))
        n_szs.append(node_sizes.get(dtype, 32))

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_txt,
        textposition="top center",
        textfont=dict(size=11, color="#2B1F3A", family="DM Sans, sans-serif"),
        marker=dict(size=n_szs, color=n_cols, line=dict(width=2, color="#FFFFFF")),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=node_hover,
        name="Network Devices",
        showlegend=False,
    ))

    fig.update_layout(
        paper_bgcolor="#FFF9FB",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#3B2F4A", family="DM Sans, sans-serif"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5),
        margin=dict(t=45, b=20, l=20, r=20),
        height=470,
    )
    st.plotly_chart(fig, width="stretch")

    # Rationales
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(
            f"""
            <div class="na-card na-card-lavender">
                <strong>Routing Decision Rationale</strong><br/>
                <p style="margin:0.4rem 0 0 0;font-size:0.9rem;">{html.escape(routing['rationale'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_r:
        st.markdown(
            f"""
            <div class="na-card na-card-mint">
                <strong>Tier & Latency Design Objective Note</strong><br/>
                <p style="margin:0.4rem 0 0.35rem 0;font-size:0.9rem;">{html.escape(tier['rationale'])}</p>
                <p style="margin:0;font-size:0.84rem;color:#5F5170;"><em>{html.escape(topo['latency_statement'])}</em></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    t1, t2 = st.tabs(["N-1 Single-Link Failure Simulation", "All-Pairs Shortest-Path Latencies"])
    with t1:
        res_df = pd.DataFrame(topo.get("resiliency_evaluations", []))
        st.dataframe(res_df, width="stretch", hide_index=True)
    with t2:
        paths_df = pd.DataFrame([
            {
                "Device Pair": p["pair"],
                "Shortest Path": " -> ".join(p["path"]),
                "Hops": p["hops"],
                "Distance (km)": p["distance_km"],
                "Latency (us)": p["latency_us"],
                "Latency (ms)": p["latency_ms"],
            }
            for p in topo.get("path_details", [])
        ])
        st.dataframe(paths_df, width="stretch", hide_index=True)
