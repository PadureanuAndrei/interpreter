from collections import deque
from typing import Set, Dict, Tuple, List

from .dfa import DFA

EPSILON = 'EPSILON'


class NFA:
    def __init__(self, alphabet: Set[str], initial_state: int, final_state: int, states_count: int,
                 delta: Dict[int, Dict[str, List[int]]]):
        self.__alphabet = alphabet
        self.__initial_state = initial_state
        self.__final_state = final_state
        self.__delta = delta
        self.__states_count = states_count

    def union(self, other):
        if not isinstance(other, NFA):
            raise NotImplemented("can union only with another NFA")

        nfa_a: NFA = self.__shift_states(1)
        nfa_b: NFA = other.__shift_states(self.__states_count + 1)

        initial_state = 0
        final_state = nfa_b.__final_state + 1

        nfa_a.__delta.update(nfa_b.__delta)

        nfa_a.__delta.update({
            initial_state: {
                EPSILON: [nfa_a.__initial_state, nfa_b.__initial_state],
            },
            nfa_a.__final_state: {
                EPSILON: [final_state],
            },
            nfa_b.__final_state: {
                EPSILON: [final_state],
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

        nfa.__delta.update({
            initial_state: {
                EPSILON: [nfa.__initial_state, final_state],
            },
            nfa.__final_state: {
                EPSILON: [final_state, nfa.__initial_state],
            },
        })
        nfa.__initial_state = initial_state
        nfa.__final_state = final_state
        nfa.__states_count += 2

        return nfa

    def concat(self, other):
        if not isinstance(other, NFA):
            raise NotImplemented("can concat only with another NFA")

        nfa_a: NFA = self.__shift_states(0)
        nfa_b: NFA = other.__shift_states(self.__states_count + 0)

        nfa_a.__delta.update(nfa_b.__delta)
        nfa_a.__delta.update({
            nfa_a.__final_state: {
                EPSILON: [nfa_b.__initial_state]
            }
        })

        nfa_a.__final_state = nfa_b.__final_state
        nfa_a.__states_count += nfa_b.__states_count
        nfa_a.__alphabet.update(nfa_b.__alphabet)

        return nfa_a

    def __shift_states(self, count: int):
        delta = {
            state + count: {
                char: [x + count for x in self.__delta[state][char]]
                for char in self.__delta[state]
            }
            for state in self.__delta
        }

        return NFA(self.__alphabet, self.__initial_state + count,
                   self.__final_state + count, self.__states_count, delta)

    def to_dfa(self) -> DFA:
        def compute_epsilon_closure() -> Dict[int, Set[int]]:
            def get_epsilon_closure(state: int):
                states = set()
                queue = deque([state])
                while queue:
                    from_state = queue.popleft()
                    states.add(from_state)

                    if from_state not in self.__delta or EPSILON not in self.__delta[from_state]:
                        continue

                    queue.extend([
                        to_state
                        for to_state in self.__delta[from_state][EPSILON] if to_state not in states
                    ])

                return states

            return {i: get_epsilon_closure(i) for i in range(self.__states_count)}

        def set_to_state(state_set: Set[int]) -> str:
            return ','.join([str(x) for x in state_set])

        def normalize(initial_state: str, final_states: Set[str], delta: Dict[str, Dict[str, str]]) ->\
                Tuple[int, Set[int], Dict[int, Dict[str, int]]]:
            states = {initial_state}
            states.update(final_states)
            states.update({state for state in delta})
            states.update({delta[state][char] for state in delta for char in delta[state]})

            translate = {old_name: new_name for new_name, old_name in enumerate(states)}

            new_delta = {
                translate[state]: {
                    char: translate[delta[state][char]] for char in delta[state]
                } for state in delta
            }

            new_initial_state = translate[initial_state]
            new_final_states = {translate[x] for x in final_states}

            return new_initial_state, new_final_states, new_delta

        epsilon_closure = compute_epsilon_closure()
        delta = {}
        final_states = set()
        sink_state = self.__states_count

        queue = deque([epsilon_closure[self.__initial_state]])
        visited = {set_to_state(epsilon_closure[self.__initial_state])}
        while queue:
            from_state_set = queue.popleft()
            from_state = set_to_state(from_state_set)
            delta[from_state] = {}

            if self.__final_state in from_state_set:
                final_states.add(from_state)

            for char in self.__alphabet:
                to_state_set = {
                    item

                    for nfa_state in from_state_set if nfa_state in self.__delta and char in self.__delta[nfa_state]
                    for another_state in self.__delta[nfa_state][char]
                    for item in epsilon_closure[another_state]
                } or {sink_state}

                to_state = set_to_state(to_state_set)

                delta[from_state][char] = to_state

                if to_state not in visited:
                    visited.add(to_state)
                    queue.append(to_state_set)

        initial_state = set_to_state(epsilon_closure[self.__initial_state])

        initial_state, final_states, delta = normalize(initial_state, final_states, delta)

        return DFA(self.__alphabet, initial_state, final_states, delta)

    def __str__(self):
        result = 'from,char,to\n'

        result += ''.join([
            '{} {} {}\n'.format(from_state, to_state, char)

            for from_state in self.__delta
            for char in self.__delta[from_state]
            for to_state in self.__delta[from_state][char]
        ])

        return result
