from wild.nodes.base import ASTNode
from wild.nodes.expression import Variable
from dataclasses import dataclass

__all__ = (
    "Assignment",
    "Block",
    "Break",
    "Continue",
    "For",
    "FunctionDefinition",
    "If",
    "Program",
    "Return",
    "VariableDeclaration",
    "While",
)

@dataclass
class Assignment(ASTNode):
    target: Variable
    value: ASTNode

@dataclass
class Block(ASTNode):
    statements: list[ASTNode]

class Break(ASTNode):...
class Continue(ASTNode):...

@dataclass
class For(ASTNode):
    initializer: ASTNode
    condition: ASTNode
    increment: ASTNode
    body: ASTNode

@dataclass
class FunctionDefinition(ASTNode):
    name: str
    parameters: list[tuple[str, str]]
    body: Block
    return_type: str

@dataclass
class If(ASTNode):
    condition: ASTNode
    branch_true: Block
    branch_false: Block | None = None

@dataclass
class Program(ASTNode):
    statements: list[ASTNode]

@dataclass
class Return(ASTNode):
    value: ASTNode | None

@dataclass
class VariableDeclaration(ASTNode):
    name: str
    type_name: str
    value: ASTNode

@dataclass
class While(ASTNode):
    condition: ASTNode
    body: Block