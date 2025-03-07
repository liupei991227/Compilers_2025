from typing import Generic, TypeVar, Dict, Any, List, Optional
from compiler import types, ast
from compiler.types import Int, Bool, FunctionType, Unit, Type
from compiler.ir import Call, LoadIntConst, IRvar, Label, Jump, Copy, CondJump, LoadBoolConst

T = TypeVar("T")


class SymTab():
    def __init__(self, parent: Optional['SymTab'] | None):
        self.locals: List[Dict[str, tuple[Any, Type]]] = [{}]
        self.parent = parent
        self.symbols: Dict[str, tuple[Any, Type]] = {}

        if parent is None:  # 只在顶级作用域添加内置符号
            add_builtin_symbols(self)
    
    def enter_locals(self) -> None:
        self.locals.append({})

    def leave_locals(self) -> None:
        self.locals.pop()
    
    def lookup_variable(self, name: str, flag: bool = False) -> T | Any:
        #print(self.locals)
        for local in reversed(self.locals):
            if name in local:
                entry = local[name]
                if isinstance(entry, tuple):
                    value, var_type = entry
                    print(entry)
                else:
                    value = entry
                    var_type = None
                    #(local[name], None)
                
                if flag:
                    return (value, var_type)
                else:
                    return value


                # value, var_type = local[name] if isinstance(local[name], tuple) else (local[name], None)
                # return (value, var_type) if flag else value
            
                #return (value, None) if flag else value

            #if isinstance(var_type, list):
            #    return var_type  # 返回所有可用类型
            #return var_type
        
                # = local[name]
                #if str(type(value)) == "<class 'tuple'>":
                #    if flag:
                #        return local[name]
                #    else:
                #        return local[name][0]
                #else:
                #    return local[name]
        
        if self.parent:
            return self.parent.lookup_variable(name, flag)
        
        raise KeyError(f"Variable '{name}' not found.")
    
    def define_variable(self, name: str, value: Any, var_type: Any) -> None:

        self.locals[-1][name] = (value, var_type)

    def update_variable(self, name: str, value: Any) -> None:
        # Update the value of a variable in an existing scope if the variable exists
        for local in reversed(self.locals):
            if name in local:
                #local[name] = value
                _, var_type = local[name]  # 保留原始类型
                local[name] = (value, var_type)
                return
        raise KeyError(f"Variable '{name}' not defined.")
    
    def lookup_variable_type(self, name: str) -> Type:
        for local in reversed(self.locals):
            if name in local:
                _, var_type = local[name]
                return var_type
        raise KeyError(f"Type for variable '{name}' not found.")
    



    

def add_builtin_symbols(symtab: SymTab) -> None:

    symtab.define_variable("Int", Int(), Int())
    symtab.define_variable("Bool",Bool(), Bool())
    symtab.define_variable("true", True, types.Bool())
    symtab.define_variable("false", False, types.Bool())
    symtab.define_variable("+", lambda a, b: a + b, FunctionType([Int(), Int()], Int()))
    symtab.define_variable("-", lambda a, b: a - b, FunctionType([Int(), Int()], Int()))
    symtab.define_variable("*", lambda a, b: a * b, FunctionType([Int(), Int()], Int()))
    symtab.define_variable("/", lambda a, b: a // b, FunctionType([Int(), Int()], Int()))
    symtab.define_variable("%", lambda a, b: a % b, FunctionType([Int(), Int()], Int()))

    symtab.define_variable("==", lambda a, b: a == b, [
        FunctionType([Int(), Int()], Bool()),
        FunctionType([Bool(), Bool()], Bool())
    ])
    symtab.define_variable("!=", lambda a, b: a != b, [
        FunctionType([Int(), Int()], Bool()),
        FunctionType([Bool(), Bool()], Bool())
    ])
    
    symtab.define_variable("<", lambda a, b: a < b, FunctionType([Int(), Int()], Bool()))
    symtab.define_variable("<=", lambda a, b: a <= b, FunctionType([Int(), Int()], Bool()))
    symtab.define_variable(">", lambda a, b: a > b, FunctionType([Int(), Int()], Bool()))
    symtab.define_variable(">=", lambda a, b: a >= b, FunctionType([Int(), Int()], Bool()))

    symtab.define_variable("and", lambda a, b: a and b, FunctionType([Bool(), Bool()], Bool()))
    symtab.define_variable("or", lambda a, b: a or b, FunctionType([Bool(), Bool()], Bool()))
    symtab.define_variable("unary_not", lambda a: not a, FunctionType([Bool()], Bool()))
    symtab.define_variable("unary_-", lambda a: -a, FunctionType([Int()], Int()))
    symtab.define_variable("print_int", IRvar("print_int"), FunctionType([Int()], Unit()))
    symtab.define_variable("print_bool", IRvar("print_bool"), FunctionType([Bool()], Unit()))
    symtab.define_variable("read_int", IRvar("read_int"), FunctionType([], Int()))






