import unittest
from compiler import types, ast
from compiler.SymTab import SymTab, add_builtin_symbols
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck
from compiler.types import Int, Bool, Unit


def assert_fails_typecheck(code: str) -> None:
    failed = False
    expr = parse(tokenize(code))
    symtab = SymTab(parent=None)
    add_builtin_symbols(symtab)
    try:
        typecheck(expr, symtab)
    except Exception:
        failed = True
    assert failed, f"Type-checking succeeded for: {code}"



class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.symtab = SymTab(parent=None)
        add_builtin_symbols(self.symtab)
    def test_something(self) -> None:
        assert str(typecheck(parse(tokenize("1 + 2 ")),self.symtab)) == 'Int'
        assert str(typecheck(parse(tokenize("1 + 2 < 3")),self.symtab)) == 'Bool'
        assert_fails_typecheck(" ( 1 < 2 ) + 3")
    
    def test_type_check_if_then_else(self) -> None:
        assert str(typecheck(parse(tokenize("if 1 < 2 then 3 else 4")),self.symtab)) == 'Int'
        assert_fails_typecheck("if 1 then 3 else 4 < 5")
        assert_fails_typecheck("if 1 < 2 then 3 else 4 < 5")


class TestTypeChecker(unittest.TestCase):
    def setUp(self) -> None:
        self.symtab = SymTab(parent=None)
        add_builtin_symbols(self.symtab)

    def test_int_literal(self) -> None:
        node = parse(tokenize("42"))
        self.assertIsInstance(typecheck(node, self.symtab), types.Int)

    def test_bool_literal(self) -> None:
        node = parse(tokenize("True"))
        self.assertIsInstance(typecheck(node, self.symtab), types.Bool)

    def test_binary_op_ints(self) -> None:
        node = parse(tokenize("42 + 1"))
        self.assertIsInstance(typecheck(node, self.symtab), types.Int)
    
    def test_binary_op_type_mismatch(self) -> None:
        node = parse(tokenize("42 + True"))
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)
    
    def test_variable_lookup(self) -> None:
        self.symtab.define_variable("x", 10, types.Int())
        node = ast.Identifier(name="x")
        self.assertIsInstance(typecheck(node, self.symtab), types.Int)

    def test_if_expr(self) -> None:
        node = parse(tokenize("if True then 42 else 1"))
        self.assertIsInstance(typecheck(node, self.symtab), types.Int)

    def test_if_expr_type_mismatch(self) -> None:
        node = parse(tokenize("if True then 42 else False"))
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)


class TestTypeCheckerWithFunctionTypes(unittest.TestCase):
    def setUp(self) -> None:
        self.symtab = SymTab(parent=None)
        add_builtin_symbols(self.symtab)  

    def test_function_call_with_correct_types(self) -> None:
        source_code = "print_int(42)"
        node = parse(tokenize(source_code))
        self.assertIsInstance(typecheck(node, self.symtab), Unit)

    def test_binary_op_with_correct_types(self) -> None:
        source_code = "42 + 1"
        node = parse(tokenize(source_code))
        self.assertIsInstance(typecheck(node, self.symtab), Int)

    def test_function_call_with_incorrect_argument_type(self) -> None:
        source_code = "print_int(True)"
        node = parse(tokenize(source_code))
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)


class TestUnaryOpTypeCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.symtab = SymTab(parent=None)
        add_builtin_symbols(self.symtab)

    def test_not_operator_with_bool(self) -> None:
        source_code = "not true"
        node = parse(tokenize(source_code))
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Bool)

    def test_not_operator_with_int(self) -> None:
        source_code = "not 42"
        node = parse(tokenize(source_code))
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)


class TestBlockTypeCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.symtab = SymTab(parent=None)
        add_builtin_symbols(self.symtab)

    def test_empty_block(self) -> None:
        source_code = "{}"
        node = parse(tokenize(source_code))
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Unit)

    def test_block_with_last_expression_int(self) -> None:
        source_code = "{ true; 42 }"
        node = parse(tokenize(source_code))
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Int)

    def test_block_with_last_expression_bool(self) -> None:
        source_code = "{ 42; false }"
        node = parse(tokenize(source_code))
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Bool)

    def test_block_with_variable_declaration(self) -> None:
        source_code = "{ var x : Bool = true; x }"
        self.symtab.define_variable("x","x", Bool()) 
        print(tokenize(source_code))
        node = parse(tokenize(source_code))

        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Bool)



