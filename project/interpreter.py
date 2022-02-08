from .parser import Parser
from .ast import Assign, Expr, While, InstructionList, If, Node


class Interpreter:
    def __init__(self, lexer_file: str):
        self.__parser = Parser(lexer_file)

    def interpret(self, program_file: str):
        store = {}

        def interpret_expr(expr: Expr) -> int:
            # a + b + 2
            if expr.type in 'iv':
                return eval(expr.left, store.copy())

            left = interpret_expr(expr.left)
            right = interpret_expr(expr.right)

            return eval('{} {} {}'.format(left, expr.type, right))

        def interpret_while(ast: While):
            while interpret_expr(ast.expr):
                interpret_program(ast.prog)

        def interpret_if(ast: If):
            if interpret_expr(ast.expr):
                interpret_program(ast.then_branch)
            else:
                interpret_program(ast.else_branch)

        def interpret_instruction_list(ast: InstructionList):
            for instruction in ast.list:
                interpret_program(instruction)

        def interpret_assign(ast: Assign):
            store[ast.variable.left] = interpret_expr(ast.expr)

        def interpret_program(ast: Node):
            if isinstance(ast, Assign):
                interpret_assign(ast)
            elif isinstance(ast, If):
                interpret_if(ast)
            elif isinstance(ast, InstructionList):
                interpret_instruction_list(ast)
            elif isinstance(ast, While):
                interpret_while(ast)

        program = self.__parser.parse(program_file)
        interpret_program(program)

        return store
