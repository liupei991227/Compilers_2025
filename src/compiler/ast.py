from dataclasses import dataclass
from typing import List, Optional, Tuple
from compiler.types import Type

@dataclass
class SourceLocation:
    row: int
    column: int

@dataclass
class Location(SourceLocation):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, SourceLocation):
            return True
        return False


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    #location: Location



@dataclass
class Literal(Expression): #数字
    value: int | bool | None

@dataclass
class Identifier(Expression): #加减乘除等操作符
    name: str

@dataclass
class BinaryOp(Expression): #二叉树
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression


@dataclass
class IfExpression(Expression):
    condition: Expression
    then_branch: Expression
    else_branch: Expression | None  # Allow optional else



@dataclass
class FunctionCall(Expression):
    name: Expression  # Normally is an Identifier
    arguments: list[Expression]


@dataclass
class UnaryOp(Expression):
    """AST node for unary operations like -x or not x"""
    op: str
    operand: Expression


@dataclass
class Assignment(Expression):
    """分配，右结合"""
    target: Identifier
    value: Expression

@dataclass
class Block(Expression):
    expressions: List[Expression]
    result_expression: Optional[Expression] = None


@dataclass
class VariableDeclaration(Expression):
    name: Identifier
    value: Expression
    type_annotation: Optional[Type] = None

@dataclass
class WhileExpr(Expression):
    condition: Expression
    body: Expression


@dataclass
class PointerType(Expression):
    base_type: Expression  # basci type


@dataclass
class AddressOf(Expression):
    expr: Expression


@dataclass
class FunctionDef:
    name: str
    params: List[Tuple[str, Type]]
    return_type: Type
    body: List[Expression]

@dataclass
class Break(Expression):
    value: Optional[Expression] = None 

@dataclass
class Continue(Expression):
    pass
