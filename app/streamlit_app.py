"""Interactive dashboard for the AI RMF Audit Matrix.

Run locally:   streamlit run app/streamlit_app.py

Layout: no sidebar. Data is chosen in the top row, and the audit matrix (AI systems by checks) is the main
screen, with a drill-down into any one system underneath it.
"""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ui  # noqa: E402
from ai_rmf import __version__, assess, load_assessment, parse_assessment  # noqa: E402
from ai_rmf.engine import DataError, load_program  # noqa: E402
from ai_rmf.reporting import (DISCLAIMER, LABELS, LEVEL_COLORS, MATRIX_CSS, matrix_html, radar_svg,  # noqa: E402
                              to_csv, to_html, to_json, to_markdown)

S = ROOT / "samples"
SAMPLES = {
    "Community bank with AI gaps (fictional)": "lakeview_bank",
    "Logistics company with a mature program (fictional)": "northgate_logistics",
}
TIER_COLOR = {"High": "#B91C1C", "Medium": "#C2410C", "Low": "#0891B2"}
ANSWER = {"yes": "Yes", "partial": "Partial", "no": "No"}

PAL = ui.Palette(accent="#0891B2", band="#0B1B33", band_text="#FFFFFF", band_sub="#9FB6CC",
                 card="#FFFFFF", line="#D6E2EC", ink="#0B1B33", muted="#51657C")
ui.setup("Is your AI under control?", "NIST AI RMF audit matrix · AI 600-1 Generative AI Profile",
         "Score AI risk management across Govern, Map, Measure and Manage, tier every AI system in use "
         "(including AI inside vendor products), and map each gap to the NIST AI RMF and the Generative AI Profile.",
         "🧭", PAL)

# ---- Top row: data -----------------------------------------------------------------------------------
t1, t2, t3 = st.columns([1.5, 2.6, 1.3], vertical_alignment="top")
with t1:
    st.caption("Data")
    source = ui.choose("Data", ["Use a sample", "Upload my own"], key="source", format_func=ui.source_label)
assessment = None
try:
    if source == "Use a sample":
        with t2:
            st.caption("Sample organization")
            assessment = load_assessment(S / SAMPLES[st.selectbox("Sample organization", list(SAMPLES),
                                                                  label_visibility="collapsed")])
    else:
        with t2:
            st.caption("AI system inventory (ai_systems.csv)")
            csv_up = st.file_uploader("AI system inventory (ai_systems.csv)", type=["csv"],
                                      label_visibility="collapsed")
        with t3:
            with st.popover("Program practices", use_container_width=True):
                json_up = st.file_uploader("Practice answers (assessment.json, optional)", type=["json"])
                st.download_button("Blank inventory template", (S / "template" / "ai_systems.csv").read_bytes(),
                                   "ai_systems.csv", "text/csv")
                settings = json.loads(json_up.getvalue().decode("utf-8-sig")) if json_up else {}
                if not json_up:
                    settings["organization"] = st.text_input("Organization", "My organization")
                    st.caption("Or answer the 18 program practices here:")
                    settings["answers"] = {
                        p["id"]: st.selectbox(f"{p['id']} · {p['text']}", ["no", "partial", "yes"], key=p["id"])
                        for p in load_program()["practices"]}
        if csv_up:
            assessment = parse_assessment(settings, csv_up.getvalue().decode("utf-8-sig", errors="replace"))
except (DataError, json.JSONDecodeError) as exc:
    st.error(f"The files could not be read. {exc}")

if assessment is None:
    st.info("Upload an AI system inventory above, or switch to a sample, to see the matrix. Program practice "
            "answers and a blank template are under Program practices.")
    ui.footer("ai_rmf", __version__, "ai-rmf-audit-matrix", DISCLAIMER)
    st.stop()

r = assess(assessment)
k = r.counts()

# ---- Function strip ----------------------------------------------------------------------------------
st.markdown(f"<div class='g-sec'>{escape(r.organization)}</div>", unsafe_allow_html=True)
st.caption(f"Assessed {r.assessment_date} · {k['systems']} AI systems · {k['tiers']['High']} high risk · "
           f"{k['gaps']} gaps ({k['severity']['critical']} critical, {k['severity']['high']} high)")
cols = st.columns(5)
cols[0].markdown(f"<div class='g-tile' style='border-top-color:{LEVEL_COLORS[k['level']]}'><b>{k['overall']:.0f}"
                 f"</b><span>Overall maturity · {escape(k['level'])}</span>"
                 f"{ui.bar(k['overall'], LEVEL_COLORS[k['level']])}</div>", unsafe_allow_html=True)
for col, f in zip(cols[1:], r.functions):
    c = LEVEL_COLORS[f.level]
    col.markdown(f"<div class='g-tile' style='border-top-color:{c}'><b>{f.score:.0f}</b>"
                 f"<span>{LABELS[f.function]} · {escape(f.level)} · {f.gaps} gap(s)</span>{ui.bar(f.score, c)}</div>",
                 unsafe_allow_html=True)

VIEWS = ["Audit matrix", "Maturity radar", "AI system inventory", "Program practices"]
view = ui.choose("View", VIEWS, key="view")

