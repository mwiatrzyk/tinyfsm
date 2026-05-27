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

Here's a simple text tokenizer written using **TinyFSM** library that splits
text composed of alphanumeric characters into groups of words and numbers and
returns list of ``(token_name, token_data)`` tuples:

```python
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
```

And the tokenizer from above will split any text composed of just words and
numbers into something like this:

```python
out = tokenize("foo123bar456")
print(out)  # Would print: [("WORD", "foo"), ("NUMBER", "123"), ("WORD", "bar"), ("NUMBER", "456")]
```

# License

This project is released under the terms of the MIT license.
