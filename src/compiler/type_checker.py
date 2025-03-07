from compiler import ast, types
from compiler.SymTab import SymTab
from compiler.types import Type, Unit, FunctionType


def typecheck(node: ast.Expression, symtab: SymTab) -> Type:
    match node:

        case bool():
            return types.Bool()
        case int():
            return types.Int()
        case ast.Literal(value=bool()):
            return types.Bool()
        case ast.Literal(value=int()):
            return types.Int()
        
        case ast.Identifier():
            var_type = symtab.lookup_variable_type(node.name)
            if var_type is None:
                raise TypeError(f"Variable '{node.name}' is not defined")
            return var_type
        
        case ast.UnaryOp():
            operand_type = typecheck(node.operand, symtab)
            op_type = symtab.lookup_variable_type(f"unary_{node.op}")

            if isinstance(op_type, FunctionType) and str(operand_type) == str(op_type.param_types[0]):
                return op_type.return_type
            else:
                raise TypeError(f"Unsupported unary operation: {node.op} for {operand_type}")
            
        case ast.BinaryOp():
            #if node.op == "=":
            #    if isinstance(node.left, ast.Identifier):
            #        value = typecheck(node.right, symtab)
            #        if str(symtab.lookup_variable_type(node.left.name)) != str(value):
            #            raise TypeError("Left side of assignment must be isinstance with right side")
            #        symtab.update_variable(node.left.name, value)
            #        return value
            #    else:
            #        raise TypeError("Left side of assignment must be an identifier.")

            left_type = typecheck(node.left, symtab)
            right_type = typecheck(node.right, symtab)
            op_types = symtab.lookup_variable_type(node.op)  # 这里可能是 `list`

            if isinstance(op_types, list):
                for op_type in op_types:
                    if isinstance(op_type, FunctionType):
                        if [type(left_type), type(right_type)] == [type(t) for t in op_type.param_types]:
                            return op_type.return_type
                raise TypeError(f"Operand type mismatch for operator '{node.op}'")

            # 旧代码逻辑（如果 `op_types` 只是单个 `FunctionType`）
            if isinstance(op_types, FunctionType):
                if [type(left_type), type(right_type)] != [type(t) for t in op_types.param_types]:
                    raise TypeError(f"Operand type mismatch for operator '{node.op}'")
                return op_types.return_type

            raise TypeError(f"Operator '{node.op}' not defined")
        
        case ast.Assignment():
            # 检查左侧是否为 Identifier
            if not isinstance(node.target, ast.Identifier):
                raise TypeError("Assignment target must be an identifier")
            
            # 检查右侧表达式类型
            value_type = typecheck(node.value, symtab)
            
            # 获取左侧变量的声明类型
            target_name = node.target.name
            target_type = symtab.lookup_variable_type(target_name)
            if target_type is None:
                raise TypeError(f"Variable '{target_name}' is not defined")
            
            # 检查类型兼容性
            if type(value_type) != type(target_type):
                raise TypeError(f"Cannot assign {value_type} to {target_type}")
            
            return target_type
            
        case ast.IfExpression():
            cond_type = typecheck(node.condition, symtab)

            if not isinstance(cond_type, types.Bool):
                raise TypeError("Condition in 'if' must be a Bool")
            then_type = typecheck(node.then_branch, symtab)
            if node.else_branch is None:
                else_type = None
            else:
                else_type = typecheck(node.else_branch, symtab)
                if type(then_type) != type(else_type):
                    raise TypeError("'then' and 'else' branches must have the same type")
            return then_type
        
        case ast.FunctionCall():
            if not isinstance(node.name, ast.Identifier):
                raise TypeError("Function name must be an identifier")
            func_name = node.name.name

            func_type = symtab.lookup_variable_type(func_name)
            if not isinstance(func_type, FunctionType):
                raise TypeError(f"{node.name} is not a function")

            if len(node.arguments) != len(func_type.param_types):
                raise TypeError("Incorrect number of arguments")

            for arg, param_type in zip(node.arguments, func_type.param_types):
                arg_type = typecheck(arg, symtab)
                if type(arg_type) != type(param_type):
                    raise TypeError("Argument type mismatch")
            
            return func_type.return_type
            
            
        
        case ast.Block():
            symtab.enter_locals()
            for expr in node.expressions:
                typecheck(expr, symtab)  
            result_type = types.Unit() if not node.result_expression else typecheck(node.result_expression, symtab)
            #symtab.enter_locals()
            symtab.leave_locals()
            return result_type
        
        case ast.VariableDeclaration():
            return typecheck_var_decl(node, symtab)
                
        case ast.WhileExpr():
            cond_type = typecheck(node.condition, symtab)
            #print('con', cond_type)
            if not isinstance(cond_type, types.Bool):
                raise TypeError("Condition in 'while' must be a Bool")
            body_type = typecheck(node.body, symtab)
            #print('body', body_type)
            return types.Unit()
        
        case ast.Break(value):
            if value:
                value_type = typecheck(value, symtab)
            return Unit()
        
        case ast.Continue():
            return Unit()

        case _:
            raise Exception(f'Unsupported AST node: {node}.')



def typecheck_var_decl(node: ast.VariableDeclaration, symtab: SymTab) -> types.Type:
    value_type = typecheck(node.value, symtab)
    annotated_type = None
    if node.type_annotation:
        # Map AST type expression to type checker's type
        annotated_type = node.type_annotation 
        if type(value_type) != type(annotated_type):
            raise TypeError(f"Type of initializer does not match variable type annotation in declaration of '{node.name}'")
    symtab.define_variable(node.name.name,node.value, value_type)
    return value_type

def map_ast_type_expr_to_type(type_expr: ast.Expression) -> types.Type:
    if str(type_expr) == 'Bool':
        return types.Bool()
    elif str(type_expr) == 'Int':
        return types.Int()
    else:
        raise Exception("Unknown type expression")




