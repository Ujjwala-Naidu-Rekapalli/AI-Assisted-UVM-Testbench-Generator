from __future__ import annotations

from ai.models import BugRisk, ModuleSpec


def predict_bug_risk(spec: ModuleSpec) -> BugRisk:
    in_w = sum(p.width for p in spec.inputs)
    out_w = sum(p.width for p in spec.outputs)
    io_ratio = in_w / max(out_w, 1)
    ctrl_like = sum(1 for p in spec.inputs if p.name.lower() in {"op", "opcode", "sel", "cmd", "valid", "ready"})
    wide_ports = sum(1 for p in spec.ports if p.width >= 16)

    # Self-contained weighted heuristic model (ML-lite scoring without external deps).
    score = 0.15
    score += min(io_ratio / 8.0, 0.35)
    score += min(ctrl_like * 0.12, 0.24)
    score += min(wide_ports * 0.08, 0.24)
    score = max(0.0, min(score, 0.99))

    if score >= 0.67:
        priority = "HIGH"
    elif score >= 0.34:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    reasons = []
    if io_ratio > 2.0:
        reasons.append("High input/output width ratio indicates datapath/control imbalance.")
    if ctrl_like >= 2:
        reasons.append("Multiple control-like input signals may increase state-space complexity.")
    if wide_ports > 0:
        reasons.append("Wide ports detected; overflow/sign issues are common bug hotspots.")
    if not reasons:
        reasons.append("Balanced structural features suggest lower relative implementation risk.")

    return BugRisk(score=score, priority=priority, reasons=reasons)
