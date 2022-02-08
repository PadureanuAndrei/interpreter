import os
import sys
from project import Lexer, Regex, Parser, encode, Interpreter


def runcompletelexer(lexer_file: str, input_file: str, output_file: str):
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


def runparser(input_file: str, output_file: str):
    # creates output file (and intermediate folders) if it doesn't exist
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    with open(output_file, 'w+') as file:
        file.write(str(Parser('lexer.txt').parse(input_file)))


def read_lexer(file_name: str) -> Lexer:
    def parse_lexer(text: str) -> Lexer:
        dfas = []
        for line in text.split(';\n'):
            if not line:
                continue
            token, regex = line.split(' ', maxsplit=1)
            dfa = Regex.parse(regex).to_nfa().to_dfa()

            dfas.append((token, dfa))

        return Lexer(dfas)
    
    with open(file_name, 'r') as file:
        return parse_lexer(file.read())


def read_word(file_name: str) -> str:
    with open(file_name, 'r') as file:
        return file.read()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        raise Exception("python3 CompleteLexer.py <program_file>")

    file_name = sys.argv[1]
    print(Interpreter("lexer.txt").interpret(file_name))
