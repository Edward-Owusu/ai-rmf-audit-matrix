"""Write AI RMF audit results as an HTML report, Markdown, CSV (one row per gap), or JSON."""

from __future__ import annotations

import csv
import io
import json
import math
from html import escape

from .engine import FUNCTIONS, Result, load_checks

DISCLAIMER = (
    "This report scores the answers and inventory supplied against the NIST AI Risk Management Framework (AI RMF 1.0) "
    "and the Generative AI Profile (NIST AI 600-1). It is a self-assessment aid, not a certification or legal opinion. "
    "The AI RMF is voluntary; laws that apply to specific AI uses, such as lending, hiring, and consumer protection "
    "rules, should be reviewed with counsel."
)
NAVY, CYAN, INK = "#0B1B33", "#0891B2", "#0B1B33"
SEV_COLORS = {"critical": ("#7F1D1D", "#FEE2E2"), "high": ("#9A3412", "#FFEDD5"),
              "medium": ("#854D0E", "#FEF9C3"), "low": ("#155E75", "#CFFAFE")}
TIER_COLORS = {"High": ("#fff", "#B91C1C"), "Medium": ("#78350F", "#FDE68A"), "Low": ("#0E4F5C", "#CCF4FB")}
LEVEL_COLORS = {"Initial": "#B91C1C", "Developing": "#C2410C", "Defined": "#0891B2", "Managed": "#047857"}
SHORT = {"SYS-01": "Accountable owner", "SYS-02": "Impact assessment", "SYS-03": "Human review of decisions",
         "SYS-04": "Bias testing", "SYS-05": "Production monitoring", "SYS-06": "Vendor AI review",
         "SYS-07": "Vendor data-use terms", "SYS-08": "AI disclosure", "SYS-09": "Review of generated output",
         "SYS-10": "Incident process", "SYS-11": "Purpose documented"}
LABELS = {"GOVERN": "Govern", "MAP": "Map", "MEASURE": "Measure", "MANAGE": "Manage"}


def radar_svg(r: Result, size: int = 380) -> str:
    """Four-axis maturity radar: Govern (top), Map (right), Measure (bottom), Manage (left)."""
    pad = 58  # room for the side labels
    c, rad = size / 2, size / 2 - 62
    angles = {f: -math.pi / 2 + i * math.pi / 2 for i, f in enumerate(FUNCTIONS)}

    def pt(f: str, v: float) -> tuple[float, float]:
        return pad + c + rad * v / 100 * math.cos(angles[f]), c + rad * v / 100 * math.sin(angles[f])

    parts = [f'<svg viewBox="0 0 {size + 2 * pad} {size}" width="{size + 2 * pad}" height="{size}" role="img" '
             f'aria-label="AI RMF maturity radar" xmlns="http://www.w3.org/2000/svg" '
             f'style="max-width:100%;height:auto;font-family:Segoe UI,Roboto,Arial,sans-serif">']
    for ring, label in [(25, "Initial"), (50, "Developing"), (75, "Defined"), (100, "Managed")]:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(f, ring) for f in FUNCTIONS))
        parts.append(f'<polygon points="{pts}" fill="{"#EAF6FA" if ring == 100 else "none"}" '
                     f'stroke="#B9D3E0" stroke-width="1" stroke-dasharray="{"0" if ring == 100 else "3 3"}"/>')
        x, y = pt("GOVERN", ring)
        parts.append(f'<text x="{x + 4:.1f}" y="{y + 11:.1f}" font-size="9" fill="#6B8199">{ring}</text>')
    for f in FUNCTIONS:
        x, y = pt(f, 100)
        parts.append(f'<line x1="{pad + c}" y1="{c}" x2="{x:.1f}" y2="{y:.1f}" stroke="#B9D3E0"/>')
    scores = {fs.function: fs.score for fs in r.functions}
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(f, max(scores[f], 2)) for f in FUNCTIONS))
    parts.append(f'<polygon points="{pts}" fill="{CYAN}" fill-opacity=".28" stroke="{CYAN}" stroke-width="2.5" '
                 f'stroke-linejoin="round"/>')
    for fs in r.functions:
        x, y = pt(fs.function, max(fs.score, 2))
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{NAVY}" stroke="#fff" stroke-width="2"/>')
        lx, ly = pt(fs.function, 100)
        dx = {"MAP": 12, "MANAGE": -12}.get(fs.function, 0)
        dy = {"GOVERN": -26, "MEASURE": 22}.get(fs.function, -4)
        anchor = {"MAP": "start", "MANAGE": "end"}.get(fs.function, "middle")
        parts.append(f'<text x="{lx + dx:.1f}" y="{ly + dy:.1f}" text-anchor="{anchor}" font-size="13" '
                     f'font-weight="700" fill="{NAVY}">{LABELS[fs.function]}</text>'
                     f'<text x="{lx + dx:.1f}" y="{ly + dy + 15:.1f}" text-anchor="{anchor}" font-size="12" '
                     f'fill="{LEVEL_COLORS[fs.level]}" font-weight="600">{fs.score:.0f} · {fs.level}</text>')
    parts.append("</svg>")
    return "".join(parts)


