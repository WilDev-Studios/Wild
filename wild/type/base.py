from wild.errors import *
from dataclasses import dataclass
from typing import Any

__all__ = ("RuntimeType",)

def validate_arguments(expected: int, types: list[type[RuntimeType]], arguments: list[RuntimeType]) -> None:
    arg_len: int = len(arguments)
    if arg_len != expected:
        error: str = f"Expected {expected} argument{'s' if len(expected) > 1 else ''}, got {arg_len}"
        raise ArgumentCountError(error)
    
    for index, (arg_type, arg) in enumerate(zip(types, arguments)):
        if isinstance(arg, arg_type):
            continue

        error: str = f"Argument #{index + 1} must be {arg_type.__name__}, got {arg.__class__.__name__}"
        raise ArgumentTypeError(error)

@dataclass
class RuntimeType:
    value: Any
    def __repr__(self) -> str: return f"{self.value}"