from wild.type.base import RuntimeType
from wild.type.boolean import Boolean
from dataclasses import dataclass

__all__ = (
    "Float",
    "Integer",
)

class Numeric(RuntimeType):
    def _get_val(self, other): return other.value if isinstance(other, Numeric) else other
    def _coerce(self, result): return Float(result) if isinstance(result, float) else Integer(result)
    def __add__(self, o): return self._coerce(self.value + self._get_val(o))
    def __sub__(self, o): return self._coerce(self.value - self._get_val(o))
    def __mul__(self, o): return self._coerce(self.value * self._get_val(o))
    def __truediv__(self, o): return Float(self.value / self._get_val(o))
    def __mod__(self, o): return Integer(int(self.value % self._get_val(o)))
    def __lt__(self, o): return Boolean(self.value < self._get_val(o))
    def __gt__(self, o): return Boolean(self.value > self._get_val(o))
    def __le__(self, o): return Boolean(self.value <= self._get_val(o))
    def __ge__(self, o): return Boolean(self.value >= self._get_val(o))
    def __eq__(self, o): return Boolean(self.value == self._get_val(o))
    def __ne__(self, o): return Boolean(self.value != self._get_val(o))

@dataclass
class Float(Numeric):
    """64-bit floating decimal number."""

    value: float

@dataclass
class Integer(Numeric):
    """32-bit, signed integer."""
    
    value: int