MATRIX_CSS = """
.mx{border-collapse:separate;border-spacing:3px;font:12px/1.3 "Segoe UI",Roboto,Arial,sans-serif}
.mx th{font-weight:600;color:#3A5068;padding:4px 6px;vertical-align:bottom}
.mx th.col{writing-mode:vertical-rl;transform:rotate(180deg);text-align:left;height:170px;white-space:nowrap}
.mx th.row{text-align:left;white-space:nowrap;padding-right:10px;color:#0B1B33}
.mx th.fn{font-size:10px;letter-spacing:.08em;color:#fff;background:#0B1B33;border-radius:4px;padding:3px 0;text-align:center}
.mx td{width:30px;height:28px;text-align:center;border-radius:5px;font-weight:700}
.mx td.na{background:#EEF2F6;color:#B4C0CC}
.mx td.ok{background:#CCF4FB;color:#0E7490}
.mx td.critical{background:#7F1D1D;color:#fff}.mx td.high{background:#DC2626;color:#fff}
.mx td.medium{background:#F59E0B;color:#3B2300}.mx td.low{background:#FDE68A;color:#5C4200}
.tier{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;font-weight:700;margin-left:6px}
"""


def matrix_html(r: Result) -> str:
    """Systems (rows) by checks (columns). Cyan: passed. Coloured by severity: gap. Grey: does not apply."""
    e = escape
    checks = sorted(load_checks(), key=lambda c: (FUNCTIONS.index(c["function"]), c["id"]))
    groups = []
    for f in FUNCTIONS:
        n = sum(c["function"] == f for c in checks)
        groups.append(f'<th class="fn" colspan="{n}">{LABELS[f].upper()}</th>')
    head = "".join(f'<th class="col" title="{e(c["id"])}: {e(c["title"])}">{e(SHORT[c["id"]])}</th>' for c in checks)
    rows = []
    for s in r.systems:
        gaps = {g.check: g for g in s.gaps}
        cells = []
        for c in checks:
            if c["id"] in gaps:
                g = gaps[c["id"]]
                cells.append(f'<td class="{g.severity}" title="{e(g.title)}: {e(g.detail)}">✕</td>')
            elif c["id"] in s.applied:
                cells.append(f'<td class="ok" title="{e(c["id"])} met">✓</td>')
            else:
                cells.append('<td class="na" title="Does not apply">·</td>')
        fg, bg = TIER_COLORS[s.system.tier]
        rows.append(f'<tr><th class="row">{e(s.system.system)}<span class="tier" style="color:{fg};background:{bg}">'
                    f'{e(s.system.tier)}</span></th>{"".join(cells)}</tr>')
    return (f'<table class="mx"><tr><th></th>{head}</tr><tr><th></th>{"".join(groups)}</tr>'
            f'{"".join(rows)}</table>')


def to_json(r: Result) -> str:
    return json.dumps(r.to_dict(), indent=2, default=str)


def to_csv(r: Result) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["system", "risk_tier", "vendor", "check", "title", "function", "severity", "detail", "remediation",
                "ai_rmf", "genai_risks"])
    for g in r.gaps:
        vendor = next(s.system.vendor for s in r.systems if s.system.system == g.system)
        w.writerow([g.system, g.tier, vendor, g.check, g.title, g.function, g.severity, g.detail, g.remediation,
                    "; ".join(g.rmf), "; ".join(g.genai)])
    return buf.getvalue()


