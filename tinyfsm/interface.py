import dataclasses
from typing import Callable, Generic, Protocol, TypeVar

from . import _export_list

__all__ = export = _export_list.ExportList()  # type: ignore

T = TypeVar("T")

Tc = TypeVar("Tc", contravariant=True)


@export
@dataclasses.dataclass
class Traversal(Generic[T]):
    """Object for creating state traversal definitions.

    This is the basic building block for creating state machines. It is used to
    declare source and destination states, and a traversal function that is
    used to check if current event should cause traversal to the destination
    state.
    """

    #: Source event name.
    src: str

    #: Destination event name.
    dest: str

    #: Condition function.
    #:
    #: It will be called with the current event and if the return value is #:
    #: ``True`` then state traversal from :attr:`src` to :attr:`dest`).is
    #: performed. If the current state is not the source state, then the
    #: function will not be called.
    cond: Callable[[T], bool]


@export
class StateMachineListener(Protocol, Generic[Tc]):
    """State machine listener protocol.

    Defines interface to be used by custom state machine listeners receiving
    notifications about event objects and state traversals. Implementations may
    use this to add events to internal buffers, queues etc.
    """

    def on_state_change(self, event: Tc, prev_state: str, current_state: str):
        """Triggered when *event* caused state traversal from *prev_state* to
        *current_state*.

        This will only be called if one of state traversal condition functions
        returned ``True``.

        :param event:
            The event that caused traversal.

        :param prev_state:
            The name of a previous state.

        :param current_state:
            The name of a current state.
        """
        ...

    def on_dispatch_done(self, event: Tc, current_state: str):
        """Triggered when event dispatching ends.

        This method will be called for every successfully accepted event even
        if there was no state change.

        :param event:
            The event object.

        :param current_state:
            The name of the state the state machine was left in once *event*
            was processed.
        """
        ...
