from collections import deque
from typing import Set, Dict, Union, List, Tuple


class DFA:
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

    def __init__(self, alphabet: Set[str], initial_state: int, final_states: Set[int],
                 delta: Dict[int, Dict[str, int]]):
        def states() -> Set[int]:
            _states = {initial_state}
            _states.update(final_states)
            _states.update([delta[state][x] for state in delta for x in delta[state]])

            return _states

        def reversed_delta() -> Dict[int, List[int]]:
            _reversed = {}

            for state in delta:
                for x in delta[state]:
                    if delta[state][x] not in _reversed:
                        _reversed[delta[state][x]] = []

                    _reversed[delta[state][x]].append(state)

            return _reversed

        def sink_states() -> Set[int]:
            _delta = reversed_delta()
            _sink: Set[Union[None, int]] = states.difference(final_states)

            # Run BFS from all final states in reversed graph
            queue = deque(final_states)
            while queue:
                u = queue.popleft()

                if u in _delta:
                    for v in _delta[u]:
                        if v in _sink:
                            _sink.remove(v)
                            queue.append(v)

            _sink.add(None)  # None is default sink state

            return _sink

        self.__alphabet = alphabet
        self.__initial_state = initial_state
        self.__final_states = final_states
        self.__delta = delta
        self.__states = states = states()
        self.__sink_states = sink_states()

    def __next_state(self, current_state: int, x: str):
        try:
            return self.__delta[current_state][x]
        except KeyError:
            return None

    def __str__(self):
        alphabet = ''.join(sorted([str(x) for x in self.__alphabet]))
        states_count = str(len(self.__states))
        initial_state = str(self.__initial_state)
        final_states = ' '.join([str(x) for x in self.__final_states])

        transitions = '\n'.join(['{},\'{}\',{}'.format(str(from_state), char, str(self.__delta[from_state][char]))
                                for from_state in self.__delta for char in self.__delta[from_state]])

        return alphabet + '\n' + states_count + '\n' + initial_state + '\n' + final_states + '\n' + transitions
