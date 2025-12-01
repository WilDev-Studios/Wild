from wild.type.base import RuntimeType
from dataclasses import dataclass

__all__ = ("Boolean",)

@dataclass
class Boolean(RuntimeType):
    """State of `true`/`false`."""
    
    value: bool
    def __bool__(self) -> Boolean: return self.value
    def __and__(self, other: Boolean) -> Boolean: return Boolean(self.value and other.value)
    def __or__(self, other: Boolean) -> Boolean: return Boolean(self.value or other.value)
    def __invert__(self) -> Boolean: return Boolean(not self.value)