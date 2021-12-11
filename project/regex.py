from abc import ABC, abstractmethod

from .nfa import NFA


class Regex(ABC):
    @staticmethod
    def parse(text: str):
        def get_param() -> Regex:
            token = tokens[len(tokens) - 1]
            if token in {'UNION', 'STAR', 'CONCAT', 'PLUS'}:
                return helper()

            return RegexChar(tokens.pop())

        def helper() -> Regex:
            regex_type = tokens.pop()
            if regex_type == 'UNION':
                a = get_param()
                b = get_param()
                return RegexUnion(a, b)

            if regex_type == 'STAR':
                a = get_param()
                return RegexStar(a)

            if regex_type == 'CONCAT':
                a = get_param()
                b = get_param()
                return RegexConcat(a, b)

            if regex_type == 'PLUS':
                a = get_param()
                return RegexPlus(a)

            return RegexChar(regex_type)

        tokens = list(reversed(text.split(' ')))

        return helper()

    @abstractmethod
    def to_nfa(self) -> NFA:
        pass


class RegexUnion(Regex):
    def __init__(self, a: Regex, b: Regex):
        self.__a = a
        self.__b = b

    def to_nfa(self) -> NFA:
        nfa_a = self.__a.to_nfa()
        nfa_b = self.__b.to_nfa()

        return nfa_a.union(nfa_b)

    def __str__(self):
        return 'UNION ' + str(self.__a) + ' ' + str(self.__b)

    __repr__ = __str__


class RegexConcat(Regex):
    def __init__(self, a: Regex, b: Regex):
        self.__a = a
        self.__b = b

    def to_nfa(self) -> NFA:
        nfa_a = self.__a.to_nfa()
        nfa_b = self.__b.to_nfa()

        return nfa_a.concat(nfa_b)

    def __str__(self):
        return 'CONCAT ' + str(self.__a) + ' ' + str(self.__b)

    __repr__ = __str__


class RegexStar(Regex):
    def __init__(self, a: Regex):
        self.__a = a

    def to_nfa(self) -> NFA:
        nfa = self.__a.to_nfa()

        return nfa.star()

    def __str__(self):
        return 'STAR ' + str(self.__a)

    __repr__ = __str__


class RegexPlus(Regex):
    def __init__(self, a: Regex):
        self.__a = a

    def to_nfa(self) -> NFA:
        nfa = self.__a.to_nfa()

        return nfa.concat(nfa.star())

    def __str__(self):
        return 'PLUS ' + str(self.__a)

    __repr__ = __str__


class RegexChar(Regex):
    def __init__(self, char: str):
        self.__char = char

    def to_nfa(self) -> NFA:
        return NFA({self.__char}, 0, 1, 2, {0: {self.__char: {1}}})

    def __str__(self):
        return self.__char

    __repr__ = __str__


if __name__ == '__main__':
    s = "STAR UNION a b"
    print(Regex.from_input(s).to_nfa().to_dfa())
