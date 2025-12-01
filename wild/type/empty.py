from wild.type.base import RuntimeType
from dataclasses import dataclass

__all__ = (
    "Null",
    "Void",
)

@dataclass
class Null(RuntimeType):
    """Represents a value that doesn't contain anything."""

    value: None = None

@dataclass
class Void(RuntimeType):
    """No value exists."""

    value: None = None