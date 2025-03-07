from compiler import ast
from compiler import ir
from compiler.SymTab import SymTab, add_builtin_symbols
from compiler.ir import IRvar
from compiler.type_checker import typecheck
from compiler.types import Type, Unit, Int, Bool
from typing import Generic, TypeVar, Dict, Any, List, Optional, cast


def generate_ir(root_node: ast.Expression) -> list[ir.Instruction]:

    next_var_number = 1
    next_label_number = 1

    symtab = SymTab(parent=None)
    add_builtin_symbols(symtab)

    var_types: dict[IRvar, Type] = {}
    #var_types = {}
    var_unit = IRvar("unit")
    var_types[var_unit] = Unit()

    def new_var(t: Type) -> IRvar:
        nonlocal next_var_number
        var = IRvar(f'x{next_var_number}')
        next_var_number += 1
        var_types[var] = t
        return var

    def new_label(prefix: str) -> ir.Label:
        nonlocal next_label_number
        label = ir.Label(f'{prefix}{next_label_number}')
        next_label_number += 1
        return label

    instructions: list[ir.Instruction] = []

    def visit(node: ast.Expression, loop_start: Optional[ir.Label] = None, loop_end: Optional[ir.Label] = None) -> IRvar:
        nonlocal symtab
        var_type = typecheck(node, symtab)

        match node:
            case ast.Literal():
                var = new_var(var_type)
                if isinstance(var_type, Int):
                    value = cast(int, node.value)
                    instructions.append(ir.LoadIntConst(value, var))
                elif isinstance(var_type, Bool):
                    value = cast(bool, node.value)
                    instructions.append(ir.LoadBoolConst(value, var))
                else:
                    raise NotImplementedError(
                        f"Unsupported literal type: {var_type}")
                return var

            case ast.Identifier():
                var, var_type1 = symtab.lookup_variable(node.name, flag=True)
                print('var',var)
                print('var_type1',var_type1)
                if not isinstance(var, IRvar):
                    raise TypeError(f"Identifier {node.name} is not an IR variable")
                return var

            case ast.BinaryOp():
                if node.op == "or":
                    var_left = visit(node.left)
                    # temp_var = new_var(var_type)  # 创建临时变量
                    # instructions.append(ir.Copy(source=var_left, dest=temp_var)) # 复制左操作数的值到临时变量
                    var_result = new_var(var_type)

                    or_skip = ir.Label("or_skip")
                    or_right = ir.Label("or_right")
                    or_end = ir.Label("or_end")

                    # 使用临时变量作为条件
                    # instructions.append(ir.CondJump(cond=temp_var, then_label=or_skip, else_label=or_right))
                    instructions.append(ir.CondJump(
                        cond=var_left, then_label=or_skip, else_label=or_right))

                    instructions.append(ir.Label(or_right.name))
                    var_right = visit(node.right)
                    instructions.append(
                        ir.Copy(source=var_right, dest=var_result))
                    instructions.append(ir.Jump(label=or_end))

                    instructions.append(ir.Label(or_skip.name))
                    instructions.append(ir.LoadBoolConst(
                        value=True, dest=var_result))
                    instructions.append(ir.Jump(label=or_end))

                    instructions.append(ir.Label(or_end.name))
                    return var_result

                elif node.op == "and":
                    var_left = visit(node.left)
                    var_result = new_var(var_type)

                    and_skip = ir.Label("and_skip")
                    and_right = ir.Label("and_right")
                    and_end = ir.Label("and_end")

                    instructions.append(ir.CondJump(
                        cond=var_left, then_label=and_right, else_label=and_skip))

                    instructions.append(ir.Label(and_right.name))
                    var_right = visit(node.right)
                    instructions.append(
                        ir.Copy(source=var_right, dest=var_result))
                    instructions.append(ir.Jump(label=and_end))

                    instructions.append(ir.Label(and_skip.name))
                    instructions.append(ir.LoadBoolConst(
                        value=False, dest=var_result))
                    instructions.append(ir.Jump(label=and_end))

                    instructions.append(ir.Label(and_end.name))
                    return var_result
                else:

                    var_left = visit(node.left)
                    var_right = visit(node.right)
                    var_result = new_var(var_type)
                    instructions.append(ir.Call(
                        fun=IRvar(node.op),
                        args=[var_left, var_right],
                        dest=var_result,
                    ))
                    return var_result

            case ast.UnaryOp():
                operand_var = visit(node.operand)  # 访问操作数
                var_result = new_var(var_type)

                if node.op == "-":
                    func_var = IRvar("unary_-")
                elif node.op == "not":
                    func_var = IRvar("unary_not")
                else:
                    raise NotImplementedError(
                        f"Unsupported unary operator: {node.op}")

                instructions.append(ir.Call(
                    fun=func_var,
                    args=[operand_var],
                    dest=var_result
                ))

                return var_result

            case ast.IfExpression():

                cond_var = visit(node.condition)
                var_type = typecheck(node, symtab)

                then_label = new_label('then')
                else_label = new_label('else') if node.else_branch else None
                end_label = new_label('if_end')

                actual_else_label = else_label if node.else_branch else end_label

                assert actual_else_label is not None 
                instructions.append(
                    ir.CondJump(cond=cond_var, then_label=then_label,
                                else_label=actual_else_label))

                instructions.append(then_label)
                then_result_var = visit(node.then_branch)

                if var_type != Unit():
                    result_var = new_var(var_type)
                    instructions.append(ir.Copy(source=then_result_var, dest=result_var))
                else:
                    result_var = var_unit  # Use the predefined unit variable
                instructions.append(ir.Jump(label=end_label))

                if node.else_branch:
                    assert else_label is not None 
                    instructions.append(else_label)
                    else_result_var = visit(node.else_branch)
                    if var_type != Unit():
                        instructions.append(ir.Copy(source=else_result_var, dest=result_var))
                    #instructions.append(ir.Jump(label=end_label))

                instructions.append(end_label)

                return result_var 

            case ast.Block():
                symtab.enter_locals()
                result_var = var_unit
                for expr in node.expressions:
                    visit(expr)
                if node.result_expression:
                    result_var = visit(node.result_expression)
                else:
                    result_var = new_var(Unit())
                symtab.leave_locals()
                return result_var
            
                # if node.expressions == []:
                #     exp_var = None
                # for expr in node.expressions:
                #     # Generate IR code for each expression in the block
                #     exp_var = visit(expr)
                #     # print(exp_var)
                # if node.result_expression:
                #     result_var = visit(node.result_expression)

                # else:
                #     # If the block has no result expression, the default is Unit type
                #     result_var = new_var(Unit())
                # symtab.leave_locals()
                # return result_var

            case ast.VariableDeclaration():
                # nonlocal var_types
                init_var = visit(node.value)
                var_type = typecheck(node.value, symtab)
                var = new_var(var_type)

                symtab.define_variable(node.name.name, var, var_type)
                instructions.append(ir.Copy(init_var, var))
                return var_unit

            case ast.WhileExpr(condition, body):

                start_label = new_label('while_start')
                body_label = new_label('while_body')
                end_label = new_label('while_end')


                instructions.append(start_label)

                cond_var = visit(condition)
                instructions.append(ir.CondJump(
                    cond=cond_var, then_label=body_label, else_label=end_label)) #start_lable改成了body_label
                
                instructions.append(body_label)
                visit(body)

                #visit(body, loop_start=start_label, loop_end=end_label)

                instructions.append(ir.Jump(label=start_label))#continue_label改成了start_label
                #instructions.append(start_label)

                instructions.append(end_label)
                return var_unit

            case ast.FunctionDef(name, params, return_type, body):
                func_symtab = SymTab(parent=symtab)  # Create a new symbol table for the function scope
                for param_name, param_type in params:
                    param_var = ir.IRvar(param_name)
                    func_symtab.define_variable(param_name, param_var, param_type)
                # Process function body in the function scope
                for expr in body:
                    visit(expr)
                return var_unit
            

            case ast.FunctionCall(ast.Identifier(name), arguments):
                func_var, func_type = symtab.lookup_variable(name, True)
                #visit(func_var)
                #print('fuva',func_var,func_type)
                arg_vars = [visit(arg) for arg in arguments]
                result_var = new_var(func_type.return_type)
                instructions.append(ir.Call(fun=func_var, args=arg_vars, dest=result_var))
                return result_var
            
            case ast.Assignment(target=ast.Identifier(name=target_name), value=value_expr):

                target_var, target_type = symtab.lookup_variable(target_name, flag=True)

                value_var = visit(value_expr)
                
                if not isinstance(var_types[value_var], type(target_type)):
                    raise TypeError(f"Type mismatch in assignment to {target_name}{target_type} = {value_var}{var_types[value_var]}")

                instructions.append(ir.Copy(source=value_var, dest=target_var))

                return value_var
            case ast.Break(value):
                if value:
                    value_var = visit(value, symtab, instructions, loop_start, loop_end)
                    instructions.append(ir.Copy(source=value_var, dest=value_var))  #  assum. loop_result_var
                instructions.append(ir.Jump(label=loop_end))
                return var_unit

            case ast.Continue():
                if loop_start is None:
                    raise SyntaxError("continue statement not inside a loop")
                instructions.append(ir.Jump(label=loop_start))
                return var_unit
            
            case _:
                raise NotImplementedError(f"Unsupported node type: {type(node)}")
            

    var_result = visit(root_node)
    #print(var_result,var_types)
    if var_result != None:
        print(f"var_result type: {type(var_result)}, value: {var_result}")
        result_type = var_types.get(var_result, Unit())
        if isinstance(result_type, Int):
            instructions.append(ir.Call(IRvar('print_int'), [var_result], new_var(Int())))
        elif isinstance(result_type, Bool):
            instructions.append(ir.Call(IRvar('print_bool'), [var_result], new_var(Int())))

    return instructions
    #     if str(var_types[var_result]) == 'Int':
    #         instructions.append(ir.Call(IRvar('print_int'), [var_result], new_var(Int())))
    #     if str(var_types[var_result]) == 'Bool':
    #         instructions.append(ir.Call(IRvar('print_bool'), [var_result], new_var(Int())))

    # return instructions



    
