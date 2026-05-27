"""An example with simple text tokenizer.

It defines FSM for splitting text containing words and spaces into WORD and
SPACE tokens that are later added to the output list.
"""

import pytest

from tinyfsm.api import Traversal, StateMachineRunner, InputRejectedError


definition = [
    Traversal[str]("initial", "word", lambda input: input.isalpha()),
    Traversal[str]("initial", "space", lambda input: input == " "),
    Traversal[str]("word", "word", lambda input: input.isalpha()),
    Traversal[str]("word", "space", lambda input: input == " "),
    Traversal[str]("word", "final", lambda input: input == ""),
    Traversal[str]("space", "space", lambda input: input == " "),
    Traversal[str]("space", "word", lambda input: input.isalpha()),
    Traversal[str]("space", "final", lambda input: input == ""),
]


class Listener:
    def __init__(self, output: list[tuple[str, str]]):
        self._output = output
        self._buffer = ""

    def on_state_change(self, input: str, prev_state: str, current_state: str):
        if prev_state != current_state:
            if prev_state == "word":
                self._output.append(("WORD", self._buffer))
            if prev_state == "space":
                self._output.append(("SPACE", self._buffer))
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
        ("foo", [("WORD", "foo")]),
        ("foobar", [("WORD", "foobar")]),
        ("foo bar", [("WORD", "foo"), ("SPACE", " "), ("WORD", "bar")]),
        ("foo  bar", [("WORD", "foo"), ("SPACE", "  "), ("WORD", "bar")]),
        ("foo bar ", [("WORD", "foo"), ("SPACE", " "), ("WORD", "bar"), ("SPACE", " ")]),
        (" foo bar ", [("SPACE", " "), ("WORD", "foo"), ("SPACE", " "), ("WORD", "bar"), ("SPACE", " ")]),
    ],
)
def test_tokenize_successfully(input, expected_output):
    assert tokenize(input) == expected_output


def test_tokenization_fails_for_invalid_input():
    with pytest.raises(InputRejectedError) as excinfo:
        tokenize("123")
    assert str(excinfo.value) == "input '1' was rejected; no traversal found for current state 'initial'"
