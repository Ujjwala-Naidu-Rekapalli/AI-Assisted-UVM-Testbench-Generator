from __future__ import annotations

import json
import os
import random
from dataclasses import asdict

from ai.models import ModuleSpec, SequencePlan


def _rand_value(width: int) -> int:
    if width <= 0:
        return 0
    return random.randint(0, (1 << min(width, 16)) - 1)


def _heuristic_plan(spec: ModuleSpec) -> SequencePlan:
    random.seed(7)
    smoke = []
    corner = []

    input_ports = spec.inputs

    for _ in range(10):
        smoke.append({p.name: _rand_value(p.width) for p in input_ports})

    for p in input_ports:
        maxv = (1 << min(p.width, 16)) - 1
        corner.append({q.name: 0 for q in input_ports} | {p.name: maxv})

    directed = []
    op_port = next((p for p in input_ports if p.name in {"op", "opcode", "sel", "cmd"}), None)
    if op_port:
        for op in range(min(1 << min(op_port.width, 4), 8)):
            vec = {p.name: _rand_value(p.width) for p in input_ports}
            vec[op_port.name] = op
            directed.append(vec)

    return SequencePlan(smoke_vectors=smoke, corner_vectors=corner, directed_vectors=directed)


def _llm_plan(spec: ModuleSpec) -> SequencePlan | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    # Optional integration path: keep soft dependency to avoid runtime breakage.
    try:
        from openai import OpenAI
    except Exception:
        return None

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    prompt = (
        "Create JSON with keys smoke_vectors, corner_vectors, directed_vectors for RTL module inputs. "
        "Each vector is object {signal:value}. Keep <=10 vectors per category. Module:\n"
        f"{json.dumps(asdict(spec))}"
    )
    resp = client.responses.create(model=model, input=prompt)
    text = resp.output_text
    try:
        obj = json.loads(text)
        return SequencePlan(
            smoke_vectors=obj.get("smoke_vectors", []),
            corner_vectors=obj.get("corner_vectors", []),
            directed_vectors=obj.get("directed_vectors", []),
        )
    except Exception:
        return None


def generate_sequence_plan(spec: ModuleSpec) -> SequencePlan:
    llm = _llm_plan(spec)
    if llm is not None:
        return llm
    return _heuristic_plan(spec)
