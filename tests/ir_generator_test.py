import unittest

from compiler import ast
from compiler.ast import Continue, Break
from compiler.ir import Call, LoadIntConst, IRvar, Label, Jump, Copy, CondJump, LoadBoolConst
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.tokenizer import tokenize


class MyTestCase(unittest.TestCase):

    # def test_variable_shadowing_and_assignment(self) -> None:
    #     source_code = """
    # var x = 3;
    # {
    #     var x = 4;
    # }
    # x = 5;
    # x
    # """
    #     ast_root = parse(tokenize(source_code))
    #     print(ast_root)
    #     ir_instructions = generate_ir(ast_root)
    #     assert ir_instructions == [
    #         LoadIntConst(value=3, dest=IRvar('x1')),
    #         Copy(source=IRvar('x1'), dest=IRvar('x2')),

    #         LoadIntConst(value=4, dest=IRvar('x3')),
    #         Copy(source=IRvar('x3'), dest=IRvar('x4')),

    #         LoadIntConst(value=5, dest=IRvar('x5')),
    #         Copy(source=IRvar('x5'), dest=IRvar('x2')),

    #         Call(fun=IRvar('print_int'), args=[IRvar('x2')], dest=IRvar('x6'))
    #     ]

    def test_variable_assignment(self) -> None:
        source_code = "var x = 1"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)

        assert ir_instructions == [
            LoadIntConst(value=1, dest=IRvar('x1')),
            Copy(source=IRvar('x1'), dest=IRvar('x2'))  # x2 代表变量 x
        ]

    def test_single_integer_literal(self) -> None:
        source_code = "123;"
        ast_root = parse(tokenize(source_code))
        print(ast_root)
        ir_instructions = generate_ir(ast_root)

        assert ir_instructions == [
            LoadIntConst(value=123, dest=IRvar('x1'))
        ]


    # def test_while_i_s(self) -> None:
    #     source_code = """
    #     var i = 1;
    #     var s = 0;
    #     while i <= 5 do {
    #         s = s + i;
    #         i = i + 1;
    #     }
    #     s
    #     """
    #     ast_root = parse(tokenize(source_code))
    #     print(ast_root)
    #     ir_instructions = generate_ir(ast_root)
    
    #     assert ir_instructions == [
    #         LoadIntConst(value=1, dest=IRvar('x1')),
    #         Copy(source=IRvar('x1'), dest=IRvar('x2')),
    #         LoadIntConst(value=0, dest=IRvar('x3')),
    #         Copy(source=IRvar('x3'), dest=IRvar('x4')),
    
    #         Label('while_start'),
    #         LoadIntConst(value=5, dest=IRvar('x5')),
    #         Call(fun=IRvar('<='), args=[IRvar('x2'), IRvar('x5')], dest=IRvar('x6')),
    #         CondJump(cond=IRvar('x6'), then_label=Label('while_body'), else_label=Label('while_end')),
    
    #         Label('while_body'),
    #         Call(fun=IRvar('+'), args=[IRvar('x4'), IRvar('x2')], dest=IRvar('x7')),
    #         Copy(source=IRvar('x7'), dest=IRvar('x4')),
    #         LoadIntConst(value=1, dest=IRvar('x8')),
    #         Call(fun=IRvar('+'), args=[IRvar('x2'), IRvar('x8')], dest=IRvar('x9')),
    #         Copy(source=IRvar('x9'), dest=IRvar('x2')),
    #         Jump(label=Label('while_start')),
    
    #         Label('while_end'),
    #         Call(fun=IRvar('print_int'), args=[IRvar('x4')], dest=IRvar('x10'))
    #     ]


    def test_nested_if_then_else(self) -> None:
        source_code = "if if true then true else false then 1 else 2"
        ast_root = parse(tokenize(source_code))
        print(ast_root)
        ir_instructions = generate_ir(ast_root)
    
        assert ir_instructions == [
            LoadBoolConst(value=True, dest=IRvar('x1')),
            CondJump(cond=IRvar('x1'), then_label=Label('then1'), else_label=Label('else2')),

            Label('then1'),  
            LoadBoolConst(value=True, dest=IRvar('x2')), 
            Copy(source=IRvar('x2'), dest=IRvar('x3')), 
            Jump(label=Label('if_end3')),

            Label('else2'),  
            LoadBoolConst(value=False, dest=IRvar('x4')), 
            Copy(source=IRvar('x4'), dest=IRvar('x3')), 

            Label('if_end3'), 

            CondJump(cond=IRvar('x3'), then_label=Label('then4'), else_label=Label('else5')),

            Label('then4'),
            LoadIntConst(value=1, dest=IRvar('x5')),  
            Copy(source=IRvar('x5'), dest=IRvar('x6')), 
            Jump(label=Label('if_end6')),

            Label('else5'),  
            LoadIntConst(value=2, dest=IRvar('x7')), 
            Copy(source=IRvar('x7'), dest=IRvar('x6')), 

            Label('if_end6'), 
            Call(fun=IRvar('print_int'), args=[IRvar('x6')], dest=IRvar('x8')) 
    ]


    # def test_while_with_if_mod(self) -> None:
    #     source_code = """
    #     var i = 0;
    #     while i <= 3 do {
    #         if i % 2 == 1 then {
    #             print_int(i);
    #         }
    #         i = i + 1;
    #     }
    #     """
    #     #print(tokenize(source_code))
    #     ast_root = parse(tokenize(source_code))
        
    #     print(ast_root)
    #     ir_instructions = generate_ir(ast_root)
    
    #     assert ir_instructions == [
    #         LoadIntConst(value=0, dest=IRvar('x1')), 
    #         Copy(source=IRvar('x1'), dest=IRvar('x2')), 

    #         Label('while_start'), 
    #         LoadIntConst(value=3, dest=IRvar('x3')), 
    #         Call(fun=IRvar('<='), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')), 
    #         CondJump(cond=IRvar('x4'), then_label=Label('while_body'), else_label=Label('while_end')), 

    #         Label('while_body'), 
    #         LoadIntConst(value=2, dest=IRvar('x5')), 
    #         Call(fun=IRvar('%'), args=[IRvar('x2'), IRvar('x5')], dest=IRvar('x6')), 
    #         LoadIntConst(value=1, dest=IRvar('x7')), 
    #         Call(fun=IRvar('=='), args=[IRvar('x6'), IRvar('x7')], dest=IRvar('x8')), 
    #         CondJump(cond=IRvar('x8'), then_label=Label('then'), else_label=Label('if_end')), 

    #         Label('then'),
    #         Call(fun=IRvar('print_int'), args=[IRvar('x2')], dest=IRvar('x9')),

    #         Label('if_end'), 
    #         LoadIntConst(value=1, dest=IRvar('x10')), 
    #         Call(fun=IRvar('+'), args=[IRvar('x2'), IRvar('x10')], dest=IRvar('x11')),
    #         Copy(source=IRvar('x11'), dest=IRvar('x2')),
    #         Jump(label=Label('while_start')), 

    #         Label('while_end') 
    #     ]


    # def test_or_with_block(self) -> None:
    #     source_code = "var x = true; x or { print_int(123); true };"
    #     ast_root = parse(tokenize(source_code))
    #     #print(tokenize(source_code))
    #     print(ast_root)
    #     ir_instructions = generate_ir(ast_root)
    #     assert ir_instructions == [
    #         LoadBoolConst(value=True, dest=IRvar('x1')),  
    #         Copy(source=IRvar('x1'), dest=IRvar('x2')),  
    #         CondJump(cond=IRvar('x2'), then_label=Label('or_skip'), else_label=Label('or_right')),
        
    #         Label('or_right'),  
    #         LoadIntConst(value=123, dest=IRvar('x3')),  
    #         Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x4')),  
    #         LoadBoolConst(value=True, dest=IRvar('x5')),  
    #         Copy(source=IRvar('x5'), dest=IRvar('x6')),  
    #         Jump(label=Label('or_end')), 

    #         Label('or_skip'),  
    #         LoadBoolConst(value=True, dest=IRvar('x6')),  
    #         Jump(label=Label('or_end')),  

    #         Label('or_end')  
    #     ]


    def test_bool_equality(self) -> None:
        source_code = "true == false"
        ast_root = parse(tokenize(source_code))
        print(tokenize(source_code))
        print(ast_root)
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [
            LoadBoolConst(value=True, dest=IRvar('x1')),
            LoadBoolConst(value=False, dest=IRvar('x2')),
            Call(fun=IRvar('=='), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
            Call(fun=IRvar('print_bool'), args=[IRvar('x3')], dest=IRvar('x4'))
        ]


    def test_or_ture_or_false(self) -> None:
        source_code = "true or false"
        ast_root = parse(tokenize(source_code))
        print(tokenize(source_code))
        print(ast_root)
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [
            LoadBoolConst(value=True, dest=IRvar('x1')),
            CondJump(cond=IRvar('x1'), then_label=Label('or_skip'), else_label=Label('or_right')),
            Label('or_right'),
            LoadBoolConst(value=False, dest=IRvar('x3')),
            Copy(source=IRvar('x3'), dest=IRvar('x2')),
            Jump(label=Label('or_end')),
            Label('or_skip'),
            LoadBoolConst(value=True, dest=IRvar('x2')),
            Jump(label=Label('or_end')),
            Label('or_end'),
            Call(fun=IRvar('print_bool'), args=[IRvar('x2')], dest=IRvar('x4'))
        ]

    def test_toplevel_print1(self) -> None:
        source_code = "123; 456"
        ast_root = parse(tokenize(source_code))
        print(ast_root)
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [
            LoadIntConst(value=123, dest=IRvar('x1')),
            LoadIntConst(value=456, dest=IRvar('x2')),
            Call(fun=IRvar('print_int'), args=[IRvar('x2')], dest=IRvar('x3'))
        ]

#有问题
    def test_negate_and_print(self) -> None:
        source_code = "var x = 3; -x"
        ast_root = parse(tokenize(source_code))
        print(ast_root)
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [
           LoadIntConst(value=3, dest=IRvar('x1')),
           Copy(source=IRvar('x1'), dest=IRvar('x2')),
           Call(fun=IRvar('unary_-'), args=[IRvar('x2')], dest=IRvar('x3')),
           Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x4'))
       ]

    def test_print_int_division(self) -> None:
        source_code = "print_int(5 / 4)"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
    
        assert ir_instructions == [
            LoadIntConst(value=5, dest=IRvar('x1')),
            LoadIntConst(value=4, dest=IRvar('x2')),
            Call(fun=IRvar('/'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
            Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x4'))
        ]

    def test_unary_minus(self) -> None:
        source_code = "-3"
        ast_root = parse(tokenize(source_code))
        #print(ast_root)  # 调试用，打印 AST 结构
        ir_instructions = generate_ir(ast_root)
    
        assert ir_instructions == [
           LoadIntConst(value=3, dest=IRvar('x1')),  # 加载整数 3
            Call(fun=IRvar('unary_-'), args=[IRvar('x1')], dest=IRvar('x2')),  # 取负操作
            Call(fun=IRvar('print_int'), args=[IRvar('x2')], dest=IRvar('x3'))  # 打印结果
        ]

    def test_blocks_1(self) -> None:
        source_code = "{ true; 1 + 2 } + 3"
        ast_root = parse(tokenize(source_code))
        print(tokenize(source_code))
        print(ast_root)
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadBoolConst(value=True, dest=IRvar('x1')),
                                   LoadIntConst(value=1, dest=IRvar('x2')),
                                   LoadIntConst(value=2, dest=IRvar('x3')),
                                   Call(fun=IRvar('+'), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')),
                                   LoadIntConst(value=3, dest=IRvar('x5')),
                                   Call(fun=IRvar('+'), args=[IRvar('x4'), IRvar('x5')], dest=IRvar('x6')),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x6')], dest=IRvar('x7'))]
        


    def test_binary_op_addition1(self) -> None:
        source_code = "1"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')), 
                                   Call(fun=IRvar('print_int'), args=[IRvar('x1')], dest=IRvar('x2'))]

    def test_binary_op_addition2(self) -> None:
        source_code = "1 + 2"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x4'))]

        source_code = "1 + 2 * 3"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   LoadIntConst(value=3, dest=IRvar('x3')),
                                   Call(fun=IRvar('*'), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x4')], dest=IRvar('x5')),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x5')], dest=IRvar('x6'))]

    # def test_binary_if_then_else1(self) -> None:
    #     source_code = "if 1 < 2 then 3 else 4"
    #     ast_root = parse(tokenize(source_code))
    #     ir_instructions = generate_ir(ast_root)
    #     assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
    #                                LoadIntConst(value=2, dest=IRvar('x2')),
    #                                Call(fun=IRvar('<'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
    #                                CondJump(cond=IRvar('x3'), then_label=Label(name='then'), else_label=Label(name='else')),
    #                                Label(name='then'),
    #                                LoadIntConst(value=3, dest=IRvar('x4')),
    #                                Copy(source=IRvar('x4'), dest=IRvar('x5')),
    #                                Jump(label=Label(name='if_end')),
    #                                Label(name='else'),
    #                                LoadIntConst(value=4, dest=IRvar('x6')),
    #                                Copy(source=IRvar('x6'), dest=IRvar('x5')),
    #                                Label(name='if_end'),
    #                                Call(fun=IRvar('print_int'), args=[IRvar('x5')], dest=IRvar('x7'))]

    # def test_binary_if_then_else2(self) -> None:
    #     source_code = "1 + if 2 < 3 then 4 * 5 else 6 * 7"
    #     ast_root = parse(tokenize(source_code))
    #     ir_instructions = generate_ir(ast_root)

    #     assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
    #                                LoadIntConst(value=2, dest=IRvar('x2')),
    #                                LoadIntConst(value=3, dest=IRvar('x3')),
    #                                Call(fun=IRvar('<'), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')),
    #                                CondJump(cond=IRvar('x4'), then_label=Label(name='then'), else_label=Label(name='else')),
    #                                Label(name='then'),
    #                                LoadIntConst(value=4, dest=IRvar('x5')),
    #                                LoadIntConst(value=5, dest=IRvar('x6')),
    #                                Call(fun=IRvar('*'), args=[IRvar('x5'), IRvar('x6')], dest=IRvar('x7')),
    #                                Copy(source=IRvar('x7'), dest=IRvar('x8')),
    #                                Jump(label=Label(name='if_end')),
    #                                Label(name='else'),
    #                                LoadIntConst(value=6, dest=IRvar('x9')),
    #                                LoadIntConst(value=7, dest=IRvar('x10')),
    #                                Call(fun=IRvar('*'), args=[IRvar('x9'), IRvar('x10')], dest=IRvar('x11')),
    #                                Copy(source=IRvar('x11'), dest=IRvar('x8')),
    #                                Label(name='if_end'),
    #                                Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x8')], dest=IRvar('x12')),
    #                                Call(fun=IRvar('print_int'),args=[IRvar('x12')], dest=IRvar('x13'))]

    # def test_binary_if_then_else3(self) -> None:
    #     source_code = "1 + if 2 < 3 then 4 * 5 "
    #     ast_root = parse(tokenize(source_code))
    #     ir_instructions = generate_ir(ast_root)
    #     print(ir_instructions)
    #     assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
    #                                LoadIntConst(value=2, dest=IRvar('x2')),
    #                                LoadIntConst(value=3, dest=IRvar('x3')),
    #                                Call(fun=IRvar('<'), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')),
    #                                CondJump(cond=IRvar('x4'), then_label=Label(name='then'), else_label=Label(name='if_end')),
    #                                Label(name='then'),
    #                                LoadIntConst(value=4, dest=IRvar('x5')),
    #                                LoadIntConst(value=5, dest=IRvar('x6')),
    #                                Call(fun=IRvar('*'), args=[IRvar('x5'), IRvar('x6')], dest=IRvar('x7')),
    #                                Copy(source=IRvar('x7'), dest=IRvar('x8')),
    #                                Jump(label=Label(name='if_end')),
    #                                Label(name='if_end'),
    #                                Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x8')], dest=IRvar('x9')),
    #                                Call(fun=IRvar('print_int'),args=[IRvar('x9')], dest=IRvar('x10'))]




