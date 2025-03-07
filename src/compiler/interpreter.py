from typing import Any, Optional, Callable
import compiler.ast as ast

from compiler.SymTab import SymTab

type Value = int | bool | None

class BreakException(Exception):
    def __init__(self, value: Optional[Value] = None) -> None:
        self.value = value

class ContinueException(Exception):
    pass

def interpret(node: Optional[ast.Expression], symtab: SymTab) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            if node.op == "=":
                # 确保左侧是标识符
                if isinstance(node.left, ast.Identifier):
                    # 计算右侧表达式的值
                    value = interpret(node.right, symtab)
                    # 更新现有变量的值
                    symtab.update_variable(node.left.name, value)
                    return value
                else:
                    raise TypeError("Left side of assignment must be an identifier.")
            if node.op == 'and':
                left_value = interpret(node.left, symtab)
                if not left_value:  # 如果左侧为假，则不需要评估右侧
                    return False
                return interpret(node.right, symtab)
            elif node.op == 'or':
                left_value = interpret(node.left, symtab)
                if left_value:  # 如果左侧为真，则不需要评估右侧
                    return True
                return interpret(node.right, symtab)
            else:
                a: Value = interpret(node.left, symtab)
                b: Value = interpret(node.right, symtab)
                op_func = symtab.lookup_variable(node.op)
                return op_func(a, b)

        case ast.IfExpression():
            if interpret(node.condition, symtab):
                return interpret(node.then_branch,symtab)
            else:
                return interpret(node.else_branch,symtab)
        
        case ast.UnaryOp():
            operand_val: Value = interpret(node.operand, symtab)
            op_func = symtab.lookup_variable(f"unary_{node.op}")
            return op_func(operand_val)
        
        case ast.Break(value):
            # if break has value, return optional value
            raise BreakException(interpret(value, symtab) if value else None)
        case ast.Continue():
            raise ContinueException()
    

        case _:
            raise ValueError(f"Unknown AST node {node}")