if view == "Audit matrix":
    ui.section("Audit matrix", "Each row is an AI system and each column a check. Cyan ✓ means met; a coloured ✕ "
               "marks a gap by severity (dark red critical, red high, amber medium, yellow low); grey means the "
               "check does not apply. Hover over a cell for the detail.")
    st.markdown(f"<style>{MATRIX_CSS}</style><div style='overflow-x:auto;background:#fff;border:1px solid #D6E2EC;"
                f"border-radius:12px;padding:14px'>{matrix_html(r)}</div>", unsafe_allow_html=True)

    ui.section("Drill into one system")
    order = sorted(r.systems, key=lambda s: (["High", "Medium", "Low"].index(s.system.tier), -len(s.gaps)))
    names = [s.system.system for s in order]
    pick = st.selectbox("AI system", names, label_visibility="collapsed",
                        format_func=lambda n: next(f"{n} · {s.system.tier} risk · {len(s.gaps)} gap(s)"
                                                   for s in order if s.system.system == n))
    s = next(x for x in order if x.system.system == pick)
    sysd = s.system
    a, b = st.columns([1, 2])
    with a:
        ui.card(f"<div class='h'>{ui.pill(sysd.tier + ' risk', TIER_COLOR[sysd.tier])}{escape(sysd.system)}</div>",
                f"<div class='s'>Vendor: {escape(sysd.vendor or 'built in-house')}</div>"
                f"<div class='s'>Owner: {escape(sysd.owner or 'none named')}</div>"
                f"<div class='d'>{escape(sysd.use_case)}</div>"
                f"<div class='s'>Decisions: {escape(sysd.decision_impact)} · Data: {escape(sysd.data_sensitivity)}"
                f"<br>Generative: {'yes' if sysd.generative else 'no'} · Customer-facing: "
                f"{'yes' if sysd.customer_facing else 'no'}</div>"
                f"{ui.bar(100 * s.passed / s.applicable if s.applicable else None, PAL.accent)}"
                f"<div class='s'>{s.passed} of {s.applicable} checks met</div>", accent=TIER_COLOR[sysd.tier])
    with b:
        if not s.gaps:
            st.success("No gaps for this system.")
        for g in s.gaps:
            refs = ", ".join(g.rmf) + (f" · GAI risk: {', '.join(g.genai)}" if g.genai else "")
            ui.card(f"<div class='h'>{ui.sev_pill(g.severity)}{escape(g.title)} "
                    f"<span class='s'>({escape(g.check)})</span></div>",
                    f"<div class='d'>{escape(g.detail)}</div><div class='f'><b>Fix:</b> {escape(g.remediation)}</div>"
                    f"<div class='s'>AI RMF {escape(refs)}</div>", accent=ui.SEV_COLORS[g.severity])

elif view == "Maturity radar":
    left, right = st.columns([5, 6])
    with left:
        st.markdown(f"<div style='background:#fff;border:1px solid #D6E2EC;border-radius:12px;padding:8px;"
                    f"text-align:center'>{radar_svg(r)}</div>", unsafe_allow_html=True)
    with right:
        for f in r.functions:
            c = LEVEL_COLORS[f.level]
            sys_s = "n/a" if f.system_score is None else f"{f.system_score:.0f}"
            ui.card(f"<div class='h'>{LABELS[f.function]} <span style='float:right;color:{c}'>{f.score:.0f} · "
                    f"{escape(f.level)}</span></div>",
                    f"{ui.bar(f.score, c)}<div class='s'>Practices {f.practice_score:.0f} · Systems {sys_s} · "
                    f"{f.gaps} gap(s)</div><div class='d'>{escape(f.description)}</div>", accent=c)

elif view == "AI system inventory":
    ui.section("AI system inventory", "Risk tier: High if the system makes consequential decisions about people, "
               "or handles sensitive data and faces customers. Medium if it handles personal data, faces customers, "
               "or advises on decisions. Otherwise Low.")
    st.dataframe(pd.DataFrame([{
        "System": s.system.system, "Risk tier": s.system.tier, "Vendor": s.system.vendor,
        "Owner": s.system.owner or "none", "Use case": s.system.use_case,
        "Decisions": s.system.decision_impact, "Data": s.system.data_sensitivity,
        "Generative": "yes" if s.system.generative else "no",
        "Customer-facing": "yes" if s.system.customer_facing else "no",
        "Checks met": f"{s.passed} of {s.applicable}", "Gaps": len(s.gaps)} for s in r.systems]),
        hide_index=True, use_container_width=True)

else:
    for f in r.functions:
        ui.section(LABELS[f.function], f.description)
        st.dataframe(pd.DataFrame([{"ID": p.id, "AI RMF": p.ref, "Practice": p.text, "Weight": p.weight,
                                    "Answer": ANSWER.get(p.answer, "Not answered")}
                                   for p in r.practices if p.function == f.function]),
                     hide_index=True, use_container_width=True)

ui.downloads([("HTML report", to_html(r), "ai_rmf_report.html", "text/html"),
              ("Markdown", to_markdown(r), "ai_rmf_report.md", "text/markdown"),
              ("CSV (one row per gap)", to_csv(r), "ai_rmf_gaps.csv", "text/csv"),
              ("JSON results", to_json(r), "ai_rmf_results.json", "application/json")])
ui.footer("ai_rmf", __version__, "ai-rmf-audit-matrix", DISCLAIMER)