def to_markdown(r: Result) -> str:
    k = r.counts()
    L = [f"# AI RMF audit: {r.organization}", "",
         f"Assessed {r.assessment_date} | Generated {r.generated_at} | ai_rmf {r.tool_version}", "",
         f"- Overall maturity: **{k['overall']:.0f} / 100 ({k['level']})**",
         f"- AI systems: **{k['systems']}** ({k['tiers']['High']} high, {k['tiers']['Medium']} medium, "
         f"{k['tiers']['Low']} low risk; {k['vendor_systems']} from vendors; {k['generative']} generative)",
         f"- Gaps: **{k['gaps']}** ({k['severity']['critical']} critical, {k['severity']['high']} high, "
         f"{k['severity']['medium']} medium, {k['severity']['low']} low)", "",
         "## Maturity by function", "", "| Function | Practices | Systems | Score | Level |", "|---|---|---|---|---|"]
    for f in r.functions:
        sys_score = "n/a" if f.system_score is None else f"{f.system_score:.0f}"
        L.append(f"| {LABELS[f.function]} | {f.practice_score:.0f} | {sys_score} | **{f.score:.0f}** | {f.level} |")
    L += ["", "## AI system inventory", "", "| System | Vendor | Risk tier | Checks passed | Gaps |", "|---|---|---|---|---|"]
    L += [f"| {s.system.system} | {s.system.vendor} | {s.system.tier} | {s.passed} of {s.applicable} | {len(s.gaps)} |"
          for s in r.systems]
    L += ["", "## Gaps", ""]
    for g in r.gaps:
        refs = ", ".join(g.rmf) + (f"; GAI: {', '.join(g.genai)}" if g.genai else "")
        L.append(f"- **{g.severity.upper()}** {g.system} ({g.tier}): {g.title}. {g.detail} "
                 f"Fix: {g.remediation} _({refs})_")
    if not r.gaps:
        L.append("No gaps found.")
    L += ["", "## Program practices", "", "| ID | Function | AI RMF | Practice | Answer |", "|---|---|---|---|---|"]
    L += [f"| {p.id} | {LABELS[p.function]} | {p.ref} | {p.text} | {p.answer or 'not answered'} |" for p in r.practices]
    L += ["", f"_{DISCLAIMER}_", ""]
    return "\n".join(L)


_CSS = """
*{box-sizing:border-box}
body{margin:0;background:#F4F7FB;color:#0B1B33;font:14px/1.55 "Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.band{background:#0B1B33;color:#E6F4F8;padding:28px 0 64px}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
.kick{text-transform:uppercase;letter-spacing:.16em;font-size:11px;color:#22D3EE;font-weight:700;margin:0}
h1{font-size:30px;margin:6px 0 6px;color:#fff;font-weight:700}
.sub{color:#9FB6CC;margin:0}
.card{background:#fff;border:1px solid #D6E2EC;border-radius:12px;padding:20px 22px;box-shadow:0 2px 10px rgba(11,27,51,.06)}
.hero{display:grid;grid-template-columns:minmax(320px,480px) 1fr;gap:18px;margin-top:-44px}
@media(max-width:820px){.hero{grid-template-columns:1fr}}
.overall{display:flex;align-items:baseline;gap:10px;margin:0 0 6px}
.overall b{font-size:44px;line-height:1}.overall span{font-weight:700}
.fn{border-top:1px solid #E3ECF3;padding:10px 0}
.fn:first-of-type{border-top:0}
.fn h3{margin:0;font-size:14px;display:flex;justify-content:space-between}
.fn p{margin:2px 0 6px;color:#51657C;font-size:12.5px}
.bar{height:8px;background:#E3ECF3;border-radius:6px;overflow:hidden}
.bar i{display:block;height:100%;border-radius:6px}
.fn small{color:#51657C;font-size:12px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:18px 0}
.tile{background:#fff;border:1px solid #D6E2EC;border-left:4px solid #0891B2;border-radius:8px;padding:10px 14px}
.tile b{display:block;font-size:24px}.tile span{color:#51657C;font-size:12.5px}
h2{font-size:19px;margin:30px 0 10px;color:#0B1B33;display:flex;align-items:center;gap:8px}
h2:before{content:"";width:6px;height:20px;background:#0891B2;border-radius:3px}
.scroll{overflow-x:auto}
table.t{border-collapse:collapse;width:100%;background:#fff;border:1px solid #D6E2EC;border-radius:8px;overflow:hidden}
.t th{background:#E1ECF4;text-align:left;padding:8px 10px;font-size:12.5px}
.t td{padding:8px 10px;border-top:1px solid #E3ECF3;vertical-align:top}
.chip{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11.5px;font-weight:700;white-space:nowrap}
.refs{color:#51657C;font-size:12px}
.fix{color:#0E5466;font-size:12.5px}
.legend{color:#51657C;font-size:12.5px;margin-top:8px}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-2px;margin:0 4px 0 12px}
.note{color:#51657C;font-size:12.5px;margin-top:28px}
"""


def _chip(text: str, fg: str, bg: str) -> str:
    return f'<span class="chip" style="color:{fg};background:{bg}">{escape(text)}</span>'


