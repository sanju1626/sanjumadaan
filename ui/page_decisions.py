"""
Page 8: Architectural Decision Log ("Why?" Expandable Engine Records)
"""

import html
import streamlit as st
from ui.pipeline import render_hero


def render_decisions(pipeline_result: dict) -> None:
    scen = pipeline_result["scenario"]
    scen_id = scen.get("scenario_id", "custom_network")
    records = pipeline_result["decisions"]
    rationale_md = pipeline_result["rationale_md"]

    render_hero(
        "Explainable Architectural Decision Log",
        "Every media selection, VLSM prefix, routing protocol, QoS policy, redundancy verdict, and ACL is justified dynamically from mathematical inputs and IEEE/IETF standards.",
        badges=[(f"{len(records)} Decision Records", "lavender"), ("RFC & IEEE Backed", "mint")],
    )

    col_f, col_d = st.columns([2, 1])
    search_q = col_f.text_input("Filter decisions by topic, standard, or solution keyword", placeholder="e.g. OSPF, VLSM, Cat6a, QoS, ACL...")
    col_d.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)
    col_d.download_button(
        f"Download rationale_{scen_id}.md",
        data=rationale_md,
        file_name=f"rationale_{scen_id}.md",
        mime="text/markdown",
        type="primary",
        width="stretch",
    )

    filtered = [
        r for r in records
        if not search_q
        or search_q.lower() in r["topic"].lower()
        or search_q.lower() in r["selected_solution"].lower()
        or search_q.lower() in r["reasoning"].lower()
        or search_q.lower() in r["standard_or_math_basis"].lower()
    ]

    for idx, rec in enumerate(filtered, 1):
        with st.expander(f"#{idx} Why {rec['topic']} -> {rec['selected_solution']}", expanded=(idx <= 4)):
            inputs_str = ", ".join(f"{k} = {v}" for k, v in rec.get("inputs_used", {}).items())
            warns_html = ""
            if rec.get("warnings"):
                warns_html = (
                    f"<div class='na-pill na-pill-blush' style='margin-top:0.45rem;'>"
                    f"Warning: {html.escape('; '.join(rec['warnings']))}</div>"
                )
            st.markdown(
                f"""
                <div style="font-size:0.92rem;line-height:1.5;">
                    <span class="na-pill na-pill-lavender">Standard / Math Basis</span> <em>{html.escape(rec['standard_or_math_basis'])}</em><br/>
                    <span class="na-pill na-pill-peach">Condition Triggered</span> {html.escape(rec['condition_triggered'])}<br/>
                    <span class="na-pill na-pill-butter">Inputs Used</span> <code>{html.escape(inputs_str)}</code>
                    <p style="margin:0.55rem 0 0 0;"><strong>Engineering Rationale:</strong> {html.escape(rec['reasoning'])}</p>
                    {warns_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
