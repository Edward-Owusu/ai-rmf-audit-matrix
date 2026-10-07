"""Interactive dashboard for the AI RMF Audit Matrix.

Run locally:   streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_rmf import __version__, assess, load_assessment, parse_assessment  # noqa: E402
from ai_rmf.engine import DataError, load_program  # noqa: E402
from ai_rmf.reporting import (DISCLAIMER, LABELS, LEVEL_COLORS, MATRIX_CSS, matrix_html, radar_svg,  # noqa: E402
                              to_csv, to_html, to_json, to_markdown)

S = ROOT / "samples"
SAMPLES = {
    "Community bank with AI gaps (fictional)": "lakeview_bank",
    "Logistics company with a mature program (fictional)": "northgate_logistics",
}
SEV_ICON = {"critical": "🟥", "high": "🔴", "medium": "🟠", "low": "🟡"}
TIER_ICON = {"High": "🔺 High", "Medium": "🔸 Medium", "Low": "🔹 Low"}

st.set_page_config(page_title="AI RMF Audit Matrix", page_icon="🧭", layout="wide")
st.markdown("""<style>
.hero{background:#0B1B33;color:#E6F4F8;border-radius:14px;padding:18px 24px;margin-bottom:14px}
.hero p{margin:0;color:#9FB6CC}.hero .k{color:#22D3EE;text-transform:uppercase;letter-spacing:.16em;font-size:11px;font-weight:700}
.hero h2{color:#fff;margin:4px 0 4px;padding:0}
.fcard{background:#fff;border:1px solid #D6E2EC;border-radius:10px;padding:10px 14px;margin-bottom:8px}
.fcard b{font-size:15px}.fcard .bar{height:7px;background:#E3ECF3;border-radius:5px;margin:6px 0 4px;overflow:hidden}
.fcard .bar i{display:block;height:100%}.fcard small{color:#51657C}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("1. Choose data")
    source = st.radio("Data", ["Use a sample", "Upload my own"], label_visibility="collapsed")
    assessment = None
    try:
        if source == "Use a sample":
            assessment = load_assessment(S / SAMPLES[st.selectbox("Sample organization", list(SAMPLES))])
        else:
            csv_up = st.file_uploader("AI system inventory (ai_systems.csv)", type=["csv"])
            json_up = st.file_uploader("Practice answers (assessment.json, optional)", type=["json"])
            st.download_button("Download a blank inventory template",
                               (S / "template" / "ai_systems.csv").read_bytes(), "ai_systems.csv", "text/csv")
            settings = json.loads(json_up.getvalue().decode("utf-8-sig")) if json_up else {}
            if not json_up:
                settings["organization"] = st.text_input("Organization", "My organization")
                with st.expander("2. Answer the 18 program practices"):
                    settings["answers"] = {
                        p["id"]: st.selectbox(f"{p['id']} · {p['text']}", ["no", "partial", "yes"], key=p["id"])
                        for p in load_program()["practices"]}
            if csv_up:
                assessment = parse_assessment(settings, csv_up.getvalue().decode("utf-8-sig", errors="replace"))
    except (DataError, json.JSONDecodeError) as exc:
        st.error(f"The files could not be read. {exc}")
    st.caption(f"ai_rmf {__version__}. Runs entirely in this session; files are not stored.")

st.markdown("<div class='hero'><p class='k'>NIST AI RMF audit matrix</p><h2>Is your AI under control?</h2>"
            "<p>Score AI risk management across Govern, Map, Measure, and Manage, tier every AI system in use "
            "(including AI inside vendor products), and map each gap to the NIST AI RMF and the Generative AI "
            "Profile (NIST AI 600-1). Built for small and mid-sized organizations.</p></div>", unsafe_allow_html=True)

if assessment is None:
    st.info("Upload an AI system inventory in the sidebar, or switch to a sample, to see the matrix.")
    st.stop()

r = assess(assessment)
k = r.counts()
st.subheader(r.organization)
st.caption(f"Assessed {r.assessment_date}")

left, right = st.columns([5, 6])
with left:
    st.markdown(f"<div style='background:#fff;border:1px solid #D6E2EC;border-radius:12px;padding:8px;"
                f"text-align:center'>{radar_svg(r)}</div>", unsafe_allow_html=True)
with right:
    m = st.columns(3)
    m[0].metric("Overall maturity", f"{k['overall']:.0f} / 100", k["level"], delta_color="off")
    m[1].metric("AI systems", k["systems"], f"{k['tiers']['High']} high risk", delta_color="off")
    m[2].metric("Gaps", k["gaps"], f"{k['severity']['critical']} critical · {k['severity']['high']} high",
                delta_color="off")
    for f in r.functions:
        col = LEVEL_COLORS[f.level]
        sys_s = "n/a" if f.system_score is None else f"{f.system_score:.0f}"
        st.markdown(f"<div class='fcard'><b>{LABELS[f.function]}</b> <span style='float:right;color:{col};"
                    f"font-weight:700'>{f.score:.0f} · {f.level}</span><div class='bar'><i style='width:{f.score:.0f}%;"
                    f"background:{col}'></i></div><small>Practices {f.practice_score:.0f} · Systems {sys_s} · "
                    f"{f.gaps} gap(s)</small></div>", unsafe_allow_html=True)

tabs = st.tabs(["🧩 Audit matrix", "🗂️ AI system inventory", "🛠️ Gaps and remediation", "📋 Program practices"])
with tabs[0]:
    st.markdown("Each row is an AI system and each column a check. **Cyan ✓** means met; coloured **✕** marks a gap "
                "by severity (dark red critical, red high, amber medium, yellow low); grey means the check does not "
                "apply. Hover over a cell for the detail.")
    st.markdown(f"<style>{MATRIX_CSS}</style><div style='overflow-x:auto;background:#fff;border-radius:12px;"
                f"padding:14px'>{matrix_html(r)}</div>", unsafe_allow_html=True)
with tabs[1]:
    st.dataframe(pd.DataFrame([{
        "System": s.system.system, "Risk tier": TIER_ICON[s.system.tier], "Vendor": s.system.vendor,
        "Owner": s.system.owner or "⚠️ none", "Use case": s.system.use_case,
        "Decisions": s.system.decision_impact, "Data": s.system.data_sensitivity,
        "Generative": "yes" if s.system.generative else "no",
        "Customer-facing": "yes" if s.system.customer_facing else "no",
        "Checks met": f"{s.passed} of {s.applicable}", "Gaps": len(s.gaps)} for s in r.systems]), hide_index=True)
    st.caption("Risk tier: High if the system makes consequential decisions about people, or handles sensitive data "
               "and faces customers. Medium if it handles personal data, faces customers, or advises on decisions. "
               "Otherwise Low.")
with tabs[2]:
    if not r.gaps:
        st.success("No gaps found in the AI system inventory.")
    for s in r.systems:
        if not s.gaps:
            continue
        with st.expander(f"{TIER_ICON[s.system.tier]} · {s.system.system} · {len(s.gaps)} gap(s)",
                         expanded=s.system.tier == "High"):
            for g in s.gaps:
                refs = ", ".join(g.rmf) + (f" · GAI risk: {', '.join(g.genai)}" if g.genai else "")
                st.markdown(f"{SEV_ICON[g.severity]} **{g.severity.title()}: {g.title}** ({g.check})  \n{g.detail}  \n"
                            f"**Fix:** {g.remediation}  \n<small>AI RMF {refs}</small>", unsafe_allow_html=True)
with tabs[3]:
    for f in r.functions:
        st.markdown(f"**{LABELS[f.function]}**: {f.description}")
        st.dataframe(pd.DataFrame([{"ID": p.id, "AI RMF": p.ref, "Practice": p.text, "Weight": p.weight,
                                    "Answer": {"yes": "✅ Yes", "partial": "🟡 Partial", "no": "❌ No"}.get(p.answer,
                                                                                                         "➖ Not answered")}
                                   for p in r.practices if p.function == f.function]), hide_index=True)

st.markdown("### Download the report")
d = st.columns(4)
d[0].download_button("HTML report", to_html(r), "ai_rmf_report.html", "text/html")
d[1].download_button("Markdown", to_markdown(r), "ai_rmf_report.md", "text/markdown")
d[2].download_button("CSV (one row per gap)", to_csv(r), "ai_rmf_gaps.csv", "text/csv")
d[3].download_button("JSON results", to_json(r), "ai_rmf_results.json", "application/json")
st.caption(DISCLAIMER)
