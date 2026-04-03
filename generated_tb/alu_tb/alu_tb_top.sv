`timescale 1ns/1ps
import uvm_pkg::*;
`include "uvm_macros.svh"
import alu_tb_pkg::*;

module alu_tb_top;
  logic clk; logic rst_n;
  alu_if vif(.clk(clk), .rst_n(rst_n));
  alu dut (
    .clk(vif.clk),
    .rst_n(vif.rst_n),
    .a(vif.a),
    .b(vif.b),
    .op(vif.op),
    .y(vif.y),
    .carry(vif.carry),
    .zero(vif.zero)
  );
  initial begin clk=0; forever #5 clk=~clk; end
  initial begin rst_n=0; repeat(5) @(posedge clk); rst_n=1; end
  initial begin
    uvm_config_db#(virtual alu_if)::set(null, "*", "vif", vif);
    run_test("alu_test");
  end
endmodule
