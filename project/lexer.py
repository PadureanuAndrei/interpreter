from typing import List, Tuple
from .dfa import DFA


class Lexer:
    class ParseException(Exception):
        def __init__(self, line: int, char: int):
            self.line = line
            self.char = char

        def __str__(self):
            position = 'EOF' if self.char == -1 else self.char

            return 'No viable alternative at character {}, line {}'.format(position, self.line)

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

                raise Lexer.ParseException(line_count, position)

            tokens.append((max_token, text[position:position + max_len]))
            position += max_len

        return tokens
