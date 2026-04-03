package alu_tb_pkg;
  import uvm_pkg::*;
  `include "uvm_macros.svh"

  class alu_seq_item extends uvm_sequence_item;
    rand bit clk;
    rand bit rst_n;
    rand bit [7:0] a;
    rand bit [7:0] b;
    rand bit [2:0] op;
    bit [7:0] y;
    bit carry;
    bit zero;
    `uvm_object_utils_begin(alu_seq_item)
      `uvm_field_int(clk, UVM_ALL_ON)
      `uvm_field_int(rst_n, UVM_ALL_ON)
      `uvm_field_int(a, UVM_ALL_ON)
      `uvm_field_int(b, UVM_ALL_ON)
      `uvm_field_int(op, UVM_ALL_ON)
      `uvm_field_int(y, UVM_ALL_ON)
      `uvm_field_int(carry, UVM_ALL_ON)
      `uvm_field_int(zero, UVM_ALL_ON)
    `uvm_object_utils_end
    function new(string n="alu_seq_item"); super.new(n); endfunction
  endclass

  class alu_sequence extends uvm_sequence#(alu_seq_item);
    `uvm_object_utils(alu_sequence)
    function new(string n="alu_sequence"); super.new(n); endfunction
    virtual task body();
      alu_seq_item req;
      req = alu_seq_item::type_id::create("req_0");
      start_item(req);
      req.clk = 'd1;
      req.rst_n = 'd0;
      req.a = 'd202;
      req.b = 'd24;
      req.op = 'd1;
      finish_item(req);
      req = alu_seq_item::type_id::create("req_1");
      start_item(req);
      req.clk = 'd0;
      req.rst_n = 'd1;
      req.a = 'd29;
      req.b = 'd109;
      req.op = 'd0;
      finish_item(req);
      req = alu_seq_item::type_id::create("req_2");
      start_item(req);
      req.clk = 'd0;
      req.rst_n = 'd1;
      req.a = 'd214;
      req.b = 'd35;
      req.op = 'd3;
      finish_item(req);
      req = alu_seq_item::type_id::create("req_3");
      start_item(req);
      req.clk = 'd0;
      req.rst_n = 'd1;
      req.a = 'd30;
      req.b = 'd63;
      req.op = 'd3;
      finish_item(req);
      req = alu_seq_item::type_id::create("req_4");
      start_item(req);
      req.clk = 'd0;
      req.rst_n = 'd1;
      req.a = 'd25;
      req.b = 'd113;
      req.op = 'd0;
      finish_item(req);
    endtask
  endclass

  class alu_driver extends uvm_driver#(alu_seq_item);
    `uvm_component_utils(alu_driver)
    virtual alu_if vif;
    function new(string n, uvm_component p); super.new(n,p); endfunction
    virtual function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual alu_if)::get(this, "", "vif", vif)) `uvm_fatal("NOVIF","driver vif not set");
    endfunction
    virtual task run_phase(uvm_phase phase);
      forever begin
        seq_item_port.get_next_item(req);
        @(vif.drv_cb);
        vif.drv_cb.clk <= req.clk;
        vif.drv_cb.rst_n <= req.rst_n;
        vif.drv_cb.a <= req.a;
        vif.drv_cb.b <= req.b;
        vif.drv_cb.op <= req.op;
        seq_item_port.item_done();
      end
    endtask
  endclass

  class alu_monitor extends uvm_component;
    `uvm_component_utils(alu_monitor)
    virtual alu_if vif;
    uvm_analysis_port#(alu_seq_item) ap;
    function new(string n, uvm_component p); super.new(n,p); ap = new("ap", this); endfunction
    virtual function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(virtual alu_if)::get(this, "", "vif", vif)) `uvm_fatal("NOVIF","monitor vif not set");
    endfunction
    virtual task run_phase(uvm_phase phase);
      alu_seq_item tr;
      forever begin
        @(vif.mon_cb);
        tr = alu_seq_item::type_id::create("tr");
        tr.clk = vif.mon_cb.clk;
        tr.rst_n = vif.mon_cb.rst_n;
        tr.a = vif.mon_cb.a;
        tr.b = vif.mon_cb.b;
        tr.op = vif.mon_cb.op;
        tr.y = vif.mon_cb.y;
        tr.carry = vif.mon_cb.carry;
        tr.zero = vif.mon_cb.zero;
        ap.write(tr);
      end
    endtask
  endclass

  class alu_scoreboard extends uvm_component;
    `uvm_component_utils(alu_scoreboard)
    uvm_analysis_imp#(alu_seq_item, alu_scoreboard) imp;
    function new(string n, uvm_component p); super.new(n,p); imp = new("imp", this); endfunction
    virtual function void write(alu_seq_item t);
      `uvm_info("SB", $sformatf("Observed alu transaction"), UVM_LOW)
    endfunction
  endclass

  class alu_agent extends uvm_component;
    `uvm_component_utils(alu_agent)
    alu_driver drv; alu_monitor mon; uvm_sequencer#(alu_seq_item) seqr;
    function new(string n, uvm_component p); super.new(n,p); endfunction
    virtual function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      drv = alu_driver::type_id::create("drv", this);
      mon = alu_monitor::type_id::create("mon", this);
      seqr = uvm_sequencer#(alu_seq_item)::type_id::create("seqr", this);
    endfunction
    virtual function void connect_phase(uvm_phase phase);
      super.connect_phase(phase);
      drv.seq_item_port.connect(seqr.seq_item_export);
    endfunction
  endclass

  class alu_env extends uvm_env;
    `uvm_component_utils(alu_env)
    alu_agent agent; alu_scoreboard sb;
    function new(string n, uvm_component p); super.new(n,p); endfunction
    virtual function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      agent = alu_agent::type_id::create("agent", this);
      sb = alu_scoreboard::type_id::create("sb", this);
    endfunction
    virtual function void connect_phase(uvm_phase phase);
      super.connect_phase(phase);
      agent.mon.ap.connect(sb.imp);
    endfunction
  endclass

  class alu_test extends uvm_test;
    `uvm_component_utils(alu_test)
    alu_env env;
    function new(string n, uvm_component p); super.new(n,p); endfunction
    virtual function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      env = alu_env::type_id::create("env", this);
    endfunction
    virtual task run_phase(uvm_phase phase);
      alu_sequence seq;
      phase.raise_objection(this);
      seq = alu_sequence::type_id::create("seq");
      seq.start(env.agent.seqr);
      #100;
      phase.drop_objection(this);
    endtask
  endclass
endpackage
