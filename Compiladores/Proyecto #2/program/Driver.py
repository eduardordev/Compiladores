import sys
import os
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

def run(filepath: str, tac: bool = False, ast: bool = False) -> int:
    input_stream = FileStream(filepath, encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)

    syn = ThrowingSyntaxErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(syn)
    tree = parser.program()


    if ast:
        try:
            print(tree.toStringTree(recog=parser))
        except Exception:
            print(str(tree))
        return 0

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

    for w in getattr(visitor, "warnings", []):
        print(f"[Warn] {w}")

    if tac:
        try:
            from codegen.generate_tac import run as run_tac
            print("\n=== Código Intermedio (TAC) ===\n")
            run_tac(filepath)
            print("\n===============================\n")
        except Exception as e:
            print(f"[Error] Fallo al generar TAC: {e}")
            return 3

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 Driver.py <archivo.cps> [--tac] [--ast]")
        sys.exit(64)

    path = sys.argv[1]
    flags = sys.argv[2:]

    ast_flag = "--ast" in flags
    tac_flag = "--tac" in flags

    sys.exit(run(path, tac=tac_flag, ast=ast_flag))
