from wild.nodes.statement import FunctionDefinition
from wild.signals import ReturnSignal
from wild.type.base import RuntimeType
from wild.type.empty import Void
from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from interpreter import Interpreter

class RuntimeFunction(ABC):
    @abstractmethod
    def arity(self) -> int:...
    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list):...

class UserFunction(RuntimeFunction):
    def __init__(self, declaration: FunctionDefinition) -> None:
        self.declaration: FunctionDefinition = declaration
    
    def __repr__(self) -> str: return f"<fn {self.declaration.name}>"
    def arity(self) -> int: return len(self.declaration.parameters)
    def call(self, interpreter: Interpreter, arguments: list) -> RuntimeType:
        environment: dict[str, RuntimeType] = {}

        for (_, parameter_name), argument in zip(self.declaration.parameters, arguments):
            environment[parameter_name] = argument
        
        interpreter.env_stack.append(environment)
        try:
            interpreter.visit(self.declaration.body)
        except ReturnSignal as signal:
            return signal.value
        finally:
            interpreter.env_stack.pop()
        
        return Void()

class NativeFunction(RuntimeFunction):
    def __init__(self, arity: int, func: Callable[[Interpreter, list], RuntimeType]) -> None:
        self._arity: int = arity
        self._func: Callable[[Interpreter, list], RuntimeType] = func
    
    def __repr__(self) -> str: return "<builtin>"
    def arity(self) -> int: return self._arity
    def call(self, interpreter: Interpreter, arguments: list) -> RuntimeType: return self._func(interpreter, arguments)

class NativeMethod(RuntimeFunction):
    def __init__(self, instance: RuntimeType, arity: int, func: Callable[[Interpreter, RuntimeType, list], RuntimeType]) -> None:
        self._instance: RuntimeType = instance
        self._arity: int = arity
        self._func: Callable[[Interpreter, RuntimeType, list], RuntimeType] = func
    
    def __repr__(self) -> str: return "<builtin>"
    def arity(self) -> int: return self._arity
    def call(self, interpreter: Interpreter, arguments: list) -> RuntimeType: return self._func(interpreter, self._instance, arguments)