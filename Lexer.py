import os
from typing import List, Tuple, Union
from dfa import DFA, State


class LexerParseException(Exception):
    def __init__(self, line: int, char: Union[int, str]):
        self.line = line
        self.char = char

    def __str__(self):
        position = 'EOF' if self.char == -1 else self.char

        return 'No viable alternative at character {}, line {}'.format(position, self.line)


class Lexer:
    def __init__(self, dfas: List[Tuple[str, DFA]]):
        self.__dfas = dfas

    def parse(self, text: str) -> List[Tuple[str, str]]:
        position = 0
        tokens: List[Tuple[str, str]] = []

        while position < len(text):
            max_token = None
            max_len = 0
            max_last = 0

            for token, dfa in self.__dfas:
                accepted, last = dfa.max_accepted(text[position:])
                if accepted > max_len:
                    max_token, max_len = token, accepted
                if last > max_last:
                    max_last = last

            if not max_token:
                position += max_last
                line_count = -1
                is_eof = position == len(text)

                for line in text.split('\n'):
                    line_count += 1
                    if position < len(line):
                        break
                    position -= len(line)

                if is_eof:
                    position = -1

                raise LexerParseException(line_count, position)

            tokens.append((max_token, text[position:position + max_len]))
            position += max_len

        return tokens


# Test part

# Encodes string: '\n' -> '\\n'
def encode(text: str) -> str:
    return text.encode('unicode_escape').decode('latin1')


# Decodes string: '\\n' -> '\n'
def decode(text: str) -> str:
    return text.encode('latin1').decode('unicode-escape')


def read_lexer(file: str) -> Lexer:
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

    file = open(file, 'r')
    lexer_input = file.read()
    file.close()

    return parse_lexer(lexer_input)


def read_word(file: str) -> str:
    file = open(file, 'r')
    word = file.read()
    file.close()

    return word


def runlexer(lexer_file: str, input_file: str, output_file: str):
    lexer = read_lexer(lexer_file)
    input_word = read_word(input_file)

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    file = open(output_file, 'w+')
    try:
        for token, word in lexer.parse(input_word):
            file.write('{} {}\n'.format(token, encode(word)))
    except LexerParseException as err:
        file.write(str(err))
    file.close()
