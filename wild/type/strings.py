from wild.type.base import validate_arguments, RuntimeType
from wild.type.boolean import Boolean
from wild.type.numeric import Float, Integer
from wild.errors import ConversionError
from wild.natives.base import NativeMethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interpreter import Interpreter

__all__ = ("String",)

@dataclass
class String(RuntimeType):
    """Character or string of characters."""

    value: str
    def __add__(self, other: String) -> String: return String(self.value + other.value)
    def __eq__(self, other: RuntimeType) -> Boolean: return Boolean(self.value == other.value)
    def __repr__(self) -> str: return f"\"{self.value}\""

    @staticmethod
    def _capitalize(_: Interpreter, instance: String, args: list[RuntimeType]) -> String:
        validate_arguments(0, [], args)
        return String(instance.value.capitalize())

    @staticmethod
    def _contains(_: Interpreter, instance: String, args: list[RuntimeType]) -> Boolean:
        validate_arguments(1, [String], args)
        return Boolean(args[0].value in instance.value)

    @staticmethod
    def _endsWith(_: Interpreter, instance: String, args: list[RuntimeType]) -> Boolean:
        validate_arguments(1, [String], args)
        return Boolean(instance.value.endswith(args[0].value))

    @staticmethod
    def _find(_: Interpreter, instance: String, args: list[RuntimeType]) -> Integer:
        validate_arguments(1, [String], args)
        return Integer(instance.value.find(args[0].value))

    @staticmethod
    def _isEmpty(_: Interpreter, instance: String, args: list[RuntimeType]) -> Boolean:
        validate_arguments(0, [], args)
        return Boolean(len(instance.value) == 0)
    
    @staticmethod
    def _length(_: Interpreter, instance: String, args: list[RuntimeType]) -> Integer:
        validate_arguments(0, [], args)
        return Integer(len(instance.value))
    
    @staticmethod
    def _replace(_: Interpreter, instance: String, args: list[RuntimeType]) -> String:
        validate_arguments(2, [String, String], args)
        return String(instance.value.replace(args[0].value, args[1].value))

    @staticmethod
    def _substring(_: Interpreter, instance: String, args: list[RuntimeType]) -> String:
        validate_arguments(2, [Integer, Integer], args)
        start: int = args[0].value

        return String(instance.value[start:start + args[1].value])
    
    @staticmethod
    def _startsWith(_: Interpreter, instance: String, args: list[RuntimeType]) -> Boolean:
        validate_arguments(1, [String], args)
        return Boolean(instance.value.startswith(args[0].value))
    
    @staticmethod
    def _toFloat(_: Interpreter, instance: String, args: list[RuntimeType]) -> Float:
        validate_arguments(0, [], args)

        try:
            return Float(float(instance.value))
        except ValueError:
            error: str = f"Cannot convert \"{instance.value}\" to Float"
            raise ConversionError(error)

    @staticmethod
    def _toInteger(_: Interpreter, instance: String, args: list[RuntimeType]) -> Integer:
        validate_arguments(0, [], args)

        try:
            return Integer(int(instance.value))
        except ValueError:
            error: str = f"Cannot convert \"{instance.value}\" to Integer"
            raise ConversionError(error)

    @staticmethod
    def _toLowerCase(_: Interpreter, instance: String, args: list[RuntimeType]) -> String:
        validate_arguments(0, [], args)
        return String(instance.value.lower())
    
    @staticmethod
    def _toUpperCase(_: Interpreter, instance: String, args: list[RuntimeType]) -> String:
        validate_arguments(0, [], args)
        return String(instance.value.upper())

    @staticmethod
    def _trim(_: Interpreter, instance: String, args: list[RuntimeType]) -> String:
        validate_arguments(0, [], args)
        return String(instance.value.strip())

    def get_method(self, name: str) -> NativeMethod | None:
        match name:
            case "capitalize": return NativeMethod(self, 0, String._capitalize)
            case "contains": return NativeMethod(self, 1, String._contains)
            case "endsWith": return NativeMethod(self, 1, String._endsWith)
            case "find": return NativeMethod(self, 1, String._find)
            case "isEmpty": return NativeMethod(self, 0, String._isEmpty)
            case "length": return NativeMethod(self, 0, String._length)
            case "replace": return NativeMethod(self, 2, String._replace)
            case "substring": return NativeMethod(self, 2, String._substring)
            case "startsWith": return NativeMethod(self, 1, String._startsWith)
            case "toFloat": return NativeMethod(self, 0, String._toFloat)
            case "toInteger": return NativeMethod(self, 0, String._toInteger)
            case "toLowerCase": return NativeMethod(self, 0, String._toLowerCase)
            case "toUpperCase": return NativeMethod(self, 0, String._toUpperCase)
            case "trim": return NativeMethod(self, 0, String._trim)
        
        return None