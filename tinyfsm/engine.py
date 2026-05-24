from typing import Generic, Optional, Sequence, TypeVar

from . import _export_list
from .exc import EventRejectedError, FinalStateNotReached
from .interface import StateMachineListener, Traversal

__all__ = export = _export_list.ExportList()  # type: ignore

T = TypeVar("T")


@export
class StateMachine(Generic[T]):
    """State machine engine.

    Each instance of this class can only parse single chain of events (as it
    keeps the state between :meth:`dispatch` calls) and therefore a brand new
    instance must be created to parse another chain of events.

    You can feed state machine with events by using :meth:`dispatch` method.
    Each dispatched event may cause state traversal, or event rejection (if the
    input chain of events could not be parsed using defined state machine). It
    is recommended, although not required, to call :meth:`close` once all the
    events are dispatched.

    The state machine can also be used as a context manager to automatically
    call :meth:`close` on context exit::

        sm = StateMachine(...)
        with sm:
            for event in sequence_of_events:
                sm.dispatch(event)

    :param definition:
        State machine definition as a sequence of state traversals defined
        using :class:`tinyfsm.interface.Traversal` objects.

    :param listener:
        Instance of :class:`StateMachineListener` protocol.

        This object will receive notifications from the state machine once it
        is processing events.

    :param initial_state:
        The name of the initial state.

        It is required to have at least one initial state name used in the
        state machine definition as a :attr:`tinyfsm.interface.Traversal.src`
        attribute.

    :param final_state:
        The name of the final state.

        It is required to have at least one final state name used in the state
        machine definition as a :attr:`tinyfsm.interface.Traversal.dest`
        attribute.
    """

    def __init__(
        self,
        definition: Sequence[Traversal[T]],
        listener: StateMachineListener[T],
        initial_state: str = "initial",
        final_state: str = "final",
    ):
        self.__traversal_map: dict[str, list[Traversal]] = {}
        has_initial = has_final = False
        for traversal in definition:
            if traversal.src == initial_state:
                has_initial = True
            if traversal.dest == final_state:
                has_final = True
            self.__traversal_map.setdefault(traversal.src, []).append(traversal)
        if not has_initial:
            raise TypeError(f"no initial state found: {initial_state}")
        if not has_final:
            raise TypeError(f"no final state found: {final_state}")
        self.__listener = listener
        self.__initial_state = initial_state
        self.__final_state = final_state
        self.__current_state = self.__initial_state
        self.__last_event: Optional[T] = None

    def __enter__(self) -> "StateMachine":
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is not None:
            return None
        return self.close()

    def dispatch(self, event: T):
        """Dispatch event to the state machine.

        This should be called for each event, and state machine can either
        accept the event, and maybe traverse to a different state in response
        for that event, or reject it by raising :exc:`EventRejectedError`
        exception.

        :param event:
            The event object to dispatch.
        """
        self.__last_event = event
        current_state_traversals = self.__traversal_map.get(self.__current_state)
        if current_state_traversals is None:
            raise EventRejectedError(event, self.__current_state)
        print(current_state_traversals)
        for traversal in current_state_traversals:
            if traversal.cond(event):
                next_state = traversal.dest
                self.__listener.on_state_change(event, self.__current_state, next_state)
                self.__current_state = next_state
                break
        else:
            raise EventRejectedError(event, self.__current_state)
        self.__listener.on_dispatch_done(event, self.__current_state)

    def close(self):
        """Close this state machine.

        This method should be called after event dispatching ends. Its role is
        to check if the final state was reached; if the final state was
        reached, the method silently returns. Otherwise it raises
        :exc:`tinyfsm.exc.FinalStateNotReached` error.
        """
        if not self.is_final():
            raise FinalStateNotReached(self.__last_event, self.__final_state, self.__current_state)

    def is_final(self) -> bool:
        """Check if the final state is reached."""
        return self.__current_state == self.__final_state
