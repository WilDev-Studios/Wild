from __future__ import annotations

from wild.errors import *
from wild.nodes.base import *
from wild.nodes.expression import *
from wild.nodes.statement import *
from wild.natives.base import NativeFunction, NativeMethod, UserFunction, RuntimeFunction
from wild.natives.print import native_print
from wild.signals import *
from wild.tokens import *
from wild.type.base import RuntimeType
from wild.type.empty import Void
from wild.type.numeric import Integer
from typing import Callable

__all__ = ("Interpreter",)

class Interpreter:
    def __init__(self) -> None:
        self.globals: dict[str, RuntimeType | FunctionDefinition] = {
            "print": NativeFunction(1, native_print)
        }
        self.env_stack: list[dict[str, RuntimeType | FunctionDefinition]] = [self.globals]

    @property
    def env(self) -> dict[str, RuntimeType]: return self.env_stack[-1]

    def generic_visit(self, node: ASTNode) -> RuntimeType:
        error: str = f"No visit method for {type(node).__name__}"
        raise InterpreterError(error)

    def lookup_variable(self, name: str) -> RuntimeType:
        for env in reversed(self.env_stack):
            if name in env:
                return env[name]
        
        error: str = f"Undefined variable or function `{name}`"
        raise InterpreterError(error)

    def visit(self, node: ASTNode) -> Callable[[ASTNode], RuntimeType | None]:
        method: str = f"visit_{type(node).__name__}"
        visitor = getattr(self, method, self.generic_visit)

        return visitor(node)
    
    def visit_Assignment(self, node: Assignment) -> None:
        value: RuntimeType = self.visit(node.value)

        for env in reversed(self.env_stack):
            if node.target.name in env:
                env[node.target.name] = value
                return
        
        error: str = f"Cannot assign to undefined variable `{node.target.name}`"
        raise InterpreterError(error)

    def visit_BinaryOperation(self, node: BinaryOperation) -> RuntimeType:
        left: RuntimeType = self.visit(node.left)
        right: RuntimeType = self.visit(node.right)
        operator: TokenType = node.operator

        match operator:
            case TokenType.PLUS: return left + right
            case TokenType.MINUS: return left - right
            case TokenType.MULT: return left * right
            case TokenType.DIV: return left / right
            case TokenType.MOD: return left % right
            case TokenType.EQUAL: return left == right
            case TokenType.NOT_EQ: return not (left == right)
            case TokenType.LESS: return left < right
            case TokenType.GREATER: return left > right
            case TokenType.LESS_EQ: return left <= right
            case TokenType.GREATER_EQ: return left >= right
            case TokenType.AND: return left & right
            case TokenType.OR: return left | right
            case _:
                error: str = f"Unknown operator {operator}"
                raise InterpreterError(error)

    def visit_Block(self, node: Block) -> None:
        for statement in node.statements:
            self.visit(statement)

    def visit_Break(self, _: Break) -> None: raise BreakSignal()
    def visit_Continue(self, _: Continue) -> None: raise ContinueSignal()

    def visit_For(self, node: For) -> RuntimeType:
        self.env_stack.append({})

        try:
            if node.initializer:
                self.visit(node.initializer)
            
            while True:
                condition_value: RuntimeType = self.visit(node.condition)
                if not condition_value.value:
                    break

                try:
                    self.visit(node.body)
                except BreakSignal: break
                except ContinueSignal: ...

                if node.increment:
                    self.visit(node.increment)
        finally:
            self.env_stack.pop()
        
        return Void()

    def visit_FunctionCall(self, node: FunctionCall) -> RuntimeType:
        callee: ASTNode | RuntimeType = self.lookup_variable(node.name)

        if not isinstance(callee, RuntimeFunction):
            error: str = f"Can only call functions, got {callee}."
            raise InterpreterError(error)
        
        if len(node.arguments) != callee.arity():
            error: str = f"Expected {callee.arity()} argument{'s' if callee.arity() > 1 else ''}, got {len(node.arguments)}"
            raise ArgumentCountError(error)
        
        arguments: list[ASTNode] = [self.visit(argument) for argument in node.arguments]
        return callee.call(self, arguments)

    def visit_FunctionDefinition(self, node: FunctionDefinition) -> None:
        function_object: UserFunction = UserFunction(node)
        self.globals[node.name] = function_object

    def visit_If(self, node: If) -> None:
        condition: RuntimeType = self.visit(node.condition)

        if condition.value:
            self.visit(node.branch_true)
        elif node.branch_false:
            self.visit(node.branch_false)

    def visit_Literal(self, node: Literal) -> RuntimeType:
        return node.value

    def visit_MethodCall(self, node: MethodCall) -> RuntimeType:
        obj_instance: RuntimeType = self.visit(node.obj)

        if hasattr(obj_instance, "get_method"):
            method_obj: NativeMethod = obj_instance.get_method(node.name)
        else:
            error: str = f"{obj_instance.__class__.__name__} has no method \"{node.name}\""
            raise ExistenceError(error)
        
        if not isinstance(method_obj, RuntimeFunction):
            error: str = f"Property \"{node.name}\" is not callable"
            raise CallError(error)
        
        args: list[RuntimeType] = [self.visit(arg) for arg in node.arguments]
        return method_obj.call(self, args)

    def visit_Postfix(self, node: Postfix) -> RuntimeType:
        if not isinstance(node.target, Variable):
            error: str = "Postfix target must be a variable"
            raise InterpreterError(error)
        
        variable_name: str = node.target.name
        old_value: Integer = self.lookup_variable(variable_name)

        if node.operator == TokenType.PLUS_PLUS:
            new_value: Integer = Integer(old_value.value + 1)
        elif node.operator == TokenType.MINUS_MINUS:
            new_value: Integer = Integer(old_value.value - 1)
        else:
            error: str = f"Unknown postfix operator: {node.operator}"
            raise InterpreterError(error)
        
        for env in reversed(self.env_stack):
            if variable_name in env:
                env[variable_name] = new_value
                break

        return old_value

    def visit_Program(self, node: Program) -> RuntimeType:
        for statement in node.statements:
            if isinstance(statement, FunctionDefinition):
                self.visit(statement)
        
        for statement in node.statements:
            if not isinstance(statement, FunctionDefinition):
                self.visit(statement)
        
        if "main" not in self.globals:
            error: str = "Entry function \"main\" must be defined"
            raise InterpreterError(error)

        call_main: FunctionCall = FunctionCall("main", [])
        main_result: RuntimeType = self.visit(call_main)
    
        if isinstance(main_result, Integer):
            return main_result.value
        else:
            error: str = "Entry function \"main\" must return Int"
            raise ReturnTypeError(error)

    def visit_Return(self, node: Return) -> RuntimeType:
        value: RuntimeType = self.visit(node.value) if node.value else Void()
        raise ReturnSignal(value)

    def visit_UnaryOperation(self, node: UnaryOperation) -> RuntimeType:
        value: RuntimeType = self.visit(node.operand)

        match node.operator:
            case TokenType.MINUS: return value * Integer(-1)
            case TokenType.NOT: return not value
        
        return value

    def visit_Variable(self, node: Variable) -> RuntimeType:
        for env in reversed(self.env_stack):
            if node.name in env:
                return env[node.name]
        
        error: str = f"Undefined variable `{node.name}`"
        raise InterpreterError(error)
    
    def visit_VariableDeclaration(self, node: VariableDeclaration) -> None:
        value: RuntimeType = self.visit(node.value)
        self.env[node.name] = value
    
    def visit_While(self, node: While) -> None:
        while self.visit(node.condition).value:
            try:
                self.visit(node.body)
            except BreakSignal: break
            except ContinueSignal: continue