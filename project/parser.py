from .lexer import Lexer
from .regex import Regex
from .ast import *


class Parser:
    def __init__(self, lexer_file: str):
        def parse_lexer(text: str) -> Lexer:
            dfas = []
            for line in text.split(';\n'):
                if not line:
                    continue
                token, regex = line.split(' ', maxsplit=1)

                dfa = Regex.parse(regex).to_nfa().to_dfa()

                dfas.append((token, dfa))

            return Lexer(dfas)

        with open(lexer_file, 'r') as file:
            self.__lexer = parse_lexer(file.read())

    def parse(self, program_file: str) -> Node:
        with open(program_file, 'r') as file:
            program = file.read()

        tokens = [x for x in self.__lexer.parse(program) if x[0] not in {'WHITESPACES', 'PARENTHESES'}]
        index = 0

        def parse_operand(height: int) -> Node:
            nonlocal index

            if tokens[index][0] == 'INTEGER':
                node = Expr(height, 'i', tokens[index][1])
            elif tokens[index][0] == 'VARIABLE':
                node = Expr(height, 'v', tokens[index][1])
            else:
                raise Exception()
            index += 1

            return node

        def parse_expr(height) -> Node:
            nonlocal index

            if tokens[index + 1][0] != 'OPERATOR':
                return parse_operand(height)

            operators = 0
            i = index + 1
            while i < len(tokens):
                if tokens[i][0] == 'OPERATOR':
                    operators += 1
                    i += 1
                else:
                    break

            height += operators - 1

            a = parse_operand(height + 1)
            operator = tokens[index][1]
            index += 1
            b = parse_operand(height + 1)

            node = Expr(height, operator, a, b)

            while index < len(tokens) and tokens[index][0] == 'OPERATOR':
                height -= 1
                operator = tokens[index][1]
                index += 1
                operand = parse_operand(height + 1)

                node = Expr(height, operator, node, operand)

            return node

        def parse_ast(height: int = 0) -> Node:
            nonlocal index

            while index < len(tokens):
                if tokens[index][0] == 'BEGIN':
                    instructions = []
                    index += 1
                    while tokens[index][0] != 'END':
                        instructions.append(parse_ast(height + 1))

                    index += 1
                    return InstructionList(height, instructions)

                if tokens[index][0] == 'WHILE':
                    index += 1  # escape WHILE

                    condition = parse_expr(height + 1)
                    index += 1  # escape DO

                    program = parse_ast(height + 1)
                    index += 1  # escape OD

                    return While(height, condition, program)

                if tokens[index][0] == 'IF':
                    index += 1  # escape IF

                    condition = parse_expr(height + 1)
                    index += 1  # escape THEN

                    if_true = parse_ast(height + 1)
                    index += 1  # escape ELSE

                    if_false = parse_ast(height + 1)
                    index += 1  # escape FI

                    return If(height, condition, if_true, if_false)

                if tokens[index][0] == 'VARIABLE':
                    if tokens[index + 1][0] == 'EQUAL':
                        variable = parse_operand(height + 1)
                        index += 1
                        expr = parse_expr(height + 1)

                        return Assign(height, variable, expr)

                return parse_expr(height + 1)

        return parse_ast()
