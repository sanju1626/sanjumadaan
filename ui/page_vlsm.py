"""
Page 5: Pure Bitwise VLSM Calculator & Address-Space Block Chart
"""

import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from engine.addr import ip_to_int
from ui.pipeline import render_hero, render_metric_card


def render_vlsm(pipeline_result: dict) -> None:
    vlsm = pipeline_result["vlsm"]
    scen = pipeline_result["scenario"]
    allocs = vlsm["allocated_subnets"]

    render_hero(
        f"Bitwise VLSM Address Allocator — {vlsm['root_cidr']}",
        "Power-of-two contiguous allocation using pure integer shifts and masks (<<, >>, &, |, ~). Blocks are descending-sorted and naturally aligned (network % size == 0).",
        badges=[("Zero Overlap Verified", "mint"), ("RFC 3021 Support", "lavender"), ("RFC 4632 Summaries", "peach")],
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Root Space Capacity", f"{vlsm['root_size']:,} IPs", vlsm["root_cidr"], tone="lavender")
    with c2:
        render_metric_card("Total Allocated", f"{vlsm['total_allocated_size']:,} IPs", f"{len(allocs)} non-overlapping blocks", tone="mint")
    with c3:
        render_metric_card("Allocation Efficiency", f"{vlsm['overall_efficiency_pct']}%", f"{vlsm['total_requested_hosts']:,} hosts requested", tone="butter")
    with c4:
        render_metric_card("Remaining Free Space", f"{vlsm['remaining_addresses']:,} IPs", f"Utilization: {vlsm['overall_utilization_pct']}%", tone="peach")

    st.markdown("### Bitwise Subnet Allocation Table & Arithmetic Trace")
    df = pd.DataFrame([
        {
            "Subnet Name": s["name"],
            "VLAN": str(s["vlan"]) if s["vlan"] is not None else "P2P",
            "Group": s.get("group") or "-",
            "Req Hosts": s["requested_hosts"],
            "Size": s["size"],
            "Usable": s["usable_hosts"],
            "CIDR": s["cidr"],
            "Gateway / First": s["gateway"],
            "Last Host": s["last_host"],
            "Broadcast": s["broadcast"],
            "Subnet Mask": s["mask"],
            "Wildcard Mask": s["wildcard"],
            "Eff (%)": s["efficiency_pct"],
            "Arithmetic Step": s["arithmetic_trace"],
        }
        for s in allocs
    ])
    st.dataframe(df, width="stretch", hide_index=True)

    # Address-Space Block Visualization (Plotly Horizontal Allocation Bar)
    st.markdown("### Address-Space Block Map Inside Root Block")
    root_int = ip_to_int(vlsm["root_network"])
    palette = ["#B79CED", "#7EC8A7", "#F28FB0", "#F6B26B", "#88C9E8", "#E3C567", "#C6A4F7", "#99D8C9"]

    fig = go.Figure()
    for idx, s in enumerate(allocs):
        rel_start = s["network_int"] - root_int
        fig.add_trace(go.Bar(
            y=["IPv4 Space"],
            x=[s["size"]],
            base=[rel_start],
            orientation="h",
            name=f"{s['name']} ({s['cidr']})",
            marker_color=palette[idx % len(palette)],
            hovertemplate=(
                f"<b>{s['name']}</b><br>"
                f"CIDR: {s['cidr']}<br>"
                f"Range: {s['network']} - {s['broadcast']}<br>"
                f"Gateway: {s['gateway']}<br>"
                f"Size: {s['size']} IPs ({s['requested_hosts']} req)<extra></extra>"
            ),
        ))

    if vlsm["remaining_addresses"] > 0:
        used_end = max(s["end_int"] - root_int for s in allocs)
        fig.add_trace(go.Bar(
            y=["IPv4 Space"],
            x=[vlsm["remaining_addresses"]],
            base=[used_end],
            orientation="h",
            name="Unallocated Free Space",
            marker_color="#F0EAF8",
            marker_line=dict(color="#C8B8E8", width=1),
            hovertemplate=f"<b>Unallocated Reserve</b><br>Remaining: {vlsm['remaining_addresses']:,} IPs<extra></extra>",
        ))

    # Zoom x-axis comfortably if very sparse WAN (e.g. /16 with /23 blocks) or full root
    max_used = max((s["end_int"] - root_int) for s in allocs) if allocs else vlsm["root_size"]
    zoom_option = st.radio(
        "Address-Space Bar Zoom",
        ["Allocated Region + Buffer (Detailed)", "Full Root CIDR Capacity"],
        horizontal=True,
    )
    x_max = max(max_used * 1.15, 256) if zoom_option.startswith("Allocated") else vlsm["root_size"]

    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="#FFF9FB",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#3B2F4A", family="DM Sans, sans-serif"),
        xaxis=dict(title=f"Address Offset from {vlsm['root_network']}", range=[0, x_max]),
        yaxis=dict(showticklabels=False),
        legend=dict(orientation="h", yanchor="top", y=-0.22),
        margin=dict(t=25, b=80, l=20, r=20),
        height=240,
    )
    st.plotly_chart(fig, width="stretch")

    # Group Summaries (OSPF Area / BGP Route Aggregation)
    grp_sums = vlsm.get("group_summaries", {})
    if grp_sums:
        st.markdown("### Contiguous Group Route Summaries (RFC 4632 ABR / BGP Aggregation)")
        gs_rows = []
        for grp_name, gs in grp_sums.items():
            subnet_count = sum(1 for s in allocs if s.get("group") == grp_name)
            gs_rows.append({
                "Group / OSPF Area": grp_name,
                "Summary CIDR": gs["summary_cidr"],
                "Summary Mask": gs["summary_mask"],
                "Subnet Count": subnet_count,
                "Allocated IPs": gs["total_allocated_size"],
                "Summary Span Size": gs["summary_size"],
                "Exact Contiguous Summary": "Yes (Exact)" if gs["exact"] else "Covering (Has Slack)",
            })
        st.dataframe(pd.DataFrame(gs_rows), width="stretch", hide_index=True)
