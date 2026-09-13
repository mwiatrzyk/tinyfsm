from collections.abc import Sequence
from typing import Any

from . import _export_list

__all__ = export = _export_list.ExportList()  # type: ignore # noqa: PLE0605


@export
class TinyFSMError(Exception):
    """Common base class for all exception this library may raise."""


@export
class InconsistentDefinitionError(TinyFSMError):
    """Raised when state machine definition is found to be inconsistent.

    This means that no traversal was defined for the current state, i.e. there
    is no next state to move to, no matter what the input will be.
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
        return f"input {self.input!r} was rejected; no next state defined for the current state {self.current_state!r}"


@export
class InputRejectedError(TinyFSMError):
    """Raised when input was rejected by the state machine.

    Input is rejected when it is not possible to deterministically choose the
    next state for the current input.
    """

    #: The rejected input object.
    input: Any

    #: The current state name.
    current_state: str

    #: The candidate state names.
    #:
    #: These are names of the states that are accessible from the current state
    #: given via :attr:`current_state`.
    next_state_candidates: Sequence[str]

    def __init__(self, input: Any, current_state: str, next_state_candidates: Sequence[str]):
        super().__init__()
        self.input = input
        self.current_state = current_state
        self.next_state_candidates = next_state_candidates

    def __str__(self) -> str:
        return (
            f"input {self.input!r} was rejected; "
            f"cannot traverse from {self.current_state!r} to any of: "
            f"{', '.join(repr(x) for x in self.next_state_candidates)}"
        )


@export
class FinalStateNotReached(TinyFSMError):
    """Raised when closing state machine if final state was not reached.

    This usually means that either the input sequence is incomplete and more
    data is required to reach the final state. For example, a final state
    requires text to end with a period, but a period is missing and no more
    characters are fed into the state machine.
    """

    #: The last dispatched input.
    last_input: Any

    #: The name of the final state.
    final_state: str

    #: The name of the current state.
    current_state: str

    #: The candidate state names.
    #:
    #: These are names of the states that are accessible from the current state
    #: given via :attr:`current_state`.
    next_state_candidates: Sequence[str]

    def __init__(self, last_input: Any, final_state: str, current_state: str, next_state_candidates: Sequence[str]):
        super().__init__()
        self.last_input = last_input
        self.final_state = final_state
        self.current_state = current_state
        self.next_state_candidates = next_state_candidates

    def __str__(self) -> str:
        return (
            f"final state {self.final_state!r} was not reached for last input {self.last_input!r}; "
            f"more input data is expected to traverse from {self.current_state!r} "
            f"to any of: {', '.join(repr(x) for x in self.next_state_candidates)}"
        )
