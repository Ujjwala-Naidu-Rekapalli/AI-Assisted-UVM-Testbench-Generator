# AI-Assisted UVM Testbench Generator

A from-scratch framework that generates a runnable UVM testbench skeleton from an RTL module and improves stimulus using an AI-guided coverage loop.

## What it does

**Input:** RTL module (ALU/cache/pipeline-stage style modules).

**Output:** Auto-generated UVM testbench package with:
- interface
- sequence item
- sequence
- driver
- monitor
- agent
- env
- scoreboard
- test
- top testbench

It also provides a Python AI layer that supports:
- **Auto sequence generation**
- **Coverage-driven improvement loop**
- **Bug prediction/prioritization**

## Architecture

- `tools/generate_uvm.py` – main CLI orchestrator.
- `ai/rtl_parser.py` – lightweight SystemVerilog module parser.
- `ai/sequence_generator.py` – LLM-backed or heuristic sequence strategy.
- `ai/coverage_loop.py` – iterative optimization loop driven by coverage reports.
- `ai/bug_predictor.py` – simple ML model + risk ranking fallback.
- `ai/uvm_renderer.py` – SystemVerilog UVM emitter for interface/package/top files.
- `examples/rtl/alu.sv` – sample RTL target.
- `generated_tb/` – output folder.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python tools/generate_uvm.py \
  --rtl examples/rtl/alu.sv \
  --out generated_tb/alu_tb \
  --module alu
```

This generates a complete UVM package and a JSON run summary.

## Optional LLM integration

Set these environment variables to enable LLM-generated directed scenarios:

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o-mini"
```

If no API key is present, the system falls back to deterministic heuristic scenario generation.

If you enable LLM mode, install the OpenAI SDK separately (`pip install openai`).

## Coverage loop input format

The coverage loop consumes a JSON report like:

```json
{
  "total_coverage": 71.5,
  "holes": [
    {"signal": "op", "bin": "3", "hits": 0},
    {"signal": "a", "bin": "max", "hits": 1}
  ]
}
```

Use:

```bash
python tools/generate_uvm.py \
  --rtl examples/rtl/alu.sv \
  --out generated_tb/alu_tb \
  --module alu \
  --coverage-report examples/coverage/alu_cov.json
```

## Bug prediction

The bug predictor estimates risk from static features:
- input/output width balance
- operation-port complexity
- number of control-like signals
- sequential vs combinational style hints

It outputs priority buckets (`HIGH`, `MEDIUM`, `LOW`) and rationale for triage.

## Testing

```bash
pytest -q
python tools/generate_uvm.py --rtl examples/rtl/alu.sv --out generated_tb/alu_tb --module alu
```

## Notes

- Generated testbench is UVM-compliant scaffold ready for simulator integration.
- The framework is simulator-agnostic and does not require vendor tool lock-in.
