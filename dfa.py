from collections import deque
from functools import reduce
from typing import Set, Dict, Union


class State:
    def __init__(self, keys: Union[Set[int], int]):
        if isinstance(keys, int):
            keys = {keys}

        self.__keys = keys
        self.__str_keys = reduce(lambda acc, x: acc + str(x), self.__keys, '')

    def __eq__(self, other):
        if not isinstance(other, State):
            return False

        return self.__str_keys == other.__str_keys

    def __hash__(self):
        return hash(self.__str_keys)

    def __str__(self):
        return self.__str_keys

    __repr__ = __str__


class DFA:
    @classmethod
    def from_str(cls, dfa: str):
        lines = dfa.split('\n')

        initial_state = State(int(lines[0]))
        final_states = set([State(int(x)) for x in lines[-1].split(' ')])

        delta: Dict[State, Dict[str, State]] = {}
        alphabet = set()
        for [_from, x, _to] in [line.split(' ') for line in lines[1:-1]]:
            alphabet.add(x)

            _from = State(int(_from))
            _to = State(int(_to))
            if _from not in delta:
                delta[_from] = {}
            delta[_from][x] = _to

        return cls(alphabet, initial_state, final_states, delta)

    def check_word(self, word: str) -> bool:
        current_state = self.__initial_state

        for x in word:
            current_state = self.__next_state(current_state, x)
            if current_state in self.__sink_states:
                return False

        return current_state in self.__final_states

    def max_accepted(self, word: str) -> int:
        current_state = self.__initial_state

        accepted = 0
        for i in range(len(word)):
            current_state = self.__next_state(current_state, word[i])

            if current_state in self.__final_states:
                accepted = i
            elif current_state in self.__sink_states:
                return accepted

        return accepted

    def __init__(self, alphabet: Set[str], initial_state: State, final_states: Set[State],
                 delta: Dict[State, Dict[str, State]]):
        def states() -> Set[State]:
            _states = set(final_states)

            for state in delta:
                for x in delta[state]:
                    _states.add(delta[state][x])

            return _states

        def reversed_delta() -> Dict[State, list[State]]:
            _reversed = {}

            for state in delta:
                for x in delta[state]:
                    if delta[state][x] not in _reversed:
                        _reversed[delta[state][x]] = []

                    _reversed[delta[state][x]].append(state)

            return _reversed

        def sink_states() -> Set[State]:
            _delta = reversed_delta()
            _states = states()

            _sink = set(_states)
            _sink.add(None)  # None is a valid state
            for state in final_states:
                _sink.remove(state)

            # Run BFS from all final states
            queue = deque(final_states)
            while queue:
                u = queue.popleft()

                for v in _delta[u]:
                    if v in _sink:
                        _sink.remove(v)
                        queue.append(v)

            return _sink

        self.__alphabet = alphabet
        self.__initial_state = initial_state
        self.__final_states = final_states
        self.__delta = delta
        self.__sink_states = sink_states()

    def __next_state(self, current_state: State, x: str):
        try:
            return self.__delta[current_state][x]
        except KeyError:
            return None
