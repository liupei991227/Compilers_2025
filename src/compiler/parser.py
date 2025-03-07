from compiler.tokenizer import Token
import compiler.ast as ast
from compiler.types import Int, Bool, Type, PointerType

left_associative_binary_operators = [
    ['or'],
    ['and'],
    ['==', '!='],
    ['<', '<=', '>', '>='],
    ['+', '-'],
    ['*', '/','%'],
    ['not'],
]


def parse(tokens: list[Token], right_associative: bool = False) -> ast.Expression:
    pos = 0
    scopes: list[set[str]] = [set()]

    def peek() -> Token:     #查看当前位置的token
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(
                loc=tokens[-1].loc,
                type="end",
                text="",
            )
    

    def consume(expected: str | list[str] | None = None) -> Token:  #消耗当前位置的token
        nonlocal pos
        token = peek()
        if expected is not None:
            if isinstance(expected, str):
                if token.text != expected:
                    raise Exception(f'expected "{expected}"')  # 单个预期值不匹配
            elif isinstance(expected, list):
                if token.text not in expected:
                    # 修正：移除错误信息前的多余空格，改为 "expected one of:"
                    comma_separated = ", ".join([f'"{e}"' for e in expected])
                    raise Exception(f'expected one of: {comma_separated}')  # 列表值不匹配
        #if isinstance(expected, str) and token.text != expected:
        #    raise Exception(f'expected "{expected}"')
        #if isinstance(expected, list) and token.text not in expected:
        #    comma_separated = ", ".join([f'"{e}"' for e in expected])
        #    raise Exception(f' expected one of: {comma_separated}')
        pos += 1
        return token
    

    def parse_int_literal() -> ast.Literal: #解析整数
        if peek().type != 'int_literal':
            raise Exception(f'expected an integer literal')
        token = consume()

        return ast.Literal(int(token.text))
    
    def parse_bool_literal() -> ast.Literal:
        if peek().type != 'bool_literal':
            raise Exception(f'{peek().loc}: expected an integer literal')
        token = consume()
        value = token.text.lower() == 'true'
        return ast.Literal(value=value)
    

    def parse_identifier() -> ast.Identifier:  #解析标识符（加减乘除等操作符）
        if peek().type != 'identifier':
            raise Exception(f'expected an identifier')
        token = consume()
        return ast.Identifier(str(token.text))
    

    def parse_factor() -> ast.Expression:  #解析因子
        if peek().text == '{':
            return parse_block()
        elif peek().text == '(':
            return parse_parenthesized()
        elif peek().text == 'if':
            return parse_if_expression()
        elif peek().type == 'int_literal':
            next_pos = pos +1
            if next_pos < len(tokens) and tokens[next_pos].type == 'int_literal':
                raise Exception(f"Unexpected token '{peek().text}' after integer literal at {peek().loc}, expected operator or separator")
            return parse_int_literal()
        elif peek().text == 'while':
            return parse_while_expr()
        elif peek().type == 'bool_literal':
            return parse_bool_literal()
        
        elif peek().type == 'identifier':
            next_pos = pos +1
            if next_pos < len(tokens) and tokens[next_pos].text == '(':
                return parse_function_call()
            else:
                return parse_identifier()
            
        if peek().type in ['int_literal', 'bool_literal', 'identifier']:
            raise Exception(f"Unexpected token '{peek().text}' after identifier at {peek().loc}, expected operator or separator")

        else:
            raise Exception(f'expected "(", an integer literal or an identifier')
        

    def parse_parenthesized() -> ast.Expression:  #解析括号
        consume('(')
        expr = parse_expression()
        if peek().text != ')':
            raise Exception(f'Unexpected token "{peek().text}", expected ")"')
        consume(')')
        if peek().text == ')':
            raise Exception(f'Unexpected extra ")" at {peek().loc}')
        return expr



    def parse_term() -> ast.Expression:  #解析项
        left = parse_factor()
        while peek().text in ['*', '/']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    # 根据 right_associative 参数选择解析函数
    def parse_expression() -> ast.Expression:
        if right_associative:
            return parse_expression_right()
        else:
            return parse_expression_original()



    def parse_expression_original() -> ast.Expression:   #解析表达式
        # if peek().text == 'if':  # 先检查是否是 if 语句
        #     return parse_if_expression()
        if peek().text == 'var':  # 先检查是否是 var 语句
            return parse_variable_declaration()
        print(peek().text)
        if peek().text == '{':  # 确保 `{}` 代码块在解析表达式时被正确解析
            return parse_block()
        #if peek().type == 'bool_literal':
        #    return parse_bool_literal()
        next_pos = pos +1
        if next_pos < len(tokens) and tokens[next_pos].text == '=':
            return parse_assignment()
        left = parse_with_precedence(0)


        return left

    
    def parse_if_expression() -> ast.Expression: #解析if表达式
        consume('if')
        condition = parse_expression()
        consume('then')
        if peek().text == 'var':
            raise Exception(f'Unexpected "var" after "then": "then" must be followed by an expression')

        then_branch = parse_expression()
        else_branch = None
        if peek().text == 'else':
            consume('else')
            else_branch = parse_expression()
        return ast.IfExpression(condition, then_branch, else_branch)
    

    def parse_function_call() -> ast.FunctionCall:
        """Parse a function call like f(x, y + z)."""
        name_token = consume()
        consume('(')  
        args = []
    
        if peek().text != ')':  
            while True:
                args.append(parse_expression())  
                if peek().text == ',':
                    consume(',')  
                else:
                    break

        consume(')') 
        return ast.FunctionCall(ast.Identifier(name_token.text), args)
    

    def parse_expression_right() -> ast.Expression:
        """Parse an expression, handling right-associative assignment."""
        return parse_assignment()
    

    
    def parse_assignment() -> ast.Expression:
        """Parse assignment expressions (right-associative)."""
        left = parse_with_precedence(0)  
        if peek().text == '=':
            consume('=')
            right = parse_assignment()  
            if not isinstance(left, ast.Identifier):
                raise Exception("Assignment target must be an identifier")
            return ast.Assignment(left, right)
        return left
    

    def parse_with_precedence(level: int) -> ast.Expression:
        if level >= len(left_associative_binary_operators):
            return parse_unary()

        if right_associative:
        # 对于右结合，采用 if+递归（而不是 while 循环）的方式
            left = parse_with_precedence(level + 1)
            if peek().text in left_associative_binary_operators[level]:
                operator_token = consume()
                operator = operator_token.text
                # 注意这里递归调用时仍使用当前级别
                right = parse_with_precedence(level)
                left = ast.BinaryOp(left, operator, right)
            return left
        else:
            # 维持原来的左结合处理逻辑
            left = parse_with_precedence(level + 1)
            while peek().text in left_associative_binary_operators[level]:
                operator_token = consume()
                operator = operator_token.text
                right = parse_with_precedence(level + 1)
                left = ast.BinaryOp(left, operator, right)
            return left
    


    def parse_unary() -> ast.Expression:
        """Parse unary expressions: `not x` or `-x`."""
        if peek().text in ['not', '-']:
            operator_token = consume()
            operator = operator_token.text
            operand = parse_unary()  # Allow chaining (e.g., `not not x`)
            return ast.UnaryOp(operator, operand)
        return parse_factor()
    


    def parse_block() -> ast.Expression:
        nonlocal scopes
        scopes.append(set()) 
        consume('{')
        expressions = []
        result_expression: ast.Optional[ast.Expression] = None

        while peek().text != '}':
            if peek().text == 'return':
                consume('return')
                result_expression = parse_expression()
                if peek().text == ';':
                    consume(';')

            elif peek().text in ['if', 'while', '{']:
                  # Starting a new block or control structure
                expr = parse_expression()
                #expressions.append(expr)
                if peek().text == '}':
                    result_expression = expr
                else:
                    expressions.append(expr)

                    if peek().text == ';':  
                        consume(';')
            else:
                if peek().text == 'var':
                    expr = parse_variable_declaration()
                else:
                    expr = parse_expression()
                
                is_block = isinstance(expr, ast.Block)

                if peek().text == ';':
                    consume(';')
                    expressions.append(expr)
                    if pos < len(tokens) and tokens[pos].text == 'var':
                        raise Exception(f"Unexpected 'var' after ';'")
                elif peek().text == '}':
                    result_expression = expr
                elif is_block and peek().text in ['if', 'while', '{']:  # No semicolon required before these
                    expressions.append(expr)
                else:
                    raise Exception(f"{peek()}: Expected ';' or '}}' but found '{peek().text}'")
            
        consume('}')
        scopes.pop() 

        block_expr: ast.Expression = ast.Block(expressions=expressions, result_expression=result_expression)

        while peek().text in ['+', '-', '*', '/', '==', '!=', '<', '<=', '>', '>=', 'and', 'or']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_with_precedence(0)  # 继续解析右侧表达式
            block_expr = ast.BinaryOp(left=block_expr, op=operator, right=right)

        return block_expr
    

    def parse_variable_declaration() -> ast.Expression:
        nonlocal scopes
        consume('var')
        name = consume().text

        current_scope = scopes[-1]
        if name in current_scope:
            raise Exception(f"Duplicate variable declaration '{name}' at {consume().text}")
        current_scope.add(name)



        type_annotation = None
        if peek().text == ':':
            consume(':')
            base = consume()
            type_annotation = parse_type_expr(base)
            while peek().text == '*':
                consume('*')
                type_annotation = PointerType(type_annotation)   # multi-layer pointer
        consume('=')
        value = parse_expression()

        return ast.VariableDeclaration(name=ast.Identifier(name), value=value, type_annotation=type_annotation)
        #name = parse_identifier()
        #consume('=')
        #value = parse_expression_right()
        #return ast.VariableDeclaration(name, value)
    
    def parse_top_level() -> ast.Expression:
        expression = []
        while peek().type != 'end':
            if peek().text == 'var':
                expr = parse_variable_declaration()
                expression.append(expr)
            else:
                expr = parse_expression()
                expression.append(expr)
            

            if peek().text == ';':
                consume(';')
                
                if peek().type == 'end' and expression:
                    return ast.Block(expressions=expression, result_expression=None)

        if not expression:
            return ast.Block([], None)
        elif len(expression) == 1:
            return expression[0]
        else:
            return ast.Block(
                expressions=expression[:-1],
                result_expression=expression[-1]
            )
        #     else:
        #     # 如果没有分号，说明它是 result，而不是普通的表达式
        #         if len(expression) > 1:
        #             return ast.Block(expression[:-1], expression[-1])
        #         else:
        #             return expr if len(expression) == 1 else ast.Block([], None)

        # return ast.Block(expressions=expression, result_expression=None)

    
    
    def parse_while_expr() -> ast.Expression:
        name_token = consume('while')  # Consume the 'while' keyword
        # function_location = name_token.loc
        condition = parse_expression()
        consume('do')  # Consume the 'do' keyword
        body = parse_expression()
        return ast.WhileExpr(condition=condition, body=body)
    

    def parse_type_expr(token: Token) -> Type:

        if token.text == "Int":
            return Int()
        elif token.text == "Bool":
            return Bool()
        else:
            raise Exception(f"Unknown type {token.text}")
        

        
    result = parse_top_level()
    if pos != len(tokens):
        remaining_token = tokens[pos]
        raise Exception(f"{remaining_token.loc}: Unexpected token '{remaining_token.text}'")

    return result




