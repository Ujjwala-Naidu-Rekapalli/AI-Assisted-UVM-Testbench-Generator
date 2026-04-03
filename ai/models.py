from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Port:
    direction: str
    name: str
    width: int = 1


@dataclass
class ModuleSpec:
    name: str
    ports: list[Port] = field(default_factory=list)

    @property
    def inputs(self) -> list[Port]:
        return [p for p in self.ports if p.direction == "input"]

    @property
    def outputs(self) -> list[Port]:
        return [p for p in self.ports if p.direction == "output"]


@dataclass
class SequencePlan:
    smoke_vectors: list[dict]
    corner_vectors: list[dict]
    directed_vectors: list[dict]


@dataclass
class BugRisk:
    score: float
    priority: str
    reasons: list[str]
