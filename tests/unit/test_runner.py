import pytest

from mockify.api import Mock, satisfied

from tinyfsm.exc import EventRejectedError, FinalStateNotReached
from tinyfsm.interface import Traversal
from tinyfsm.runner import StateMachineRunner


class TestStateMachineRunner:

    @pytest.fixture
    def listener_mock(self):
        mock = Mock("listener_mock")
        with satisfied(mock):
            yield mock

    @pytest.mark.parametrize("definition, initial_state_name", [
        ([], "dummy"),
        ([Traversal[str]("initial", "next", lambda e: True)], "dummy"),
    ])
    def test_creating_without_initial_state_causes_error(self, definition, listener_mock, initial_state_name):
        with pytest.raises(TypeError) as excinfo:
            StateMachineRunner(definition, listener_mock, initial_state=initial_state_name)
        assert str(excinfo.value) == f"no initial state found: {initial_state_name}"

    @pytest.mark.parametrize("definition, final_state_name", [
        ([Traversal[str]("initial", "next", lambda e: True)], "dummy"),
        ([Traversal[str]("initial", "final", lambda e: True)], "dummy"),
    ])
    def test_creating_without_final_state_causes_error(self, definition, listener_mock, final_state_name):
        with pytest.raises(TypeError) as excinfo:
            StateMachineRunner(definition, listener_mock, final_state=final_state_name)
        assert str(excinfo.value) == f"no final state found: {final_state_name}"

    def test_closing_before_reaching_final_state_causes_error(self, listener_mock):
        definition = [
            Traversal[str]("initial", "dummy", lambda event: event == "dummy"),
            Traversal[str]("dummy", "spam", lambda event: event == "spam"),
            Traversal[str]("spam", "final", lambda event: event == ""),
        ]
        uut = StateMachineRunner(definition, listener_mock)
        listener_mock.on_state_change.expect_call("dummy", "initial", "dummy")
        listener_mock.on_dispatch_done.expect_call("dummy", "dummy")
        uut.dispatch("dummy")
        with pytest.raises(FinalStateNotReached) as excinfo:
            uut.close()
        assert str(excinfo.value) == "final state 'final' was not reached; current state is 'dummy', last event was 'dummy'"

    def test_dispatch_fails_if_no_traversal_is_defined(self, listener_mock):
        definition = [
            Traversal[str]("initial", "dummy", lambda event: event == "dummy"),
            Traversal[str]("spam", "final", lambda event: event == ""),
        ]
        uut = StateMachineRunner(definition, listener_mock)
        listener_mock.on_state_change.expect_call("dummy", "initial", "dummy")
        listener_mock.on_dispatch_done.expect_call("dummy", "dummy")
        uut.dispatch("dummy")
        with pytest.raises(EventRejectedError) as excinfo:
            uut.dispatch("spam")
        assert str(excinfo.value) == "event 'spam' was rejected; no traversal found for current state 'dummy'"
