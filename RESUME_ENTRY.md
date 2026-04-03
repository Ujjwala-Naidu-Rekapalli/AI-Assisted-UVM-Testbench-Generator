# Resume Entry (Copy/Paste Ready)

## Project
**AI-Assisted UVM Testbench Generator** | Python, SystemVerilog, UVM

## One-line Description
Built an end-to-end tool that converts RTL modules into auto-generated UVM testbench scaffolds and applies AI-guided sequence planning, coverage-improvement loops, and bug-risk prioritization.

## Impact Bullets
- Designed and implemented a Python CLI pipeline that parses RTL and auto-generates UVM components (interface, sequence item, sequence, driver, monitor, scoreboard, agent, environment, and test).
- Developed an AI-assisted sequence planner with both offline heuristics and optional LLM API integration for directed scenario synthesis.
- Implemented a coverage-driven feedback loop that consumes coverage-hole data and injects targeted vectors to improve closure.
- Built a bug-risk scoring module to prioritize verification effort and reduce debug turnaround.
- Added automated tests and reproducible sample artifacts for portfolio-ready demonstration on GitHub.

## Interview Talking Points
- Trade-offs between deterministic generators vs LLM-based generation in verification flows.
- How to make AI output auditable and reproducible in hardware verification pipelines.
- How risk-prioritized planning can reduce cycles to first meaningful bug discovery.
