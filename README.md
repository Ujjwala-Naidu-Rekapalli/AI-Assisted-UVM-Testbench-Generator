# AI-Assisted UVM Testbench Generator

An AI-assisted framework that helps generate and improve **UVM (Universal Verification Methodology)** testbench components for RTL designs. This project combines **SystemVerilog/UVM** with **Python-based automation** to reduce manual verification effort, improve productivity, and accelerate early-stage verification setup.

## Overview

Building a UVM testbench from scratch takes time. A verification engineer must study the RTL, understand interfaces, define transactions, write agents, sequences, monitors, scoreboards, and then refine the environment for better coverage. This project aims to simplify that process.

The idea is simple. Give the framework an RTL design or interface description, and it assists in generating reusable UVM components, test scenarios, and verification skeletons. It can also be extended to analyze coverage gaps and suggest new tests.

This project is designed for students and engineers who want to explore how **AI can improve design verification workflows**, especially for modern SoC and Systems IP verification.

## Motivation

Verification is one of the most time-consuming stages of hardware design. As SoCs become more complex, manual testbench development becomes slower and harder to scale. Companies are increasingly interested in smarter verification flows that use automation, coverage analysis, and AI-based assistance.

This repository demonstrates a practical application of that idea by focusing on:

- Faster UVM environment bring-up
- Reduced manual coding effort
- Improved test generation
- Better productivity in RTL verification flows

## Key Features

- Parses RTL module information or interface definitions
- Assists in generating UVM testbench skeletons
- Generates reusable verification components such as:
  - transaction class
  - sequence item
  - driver
  - monitor
  - sequencer
  - agent
  - scoreboard
  - environment
  - test class
- Supports Python-based automation for code generation
- Provides a framework to extend into:
  - constrained-random sequence generation
  - coverage-driven test generation
  - assertion suggestion
  - bug pattern analysis

## Project Goals

The main goals of this repository are:

1. Automate repetitive UVM coding tasks
2. Build a reusable verification productivity tool
3. Show the application of AI in hardware verification
4. Create a strong portfolio project for Design Verification and Systems IP roles

## Repository Structure

```text
AI-Assisted-UVM-Testbench-Generator/
│
├── rtl/                     # Example RTL designs
├── uvm_output/              # Generated UVM files
├── templates/               # UVM code templates
├── scripts/                 # Python automation scripts
├── docs/                    # Project notes and documentation
├── examples/                # Example generated outputs
├── tests/                   # Validation and regression scripts
└── README.md
