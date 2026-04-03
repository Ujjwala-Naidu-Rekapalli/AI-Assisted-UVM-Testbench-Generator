from __future__ import annotations

import re
from pathlib import Path

from ai.models import ModuleSpec, Port

MODULE_RE = re.compile(r"module\s+(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\s*\((?P<ports>.*?)\);", re.S)
PORT_RE = re.compile(
    r"(?P<dir>input|output|inout)\s*(?:logic|wire|reg)?\s*(?:\[(?P<msb>\d+)\s*:\s*(?P<lsb>\d+)\])?\s*(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)",
    re.S,
)


def parse_module(rtl_path: str | Path, module_name: str | None = None) -> ModuleSpec:
    text = Path(rtl_path).read_text()
    modules = MODULE_RE.finditer(text)

    selected = None
    for match in modules:
        if module_name is None or match.group("name") == module_name:
            selected = match
            break

    if selected is None:
        target = module_name or "<first module>"
        raise ValueError(f"Could not find module: {target}")

    name = selected.group("name")
    ports_blob = selected.group("ports")

    ports: list[Port] = []
    for port_match in PORT_RE.finditer(ports_blob):
        direction = port_match.group("dir")
        pname = port_match.group("name")
        msb = port_match.group("msb")
        lsb = port_match.group("lsb")
        width = 1
        if msb is not None and lsb is not None:
            width = abs(int(msb) - int(lsb)) + 1
        if direction in {"input", "output"}:
            ports.append(Port(direction=direction, name=pname, width=width))

    if not ports:
        raise ValueError("No ports parsed. Use ANSI-style module declarations.")

    return ModuleSpec(name=name, ports=ports)
