import sys
import os
from antlr4 import FileStream, CommonTokenStream
from CompiscriptLexer import CompiscriptLexer
from CompiscriptParser import CompiscriptParser
from semantic.visitor import SemanticVisitor
from Driver import ThrowingSyntaxErrorListener
from codegen.codegen import CodeGenVisitor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

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

    sem = SemanticVisitor()
    sem.visit(tree)

    cg = CodeGenVisitor()
    emitter = cg.visitProgram(tree)  

    if emitter is None:
        print("[Error] No se generó ningún código intermedio.")
        return 2

    code_str = str(emitter).strip()
    if not code_str or code_str == "(sin instrucciones TAC)":
        print("[Aviso] El programa fuente no produjo instrucciones TAC.")
    else:
        print(code_str)

    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python generate_tac.py <archivo.cps>")
        sys.exit(64)
    sys.exit(run(sys.argv[1]))
