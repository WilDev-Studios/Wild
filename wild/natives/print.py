from __future__ import annotations

from wild.type.base import RuntimeType
from wild.type.empty import Void
from wild.type.strings import String
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wild.interpreter import Interpreter

def native_print(_: Interpreter, arguments: list[RuntimeType]) -> Void:
    """
    ;;p:message:Object | Object[]
    Output a message to the terminal.
    
    Parameters
    ----------
    message : Object | Object[]
        The message to display.
    """

    raw_values: list[str] = []
    for argument in arguments:
        if isinstance(argument, String):
            raw_values.append(argument.value)
        else:
            raw_values.append(str(argument.value))
    
    print(' '.join(raw_values))
    return Void()