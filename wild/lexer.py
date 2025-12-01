from wild.tokens import *

import re

__all__ = ("Lexer",)

class Lexer:
    def __init__(self, source: str) -> None:
        self.source: str = source

        regex_parts = [f"(?P<{token.name}>{token.value})" for token in TokenType]
        self.regex: re.Pattern[str] = re.compile('|'.join(regex_parts))
    
    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        line, column = 1, 1

        for rxmatch in self.regex.finditer(self.source):
            kind_name: str = rxmatch.lastgroup
            value: str = rxmatch.group()

            if kind_name in ("WHITESPACE", "COMMENT"):
                column += len(value)
                continue

            if kind_name == "NEWLINE":
                line += 1
                column += 1
                continue

            token: Token = Token(TokenType[kind_name], value, line, column)
            tokens.append(token)
            column += len(value)
        
        return tokens