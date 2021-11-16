# An adapter script for running tests

import os
from project import DFA, State, Lexer


# Adapter function
def runlexer(lexer_file: str, input_file: str, output_file: str):
    lexer = read_lexer(lexer_file)
    input_word = read_word(input_file)

    # creates output file (and intermediate folders) if it doesn't exist
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    with open(output_file, 'w') as file:
        try:
            for token, word in lexer.parse(input_word):
                file.write('{} {}\n'.format(token, encode(word)))
        except Lexer.ParseException as err:
            file.write(str(err))


def read_lexer(file_name: str) -> Lexer:
    def to_state(state: str) -> State:
        return State(int(state))

    def parse_dfa(text: str) -> (str, DFA):
        lines = text.split('\n')
        alphabet = set(decode(lines[0]))
        token = lines[1]
        initial_state = to_state(lines[2])
        final_states = set([to_state(x) for x in lines[-1].split(' ')])

        delta = {}
        for line in lines[3:-1]:
            [_from, _char, _to] = line.split(',')
            _from = to_state(_from)
            _to = to_state(_to)
            _char = decode(_char)[1]  # the char is surrounded with apostrophes ('0', 'b')

            if _from not in delta:
                delta[_from] = {}
            delta[_from][_char] = _to

        return token, DFA(alphabet, initial_state, final_states, delta)

    def parse_lexer(text: str) -> Lexer:
        return Lexer(list(parse_dfa(dfa_str) for dfa_str in text.split('\n\n')))

    with open(file_name, 'r') as file:
        return parse_lexer(file.read())


def read_word(file_name: str) -> str:
    with open(file_name, 'r') as file:
        return file.read()


# Encodes string: '\n' (one character) -> '\\n' (two characters)
def encode(text: str) -> str:
    return text.encode('unicode_escape').decode('latin1')


# Decodes string: '\\n' (two characters) -> '\n' (one character)
def decode(text: str) -> str:
    return text.encode('latin1').decode('unicode-escape')
