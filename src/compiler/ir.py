from dataclasses import dataclass

@dataclass(frozen=True)
class IRvar:
    name: str
    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Instruction():
    "Base class for IR instructions"

@dataclass(frozen=True)
class Call(Instruction):
    fun: IRvar
    args: list[IRvar]
    dest: IRvar

@dataclass(frozen=True)
class LoadIntConst(Instruction):
    value: int
    dest: IRvar

@dataclass(frozen=True)
class LoadBoolConst(Instruction):
    value: bool
    dest: IRvar


@dataclass(frozen=True)
class Copy(Instruction):
    source: IRvar
    dest: IRvar

@dataclass(frozen=True)
class Label(Instruction):
    name: str

@dataclass(frozen=True)
class Jump(Instruction):
    label: Label

@dataclass(frozen=True)
class CondJump(Instruction):
    cond: IRvar
    then_label: Label
    else_label: Label

