from enum import StrEnum
from typing import NamedTuple

__all__ = ("TokenType", "Token",)

class TokenType(StrEnum):
    WHITESPACE   = r"[ \t]+"
    NEWLINE      = r"\n"
    COMMENT      = r"//.*|/\*[\s\S]*?\*/"
    
    BREAK    = "break"
    CONTINUE = "continue"
    ELSE     = "else"
    FALSE    = "false"
    FOR      = "for"
    IF       = "if"
    NULL     = "null"
    RETURN   = "return"
    TRUE     = "true"
    VOID     = "void"
    WHILE    = "while"
    
    TYPE_FLOAT   = "Float"
    TYPE_INT     = "Int"
    TYPE_STRING  = "String"
    TYPE_BOOLEAN = "Boolean"

    FLOAT_LITERAL  = r"\d+\.\d+([eE][+-]?\d+)?"
    INT_LITERAL    = r"\d+"
    STRING_LITERAL = r"\"[^\"\n\r]*\"|'[^\n\r]*'"

    EQUAL        = "=="
    NOT_EQ       = "!="
    PLUS_EQ      = r"\+="
    MINUS_EQ     = r"-="
    MULT_EQ      = r"\*="
    DIV_EQ       = r"/="
    MOD_EQ       = r"%="
    LESS_EQ      = "<="
    GREATER_EQ   = ">="
    AND          = r"&&|and"
    OR           = r"\|\||or"
    PLUS_PLUS    = r"\+\+"
    MINUS_MINUS  = "--"
    
    NOT          = r"!|not"
    PLUS         = r"\+"
    MINUS        = r"-"
    MULT         = r"\*"
    DIV          = r"/"
    MOD          = r"%"
    ASSIGN       = "="
    LESS         = "<"
    GREATER      = ">"

    LPAREN       = r"\("
    RPAREN       = r"\)"
    LBRACE       = r"\{"
    RBRACE       = r"\}"
    LBRACKET     = r"\["
    RBRACKET     = r"\]"
    SEMICOLON    = ";"
    COMMA        = ","
    DOT          = r"\."
    
    IDENTIFIER   = r"[a-zA-Z_][a-zA-Z0-9_]*"

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str: return f"({self.type.name}: {self.value})"