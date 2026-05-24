from typing import Any

from . import _export_list

__all__ = export = _export_list.ExportList()  # type: ignore


@export
class TinyFSMError(Exception):
    """Common base class for all exception this library may raise."""


@export
class EventRejectedError(TinyFSMError):
    """Raised when event was rejected by the state machine.

    Event is rejected only if there was no matching traversal found.
    """

    #: The rejected event object.
    event: Any

    #: The current state name.
    current_state: str

    def __init__(self, event: Any, current_state: str):
        super().__init__()
        self.event = event
        self.current_state = current_state

    def __str__(self) -> str:
        return f"event {self.event!r} was rejected; no traversal found for current state {self.current_state!r}"


@export
class FinalStateNotReached(TinyFSMError):
    """Raised when closing state machine if final state was not reached.

    This means that either the input sequence of event is incomplete, or that
    the state machine definition is malformed and final state is
    unreachable.
    """

    #: The last dispatched event.
    last_event: Any

    #: The name of the final state.
    final_state: str

    #: The name of the current state.
    current_state: str

    def __init__(self, last_event: Any, final_state: str, current_state: str):
        super().__init__()
        self.last_event = last_event
        self.final_state = final_state
        self.current_state = current_state

    def __str__(self) -> str:
        return f"final state {self.final_state!r} was not reached; current state is {self.current_state!r}, last event was {self.last_event!r}"
