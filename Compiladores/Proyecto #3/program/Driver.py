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

def run(filepath: str, tac: bool = False, ast: bool = False, mips: bool = False) -> int:
    parser, tree, syn, visitor = parse_and_semantic(filepath)

    if ast:
        if tree is not None and parser is not None:
            try:
                print(tree.toStringTree(recog=parser))
            except Exception:
                print(str(tree))
            return 0

    if syn and syn.errors:
        for e in syn.errors:
            print(e)
        return 1

    if isinstance(visitor, SemanticVisitor):
        # semantic errors already printed inside parse_and_semantic if any
        pass

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

    if mips:
        try:
            from codegen.generate_tac import run_mips
            print("\n=== Código MIPS generado ===\n")
            run_mips(filepath)
            print("\n===========================\n")
        except Exception as e:
            print(f"[Error] Fallo al generar MIPS: {e}")
            return 4

    return 0


def parse_and_semantic(filepath: str):
    """Parse file and run semantic visitor. Returns (parser, tree, syntax_listener, semantic_visitor).
    The function prints semantic errors and returns visitor regardless.
    """
    input_stream = FileStream(filepath, encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)

    syn = ThrowingSyntaxErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(syn)
    tree = parser.program()

    if syn.errors:
        return parser, tree, syn, None

    visitor = SemanticVisitor()
    try:
        visitor.visit(tree)
    except SemanticError as se:
        print(se)
        return parser, tree, syn, visitor

    return parser, tree, syn, visitor


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 Driver.py <archivo.cps> [--tac] [--ast]")
        sys.exit(64)

    path = sys.argv[1]
    flags = sys.argv[2:]

    ast_flag = "--ast" in flags
    tac_flag = "--tac" in flags
    mips_flag = "--mips" in flags

    sys.exit(run(path, tac=tac_flag, ast=ast_flag, mips=mips_flag))
