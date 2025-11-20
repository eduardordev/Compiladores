import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from codegen.mips_backend import emit_mips
from codegen.tac import Emitter
from semantic.symbols import SymbolTable, VarSymbol, FuncSymbol
from semantic.typesys import INTEGER


def test_call_uses_stack_cleanup():
    em = Emitter()
    em.emit('ARG', a='5')
    em.emit('ARG', a='10')
    em.emit('CALL', dst='t0', a='func_demo')

    out = emit_mips(em)

    assert 'addi $sp, $sp, -4' in out  # push args
    assert out.count('sw') >= 2  # two pushes
    assert 'jal func_demo' in out
    # caller cleans up its argument stack
    assert re.search(r"addi \$sp, \$sp, 8", out)


def test_spills_allocate_frame_slots():
    em = Emitter()
    em.emit('LABEL', dst='func_heavy')
    # Generar más temporales que registros disponibles para forzar spills
    for i in range(12):
        em.emit('STORE', dst=f't{i}', a=str(i))

    out = emit_mips(em)

    # Debe reservar un frame mayor que el mínimo (8 bytes)
    assert re.search(r"addi \$sp, \$sp, -[1-9][0-9]+", out)
    # Debe existir al menos un acceso a offset negativo del $fp
    assert re.search(r"-\d+\(\$fp\)", out)


def test_return_jumps_to_epilogue():
    em = Emitter()
    em.emit('LABEL', dst='func_ret')
    em.emit('RET', dst='1')

    out = emit_mips(em)

    assert 'j func_ret_end' in out
    assert 'func_ret_end:' in out
    assert re.search(r"lw \$ra, \d+\(\$sp\)", out)


def test_parameters_are_loaded_into_locals_and_use_frame_offsets():
    symtab = SymbolTable()
    symtab.define(VarSymbol('res', INTEGER))
    symtab.define(FuncSymbol('Calc', INTEGER, [VarSymbol('x', INTEGER), VarSymbol('y', INTEGER)]))
    symtab.define(FuncSymbol('Suma', INTEGER, [VarSymbol('a', INTEGER), VarSymbol('b', INTEGER), VarSymbol('c', INTEGER)]))

    em = Emitter()
    em.emit('LABEL', dst='func_Calc')
    em.emit('MUL', dst='t0', a='x', b='y')
    em.emit('STORE', dst='r', a='t0')
    em.emit('RET', dst='t0')

    em.emit('LABEL', dst='func_Suma')
    em.emit('LOAD', dst='t1', a='a')
    em.emit('LOAD', dst='t2', a='b')
    em.emit('ARG', a='t1')
    em.emit('ARG', a='t2')
    em.emit('CALL', dst='t3', a='func_Calc')
    em.emit('STORE', dst='z', a='t3')
    em.emit('LOAD', dst='t4', a='z')
    em.emit('LOAD', dst='t5', a='c')
    em.emit('ADD', dst='t6', a='t4', b='t5')
    em.emit('STORE', dst='t', a='t6')
    em.emit('RET', dst='t6')

    em.emit('ARG', a='2')
    em.emit('ARG', a='3')
    em.emit('ARG', a='4')
    em.emit('CALL', dst='t7', a='func_Suma')
    em.emit('STORE', dst='res', a='t7')

    out = emit_mips(em, symtab=symtab)

    # parámetros se cargan desde offsets positivos (argumentos) y se guardan en slots locales
    assert 'ARG0_OFF' not in out and 'ARG1_OFF' not in out and 'ARG2_OFF' not in out
    assert re.search(r"func_Calc:\n(?:.*\n)+\s+lw \$t8, \d+\(\$fp\)", out)
    assert re.search(r"func_Suma:\n(?:.*\n)+\s+lw \$t8, \d+\(\$fp\)", out)
    # variables locales y spills usan offsets negativos
    assert re.search(r"-\d+\(\$fp\)", out)
    # la sección .data debe incluir la variable global
    assert '.data' in out and 'res: .word 0' in out
