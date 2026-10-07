"""Command-line interface.

Examples:
    ai-rmf samples/lakeview_bank
    ai-rmf assessment_folder --format html md csv --out reports --fail-on high
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .engine import SEVERITY_ORDER, DataError, assess, load_assessment
from .reporting import LABELS, WRITERS


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ai-rmf", description="Audit AI risk management against the NIST AI RMF.")
    p.add_argument("folder", help="Assessment folder with assessment.json and ai_systems.csv")
    p.add_argument("--format", nargs="+", choices=sorted(WRITERS), default=["html", "csv"])
    p.add_argument("--out", default="reports", help="Output directory (default: reports)")
    p.add_argument("--fail-on", choices=list(SEVERITY_ORDER),
                   help="Exit with code 2 if any gap is at or above this severity")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        r = assess(load_assessment(args.folder))
    except (OSError, DataError, ValueError) as exc:
        print(f"Could not read input: {exc}", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(args.folder).resolve().name + "_ai_rmf"
    for fmt in args.format:
        path = out / f"{stem}.{fmt}"
        path.write_text(WRITERS[fmt](r), encoding="utf-8")
        print(f"Wrote {path}")
    k = r.counts()
    print(f"\n{r.organization} | assessed {r.assessment_date}")
    print(f"Overall maturity: {k['overall']:.0f}/100 ({k['level']}) | AI systems: {k['systems']} "
          f"(high risk: {k['tiers']['High']}) | gaps: {k['gaps']} "
          f"(critical {k['severity']['critical']}, high {k['severity']['high']})")
    for f in r.functions:
        print(f"  {LABELS[f.function]:<8} {f.score:>5.0f}  {f.level}")
    for s in r.systems:
        print(f"  {s.system.tier:<6} {s.system.system:<32} {len(s.gaps):>2} gap(s)")
    if args.fail_on and any(SEVERITY_ORDER[g.severity] <= SEVERITY_ORDER[args.fail_on] for g in r.gaps):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
