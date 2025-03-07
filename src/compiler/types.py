from dataclasses import dataclass
from typing import List


class Type:
    pass

class Int(Type):
    def __repr__(self) -> str:
        return "Int"

class Bool(Type):
    def __repr__(self) -> str:
        return "Bool"

class Unit(Type):
    def __repr__(self) -> str:
        return "Unit"

class FunctionType(Type):
    def __init__(self, param_types: List[Type], return_type: Type) -> None:
        self.param_types = param_types
        self.return_type = return_type

    def __repr__(self) -> str:
        param_types_str = ", ".join(repr(t) for t in self.param_types)
        return f"({param_types_str}) => {repr(self.return_type)}"

class PointerType(Type):
    def __init__(self, base_type: Type) -> None:
        self.base_type = base_type

    def __repr__(self) -> str:
        return f"{self.base_type}*"