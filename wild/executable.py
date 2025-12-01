from wild.lexer import Lexer
from wild.parser import Parser
from wild.interpreter import Interpreter

import sys

def parse_args(args: list[str]) -> list[str]:
    if len(args) < 2:
        print(f"Proper usage: `\"{args[0]}\" \"<file_to_run>\"`")
        sys.exit(0)
    
    return args

def main(args: list[str]) -> None:
    args = parse_args(args)

    with open(args[1]) as file:
        source: str = file.read()

    lexer: Lexer = Lexer(source)
    parser: Parser = Parser(lexer.tokenize())

    interpreter: Interpreter = Interpreter()
    interpreter.visit(parser.parse())

if __name__ == "__main__":
    main(sys.argv)