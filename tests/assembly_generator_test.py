import unittest

from compiler.assembly_generator import generate_assembly
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.tokenizer import tokenize


class MyTestCase(unittest.TestCase):
    def test_load_bool_const_true1(self) -> None:
        source_code = "1 + 2"
        tokens = tokenize(source_code)
        ast_root = parse(tokens)
        ir_instructions = generate_ir(ast_root)
        assembly_code = generate_assembly(ir_instructions)
        print(assembly_code)

    def test_load_bool_const_true2(self) -> None:
        source_code = "1 * 2"
        tokens = tokenize(source_code)
        ast_root = parse(tokens)
        ir_instructions = generate_ir(ast_root)
        assembly_code = generate_assembly(ir_instructions)
        print(assembly_code)

if __name__ == '__main__':
    unittest.main()
