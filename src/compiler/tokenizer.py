import re
from dataclasses import dataclass
from typing import List

@dataclass
class SourceLocation:
    row: int
    column: int

@dataclass
class Token:
    loc: SourceLocation
    type:str
    text:str

class Location(SourceLocation):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, SourceLocation):
            return True
        return False

L = Location(row=0, column=0)

def tokenize(source_code: str) -> List[Token]:
    token_specification = [
        ("bool_literal", r'True|true|False|false'),
        ('identifier', r'[a-zA-Z_][a-zA_Z0-9_]*'),
        ('int_literal', r'\b\d+\b'),
        ('comment', r'//.*|#.*'),
        ('operator', r'==|!=|<=|>=|\+|\*|\-|/|=|<|>|%'),
        ('punctuation', r'[(){},;:]'),
        ('SKIP', r'[ \t\n]+'),
        ('NEWLINE', r'\n'),
    ]

    token_regex = '|'.join(f'(?P<{name}>{regex})'for name, regex in token_specification)

    tokens=[]
    line_num = 1       # 当前行号
    line_start = 0   # 当前行的起始位置

    for match in re.finditer(token_regex, source_code):
        type = match.lastgroup # 当前匹配的 token 类型
        assert type is not None, "Unexpected error: type is None."
        text = match.group()
        start = match.start()

        if type == 'NEWLINE':
            line_num += 1
            line_start = match.end()
        elif type == 'SKIP' or type == 'comment':
            # 跳过空白和注释
            continue
        else:
            # 计算列号：当前匹配起始位置相对于当前行的偏移，加1后得到列号（从1开始）
            column = start - line_start + 1
            loc = SourceLocation(row=line_num, column=column)
            tokens.append(Token(loc=loc, type=type, text=text))

    return tokens




