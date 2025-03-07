import unittest
from compiler.tokenizer import tokenize, Token
from compiler.parser import parse
from compiler.tokenizer import Token, tokenize
import compiler.ast as ast
from compiler.interpreter import interpret
from compiler.SymTab import SymTab, add_builtin_symbols

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.symtab: SymTab = SymTab(parent=None)
        add_builtin_symbols(self.symtab)


    def test_interpreter_op(self) -> None:
        assert interpret(parse(tokenize("1 + 2")), self.symtab) == 3

    def test_interpret_prior(self) -> None:
        assert interpret(parse(tokenize("( 1 + 2 ) * 3")),self.symtab) == 9
    
    def test_interprete_if_then_else(self) -> None:
        assert interpret(parse(tokenize("if 1 < 2 then 3 else 4")),self.symtab) == 3
        assert interpret(parse(tokenize("if 2 < 1 then 3 else 4")),self.symtab) == 4
        assert interpret(parse(tokenize("10 + if 2 < 1 then 3 else 4")),self.symtab) == 14



