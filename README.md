# TinyFSM

A tiny finite state machine (FSM) engine for Python.

## About

**TinyFSM** allows to declare and run the finite state machine defined as list
of traversals, where each traversal is given by current and next state name and
a traversal function that is evaluated on currently processed input. Once
traversal function returns true, the current state is changed to the next state
according to matched traversal, and then process repeats for the next input.

This library is meant to be used as a backbone for creating larger scale
FSM-based tokenizers, parsers or decision trees. It handles the boilerplate of
running FSMs, providing an easy way to declare those.

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

# The FSM definition.
#
# This is a list of Traversal objects, where each such object contains
# information about current state, next state, and traversal function that is
# applied to current input; if the function returns True, FSM switches to the
# matched next state.
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
    """FSM listener.

    The role of this class is to store user-defined information while the FSM
    is running. Things like input buffers, output data collections and things
    like that all belong in this class.

    This class must implement :class:`tinyfsm.interface.StateMachineListener`
    protocol.
    """

    def __init__(self, output: list[tuple[str, str]]):
        self._output = output
        self._buffer = ""

    def on_state_change(self, input: str, prev_state: str, current_state: str):
        """Called when for given *input* the state traverses from *prev_state*
        to *current_state* (where both can be equal if FSM has loops pointing
        to the same state).

        This method should contain user-defined actions that need to take place
        in such event. For example, production of a next token from the
        content of the current buffer should take place in here.
        """
        if prev_state != current_state:
            if prev_state == "word":
                self._output.append(("WORD", self._buffer))
            if prev_state == "number":
                self._output.append(("NUMBER", self._buffer))
            self._buffer = ""

    def on_dispatch_done(self, input: str, current_state: str):
        """Called when dispatch of a given input ends.

        This is guaranteed to be called for every single input, so it is well
        suited for filling in the buffers. The *current_state* is the state FSM
        traversed to after accepting *input*.
        """
        self._buffer += input


def tokenize(text: str) -> list[tuple[str, str]]:
    """The entry point.

    Here this is a function that takes a text and returns a list of ``(name,
    value)`` tokens.
    """
    out = []  # The output buffer
    listener = Listener(out)  # Instantiate listener
    runner = StateMachineRunner(definition, listener)  # Create FSM runner giving FSM definition and the listener
    with runner:
        for char in text:
            runner.dispatch(char)  # Feed the FSM with inputs
        runner.dispatch("")
    return out  # Return the resulting token list
```

And the tokenizer from above will split any text composed of just words and
numbers into something like this:

```python
out = tokenize("foo123bar456")
print(out)  # Would print: [("WORD", "foo"), ("NUMBER", "123"), ("WORD", "bar"), ("NUMBER", "456")]
```

The example from above is generally a boilerplate code you'll be following when
using this library.

# Author

Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>

# License

This project is released under the terms of the MIT license.
