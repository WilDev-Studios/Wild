from dataclasses import dataclass
from wild.type.base import RuntimeType

__all__ = (
    "BreakSignal",
    "ContinueSignal",
    "ReturnSignal",
)

class BreakSignal(Exception):...
class ContinueSignal(Exception):...

@dataclass
class ReturnSignal(Exception):
    value: RuntimeType