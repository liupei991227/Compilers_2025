import unittest
from compiler.tokenizer import tokenize, Token, L

class test_tokenizer(unittest.TestCase):
    def test_1token(self) -> None:
        assert tokenize("hello") == [
            Token(loc=L, type='identifier', text='hello')
        ]
        assert tokenize("   \n  hi      \n\n") == [
            Token(loc=L, type='identifier',text='hi')
        ]

    def testMultoken(self) -> None:
        assert tokenize(" hi number 1 ") == [
            Token(loc=L, type='identifier', text='hi'),
            Token(loc=L, type='identifier',text='number'),
            Token(loc=L, type='int_literal',text='1'),
        ]
        assert tokenize(" 3 + -5 ") == [
            Token(loc=L, type='int_literal', text='3'),
            Token(loc=L, type='operator',text='+'),
            Token(loc=L, type='operator',text='-'),
            Token(loc=L, type='int_literal',text='5'),
        ]

        assert tokenize(" 3 - 1 ") == [
            Token(loc=L, type='int_literal', text='3'),
            Token(loc=L, type='operator', text='-'),
            Token(loc=L, type='int_literal', text='1')
        ]
        assert tokenize(" 3 * 1 ") == [
            Token(loc=L, type='int_literal', text='3'),
            Token(loc=L, type='operator', text='*'),
            Token(loc=L, type='int_literal', text='1')
        ]

    def test_tokenizer_single_line_comments(self) -> None:
        assert tokenize("// This is a comment\na = b + 1") == [
            Token(loc=L, type='identifier', text='a'),
            Token(loc=L, type='operator', text='='),
            Token(loc=L, type='identifier', text='b'),
            Token(loc=L, type='operator', text='+'),
            Token(loc=L, type='int_literal', text='1'),
        ]

    def test_tokenizer_multi_line_comments(self) -> None:  
        print(tokenize("// This is a \n#multi-line comment \na = b + 1"))
        assert tokenize("// This is a \n#multi-line comment \na = b + 1") == [
            Token(loc=L, type='identifier', text='a'),
            Token(loc=L, type='operator', text='='),
            Token(loc=L, type='identifier', text='b'),
            Token(loc=L, type='operator', text='+'),
            Token(loc=L, type='int_literal', text='1'),
        ]

    
