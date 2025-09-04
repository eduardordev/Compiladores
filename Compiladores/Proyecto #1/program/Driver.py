import sys
from antlr4 import FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from CompiscriptLexer import CompiscriptLexer
from CompiscriptParser import CompiscriptParser

from semantic.visitor import SemanticVisitor
from semantic.errors import SemanticError

class ThrowingSyntaxErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"[Syntax] line {line}:{column} {msg}")

def run(filepath: str) -> int:
    input_stream = FileStream(filepath, encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)

    syn = ThrowingSyntaxErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(syn)

    tree = parser.program()

    if syn.errors:
        for e in syn.errors:
            print(e)
        return 1

    visitor = SemanticVisitor()
    try:
        visitor.visit(tree)
    except SemanticError as se:
        print(se)
        return 2

    for w in visitor.warnings:
        print(f"[Warn] {w}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 Driver.py <archivo.cps>")
        sys.exit(64)
    sys.exit(run(sys.argv[1]))
