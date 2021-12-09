from collections import deque
from functools import reduce
from typing import Set, Dict, Union, List, Tuple


class DFA:
    class State:
        def __init__(self, keys: Union[Set[int], int]):
            if isinstance(keys, int):
                keys = {keys}

            self.__keys = keys
            self.__str_keys = reduce(lambda acc, x: acc + str(x), self.__keys, '')

        def __eq__(self, other):
            if not isinstance(other, DFA.State):
                return False

            return self.__str_keys == other.__str_keys

        def __hash__(self):
            return hash(self.__str_keys)

        def __str__(self):
            return self.__str_keys

        __repr__ = __str__

    def check_word(self, word: str) -> bool:
        current_state = self.__initial_state

        for x in word:
            current_state = self.__next_state(current_state, x)
            if current_state in self.__sink_states:
                return False

        return current_state in self.__final_states

    def max_accepted(self, word: str) -> Tuple[int, int]:
        """
            finds max accepted len from a word (text)
            @return (x, y) -> x - len of accepted word | y - the index of last read char
        """
        current_state = self.__initial_state

        accepted = 0
        for i in range(len(word)):
            current_state = self.__next_state(current_state, word[i])

            if current_state in self.__final_states:
                accepted = i + 1
            elif current_state in self.__sink_states:
                return accepted, i

        return accepted, len(word)

    def __init__(self, alphabet: Set[str], initial_state: State, final_states: Set[State],
                 delta: Dict[State, Dict[str, State]]):
        def states() -> Set[DFA.State]:
            _states = set(final_states)

            for state in delta:
                for x in delta[state]:
                    _states.add(delta[state][x])

            _states.add(None)  # None is default sink state

            return _states

        def reversed_delta() -> Dict[DFA.State, List[DFA.State]]:
            _reversed = {}

            for state in delta:
                for x in delta[state]:
                    if delta[state][x] not in _reversed:
                        _reversed[delta[state][x]] = []

                    _reversed[delta[state][x]].append(state)

            return _reversed

        def sink_states() -> Set[DFA.State]:
            _delta = reversed_delta()
            _sink: Set[Union[None, DFA.State]] = states().difference(final_states)

            # Run BFS from all final states in reversed graph
            queue = deque(final_states)
            while queue:
                u = queue.popleft()

                if u in _delta:
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

    def __str__(self):
        result = 'from,char,to\n'
        for from_state in self.__delta:
            for char in self.__delta[from_state]:
                to_state = self.__delta[from_state][char]
                result += '{} {} {}\n'.format(from_state, to_state, char)

        return result
