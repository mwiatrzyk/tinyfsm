# tinyfsm

A tiny and minimal finite state machine for Python.

## About

**tinyfsm** is a fast and minimal finite state machine engine for Python. It
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

```python
from tinyfsm.api import Traversal, StateMachine

definition = [
    Traversal("initial", "one", lambda event: event == 1),  # moves from `initial` to `one` if event==1
    Traversal("one", "two", lambda event: event == 2),  # moves from `one` to `two` if event==2
    Traversal("two", "one", lambda event: event == 1),  # moves from `two` back to `one` if event
]
```
