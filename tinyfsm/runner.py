from typing import Generic, Optional, Sequence, TypeVar

from . import _export_list
from .exc import InputRejectedError, FinalStateNotReached
from .interface import StateMachineListener, Traversal

__all__ = export = _export_list.ExportList()  # type: ignore

T = TypeVar("T")


@export
class StateMachineRunner(Generic[T]):
    """State machine runner.

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
            if traversal.source_state == initial_state:
                has_initial = True
            if traversal.target_state == final_state:
                has_final = True
            self.__traversal_map.setdefault(traversal.source_state, []).append(traversal)
        if not has_initial:
            raise TypeError(f"no initial state found: {initial_state}")
        if not has_final:
            raise TypeError(f"no final state found: {final_state}")
        self.__listener = listener
        self.__initial_state = initial_state
        self.__final_state = final_state
        self.__current_state = self.__initial_state
        self.__last_input: Optional[T] = None

    def __enter__(self) -> "StateMachineRunner":
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is not None:
            return None
        return self.close()

    def dispatch(self, input: T):
        """Dispatch input to the state machine.

        This should be called for each input, and state machine can either
        accept the input, and maybe traverse to a different state, or reject it
        by raising :exc:`InputRejectedError` exception.

        :param input:
            The current input to dispatch.
        """
        self.__last_input = input
        current_state_traversals = self.__traversal_map.get(self.__current_state)
        if current_state_traversals is None:
            raise InputRejectedError(input, self.__current_state)
        print(current_state_traversals)
        for traversal in current_state_traversals:
            if traversal.traverse_func(input):
                next_state = traversal.target_state
                self.__listener.on_state_change(input, self.__current_state, next_state)
                self.__current_state = next_state
                break
        else:
            raise InputRejectedError(input, self.__current_state)
        self.__listener.on_dispatch_done(input, self.__current_state)

    def close(self):
        """Close this state machine.

        This method should be called shortly after all inputs are dispatched.
        Its role is to ensure that the final state was reached; if the final
        state was reached, the method silently returns. Otherwise it raises
        :exc:`tinyfsm.exc.FinalStateNotReached` error.
        """
        if not self.is_final():
            raise FinalStateNotReached(self.__last_input, self.__final_state, self.__current_state)

    def is_final(self) -> bool:
        """Check if the final state is reached."""
        return self.__current_state == self.__final_state
