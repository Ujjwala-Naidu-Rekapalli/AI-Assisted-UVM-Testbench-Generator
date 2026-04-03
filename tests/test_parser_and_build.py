from pathlib import Path

from tools.generate_uvm import build


def test_build_generates_files(tmp_path: Path):
    out = tmp_path / "alu_tb"
    summary = build(
        rtl="examples/rtl/alu.sv",
        out=str(out),
        module="alu",
        coverage_report="examples/coverage/alu_cov.json",
    )

    assert summary.exists()
    assert (out / "alu_if.sv").exists()
    assert (out / "alu_tb_pkg.sv").exists()
    assert (out / "alu_tb_top.sv").exists()

    data = summary.read_text()
    assert '"module": "alu"' in data
    assert '"priority"' in data
