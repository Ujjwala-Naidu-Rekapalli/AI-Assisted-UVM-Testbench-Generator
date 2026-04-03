module alu (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [7:0]  a,
    input  logic [7:0]  b,
    input  logic [2:0]  op,
    output logic [7:0]  y,
    output logic        carry,
    output logic        zero
);

always_comb begin
    carry = 1'b0;
    unique case (op)
        3'd0: {carry, y} = a + b;
        3'd1: {carry, y} = a - b;
        3'd2: y = a & b;
        3'd3: y = a | b;
        3'd4: y = a ^ b;
        3'd5: y = (a < b) ? 8'd1 : 8'd0;
        default: y = 8'd0;
    endcase
end

assign zero = (y == 8'd0);

endmodule
