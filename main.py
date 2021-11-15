# from dfa import DFA, State
# from Lexer import Lexer
#
#
# def state_adapter(state: str) -> State:
#     return State(int(state))
#
#
# def parse_dfa(text: str) -> (str, DFA):
#     lines = text.split('\n')
#     alphabet = set(lines[0].split(' '))
#     token = lines[1]
#     initial_state = state_adapter(lines[2])
#     final_states = set([state_adapter(x) for x in lines[-1].split(' ')])
#
#     delta = {}
#     for line in lines[3:-1]:
#         [_from, _char, _to] = line.split(' ')
#         _from = state_adapter(_from)
#         _to = state_adapter(_to)
#
#         if _from not in delta:
#             delta[_from] = {}
#         delta[_from][_char] = _to
#
#     return token, DFA(alphabet, initial_state, final_states, delta)
#
#
# def parse_lexer(text: str) -> Lexer:
#     return Lexer(list(parse_dfa(dfa_str) for dfa_str in text.split('\n\n')))
#
#
# def read_word() -> str:
#     return ''
#
#
# if __name__ == '__main__':
#     pass
