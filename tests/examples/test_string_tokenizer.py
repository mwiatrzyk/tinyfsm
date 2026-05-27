"""An example with simple text tokenizer.

It defines FSM for splitting text containing words and spaces into WORD and
SPACE tokens that are later added to the output list.
"""

import pytest

from tinyfsm.api import Traversal, StateMachineRunner, InputRejectedError


definition = [
    Traversal[str]("initial", "word", str.isalpha),
    Traversal[str]("initial", "number", str.isdigit),
    Traversal[str]("initial", "final", lambda input: input == ""),
    Traversal[str]("word", "word", str.isalpha),
    Traversal[str]("word", "number", str.isdigit),
    Traversal[str]("word", "final", lambda input: input == ""),
    Traversal[str]("number", "number", str.isdigit),
    Traversal[str]("number", "word", str.isalpha),
    Traversal[str]("number", "final", lambda input: input == ""),
]


class Listener:
    def __init__(self, output: list[tuple[str, str]]):
        self._output = output
        self._buffer = ""

    def on_state_change(self, input: str, prev_state: str, current_state: str):
        if prev_state != current_state:
            if prev_state == "word":
                self._output.append(("WORD", self._buffer))
            if prev_state == "number":
                self._output.append(("NUMBER", self._buffer))
            self._buffer = ""

    def on_dispatch_done(self, input: str, current_state: str):
        self._buffer += input


def tokenize(text: str) -> list[tuple[str, str]]:
    out = []
    listener = Listener(out)
    runner = StateMachineRunner(definition, listener)
    with runner:
        for char in text:
            runner.dispatch(char)
        runner.dispatch("")
    return out


@pytest.mark.parametrize(
    "input, expected_output",
    [
        ("", []),
        ("f", [("WORD", "f")]),
        ("foo", [("WORD", "foo")]),
        ("1", [("NUMBER", "1")]),
        ("123", [("NUMBER", "123")]),
        ("foo123", [("WORD", "foo"), ("NUMBER", "123")]),
        (
            "f1o2o345",
            [("WORD", "f"), ("NUMBER", "1"), ("WORD", "o"), ("NUMBER", "2"), ("WORD", "o"), ("NUMBER", "345")],
        ),
    ],
)
def test_tokenize_successfully(input, expected_output):
    assert tokenize(input) == expected_output


def test_tokenization_fails_for_invalid_input():
    with pytest.raises(InputRejectedError) as excinfo:
        tokenize("foo123 ")
    assert str(excinfo.value) == "input ' ' was rejected; no traversal found for current state 'number'"
