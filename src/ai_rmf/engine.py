"""Audit an organization's AI risk management against the NIST AI RMF.

Two inputs make up an assessment:

* ``assessment.json``: the organization, the assessment date, and answers to 18 program-level practices
  (yes, partial, or no), grouped under the four AI RMF functions: Govern, Map, Measure, and Manage.
* ``ai_systems.csv``: an inventory of the AI systems in use, whether built in-house or bought from a vendor,
  with a few facts about how each one is used and controlled.

The engine assigns each system a risk tier, runs 11 system-level checks, and scores each function from 0 to 100
by blending the practice answers with how well the inventory meets that function's checks.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__

DATA = Path(__file__).parent / "data"
FUNCTIONS = ["GOVERN", "MAP", "MEASURE", "MANAGE"]
ANSWERS = {"yes": 1.0, "partial": 0.5, "no": 0.0, "": 0.0}
LEVELS = [(75, "Managed"), (50, "Defined"), (25, "Developing"), (0, "Initial")]
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
TIERS = ["High", "Medium", "Low"]
IMPACT = {"none", "advisory", "consequential"}
SENSITIVITY = {"none", "internal", "personal", "sensitive"}
BOOLS = ["generative", "customer_facing", "human_review", "bias_tested", "monitoring", "vendor_reviewed",
         "incident_process", "documented", "user_disclosure", "data_use_restricted"]
REQUIRED = ["system", "vendor", "decision_impact", "data_sensitivity"]
TRUE, FALSE = {"true", "yes", "y", "1"}, {"false", "no", "n", "0", ""}
REASSESS_DAYS = 365


class DataError(ValueError):
    """Raised when an input file cannot be read."""


def _json(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_program() -> dict:
    return _json("program.json")


def load_checks() -> list[dict]:
    return _json("checks.json")["checks"]


def _date(value: str, where: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError as exc:
        raise DataError(f"{where}: dates must look like 2026-03-31, got '{value}'.") from exc


def _bool(value: str, where: str) -> bool:
    v = (value or "").strip().lower()
    if v in TRUE:
        return True
    if v in FALSE:
        return False
    raise DataError(f"{where}: expected true or false, got '{value}'.")


@dataclass
class AISystem:
    system: str
    owner: str
    vendor: str
    use_case: str
    decision_impact: str
    data_sensitivity: str
    impact_assessment_date: date | None
    generative: bool = False
    customer_facing: bool = False
    human_review: bool = False
    bias_tested: bool = False
    monitoring: bool = False
    vendor_reviewed: bool = False
    incident_process: bool = False
    documented: bool = False
    user_disclosure: bool = False
    data_use_restricted: bool = False

    @property
    def is_vendor(self) -> bool:
        return self.vendor.strip().lower() not in {"", "internal", "in-house", "in house"}

    @property
    def personal_data(self) -> bool:
        return self.data_sensitivity in {"personal", "sensitive"}

    @property
    def tier(self) -> str:
        if self.decision_impact == "consequential" or (self.data_sensitivity == "sensitive" and self.customer_facing):
            return "High"
        if self.personal_data or self.customer_facing or self.decision_impact == "advisory":
            return "Medium"
        return "Low"


@dataclass
class Assessment:
    organization: str
    assessment_date: date
    answers: dict[str, str]
    systems: list[AISystem]


def parse_systems(text: str) -> list[AISystem]:
    reader = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    cols = [(c or "").strip().lower() for c in (reader.fieldnames or [])]
    missing = [c for c in REQUIRED if c not in cols]
    if missing:
        raise DataError(f"ai_systems.csv is missing required column(s): {', '.join(missing)}.")
    systems, seen = [], set()
    for n, raw in enumerate(reader, start=2):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
        if not any(r.values()):
            continue
        where = f"ai_systems.csv line {n}"
        if not r["system"]:
            raise DataError(f"{where}: every row needs a system name.")
        if r["system"].lower() in seen:
            raise DataError(f"{where}: system '{r['system']}' is listed twice.")
        seen.add(r["system"].lower())
        impact, sens = r["decision_impact"].lower(), r["data_sensitivity"].lower()
        if impact not in IMPACT:
            raise DataError(f"{where}: decision_impact must be none, advisory, or consequential, got '{impact}'.")
        if sens not in SENSITIVITY:
            raise DataError(f"{where}: data_sensitivity must be none, internal, personal, or sensitive, got '{sens}'.")
        systems.append(AISystem(
            system=r["system"], owner=r.get("owner", ""), vendor=r["vendor"] or "internal",
            use_case=r.get("use_case", ""), decision_impact=impact, data_sensitivity=sens,
            impact_assessment_date=_date(r.get("impact_assessment_date", ""), where),
            **{b: _bool(r.get(b, ""), f"{where} ({b})") for b in BOOLS}))
    return systems


def parse_assessment(settings: dict, systems_text: str) -> Assessment:
    if not isinstance(settings, dict):
        raise DataError("assessment.json must be a JSON object.")
    known = {p["id"] for p in load_program()["practices"]}
    answers = {}
    for pid, value in (settings.get("answers") or {}).items():
        if pid not in known:
            raise DataError(f"assessment.json: unknown practice '{pid}'.")
        v = str(value or "").strip().lower()
        if v not in ANSWERS:
            raise DataError(f"assessment.json: practice {pid} must be yes, partial, or no, got '{value}'.")
        answers[pid] = v
    when = _date(str(settings.get("assessment_date", "")), "assessment.json assessment_date") or date.today()
    return Assessment(organization=str(settings.get("organization") or "Unnamed organization"),
                      assessment_date=when, answers=answers, systems=parse_systems(systems_text))


def load_assessment(folder: str | Path) -> Assessment:
    folder = Path(folder)
    try:
        settings = json.loads((folder / "assessment.json").read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise DataError(f"assessment.json is not valid JSON: {exc}") from exc
    return parse_assessment(settings, (folder / "ai_systems.csv").read_text(encoding="utf-8-sig"))


# ---------------------------------------------------------------- checks

def _applies_and_fails(cid: str, s: AISystem, on: date) -> tuple[bool, bool, str]:
    """Return (applies, fails, detail) for one check against one system."""
    risky = s.tier in {"High", "Medium"}
    if cid == "SYS-01":
        return True, not s.owner, "No named owner is accountable for this system."
    if cid == "SYS-02":
        d = s.impact_assessment_date
        if d is None:
            return risky, True, f"{s.tier}-risk system with no impact assessment on file."
        age = (on - d).days
        return risky, age > REASSESS_DAYS, f"Impact assessment is {age} days old (last {d.isoformat()})."
    if cid == "SYS-03":
        return s.decision_impact != "none", not s.human_review, \
            f"Makes {s.decision_impact} decisions about people with no human review before they take effect."
    if cid == "SYS-04":
        return s.decision_impact != "none" and s.personal_data, not s.bias_tested, \
            "Uses personal data to inform decisions but has not been tested for harmful bias."
    if cid == "SYS-05":
        return risky, not s.monitoring, "Not monitored in production for errors, drift, or misuse."
    if cid == "SYS-06":
        return s.is_vendor, not s.vendor_reviewed, f"Supplied by {s.vendor}; no AI risk review of the vendor."
    if cid == "SYS-07":
        return s.is_vendor and s.generative and s.personal_data, not s.data_use_restricted, \
            f"{s.vendor} terms do not stop it from using your {s.data_sensitivity} data to train its models."
    if cid == "SYS-08":
        return s.customer_facing, not s.user_disclosure, "Customers are not told they are interacting with AI."
    if cid == "SYS-09":
        return s.generative and s.customer_facing, not s.human_review, \
            "Generated content reaches customers without human review."
    if cid == "SYS-10":
        return risky, not s.incident_process, "No process for reporting and handling incidents involving this system."
    if cid == "SYS-11":
        return True, not s.documented, "Intended purpose, known limits, and out-of-scope uses are not documented."
    raise KeyError(cid)


@dataclass
class Gap:
    check: str
    title: str
    function: str
    severity: str
    system: str
    tier: str
    detail: str
    remediation: str
    rmf: list[str]
    genai: list[str]


@dataclass
class SystemResult:
    system: AISystem
    gaps: list[Gap]
    applied: list[str]

    @property
    def applicable(self) -> int:
        return len(self.applied)

    @property
    def passed(self) -> int:
        return self.applicable - len(self.gaps)

    @property
    def worst(self) -> str:
        return min((g.severity for g in self.gaps), key=SEVERITY_ORDER.get, default="none")


@dataclass
class PracticeResult:
    id: str
    function: str
    ref: str
    weight: int
    text: str
    answer: str

    @property
    def score(self) -> float:
        return ANSWERS[self.answer]


@dataclass
class FunctionScore:
    function: str
    description: str
    practice_score: float
    system_score: float | None
    score: float
    level: str
    gaps: int


@dataclass
class Result:
    organization: str
    assessment_date: str
    systems: list[SystemResult]
    practices: list[PracticeResult]
    functions: list[FunctionScore]
    tool_version: str = __version__
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))

    @property
    def gaps(self) -> list[Gap]:
        out = [g for s in self.systems for g in s.gaps]
        return sorted(out, key=lambda g: (SEVERITY_ORDER[g.severity], TIERS.index(g.tier), g.system, g.check))

    @property
    def overall(self) -> float:
        return round(sum(f.score for f in self.functions) / len(self.functions), 1)

    @property
    def level(self) -> str:
        return maturity(self.overall)

    def counts(self) -> dict[str, Any]:
        gaps = self.gaps
        return {
            "systems": len(self.systems),
            "vendor_systems": sum(s.system.is_vendor for s in self.systems),
            "generative": sum(s.system.generative for s in self.systems),
            "tiers": {t: sum(s.system.tier == t for s in self.systems) for t in TIERS},
            "gaps": len(gaps),
            "severity": {k: sum(g.severity == k for g in gaps) for k in SEVERITY_ORDER},
            "systems_with_gaps": sum(bool(s.gaps) for s in self.systems),
            "overall": self.overall,
            "level": self.level,
        }

    def to_dict(self) -> dict:
        return {
            "organization": self.organization,
            "assessment_date": self.assessment_date,
            "generated_at": self.generated_at,
            "tool_version": self.tool_version,
            "summary": self.counts(),
            "functions": [asdict(f) for f in self.functions],
            "systems": [{**{k: (v.isoformat() if isinstance(v, date) else v) for k, v in asdict(s.system).items()},
                         "risk_tier": s.system.tier, "checks_applicable": s.applicable, "checks_passed": s.passed,
                         "gaps": [asdict(g) for g in s.gaps]} for s in self.systems],
            "practices": [{**asdict(p), "score": p.score} for p in self.practices],
        }


def maturity(score: float) -> str:
    return next(name for floor, name in LEVELS if score >= floor)


def assess(a: Assessment) -> Result:
    program = load_program()
    checks = load_checks()
    on = a.assessment_date

    systems = []
    tally = {f: [0, 0] for f in FUNCTIONS}  # applicable, failed
    for s in a.systems:
        gaps, applied = [], []
        for c in checks:
            applies, fails, detail = _applies_and_fails(c["id"], s, on)
            if not applies:
                continue
            applied.append(c["id"])
            tally[c["function"]][0] += 1
            if fails:
                tally[c["function"]][1] += 1
                severity = c["severity"]
                if c["id"] == "SYS-03" and s.decision_impact == "advisory":
                    severity = "high"
                gaps.append(Gap(c["id"], c["title"], c["function"], severity, s.system, s.tier, detail,
                                c["remediation"], c["rmf"], c.get("genai", [])))
        gaps.sort(key=lambda g: (SEVERITY_ORDER[g.severity], g.check))
        systems.append(SystemResult(s, gaps, applied))
    systems.sort(key=lambda r: (TIERS.index(r.system.tier), -len(r.gaps), r.system.system.lower()))

    practices = [PracticeResult(p["id"], p["function"], p["ref"], p["weight"], p["text"], a.answers.get(p["id"], ""))
                 for p in program["practices"]]

    functions = []
    for f in FUNCTIONS:
        ps = [p for p in practices if p.function == f]
        pscore = 100 * sum(p.score * p.weight for p in ps) / sum(p.weight for p in ps)
        applicable, failed = tally[f]
        sscore = 100 * (applicable - failed) / applicable if applicable else None
        score = pscore if sscore is None else 0.5 * pscore + 0.5 * sscore
        functions.append(FunctionScore(f, program["functions"][f], round(pscore, 1),
                                       None if sscore is None else round(sscore, 1), round(score, 1),
                                       maturity(score), failed))

    return Result(a.organization, on.isoformat(), systems, practices, functions)
