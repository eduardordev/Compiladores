"""Simple TAC -> MIPS backend (MVP).

This backend implements a conservative mapping:
- temporals t0.. -> $t0.. registers
- variables (identifiers not starting with 't') -> global labels in .data
- CALL/ARG/RET: simple calling convention using stack and $v0
- Functions get a small prologue/epilogue

This is an incremental implementation for testing and demonstration.
"""
from typing import List, Optional
from codegen.tac import Instr, Emitter
import os


class MIPSBackend:
    def __init__(self):
        # map temporary names like 't0' -> '$t0'
        self.temp_map = {}
        # registers available for temporals: $t0..$t9
        self.reg_pool = [f"$t{i}" for i in range(10)]
        self.reg_usage = {reg: None for reg in self.reg_pool}  # reg -> temp name or None
        self.spill_map = {}  # temp name -> stack offset
        self.spill_offset = 0
        self.global_vars = set()
        self.lines: List[str] = []
        self.frame_size_map = {}  # function label -> frame size (rough)

    def reg_for_temp(self, tname: str) -> str:
        # Si ya está asignado, devuelve el registro
        for reg, temp in self.reg_usage.items():
            if temp == tname:
                return reg
        # Busca registro libre
        for reg, temp in self.reg_usage.items():
            if temp is None:
                self.reg_usage[reg] = tname
                return reg
        # Si no hay registro libre, realiza spilling
        # Asigna offset en stack si no existe
        if tname not in self.spill_map:
            self.spill_offset += 4
            self.spill_map[tname] = self.spill_offset
        # Usa $t9 como registro temporal para cargar/spillear
        spill_reg = "$t9"
        self.emit(f"    lw {spill_reg}, {self.spill_map[tname]}($sp)")
        return spill_reg

    def free_temp(self, tname: str):
        # Libera el registro asociado al temporal SOLO si ya no se usará más
        for reg, temp in self.reg_usage.items():
            if temp == tname:
                self.reg_usage[reg] = None
                # Spillea el valor si fue usado
                if tname in self.spill_map:
                    self.emit(f"    sw {reg}, {self.spill_map[tname]}($sp)")
                return

    def emit(self, s: str):
        self.lines.append(s)

    def emit_data_for_globals(self):
        if not self.global_vars:
            return
        self.emit('.data')
        for v in sorted(self.global_vars):
            self.emit(f'{v}: .word 0')
        self.emit('')

    def prologue(self, func_label: str):
        # simple fixed-size frame
        size = 32
        self.frame_size_map[func_label] = size
        # Forzar etiqueta principal como 'main:'
        if func_label == 'func_main':
            self.emit('main:')
        else:
            self.emit(f'{func_label}:')
        self.emit(f'    addi $sp, $sp, -{size}')
        self.emit(f'    sw $ra, {size-4}($sp)')
        self.emit(f'    sw $fp, {size-8}($sp)')
        self.emit(f'    move $fp, $sp')

    def epilogue(self, func_label: str):
        size = self.frame_size_map.get(func_label, 32)
        self.emit(f'    move $sp, $fp')
        self.emit(f'    lw $ra, {size-4}($sp)')
        self.emit(f'    lw $fp, {size-8}($sp)')
        self.emit(f'    addi $sp, $sp, {size}')
        self.emit(f'    jr $ra')

    def instr_to_mips(self, instr: Instr, current_func: Optional[str]):
        # Ciclo de vida simple: libera temporales al final de cada instrucción
        # (En un caso real, se haría análisis de liveness)
        op = instr.op
        if op == 'LABEL':
            lbl = instr.dst
            # treat function labels specially
            if lbl.startswith('func_'):
                # emit prologue marker
                self.prologue(lbl)
                return
            self.emit(f'{lbl}:')
            return
        if op == 'GOTO':
            self.emit(f'    j {instr.dst}')
            return
        if op == 'IFZ':
            # IFZ a GOTO dst
            a = instr.a
            # a may be temp or literal
            ra = a if not isinstance(a, str) else self.reg_for_temp(a) if a.startswith('t') else a
            # if ra is a number literal
            if ra.isdigit() or (ra.startswith('-') and ra[1:].isdigit()):
                # load immediate into $t9
                self.emit(f'    li $t9, {ra}')
                self.emit(f'    beq $t9, $zero, {instr.dst}')
            else:
                self.emit(f'    beq {ra}, $zero, {instr.dst}')
            if isinstance(a, str) and a.startswith('t'):
                self.free_temp(a)
            return
        if op == 'STORE':
            # STORE a -> dst
            a = instr.a
            dst = instr.dst
            # if dst looks like temp, store into reg; if identifier, into global memory
            if dst.startswith('t'):
                rdst = self.reg_for_temp(dst)
                if isinstance(a, str) and a.startswith('t'):
                    self.emit(f'    move {rdst}, {self.reg_for_temp(a)}')
                    self.free_temp(a)
                else:
                    # immediate or var
                    if isinstance(a, str) and a.isdigit():
                        self.emit(f'    li {rdst}, {a}')
                    else:
                        # load from global
                        self.emit(f'    lw {rdst}, {a}')
            else:
                # store to global variable
                self.global_vars.add(dst)
                if isinstance(a, str) and a.startswith('t'):
                    self.emit(f'    sw {self.reg_for_temp(a)}, {dst}')
                    self.free_temp(a)
                else:
                    # immediate
                    if isinstance(a, str) and a.isdigit():
                        self.emit(f'    li $t9, {a}')
                        self.emit(f'    sw $t9, {dst}')
                    else:
                        self.emit(f'    sw {a}, {dst}')
            if dst.startswith('t'):
                self.free_temp(dst)
            return
        if op == 'LOAD':
            dst = instr.dst
            a = instr.a
            if dst and dst.startswith('t'):
                rd = self.reg_for_temp(dst)
                # a may be identifier
                if isinstance(a, str) and a.isdigit():
                    self.emit(f'    li {rd}, {a}')
                else:
                    self.global_vars.add(a)
                    self.emit(f'    lw {rd}, {a}')
            if dst and dst.startswith('t'):
                self.free_temp(dst)
            return
        if op in ('ADD', 'SUB', 'MUL', 'DIV'):
            dst = instr.dst
            a = instr.a
            b = instr.b
            rd = self.reg_for_temp(dst) if dst else '$t0'
            ra = self.reg_for_temp(a) if isinstance(a, str) and a.startswith('t') else (f'$t9' if isinstance(a,str) and a.isdigit() else a)
            rb = self.reg_for_temp(b) if isinstance(b, str) and b.startswith('t') else (f'$t8' if isinstance(b,str) and b.isdigit() else b)
            # handle immediates by loading into temp regs
            if isinstance(a, str) and a.isdigit():
                self.emit(f'    li $t9, {a}')
                ra = '$t9'
            if isinstance(b, str) and b.isdigit():
                self.emit(f'    li $t8, {b}')
                rb = '$t8'
            mop = {'ADD':'add','SUB':'sub','MUL':'mul','DIV':'div'}[op]
            # div in MIPS places quotient in LO; use div then mflo
            if op == 'DIV':
                self.emit(f'    div {ra}, {rb}')
                self.emit(f'    mflo {rd}')
            else:
                self.emit(f'    {mop} {rd}, {ra}, {rb}')
            # Liberar solo los operandos, NO el resultado
            if isinstance(a, str) and a.startswith('t') and a != dst:
                self.free_temp(a)
            if isinstance(b, str) and b.startswith('t') and b != dst:
                self.free_temp(b)
            # El resultado (dst) se mantiene hasta que se sobrescriba o se use en otra instrucción
            return

    def emit_from_emitter(self, emitter: Emitter, out_path: Optional[str]=None) -> str:
        # Escanear para detectar variables globales primero
        for instr in emitter.instrs:
            if instr.op == 'STORE' and not instr.dst.startswith('t'):
                self.global_vars.add(instr.dst)
            elif instr.op == 'LOAD' and isinstance(instr.a, str) and not instr.a.isdigit() and not instr.a.startswith('t'):
                self.global_vars.add(instr.a)
        
        # Emitir sección de datos
        self.emit_data_for_globals()
        
        # Emitir sección de código
        self.emit('.text')
        self.emit('.globl main')
        self.emit('')
        
        # Procesar instrucciones
        current_func = None
        for instr in emitter.instrs:
            if instr.op == 'LABEL' and instr.dst and instr.dst.startswith('func_'):
                current_func = instr.dst
            self.instr_to_mips(instr, current_func)
        
        # Emitir epilogos de funciones
        for f in list(self.frame_size_map.keys()):
            self.epilogue(f)
        
        # Unir todas las líneas
        out = '\n'.join(self.lines)
        
        if out_path:
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(out)
        
        return out


def emit_mips(emitter: Emitter, symtab=None, out_path: Optional[str]=None) -> str:
    backend = MIPSBackend()
    return backend.emit_from_emitter(emitter, out_path)