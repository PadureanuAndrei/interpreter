import sys
import os

from project import Regex, DFA


def read_regex(file_name: str) -> Regex:
    with open(file_name) as file:
        return Regex.from_input(file.read())


def write_dfa(file_name: str, dfa: DFA):
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))

    with open(file_name, "w") as file:
        file.write(str(dfa))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception("Correct format: python main.py <in_file> <out_file>")

    regex = read_regex(sys.argv[1])
    print(regex)
    write_dfa(sys.argv[2], regex.to_nfa().to_dfa())

# if __name__ == '__main__':
#     regex = Regex.from_input('a')
#     print(regex.to_nfa().to_dfa())
