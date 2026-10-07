import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_rmf import assess, load_assessment, parse_assessment  # noqa: E402
from ai_rmf.cli import main  # noqa: E402
from ai_rmf.engine import DataError, maturity  # noqa: E402
from ai_rmf.reporting import WRITERS, radar_svg  # noqa: E402

S = ROOT / "samples"
HEAD = ("system,owner,vendor,use_case,decision_impact,data_sensitivity,generative,customer_facing,human_review,"
        "impact_assessment_date,bias_tested,monitoring,vendor_reviewed,incident_process,documented,user_disclosure,"
        "data_use_restricted\n")
GOOD = "Router,Ops,internal,Plans routes,none,internal,false,false,true,,false,false,false,false,true,false,false\n"
SETTINGS = {"organization": "T", "assessment_date": "2026-09-30", "answers": {}}


def run(rows: str, settings: dict | None = None):
    return assess(parse_assessment(settings or SETTINGS, HEAD + rows))


def checks(r, system=None):
    s = r.systems[0] if system is None else next(x for x in r.systems if x.system.system == system)
    return [g.check for g in s.gaps]


class TestParsing(unittest.TestCase):
    def test_rejects_bad_input(self):
        with self.assertRaisesRegex(DataError, "missing required column"):
            parse_assessment(SETTINGS, "system,owner\nA,B\n")
        with self.assertRaisesRegex(DataError, "decision_impact"):
            run(GOOD.replace(",none,", ",sometimes,", 1))
        with self.assertRaisesRegex(DataError, "true or false"):
            run(GOOD.replace("internal,false,", "internal,maybe,"))
        with self.assertRaisesRegex(DataError, "listed twice"):
            run(GOOD + GOOD)
        with self.assertRaisesRegex(DataError, "unknown practice"):
            run(GOOD, dict(SETTINGS, answers={"X-99": "yes"}))
        with self.assertRaisesRegex(DataError, "yes, partial, or no"):
            run(GOOD, dict(SETTINGS, answers={"G-01": "mostly"}))
        with self.assertRaisesRegex(DataError, "2026-03-31"):
            run(GOOD.replace("true,,false", "true,03/01/2026,false"))

    def test_maturity_levels(self):
        self.assertEqual([maturity(v) for v in (0, 24.9, 25, 50, 74.9, 75, 100)],
                         ["Initial", "Initial", "Developing", "Defined", "Defined", "Managed", "Managed"])


class TestTiersAndChecks(unittest.TestCase):
    def test_low_risk_internal_system_is_clean(self):
        r = run(GOOD)
        self.assertEqual(r.systems[0].system.tier, "Low")
        self.assertEqual(checks(r), [])
        self.assertEqual(r.systems[0].applied, ["SYS-01", "SYS-11"])

    def test_consequential_decisions_without_review(self):
        row = "Screener,,TalentCo,Ranks applicants,consequential,personal,false,false,false,,false,false,false,false,false,false,false\n"
        r = run(row)
        self.assertEqual(r.systems[0].system.tier, "High")
        self.assertEqual(r.gaps[0].check, "SYS-03")
        self.assertEqual(r.gaps[0].severity, "critical")
        self.assertTrue({"SYS-01", "SYS-02", "SYS-04", "SYS-05", "SYS-06", "SYS-10", "SYS-11"} <= set(checks(r)))

    def test_advisory_without_review_is_high_not_critical(self):
        row = "Scorer,Risk,internal,Flags,advisory,internal,false,false,false,2026-01-01,false,true,false,true,true,false,false\n"
        r = run(row)
        self.assertEqual(r.systems[0].system.tier, "Medium")
        self.assertEqual([(g.check, g.severity) for g in r.gaps], [("SYS-03", "high")])

    def test_generative_vendor_chatbot(self):
        row = "Bot,CX,ChatCo,Answers customers,none,personal,true,true,false,2026-05-01,false,true,true,true,true,false,false\n"
        self.assertEqual(sorted(checks(run(row))), ["SYS-07", "SYS-08", "SYS-09"])
        fixed = row.replace("true,true,false,2026", "true,true,true,2026").replace("true,false,false\n", "true,true,true\n")
        self.assertEqual(checks(run(fixed)), [])

    def test_stale_impact_assessment(self):
        row = "Bot,CX,internal,Answers,none,personal,false,false,true,2024-06-01,false,true,false,true,true,false,false\n"
        r = run(row)
        self.assertEqual(checks(r), ["SYS-02"])
        self.assertIn("days old", r.gaps[0].detail)

    def test_function_scores_blend_practices_and_systems(self):
        answers = {"G-01": "yes", "G-02": "partial"}
        r = run(GOOD, dict(SETTINGS, answers=answers))
        gov = r.functions[0]
        self.assertEqual(gov.practice_score, 20.0)  # (1*1 + 0.5*2) / 10 weight
        self.assertEqual(gov.system_score, 100.0)
        self.assertEqual(gov.score, 60.0)
        self.assertIsNone(r.functions[2].system_score)  # no Measure checks apply


class TestSamplesAndOutput(unittest.TestCase):
    def test_samples(self):
        weak = assess(load_assessment(S / "lakeview_bank"))
        strong = assess(load_assessment(S / "northgate_logistics"))
        self.assertLess(weak.overall, 50)
        self.assertGreaterEqual(weak.counts()["severity"]["critical"], 1)
        self.assertGreaterEqual(strong.overall, 75)
        self.assertEqual(strong.counts()["severity"]["high"], 0)
        assess(load_assessment(S / "template"))

    def test_writers_and_escaping(self):
        r = run(GOOD.replace("Router", "<script>x</script>"), dict(SETTINGS, organization="<script>x</script>"))
        for fmt, w in WRITERS.items():
            self.assertTrue(w(r).strip(), fmt)
        self.assertNotIn("<script>x</script>", WRITERS["html"](r))
        json.loads(WRITERS["json"](r))
        self.assertTrue(radar_svg(r).startswith("<svg"))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(main([str(S / "lakeview_bank"), "--out", tmp, "--fail-on", "high"]), 2)
            self.assertEqual(main([str(S / "northgate_logistics"), "--out", tmp, "--fail-on", "high"]), 0)
            self.assertEqual(main([str(S / "northgate_logistics"), "--out", tmp, "--fail-on", "low"]), 2)
            self.assertEqual(main([str(Path(tmp) / "missing"), "--out", tmp]), 1)


if __name__ == "__main__":
    unittest.main()
