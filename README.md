# TinyFSM

A tiny and minimal finite state machine for Python.

## About

**TinyFSM** is a fast and minimal finite state machine engine for Python. It
runs the finite state defined as list of traversals, where each traversal is
given by current and next state name and a traversal function that is evaluated
on currently processed event. Once traversal function returns true, the current
state is changed to the next state according to matched traversal.

This library can be used as a backbone for creating larger scale FSM-based
tokenizers and parsers.

## Installation

```shell
$ pip install tinyfsm
```

## Quickstart

Below you'll find a simple text parser that split text into WORD and SPACE
tokens, where WORD is a consecutive collection of alpha characters, and SPACE
is consecutive collection of space characters:

```python
from tinyfsm.api import Traversal, StateMachineRunner, EventRejectedError

# Declaration of the state machine as list of Traversal objects.
# Each object contains source state, destination state, and a function that
# checks if current input (or event) should trigger state traversal.
definition = [
    Traversal[str]("initial", "word", lambda event: event.isalpha()),
    Traversal[str]("initial", "space", lambda event: event == " "),
    Traversal[str]("word", "word", lambda event: event.isalpha()),
    Traversal[str]("word", "space", lambda event: event == " "),
    Traversal[str]("word", "final", lambda event: event == ""),
    Traversal[str]("space", "space", lambda event: event == " "),
    Traversal[str]("space", "word", lambda event: event.isalpha()),
    Traversal[str]("space", "final", lambda event: event == ""),
]

class Listener:
    """Event listener for the state machine.

    It listens for events like state change, or input value dispatching end.
    Implementations (like this one) can use these methods to buffer inputs and
    emit tokens.
    """

    def __init__(self, output: list[tuple[str, str]]):
        self._output = output
        self._buffer = ""

    def on_state_change(self, event: str, prev_state: str, current_state: str):
        if prev_state != current_state:
            if prev_state == "word":
                self._output.append(("WORD", self._buffer))
            if prev_state == "space":
                self._output.append(("SPACE", self._buffer))
            self._buffer = ""

    def on_dispatch_done(self, event: str, current_state: str):
        self._buffer += event

def tokenize(text: str) -> list[tuple[str, str]]:
    """Tokenization function.

    This is just an example, but in general a some sort of function gluing all
    parts together is recommended. Here the function parses given text and
    outputs list of tokens parsed from it.
    """
    out = []
    listener = Listener(out)
    runner = StateMachineRunner(definition, listener)
    with runner:
        for char in text:
            runner.dispatch(char)
        runner.dispatch("")
    return out
```
