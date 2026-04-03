#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.bug_predictor import predict_bug_risk
from ai.coverage_loop import improve_plan_with_coverage
from ai.rtl_parser import parse_module
from ai.sequence_generator import generate_sequence_plan
from ai.uvm_renderer import UvmRenderer


def build(rtl: str, out: str, module: str | None, coverage_report: str | None) -> Path:
    spec = parse_module(rtl, module)
    seq_plan = generate_sequence_plan(spec)
    cov_summary = improve_plan_with_coverage(spec, seq_plan, coverage_report)
    risk = predict_bug_risk(spec)

    renderer = UvmRenderer()
    renderer.render_all(out, spec, seq_plan, risk)

    summary = {
        "module": spec.name,
        "port_count": len(spec.ports),
        "sequence_counts": {
            "smoke": len(seq_plan.smoke_vectors),
            "corner": len(seq_plan.corner_vectors),
            "directed": len(seq_plan.directed_vectors),
        },
        "coverage_loop": cov_summary,
        "bug_risk": asdict(risk),
    }
    summary_path = Path(out) / "generation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    return summary_path


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-assisted UVM TB generator")
    parser.add_argument("--rtl", required=True, help="Path to RTL file")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--module", required=False, default=None, help="Target module name")
    parser.add_argument("--coverage-report", required=False, default=None, help="Coverage report JSON")
    args = parser.parse_args()

    summary = build(args.rtl, args.out, args.module, args.coverage_report)
    print(f"Generated UVM TB in: {Path(args.out).resolve()}")
    print(f"Summary: {summary}")


if __name__ == "__main__":
    main()
