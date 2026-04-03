interface alu_if(input logic clk, input logic rst_n);
  logic clk;
  logic rst_n;
  logic [7:0] a;
  logic [7:0] b;
  logic [2:0] op;
  logic [7:0] y;
  logic carry;
  logic zero;

  clocking drv_cb @(posedge clk);
    output clk;
    output rst_n;
    output a;
    output b;
    output op;
    input y;
    input carry;
    input zero;
  endclocking

  clocking mon_cb @(posedge clk);
    input clk;
    input rst_n;
    input a;
    input b;
    input op;
    input y;
    input carry;
    input zero;
  endclocking
endinterface