class IRGeneratorTestCase(unittest.TestCase):
    def test_literal_int(self) -> None:
        source_code = "42"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)

        assert ir_instructions == [LoadIntConst(value=42, dest=IRvar('x1')), 
                                   Call(fun=IRvar('print_int'), args=[IRvar('x1')], dest=IRvar('x2'))]



    def test_literal_bool(self) -> None:
        source_code = "true"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadBoolConst(value=True, dest=IRvar('x1')),
                                   Call(fun=IRvar('print_bool'), args=[IRvar('x1')], dest=IRvar('x2'))]

    def test_binary_op_addition(self) -> None:
        source_code = "1 + 2"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x4'))]


    # def test_if_true_then_42_else_43(self) -> None:
    #     source_code = "if true then 42 else 43"
    #     ast_root = parse(tokenize(source_code))
    #     print(ast_root)
    #     ir_instructions = generate_ir(ast_root)
    #     print(ir_instructions)
    #     assert ir_instructions == [LoadBoolConst(value=True, dest=IRvar('x1')),
    #                                CondJump(cond=IRvar('x1'), then_label=Label(name='then'),else_label=Label(name='else')),
    #                                Label(name='then'),
    #                                LoadIntConst(value=42, dest=IRvar('x2')),
    #                                Copy(source=IRvar('x2'), dest=IRvar('x3')),
    #                                Jump(label=Label(name='if_end')),
    #                                Label(name='else'),
    #                                LoadIntConst(value=43, dest=IRvar('x4')),
    #                                Copy(source=IRvar('x4'), dest=IRvar('x3')),
    #                                Label(name='if_end'),
    #                                Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x5'))]


# class TestIRGeneratorScopes(unittest.TestCase):
#     #有问题
#     def test_nested_scope_var_decl_with_assignment(self) -> None:

#         source_code = "{ var x: Int = 42 ; { var x: Int = 1 ;} x}"
#         ast_root = parse(tokenize(source_code))
#         ir_instructions = generate_ir(ast_root)
#         assert ir_instructions ==[LoadIntConst(value=42, dest=IRvar("x1")), 
#                                   Copy(source=IRvar("x1"), dest=IRvar("x2")),  # 外层x赋值
#                                   LoadIntConst(value=1, dest=IRvar("x3")), 
#                                   Copy(source=IRvar('x3'), dest=IRvar('x4')),
#                                   Call(fun=IRvar('print_int'), args=[IRvar('x6')], dest=IRvar('x7'))]



if __name__ == '__main__':
    unittest.main()

