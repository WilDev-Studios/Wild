from wild.nodes.base import ASTNode
from wild.tokens import *
from wild.type.base import RuntimeType
from dataclasses import dataclass

__all__ = (
    "BinaryOperation",
    "FunctionCall",
    "Get",
    "Literal",
    "MethodCall",
    "Postfix",
    "UnaryOperation",
    "Variable",
)

@dataclass
class BinaryOperation(ASTNode):
    left: ASTNode
    operator: TokenType
    right: ASTNode

@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: list[ASTNode]

@dataclass
class Get(ASTNode):
    obj: ASTNode
    name: str

@dataclass
class Literal(ASTNode):
    value: RuntimeType

@dataclass
class MethodCall(ASTNode):
    obj: ASTNode
    name: str
    arguments: list[ASTNode]

@dataclass
class Postfix(ASTNode):
    target: Variable
    operator: TokenType

@dataclass
class UnaryOperation(ASTNode):
    operator: TokenType
    operand: ASTNode

@dataclass
class Variable(ASTNode):
    name: str