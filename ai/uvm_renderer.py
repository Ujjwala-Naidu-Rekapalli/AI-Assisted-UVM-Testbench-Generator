from __future__ import annotations

from pathlib import Path

from ai.models import BugRisk, ModuleSpec, SequencePlan


def _range(width: int) -> str:
    return f"[{width - 1}:0] " if width > 1 else ""


class UvmRenderer:
    def render_all(self, out_dir: str | Path, spec: ModuleSpec, plan: SequencePlan, risk: BugRisk) -> None:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{spec.name}_if.sv").write_text(self._render_interface(spec))
        (out / f"{spec.name}_tb_pkg.sv").write_text(self._render_package(spec, plan))
        (out / f"{spec.name}_tb_top.sv").write_text(self._render_top(spec))
        (out / "run_manifest.txt").write_text(self._render_manifest(spec, plan, risk))

    def _render_interface(self, spec: ModuleSpec) -> str:
        lines = [f"interface {spec.name}_if(input logic clk, input logic rst_n);"]
        for p in spec.inputs + spec.outputs:
            lines.append(f"  logic {_range(p.width)}{p.name};")
        lines += ["", "  clocking drv_cb @(posedge clk);"]
        for p in spec.inputs:
            lines.append(f"    output {p.name};")
        for p in spec.outputs:
            lines.append(f"    input {p.name};")
        lines += ["  endclocking", "", "  clocking mon_cb @(posedge clk);"]
        for p in spec.inputs + spec.outputs:
            lines.append(f"    input {p.name};")
        lines += ["  endclocking", "endinterface", ""]
        return "\n".join(lines)

    def _render_package(self, spec: ModuleSpec, plan: SequencePlan) -> str:
        name = spec.name
        lines = [
            f"package {name}_tb_pkg;",
            "  import uvm_pkg::*;",
            '  `include "uvm_macros.svh"',
            "",
            f"  class {name}_seq_item extends uvm_sequence_item;",
        ]
        for p in spec.inputs:
            lines.append(f"    rand bit {_range(p.width)}{p.name};")
        for p in spec.outputs:
            lines.append(f"    bit {_range(p.width)}{p.name};")
        lines += [f"    `uvm_object_utils_begin({name}_seq_item)"]
        for p in spec.inputs + spec.outputs:
            lines.append(f"      `uvm_field_int({p.name}, UVM_ALL_ON)")
        lines += [
            "    `uvm_object_utils_end",
            f"    function new(string n=\"{name}_seq_item\"); super.new(n); endfunction",
            "  endclass",
            "",
            f"  class {name}_sequence extends uvm_sequence#({name}_seq_item);",
            f"    `uvm_object_utils({name}_sequence)",
            f"    function new(string n=\"{name}_sequence\"); super.new(n); endfunction",
            "    virtual task body();",
            f"      {name}_seq_item req;",
        ]
        for i, vec in enumerate(plan.smoke_vectors[:5]):
            lines += [
                f"      req = {name}_seq_item::type_id::create(\"req_{i}\");",
                "      start_item(req);",
            ]
            for k, v in vec.items():
                lines.append(f"      req.{k} = 'd{v};")
            lines.append("      finish_item(req);")
        lines += [
            "    endtask",
            "  endclass",
            "",
            f"  class {name}_driver extends uvm_driver#({name}_seq_item);",
            f"    `uvm_component_utils({name}_driver)",
            f"    virtual {name}_if vif;",
            f"    function new(string n, uvm_component p); super.new(n,p); endfunction",
            "    virtual function void build_phase(uvm_phase phase);",
            "      super.build_phase(phase);",
            f"      if (!uvm_config_db#(virtual {name}_if)::get(this, \"\", \"vif\", vif)) `uvm_fatal(\"NOVIF\",\"driver vif not set\");",
            "    endfunction",
            "    virtual task run_phase(uvm_phase phase);",
            "      forever begin",
            "        seq_item_port.get_next_item(req);",
            "        @(vif.drv_cb);",
        ]
        for p in spec.inputs:
            lines.append(f"        vif.drv_cb.{p.name} <= req.{p.name};")
        lines += [
            "        seq_item_port.item_done();",
            "      end",
            "    endtask",
            "  endclass",
            "",
            f"  class {name}_monitor extends uvm_component;",
            f"    `uvm_component_utils({name}_monitor)",
            f"    virtual {name}_if vif;",
            f"    uvm_analysis_port#({name}_seq_item) ap;",
            f"    function new(string n, uvm_component p); super.new(n,p); ap = new(\"ap\", this); endfunction",
            "    virtual function void build_phase(uvm_phase phase);",
            "      super.build_phase(phase);",
            f"      if (!uvm_config_db#(virtual {name}_if)::get(this, \"\", \"vif\", vif)) `uvm_fatal(\"NOVIF\",\"monitor vif not set\");",
            "    endfunction",
            "    virtual task run_phase(uvm_phase phase);",
            f"      {name}_seq_item tr;",
            "      forever begin",
            "        @(vif.mon_cb);",
            f"        tr = {name}_seq_item::type_id::create(\"tr\");",
        ]
        for p in spec.inputs + spec.outputs:
            lines.append(f"        tr.{p.name} = vif.mon_cb.{p.name};")
        lines += [
            "        ap.write(tr);",
            "      end",
            "    endtask",
            "  endclass",
            "",
            f"  class {name}_scoreboard extends uvm_component;",
            f"    `uvm_component_utils({name}_scoreboard)",
            f"    uvm_analysis_imp#({name}_seq_item, {name}_scoreboard) imp;",
            f"    function new(string n, uvm_component p); super.new(n,p); imp = new(\"imp\", this); endfunction",
            f"    virtual function void write({name}_seq_item t);",
            f"      `uvm_info(\"SB\", $sformatf(\"Observed {name} transaction\"), UVM_LOW)",
            "    endfunction",
            "  endclass",
            "",
            f"  class {name}_agent extends uvm_component;",
            f"    `uvm_component_utils({name}_agent)",
            f"    {name}_driver drv; {name}_monitor mon; uvm_sequencer#({name}_seq_item) seqr;",
            f"    function new(string n, uvm_component p); super.new(n,p); endfunction",
            "    virtual function void build_phase(uvm_phase phase);",
            "      super.build_phase(phase);",
            f"      drv = {name}_driver::type_id::create(\"drv\", this);",
            f"      mon = {name}_monitor::type_id::create(\"mon\", this);",
            f"      seqr = uvm_sequencer#({name}_seq_item)::type_id::create(\"seqr\", this);",
            "    endfunction",
            "    virtual function void connect_phase(uvm_phase phase);",
            "      super.connect_phase(phase);",
            "      drv.seq_item_port.connect(seqr.seq_item_export);",
            "    endfunction",
            "  endclass",
            "",
            f"  class {name}_env extends uvm_env;",
            f"    `uvm_component_utils({name}_env)",
            f"    {name}_agent agent; {name}_scoreboard sb;",
            f"    function new(string n, uvm_component p); super.new(n,p); endfunction",
            "    virtual function void build_phase(uvm_phase phase);",
            "      super.build_phase(phase);",
            f"      agent = {name}_agent::type_id::create(\"agent\", this);",
            f"      sb = {name}_scoreboard::type_id::create(\"sb\", this);",
            "    endfunction",
            "    virtual function void connect_phase(uvm_phase phase);",
            "      super.connect_phase(phase);",
            "      agent.mon.ap.connect(sb.imp);",
            "    endfunction",
            "  endclass",
            "",
            f"  class {name}_test extends uvm_test;",
            f"    `uvm_component_utils({name}_test)",
            f"    {name}_env env;",
            f"    function new(string n, uvm_component p); super.new(n,p); endfunction",
            "    virtual function void build_phase(uvm_phase phase);",
            "      super.build_phase(phase);",
            f"      env = {name}_env::type_id::create(\"env\", this);",
            "    endfunction",
            "    virtual task run_phase(uvm_phase phase);",
            f"      {name}_sequence seq;",
            "      phase.raise_objection(this);",
            f"      seq = {name}_sequence::type_id::create(\"seq\");",
            "      seq.start(env.agent.seqr);",
            "      #100;",
            "      phase.drop_objection(this);",
            "    endtask",
            "  endclass",
            "endpackage",
            "",
        ]
        return "\n".join(lines)

    def _render_top(self, spec: ModuleSpec) -> str:
        lines = [
            "`timescale 1ns/1ps",
            "import uvm_pkg::*;",
            '`include "uvm_macros.svh"',
            f"import {spec.name}_tb_pkg::*;",
            "",
            f"module {spec.name}_tb_top;",
            "  logic clk; logic rst_n;",
            f"  {spec.name}_if vif(.clk(clk), .rst_n(rst_n));",
            f"  {spec.name} dut (",
        ]
        for i, p in enumerate(spec.inputs + spec.outputs):
            comma = "," if i < len(spec.inputs + spec.outputs) - 1 else ""
            lines.append(f"    .{p.name}(vif.{p.name}){comma}")
        lines += [
            "  );",
            "  initial begin clk=0; forever #5 clk=~clk; end",
            "  initial begin rst_n=0; repeat(5) @(posedge clk); rst_n=1; end",
            "  initial begin",
            f"    uvm_config_db#(virtual {spec.name}_if)::set(null, \"*\", \"vif\", vif);",
            f"    run_test(\"{spec.name}_test\");",
            "  end",
            "endmodule",
            "",
        ]
        return "\n".join(lines)

    def _render_manifest(self, spec: ModuleSpec, plan: SequencePlan, risk: BugRisk) -> str:
        return (
            f"# Generated run manifest for {spec.name} UVM TB\n"
            f"# Risk priority: {risk.priority} (score={risk.score:.3f})\n\n"
            "Expected files:\n"
            f"- {spec.name}_if.sv\n"
            f"- {spec.name}_tb_pkg.sv\n"
            f"- {spec.name}_tb_top.sv\n\n"
            "Compile order (example):\n"
            "1) <uvm_pkg>\n"
            f"2) {spec.name}_if.sv\n"
            f"3) {spec.name}_tb_pkg.sv\n"
            "4) <rtl file>\n"
            f"5) {spec.name}_tb_top.sv\n\n"
            f"Coverage-improvement directed vectors appended: {len(plan.directed_vectors)}\n"
        )
