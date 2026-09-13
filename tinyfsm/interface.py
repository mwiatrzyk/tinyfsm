import dataclasses
from typing import Callable, Generic, Protocol, TypeVar

from . import _export_list

__all__ = export = _export_list.ExportList()  # type: ignore # noqa: PLE0605

T = TypeVar("T")

T_contra = TypeVar("T_contra", contravariant=True)


@export
@dataclasses.dataclass
class Traversal(Generic[T]):
    """Object for creating state traversal definitions.

    This is the basic building block for creating state machines. It is used to
    declare source and destination states, and a traversal function that is
    used to check if current event should cause traversal to the destination
    state.
    """

    #: Source state name.
    source_state: str

    #: Target state name.
    target_state: str

    #: The function to be called for each input when current state is
    #: :attr:`source_state`; if the function returns ``True``, current state is
    #: changed to :attr:`target_state`.
    traverse_func: Callable[[T], bool]


@export
class StateMachineListener(Protocol, Generic[T_contra]):
    """State machine listener protocol.

    Defines interface to be used by custom state machine listeners receiving
    notifications about event objects and state traversals. Implementations may
    use this to add events to internal buffers, queues etc.
    """

    def on_state_change(self, input: T_contra, prev_state: str, current_state: str):
        """Triggered when *input* caused state traversal from *prev_state* to
        *current_state*.

        This will only be called if one of traverse functions (see
        :attr:`Traversal.traverse_func`) returned ``True``. If traversal causes
        landing back in the same state, then both *prev_state* and
        *current_state* are equal.

        :param input:
            The input that caused traversal.

        :param prev_state:
            The name of a previous state.

        :param current_state:
            The name of a current state (can be same as *prev_state*).
        """
        ...

    def on_dispatch_done(self, input: T_contra, current_state: str):
        """Triggered when input dispatching ends.

        This method will be called for every successfully accepted input even
        if there was no state change.

        :param input:
            The input object.

        :param current_state:
            The name of the state the state machine was left in once *event*
            was processed.
        """
        ...