def to_html(r: Result) -> str:
    e = escape
    k = r.counts()
    fns = "".join(
        f'<div class="fn"><h3><span>{LABELS[f.function]}</span><span style="color:{LEVEL_COLORS[f.level]}">'
        f'{f.score:.0f} · {f.level}</span></h3><p>{e(f.description)}</p>'
        f'<div class="bar"><i style="width:{f.score:.0f}%;background:{LEVEL_COLORS[f.level]}"></i></div>'
        f'<small>Practices {f.practice_score:.0f} · Systems '
        f'{"n/a" if f.system_score is None else f"{f.system_score:.0f}"} · {f.gaps} gap(s)</small></div>'
        for f in r.functions)
    inv = "".join(
        f'<tr><td><b>{e(s.system.system)}</b><div class="refs">{e(s.system.use_case)}</div></td>'
        f'<td>{e(s.system.vendor)}</td><td>{e(s.system.owner) or _chip("No owner", *SEV_COLORS["high"])}</td>'
        f'<td>{_chip(s.system.tier, *TIER_COLORS[s.system.tier])}</td>'
        f'<td>{e(s.system.decision_impact)} · {e(s.system.data_sensitivity)} data'
        f'{" · generative" if s.system.generative else ""}{" · customer-facing" if s.system.customer_facing else ""}</td>'
        f'<td>{s.passed} of {s.applicable}</td></tr>' for s in r.systems)
    gaps = "".join(
        f'<tr><td>{_chip(g.severity.title(), *SEV_COLORS[g.severity])}</td><td><b>{e(g.system)}</b><br>'
        f'{_chip(g.tier, *TIER_COLORS[g.tier])}</td><td><b>{e(g.check)} {e(g.title)}</b><br>{e(g.detail)}'
        f'<div class="fix">Fix: {e(g.remediation)}</div></td><td class="refs">{e(", ".join(g.rmf))}'
        f'{"<br>GAI: " + e(", ".join(g.genai)) if g.genai else ""}</td></tr>' for g in r.gaps)
    gaps = (f'<div class="scroll"><table class="t"><thead><tr><th>Severity</th><th>System</th><th>Gap and fix</th>'
            f'<th>AI RMF / GAI risk</th></tr></thead><tbody>{gaps}</tbody></table></div>' if gaps
            else "<p>No gaps found in the AI system inventory.</p>")
    ans = {"yes": ("#065F46", "#D1FAE5"), "partial": ("#854D0E", "#FEF9C3"), "no": ("#991B1B", "#FEE2E2"),
           "": ("#475569", "#E2E8F0")}
    prac = "".join(f'<tr><td>{e(p.id)}</td><td>{LABELS[p.function]}</td><td class="refs">{e(p.ref)}</td>'
                   f'<td>{e(p.text)}</td><td>{_chip(p.answer.title() or "Not answered", *ans[p.answer])}</td></tr>'
                   for p in r.practices)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI RMF audit: {e(r.organization)}</title><style>{_CSS}{MATRIX_CSS}</style></head><body>
<div class="band"><div class="wrap"><p class="kick">NIST AI RMF audit matrix</p><h1>{e(r.organization)}</h1>
<p class="sub">Assessed {e(r.assessment_date)} · Generated {e(r.generated_at)} · ai_rmf {e(r.tool_version)}</p></div></div>
<div class="wrap"><div class="hero"><div class="card" style="display:flex;align-items:center;justify-content:center">{radar_svg(r)}</div>
<div class="card"><p class="kick" style="color:#0891B2">Overall maturity</p><p class="overall"><b>{k['overall']:.0f}</b>
<span style="color:{LEVEL_COLORS[k['level']]}">/ 100 · {k['level']}</span></p>{fns}</div></div>
<div class="tiles"><div class="tile"><b>{k['systems']}</b><span>AI systems in inventory</span></div>
<div class="tile" style="border-left-color:#B91C1C"><b>{k['tiers']['High']}</b><span>High-risk systems</span></div>
<div class="tile"><b>{k['vendor_systems']}</b><span>Supplied by vendors</span></div>
<div class="tile"><b>{k['generative']}</b><span>Generative AI systems</span></div>
<div class="tile" style="border-left-color:#DC2626"><b>{k['gaps']}</b><span>Gaps ({k['severity']['critical']} critical, {k['severity']['high']} high)</span></div></div>
<h2>Audit matrix</h2><div class="card scroll">{matrix_html(r)}
<p class="legend"><i style="background:#CCF4FB"></i>Met<i style="background:#7F1D1D"></i>Critical gap<i style="background:#DC2626"></i>High
<i style="background:#F59E0B"></i>Medium<i style="background:#FDE68A"></i>Low<i style="background:#EEF2F6"></i>Does not apply</p></div>
<h2>AI system inventory</h2><div class="scroll"><table class="t"><thead><tr><th>System</th><th>Vendor</th><th>Owner</th>
<th>Risk tier</th><th>Use profile</th><th>Checks met</th></tr></thead><tbody>{inv}</tbody></table></div>
<h2>Gaps and remediation</h2>{gaps}
<h2>Program practices</h2><div class="scroll"><table class="t"><thead><tr><th>ID</th><th>Function</th><th>AI RMF</th>
<th>Practice</th><th>Answer</th></tr></thead><tbody>{prac}</tbody></table></div>
<p class="note">{e(DISCLAIMER)}</p></div><div style="height:40px"></div></body></html>"""


WRITERS = {"json": to_json, "csv": to_csv, "md": to_markdown, "html": to_html}
