import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from codegen.codegen import CodeGenVisitor
from Driver import parse_and_semantic
from codegen.mips_backend import emit_mips


def run(filepath: str) -> int:
    parser, tree, syn, sem_visitor = parse_and_semantic(filepath)

    if syn and syn.errors:
        for e in syn.errors:
            print(e)
        return 1

    if sem_visitor is None:
        print('[Error] Falló el análisis semántico, no se puede generar TAC.')
        return 2

    cg = CodeGenVisitor()
    emitter, _ = cg.visitProgram(tree)

    if emitter is None:
        print('[Error] No se generó ningún código intermedio.')
        return 2

    code_str = str(emitter).strip()
    if not code_str or code_str == '(sin instrucciones TAC)':
        print('[Aviso] El programa fuente no produjo instrucciones TAC.')
    else:
        print(code_str)

    return 0


def run_mips(filepath: str) -> int:
    parser, tree, syn, sem_visitor = parse_and_semantic(filepath)
    if syn and syn.errors:
        for e in syn.errors:
            print(e)
        return 1
    if sem_visitor is None:
        print('[Error] Falló el análisis semántico, no se puede generar MIPS.')
        return 2
    cg = CodeGenVisitor()
    emitter, static_arrays = cg.visitProgram(tree)
    if emitter is None:
        print('[Error] No se generó ningún código intermedio.')
        return 2
    # output path: same dir, same base name with .s
    out_path = os.path.splitext(filepath)[0] + '.s'
    mips = emit_mips(emitter, sem_visitor.symtab if sem_visitor else None, out_path=out_path, static_arrays=static_arrays)
    # Solo imprime el código ensamblador, no el mensaje de guardado
    print(mips)
    return 0

    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python generate_tac.py <archivo.cps>')
        sys.exit(64)
    sys.exit(run(sys.argv[1]))
