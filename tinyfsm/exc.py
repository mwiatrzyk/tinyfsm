from typing import Any

from . import _export_list

__all__ = export = _export_list.ExportList()  # type: ignore


@export
class TinyFSMError(Exception):
    """Common base class for all exception this library may raise."""


@export
class InputRejectedError(TinyFSMError):
    """Raised when input was rejected by the state machine.

    Input is rejected only if there was no matching traversal found or if all
    traversal functions returned ``False`` for that input.
    """

    #: The rejected input object.
    input: Any

    #: The current state name.
    current_state: str

    def __init__(self, input: Any, current_state: str):
        super().__init__()
        self.input = input
        self.current_state = current_state

    def __str__(self) -> str:
        return f"input {self.input!r} was rejected; no traversal found for current state {self.current_state!r}"


@export
class FinalStateNotReached(TinyFSMError):
    """Raised when closing state machine if final state was not reached.

    This means that either the input sequence is incomplete, or that the state
    machine definition is malformed and final state is unreachable.
    """

    #: The last dispatched input.
    last_input: Any

    #: The name of the final state.
    final_state: str

    #: The name of the current state.
    current_state: str

    def __init__(self, last_input: Any, final_state: str, current_state: str):
        super().__init__()
        self.last_input = last_input
        self.final_state = final_state
        self.current_state = current_state

    def __str__(self) -> str:
        return f"final state {self.final_state!r} was not reached; current state is {self.current_state!r}, last input was {self.last_input!r}"
