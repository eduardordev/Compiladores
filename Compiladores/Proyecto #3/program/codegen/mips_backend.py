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
        # Libera el registro asociado al temporal
        for reg, temp in self.reg_usage.items():
            if temp == tname:
                self.reg_usage[reg] = None
                # Spillea el valor si fue usado
                self.emit(f"    sw {reg}, {self.spill_map.get(tname, 0)}($sp)")
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
            class MIPSBackend:
                def __init__(self):
                    self.lines = []
                    self.data_lines = []
                    self.temporals = set()
                    self.label_count = 0
                    self.registers = [f'$t{i}' for i in range(10)]
                    self.reg_map = {}
                    self.reg_usage = {}
                    self.spill_map = {}
                    self.spill_count = 0
                    self.used_temporals = set()
                    self.func_label = None
                    self.in_func = False
                    self.func_stack = []
                    self.var_map = {}
                    self.var_order = []
                    self.return_var = None
                    self.main_label = None
                # ...existing code...
                def emit_func(self, name):
                    # Si es main, usar 'main:' y marcar como global
                    if name == 'main':
                        self.func_label = 'main'
                        self.main_label = 'main'
                        self.lines.append('main:')
                    else:
                        label = f'func_{name}'
                        self.func_label = label
                        self.lines.append(f'{label}:')
                    self.in_func = True
                    self.lines.append('    addi $sp, $sp, -32')
                    self.lines.append('    sw $ra, 28($sp)')
                    self.lines.append('    sw $fp, 24($sp)')
                    self.lines.append('    move $fp, $sp')
                # ...existing code...
                def emit(self):
                    out = []
                    out.append('.data')
                    for line in self.data_lines:
                        out.append(line)
                    out.append('.text')
                    # Siempre agregar .globl main
                    out.append('.globl main')
                    for line in self.lines:
                        out.append(line)
                    return '\n'.join(out)
                    # Eliminar código muerto y corregir indentación inesperada

    def emit_from_emitter(self, emitter: Emitter, out_path: Optional[str]=None) -> str:
        # scan emitter for labels and global vars
        current_func = None
        for instr in emitter.instrs:
            # simple detection of function label
            if instr.op == 'LABEL' and instr.dst and instr.dst.startswith('func_'):
                current_func = instr.dst
            self.instr_to_mips(instr, current_func)
            # if label was a function, after finishing func body we should emit epilogue
            if instr.op == 'LABEL' and instr.dst and instr.dst.startswith('func_'):
                # placeholder: epilogue will be emitted when RET encountered; but ensure at end
                pass

        # emit epilogue for any function if not present: naive approach - append epilogue at end
        for f in list(self.frame_size_map.keys()):
            self.epilogue(f)

        # Usar el método emit() para salida final
        out = self.emit()
        if out_path:
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(out)
        return out


def emit_mips(emitter: Emitter, symtab=None, out_path: Optional[str]=None) -> str:
    backend = MIPSBackend()
    return backend.emit_from_emitter(emitter, out_path)
