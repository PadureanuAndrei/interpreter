from functools import reduce
from typing import List, Tuple, Union
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
        # Reducer for iterating trough a list of (token, DFA) and get dfa which accepts max len word
        def reducer(acc: Tuple[Union[str, None], int, int], x: Tuple[str, DFA]):
            max_token, max_accepted, max_read = acc
            _token, dfa = x
            _accepted, _last = dfa.max_accepted(text[position:])

            if _accepted > max_accepted:
                return _token, _accepted, _last
            if _last > max_read:
                return max_token, max_accepted, _last

            return acc

        position = 0
        tokens: List[Tuple[str, str]] = []

        while position < len(text):
            # accepted - nr of chars from accepted word | last - index of max checked char
            token, accepted, last = reduce(reducer, self.__dfas, (None, 0, 0))

            if not token:
                position += last
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

            tokens.append((token, text[position:position + accepted]))
            position += accepted

        return tokens
