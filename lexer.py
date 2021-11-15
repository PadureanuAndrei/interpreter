from dfa import DFA


class Lexer:
    def __init__(self, dfas: list[str, DFA]):
        self.__dfas = dfas

    def parse(self, text: str):
        position = 0
        tokens: list[(str, str)] = []

        while position < len(str):
            max_token = None
            max_len = 0

            for token, dfa in self.__dfas:
                accepted = dfa.max_accepted(text[position:])
                if accepted > max_len:
                    max_token, max_len = token, accepted

            if not max_token:
                raise Exception("Invalid input")

            tokens.append((max_token, text[position:position + max_len]))
