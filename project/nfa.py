from collections import deque
from typing import Set, Dict, List, Union

from .dfa import DFA

EPSILON = 'EPSILON'


class NFA:
    def __init__(self, alphabet: Set[str], initial_state: int, final_state: int, states_count: int,
                 delta: Dict[int, Dict[str, Set[int]]]):
        self.__alphabet = alphabet
        self.__initial_state = initial_state
        self.__final_state = final_state
        self.__delta = delta
        self.__states_count = states_count

    def union(self, other):
        if not isinstance(other, NFA):
            raise NotImplemented("can concat only with another NFA")

        nfa_a: NFA = self.__shift_states(1)
        nfa_b: NFA = other.__shift_states(self.__states_count + 1)

        initial_state = 0
        final_state = nfa_b.__final_state + 1

        nfa_a.__delta.update(nfa_b.__delta)

        nfa_a.__delta.update({
            initial_state: {
                EPSILON: {nfa_a.__initial_state, nfa_b.__initial_state},
            },
            nfa_a.__final_state: {
                EPSILON: {final_state},
            },
            nfa_b.__final_state: {
                EPSILON: {final_state},
            },
        })

        nfa_a.__states_count += nfa_b.__states_count + 2
        nfa_a.__initial_state = initial_state
        nfa_a.__final_state = final_state
        nfa_a.__alphabet.update(nfa_b.__alphabet)

        return nfa_a

    def star(self):
        nfa: NFA = self.__shift_states(1)
        final_state = nfa.__final_state + 1
        initial_state = 0

        nfa.__delta[initial_state] = {
            EPSILON: {nfa.__initial_state, final_state},
        }
        nfa.__delta[nfa.__final_state] = {
            EPSILON: {final_state, nfa.__initial_state}
        }
        nfa.__initial_state = initial_state
        nfa.__final_state = final_state
        nfa.__states_count += 2

        return nfa

    def concat(self, other):
        if not isinstance(other, NFA):
            raise NotImplemented("can union only with another NFA")

        nfa_a: NFA = self.__shift_states(0)
        nfa_b: NFA = other.__shift_states(self.__states_count + 0)

        nfa_a.__delta.update(nfa_b.__delta)
        nfa_a.__delta.update({
            nfa_a.__final_state: {
                EPSILON: {nfa_b.__initial_state}
            }
        })

        nfa_a.__final_state = nfa_b.__final_state
        nfa_a.__states_count += nfa_b.__states_count
        nfa_a.__alphabet.update(nfa_b.__alphabet)

        return nfa_a

    def __shift_states(self, count: int):
        delta = {}

        for from_state in self.__delta:
            delta[from_state + count] = {}
            for char in self.__delta[from_state]:
                delta[from_state + count][char] = set(map(lambda state: state + count, self.__delta[from_state][char]))

        return NFA(self.__alphabet, self.__initial_state + count,
                   self.__final_state + count, self.__states_count, delta)

    def to_dfa(self) -> DFA:
        def compute_epsilon_closure() -> Dict[int, Set[int]]:
            def get_epsilon_closure(_state: int):
                _states = set()
                _queue = deque([_state])
                while _queue:
                    _from_state = _queue.popleft()
                    _states.add(_from_state)

                    if _from_state in self.__delta and EPSILON in self.__delta[_from_state]:
                        for _to_state in self.__delta[_from_state][EPSILON]:
                            if _to_state not in _states:
                                _queue.append(_to_state)

                return _states

            result = {}
            for i in range(self.__states_count):
                result[i] = get_epsilon_closure(i)

            return result

        epsilon_closure = compute_epsilon_closure()

        delta: Dict[DFA.State, Dict[str, DFA.State]] = {}
        final_states = set()

        sink_state = self.__states_count

        queue = deque()
        queue.append(epsilon_closure[self.__initial_state])
        visited = {DFA.State(epsilon_closure[self.__initial_state])}
        while queue:
            from_state_set = queue.popleft()
            from_state = DFA.State(from_state_set)

            if self.__final_state in from_state_set:
                final_states.add(from_state)

            for char in self.__alphabet:
                to_state_set = set()
                for nfa_state in from_state_set:
                    if nfa_state in self.__delta and char in self.__delta[nfa_state]:
                        for another_state in self.__delta[nfa_state][char]:
                            to_state_set.update(epsilon_closure[another_state])

                if not to_state_set:
                    to_state_set = {sink_state}

                to_state = DFA.State(to_state_set)

                if from_state not in delta:
                    delta[from_state] = {}
                delta[from_state][char] = to_state

                if to_state not in visited:
                    visited.add(to_state)
                    queue.append(to_state_set)

        initial_state = DFA.State(epsilon_closure[self.__initial_state])

        return DFA(self.__alphabet, initial_state, final_states, delta)

    def __str__(self):
        result = 'from,char,to\n'
        for from_state in self.__delta:
            for char in self.__delta[from_state]:
                for to_state in self.__delta[from_state][char]:
                    result += '{} {} {}\n'.format(from_state, to_state, char)

        return result
