import unittest
from compiler.parser import parse
from compiler.tokenizer import Token, tokenize
import compiler.ast as ast


if not hasattr(Token, "loc"):
    setattr(Token, "loc", "L")

class MyTestCase(unittest.TestCase):

    # def test_parse_while_loop(self) -> None:
    #     tokens = tokenize("""
    #     var x = 7;
    #     while true do {
    #         if x % 5 == 0 then {
    #             break;
    #         }
    #         x = x + 1;
    #     }
    #     x
    # """)
    
    #     parsed_block = parse(tokens)
    #     print(parsed_block)

    #     assert parsed_block == ast.Block(
    #         expressions=[
    #             ast.VariableDeclaration(
    #                 name=ast.Identifier(name='x'),
    #                 value=ast.Literal(value=7),
    #                 type_annotation=None
    #             ),
    #             ast.WhileExpr(
    #                 condition=ast.Literal(value=True),
    #                 body=ast.Block(
    #                     expressions=[
    #                         ast.IfExpression(
    #                             condition=ast.BinaryOp(
    #                                 left=ast.BinaryOp(
    #                                     left=ast.Identifier(name='x'),
    #                                     op='%',
    #                                     right=ast.Literal(value=5)
    #                                 ),
    #                                 op='==',
    #                                 right=ast.Literal(value=0)
    #                             ),
    #                             then_branch=ast.Block(
    #                                 expressions=[ast.Break()],
    #                                 result_expression=None

    #                             ),
    #                             else_branch=None
    #                         ),
    #                         ast.Assignment(
    #                             target=ast.Identifier(name='x'),
    #                             value=ast.BinaryOp(
    #                                 left=ast.Identifier(name='x'),
    #                                 op='+',
    #                                 right=ast.Literal(value=1)
    #                             )
    #                         )
    #                     ],
    #                     result_expression=None
    #                 )
    #             )
    #         ],
    #         result_expression=ast.Identifier(name='x')
    #     )



    def test_nested_blocks(self) -> None:
        tokens = tokenize("{ { 1 } { 2 } }")
        parsed_block = parse(tokens)
        print(parsed_block)

        assert parsed_block == ast.Block(
            expressions=[
                ast.Block(
                    expressions=[],
                    result_expression=ast.Literal(value=1)
                )],
            
            result_expression=ast.Block(
                    expressions=[],
                    result_expression=ast.Literal(value=2)
                )
        )

    def test_parse_multiple_assignments_and_function_calls(self) -> None:
        tokens = tokenize("""
        var a = 3;
        var b = 4;
        var c = 5;
        a = b = c;
        print_int(a);
        print_int(b);
        print_int(c);
    """)
        parsed_block = parse(tokens)
        assert parsed_block == ast.Block(
            expressions=[
                ast.VariableDeclaration(
                    name=ast.Identifier(name='a'),
                    value=ast.Literal(3)
                ),
                ast.VariableDeclaration(
                    name=ast.Identifier(name='b'),
                    value=ast.Literal(4)
                ),
                ast.VariableDeclaration(
                    name=ast.Identifier(name='c'),
                    value=ast.Literal(5)
                ),
                ast.Assignment(
                    target=ast.Identifier(name='a'),
                    value=ast.Assignment(
                        target=ast.Identifier(name='b'),
                        value=ast.Identifier(name='c')
                    )
                ),
                ast.FunctionCall(
                    name=ast.Identifier(name='print_int'),
                    arguments=[ast.Identifier(name='a')]
                ),
                ast.FunctionCall(
                    name=ast.Identifier(name='print_int'),
                    arguments=[ast.Identifier(name='b')]
                ),
                ast.FunctionCall(
                    name=ast.Identifier(name='print_int'),
                    arguments=[ast.Identifier(name='c')]
                )
            ]
        )





    def test_chained_assignment(self) -> None:
        tokens = tokenize("a = b = c")
        parsed_block = parse(tokens)
        print(parsed_block)

        assert parsed_block == ast.Assignment(
            target=ast.Identifier(name='a'),
            value=ast.Assignment(
                target=ast.Identifier(name='b'),
                value=ast.Identifier(name='c')
            )
        )
    #def test_parse_integer_literal(self) -> None:
    #    tokens = tokenize("123;")  # 对输入进行词法分析，生成 token 列表
    #    print(tokens)  # 打印 token 方便调试
    #    parsed_expr = parse(tokens)  # 调用解析器
    #    assert parsed_expr is None



    def test_1_1(self) -> None:   
        assert parse(tokenize("1 == 1")) == ast.BinaryOp(
            left=ast.Literal(value=1),
            op='==',
            right=ast.Literal(value=1),
        )


    def test_true_or_false(self) -> None:   
        assert parse(tokenize("true or false")) == ast.BinaryOp(
            left=ast.Literal(True),
            op='or',
            right=ast.Literal(False),
        )

    def test_new_block1(self) -> None:
        tokens = tokenize("{ true; 1 + 2 } + 3")
        print(tokens)

        parsed_block = parse(tokens)


        assert parsed_block == ast.BinaryOp(
            left=ast.Block(
                expressions=[
                    ast.Literal(value=True)
                ],
                result_expression=ast.BinaryOp(
                    left=ast.Literal(value=1),
                    op='+',
                    right=ast.Literal(value=2)
                )
            ),
            op='+',
            right=ast.Literal(value=3)
        )

    def test_parser_iteration(self) -> None:   
        assert parse(tokenize("1 + 2 - 3")) == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(1),
                op='+',
                right=ast.Literal(2),
            ),
            op='-',
            right=ast.Literal(3),
        )

    def test_parser_ops(self) -> None:
        assert parse(tokenize("1 + 2 * 3")) == ast.BinaryOp(
            left=ast.Literal(1),
            op='+',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='*',
                right=ast.Literal(3),
            ),
        )
    
    def test_parser_parentheses(self) -> None:
        assert parse(tokenize("(1 + 2) * 3")) == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(1),
                op='+',
                right=ast.Literal(2),
            ),
            op='*',
            right=ast.Literal(3),
        )
    
    def test_parser_parentheses2(self) -> None:
        assert parse(tokenize("1 * (2 + 3)")) == ast.BinaryOp(
            left=ast.Literal(1),
            op='*',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='+',
                right=ast.Literal(3),
            ),
        )

        assert parse(tokenize(" 1 * ( 2 + 3 ) / 4 ")) == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(1),
                op='*',
                right=ast.BinaryOp(
                    left=ast.Literal(2),
                    op='+',
                    right=ast.Literal(3),
                ),
            ),
            op='/',
            right=ast.Literal(4)
        )


    def test_parse_if_then_else(self) -> None:
        assert parse(tokenize("if 1 then 2")) == ast.IfExpression(
            condition=ast.Literal(1),
            then_branch=ast.Literal(2),
            else_branch=None,
        )
        assert parse(tokenize("if 1 then 2 else 3")) == ast.IfExpression(
            condition=ast.Literal(1),
            then_branch=ast.Literal(2),
            else_branch=ast.Literal(3),
        )
        assert parse(tokenize("if 1 then 2 * 3 else 3 / 4")) == ast.IfExpression(
            condition=ast.Literal(1),
            then_branch=ast.BinaryOp(ast.Literal(2),'*',ast.Literal(3)),
            else_branch=ast.BinaryOp(ast.Literal(3),'/',ast.Literal(4)),
        )
    
    def test_parse_function_call(self) -> None:
        tokens = tokenize("f ( x, y + z )")
        parsed_expression = parse(tokens)
        print(parsed_expression)
        assert parsed_expression == ast.FunctionCall(
            name=ast.Identifier(name='f'), 
            arguments=[
                ast.Identifier(name='x'),
                ast.BinaryOp(
                    left=ast.Identifier(name='y'),
                    op='+',
                    right=ast.Identifier(name='z')
                )
            ]
        )
    
    

    def test_parse_right_associativity(self) -> None:
        assert parse(tokenize("2 + 3 + 4"),right_associative=True) == ast.BinaryOp(
            left=ast.Literal(2),
            op='+',
            right=ast.BinaryOp(
                left=ast.Literal(3),
                op='+',
                right=ast.Literal(4),
            )
        )
    
    def test_parse_block1(self) -> None:
        tokens = tokenize("{ f(a); x = y; f(x)}")
        parsed_block = parse(tokens)
        print(parsed_block)

        assert parsed_block == ast.Block(
            expressions=[
                ast.FunctionCall(
                    name=ast.Identifier(name='f'), 
                    arguments=[ast.Identifier(name='a')]
                ),
                ast.Assignment(  
                    target=ast.Identifier(name='x'),
                    value=ast.Identifier(name='y')
                )
            ],
            result_expression=ast.FunctionCall(
                name=ast.Identifier(name='f'), 
                arguments=[ast.Identifier(name='x')]
            )
        )
    
    def test_parse_variable_declaration(self) -> None:
        tokens = tokenize("var x = 1")
        parsed_declaration = parse(tokens)
        assert parsed_declaration == ast.VariableDeclaration(
            name=ast.Identifier(name='x'),
            value=ast.Literal(1)
        )
    
    def test_parse_block2(self) -> None:
        tokens = tokenize("{ { f(a) } { b } }")
        parsed_block = parse(tokens)
        print(parsed_block)

        assert parsed_block == ast.Block(
            expressions=[
                ast.Block(
                    expressions=[],
                    result_expression=ast.FunctionCall(
                            name=ast.Identifier(name='f'),
                            arguments=[ast.Identifier(name='a')]
                        )
                )
            ],
            result_expression=ast.Block(
                    expressions=[], 
                    result_expression=ast.Identifier(name='b') 
                ),  
        )
    
    def test_blocks_with_assignment1(self) -> None:
        tokens = tokenize("x = { f(a); b }")
        parsed_block = parse(tokens)
        print(parsed_block)

        assert parsed_block == ast.Assignment(
            target=ast.Identifier(name='x'),
            value=ast.Block(
                expressions=[
                    ast.FunctionCall(
                        name=ast.Identifier(name='f'),
                        arguments=[ast.Identifier(name='a')]
                    ),
                ],
                result_expression=ast.Identifier(name='b')
            )
        )
    
    def test_blocks_with_assignment2(self) -> None:

        tokens = tokenize("x = { { f(a) } { b } }")
        parsed_block = parse(tokens)
        print(parsed_block)

        assert parsed_block == ast.Assignment(
            target=ast.Identifier(name='x'),
            value=ast.Block(
                expressions=[
                    ast.Block(
                        expressions=[],
                        result_expression=ast.FunctionCall(
                                name=ast.Identifier(name='f'),
                                arguments=[ast.Identifier(name='a')]
                            ) # The inner block doesn't return anything
                    )
                ],
                result_expression=ast.Block(
                        expressions=[],
                        result_expression=ast.Identifier(name='b')
                    )  
            )
        )
    

    def test_parse_compare(self) -> None:
        assert parse(tokenize("1 < ( 2 + 3 )")) == ast.BinaryOp(
            left=ast.Literal(1),
            op='<',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='+',
                right=ast.Literal(3),
            )
        )













