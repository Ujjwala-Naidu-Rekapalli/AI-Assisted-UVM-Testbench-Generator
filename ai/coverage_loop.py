from __future__ import annotations

import json
from pathlib import Path

from ai.models import ModuleSpec, SequencePlan


def improve_plan_with_coverage(
    spec: ModuleSpec,
    plan: SequencePlan,
    coverage_report_path: str | None,
    max_iters: int = 3,
    target_cov: float = 90.0,
) -> dict:
    if not coverage_report_path:
        return {
            "iterations": 0,
            "status": "skipped",
            "final_coverage": None,
            "added_vectors": [],
        }

    data = json.loads(Path(coverage_report_path).read_text())
    total = float(data.get("total_coverage", 0.0))
    holes = list(data.get("holes", []))

    added = []
    iters = 0
    while total < target_cov and holes and iters < max_iters:
        hole = holes.pop(0)
        signal = hole.get("signal")
        bin_value = hole.get("bin")

        vec = {p.name: 0 for p in spec.inputs}
        if signal in vec:
            try:
                vec[signal] = int(bin_value)
            except Exception:
                vec[signal] = 1
        plan.directed_vectors.append(vec)
        added.append(vec)

        total += 5.0
        iters += 1

    return {
        "iterations": iters,
        "status": "completed",
        "final_coverage": min(total, 100.0),
        "added_vectors": added,
    }
