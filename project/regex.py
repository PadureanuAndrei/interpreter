from abc import ABC, abstractmethod
from typing import List, Union

from project.nfa import NFA


class Regex(ABC):
    @staticmethod
    def from_input(text: str):
        def get_param() -> Union[Regex, str]:
            token = tokens[len(tokens) - 1]
            if token == 'UNION' or token == 'STAR' or token == 'CONCAT':
                return parse()

            return tokens.pop()

        def parse() -> Regex:
            regex_type = tokens.pop()
            if regex_type == 'UNION':
                a = get_param()
                b = get_param()
                return RegexUnion(a, b)

            elif regex_type == 'STAR':
                a = get_param()
                return RegexStar(a)

            elif regex_type == 'CONCAT':
                a = get_param()
                b = get_param()
                return RegexConcat(a, b)

            else:
                # TODO: raise exception
                pass

        tokens = list(reversed(text.split(' ')))

        return parse()

    @abstractmethod
    def to_nfa(self) -> NFA:
        pass

    @staticmethod
    def simple_nfa(char: str):
        return NFA({char}, 0, 1, 2, {0: {char: {1}}})

    @staticmethod
    def get_nfa(regex):
        if isinstance(regex, str):
            return NFA({regex}, 0, 1, 2, {0: {regex: {1}}})

        if isinstance(regex, Regex):
            return regex.to_nfa()

        raise NotImplemented("can get NFA only from regex or a char")


class RegexUnion(Regex):
    def __init__(self, a: Union[Regex, str], b: Union[Regex, str]):
        self.__a = a
        self.__b = b

    def to_nfa(self) -> NFA:
        nfa_a = Regex.get_nfa(self.__a)
        nfa_b = Regex.get_nfa(self.__b)

        return nfa_a.union(nfa_b)

    def __str__(self):
        return 'UNION ' + self.__a.__str__() + ' ' + self.__b.__str__()

    __repr__ = __str__


class RegexConcat(Regex):
    def __init__(self, a: Union[Regex, str], b: Union[Regex, str]):
        self.__a = a
        self.__b = b

    def to_nfa(self) -> NFA:
        nfa_a = Regex.get_nfa(self.__a)
        nfa_b = Regex.get_nfa(self.__b)

        return nfa_a.concat(nfa_b)

    def __str__(self):
        return 'CONCAT ' + self.__a.__str__() + ' ' + self.__b.__str__()

    __repr__ = __str__


class RegexStar(Regex):
    def __init__(self, a: Union[Regex, str]):
        self.__a = a

    def to_nfa(self) -> NFA:
        nfa = Regex.get_nfa(self.__a)

        return nfa.star()

    def __str__(self):
        return 'STAR ' + self.__a.__str__()

    __repr__ = __str__


if __name__ == '__main__':
    s = "STAR UNION a b"
    print(Regex.from_input(s).to_nfa().to_dfa())
