from abc import ABC, abstractmethod
from string import ascii_lowercase
from typing import Union

from .nfa import NFA
from .utils import decode


class Regex(ABC):
    @staticmethod
    def parse(text: str):
        index = 0

        def parse_regex() -> Regex:
            nonlocal index
            regex: Union[None, Regex] = None
            last_regex: Union[None, Regex] = None

            while index < len(text):
                if text[index] == '\'':
                    if last_regex:
                        regex = RegexConcat(regex, last_regex) if regex else last_regex

                    last_index = text.find('\'', index + 1)
                    while text[last_index - 1] == '\\':
                        last_index = text.find('\'', last_index + 1)

                    last_regex = RegexChar(decode(text[index + 1:last_index]))
                    index = last_index

                elif text[index] == '[':
                    if last_regex:
                        regex = RegexConcat(regex, last_regex) if regex else last_regex

                    last_regex = REGEX_NUMBER if text[index + 1] == '0' else REGEX_WORD
                    index += 5

                elif text[index] == '(':
                    if last_regex:
                        regex = RegexConcat(regex, last_regex) if regex else last_regex

                    index += 1
                    last_regex = parse_regex()
                    index += 1

                    continue

                elif text[index] == '+':
                    last_regex = RegexPlus(last_regex)
                elif text[index] == '*':
                    last_regex = RegexStar(last_regex)

                elif text[index] == '|':
                    index += 1
                    regex1 = parse_regex()

                    last_regex = RegexUnion(last_regex, regex1) if last_regex else regex1

                elif text[index].isalnum():
                    if last_regex:
                        regex = RegexConcat(regex, last_regex) if regex else last_regex

                    last_regex = RegexChar(text[index])

                if index < len(text) and text[index] == ')':
                    if last_regex:
                        regex = RegexConcat(regex, last_regex) if regex else last_regex

                    if not regex:
                        raise Exception("Invalid regex")
                    return regex

                index += 1

            if last_regex:
                regex = RegexConcat(regex, last_regex) if regex else last_regex

            if not regex:
                raise Exception("Invalid regex")

            return regex

        return parse_regex()

    @staticmethod
    def parse_prenex_form(text: str):
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


REGEX_WORD = RegexChar('a')
for x in ascii_lowercase[1:]:
    REGEX_WORD = RegexUnion(REGEX_WORD, RegexChar(x))
REGEX_WORD = RegexPlus(REGEX_WORD)

REGEX_NUMBER = RegexChar('0')
for x in range(1, 10):
    REGEX_NUMBER = RegexUnion(REGEX_NUMBER, RegexChar(chr(ord('0') + x)))
REGEX_NUMBER = RegexPlus(REGEX_NUMBER)
