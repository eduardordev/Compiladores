from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Tuple

from codegen.tac import Instr, Emitter
from semantic.symbols import FuncSymbol, SymbolTable, VarSymbol


def is_int(value: Optional[str]) -> bool:
    try:
        int(value)  # type: ignore[arg-type]
        return True
    except Exception:
        return False


def is_temp_name(name: Optional[str]) -> bool:
    return bool(name and re.fullmatch(r"t\d+", name))


@dataclass
class TempLocation:
    kind: str  # 'reg' or 'spill'
    ref: str | int  # register name or offset


@dataclass
class FunctionContext:
    name: str
    reg_pool: List[str]
    temp_locations: Dict[str, TempLocation] = field(default_factory=dict)
    spill_count: int = 0
    local_count: int = 0
    var_slots: Dict[str, int] = field(default_factory=dict)
    param_names: List[str] = field(default_factory=list)
    param_patches: List[Tuple[int, int]] = field(default_factory=list)
    end_label: str = field(init=False)
    prologue_indices: Tuple[int, int, int] | None = None
    arg_bytes: int = 0

    def __post_init__(self) -> None:
        self.end_label = f"{self.name}_end"

    def alloc_temp(self, tname: str) -> TempLocation:
        if tname in self.temp_locations:
            return self.temp_locations[tname]
        if self.reg_pool:
            reg = self.reg_pool.pop(0)
            loc = TempLocation('reg', reg)
        else:
            self.spill_count += 1
            offset = -4 * self.spill_count
            loc = TempLocation('spill', offset)
        self.temp_locations[tname] = loc
        return loc

    def alloc_var_slot(self, vname: str) -> int:
        if vname in self.var_slots:
            return self.var_slots[vname]
        self.local_count += 1
        offset = -4 * self.local_count
        self.var_slots[vname] = offset
        return offset

    def location(self, tname: str) -> TempLocation:
        return self.alloc_temp(tname)

    @property
    def frame_size(self) -> int:
        # 8 bytes for saved $ra/$fp plus space for spills/locals.
        return 8 + max(self.spill_count, self.local_count) * 4


class MIPSBackend:
    SCRATCH_A = "$t8"
    SCRATCH_B = "$t9"
    SCRATCH_RES = "$t7"

    def __init__(self, symtab: Optional[SymbolTable] = None):
        self.symtab = symtab
        self.global_vars: set[str] = set()
        self.global_known: set[str] = set()
        self.lines: List[str] = []
        self.current_func: Optional[FunctionContext] = None
        # $t0-$t6 se usan para temporales; $t7/$t8/$t9 quedan como scratch.
        self.base_reg_pool = [f"$t{i}" for i in range(7)]
        self.pending_arg_bytes = 0
        if symtab:
            try:
                for sym in symtab.scopes[0].symbols.values():
                    if isinstance(sym, VarSymbol):
                        self.global_known.add(sym.name)
            except Exception:
                pass

    # --- utilidades de emisión ---
    def emit(self, line: str) -> None:
        self.lines.append(line)

    def start_function(self, label: str) -> None:
        # Finalizar la función previa, si existe.
        if self.current_func:
            self.finish_function()

        ctx = FunctionContext(label, list(self.base_reg_pool))
        ctx.param_names = self.lookup_params(label)
        self.current_func = ctx
        self.emit(f"{label}:")
        base = len(self.lines)
        # Placeholders de frame: se rellenan en finish_function.
        self.emit("    addi $sp, $sp, -FRAME")
        self.emit("    sw $ra, FRAME-4($sp)")
        self.emit("    sw $fp, FRAME-8($sp)")
        self.emit("    move $fp, $sp")
        ctx.prologue_indices = (base, base + 1, base + 2)
        # Cargar parámetros a slots locales para accederlos como variables.
        for idx, pname in enumerate(ctx.param_names):
            slot = ctx.alloc_var_slot(pname)
            load_idx = len(self.lines)
            self.emit(f"    lw {self.SCRATCH_A}, ARG{idx}_OFF($fp)")
            self.emit(f"    sw {self.SCRATCH_A}, {slot}($fp)")
            ctx.param_patches.append((load_idx, idx))

    def finish_function(self) -> None:
        ctx = self.current_func
        if not ctx:
            return
        size = ctx.frame_size
        # parchear offsets de parámetros
        for line_idx, pidx in ctx.param_patches:
            arg_off = size + 4 * (len(ctx.param_names) - pidx - 1)
            self.lines[line_idx] = self.lines[line_idx].replace(f"ARG{pidx}_OFF", str(arg_off))
        # Completar placeholders del prólogo.
        p0, p1, p2 = ctx.prologue_indices or (None, None, None)
        if p0 is not None:
            self.lines[p0] = f"    addi $sp, $sp, -{size}"
        if p1 is not None:
            self.lines[p1] = f"    sw $ra, {size-4}($sp)"
        if p2 is not None:
            self.lines[p2] = f"    sw $fp, {size-8}($sp)"

        # Epílogo único por función.
        self.emit(f"{ctx.end_label}:")
        self.emit("    move $sp, $fp")
        self.emit(f"    lw $ra, {size-4}($sp)")
        self.emit(f"    lw $fp, {size-8}($sp)")
        self.emit(f"    addi $sp, $sp, {size}")
        self.emit("    jr $ra")
        self.emit("")
        self.current_func = None

    # --- helpers de operandos ---
    def ensure_context(self) -> FunctionContext:
        if not self.current_func:
            # Crear una función sintética para código global.
            self.start_function("main")
        return self.current_func  # type: ignore[return-value]

    def lookup_params(self, label: str) -> List[str]:
        """Devuelve la lista de parámetros de la función asociada al label func_<name>."""
        if not hasattr(self, "global_known"):
            return []
        fname = label.replace("func_", "", 1) if label.startswith("func_") else label
        params: List[str] = []
        try:
            # symtab global scope define functions
            for sym in getattr(getattr(self, 'symtab', None), 'scopes', [{}])[0].symbols.values():
                if isinstance(sym, FuncSymbol) and sym.name == fname:
                    params = [p.name for p in sym.params]
                    break
        except Exception:
            pass
        return params

    def location_for_temp(self, temp: str) -> TempLocation:
        ctx = self.ensure_context()
        return ctx.location(temp)

    def slot_for_var(self, name: str) -> Optional[int]:
        ctx = self.current_func
        if ctx and name in ctx.var_slots:
            return ctx.var_slots[name]
        if ctx and name in ctx.param_names:
            return ctx.alloc_var_slot(name)
        return None

    def load_operand(self, op: Optional[str], scratch: str) -> str:
        """Devuelve un registro que contiene el operando op."""
        if op is None:
            return scratch
        if is_temp_name(op):
            loc = self.location_for_temp(op)
            if loc.kind == 'reg':
                return loc.ref  # type: ignore[return-value]
            self.emit(f"    lw {scratch}, {loc.ref}($fp)")
            return scratch
        if op in self.global_known:
            self.global_vars.add(op)
            self.emit(f"    lw {scratch}, {op}")
            return scratch
        if self.current_func:
            slot = self.slot_for_var(op)
            if slot is not None:
                self.emit(f"    lw {scratch}, {slot}($fp)")
                return scratch
        if is_int(op):
            self.emit(f"    li {scratch}, {op}")
            return scratch
        # Asumir identificador global.
        # si no se conoce, considerar global por defecto
        self.global_vars.add(op)
        self.emit(f"    lw {scratch}, {op}")
        return scratch

    def store_into(self, dst: Optional[str], src_reg: str) -> None:
        if dst is None:
            return
        if is_temp_name(dst):
            loc = self.location_for_temp(dst)
            if loc.kind == 'reg':
                if loc.ref != src_reg:
                    self.emit(f"    move {loc.ref}, {src_reg}")
            else:
                self.emit(f"    sw {src_reg}, {loc.ref}($fp)")
            return
        if dst in self.global_known:
            self.global_vars.add(dst)
            self.emit(f"    sw {src_reg}, {dst}")
            return
        if self.current_func:
            slot = self.slot_for_var(dst)
            if slot is None:
                slot = self.current_func.alloc_var_slot(dst)
            self.emit(f"    sw {src_reg}, {slot}($fp)")
            return
        self.global_vars.add(dst)
        self.emit(f"    sw {src_reg}, {dst}")

    # --- traducción de instrucciones ---
    def handle_ifz(self, instr: Instr) -> None:
        reg = self.load_operand(instr.a, self.SCRATCH_A)
        self.emit(f"    beq {reg}, $zero, {instr.dst}")

    def handle_binary(self, instr: Instr) -> None:
        op_map = {'ADD': 'add', 'SUB': 'sub', 'MUL': 'mul', 'DIV': 'div'}
        ra = self.load_operand(instr.a, self.SCRATCH_A)
        rb = self.load_operand(instr.b, self.SCRATCH_B)
        dst_loc = self.location_for_temp(instr.dst or "t0")
        target = dst_loc.ref if dst_loc.kind == 'reg' else self.SCRATCH_RES

        mop = op_map[instr.op]
        if instr.op == 'DIV':
            self.emit(f"    {mop} {ra}, {rb}")
            self.emit(f"    mflo {target}")
        elif instr.op == 'MUL':
            self.emit(f"    {mop} {target}, {ra}, {rb}")
        else:
            self.emit(f"    {mop} {target}, {ra}, {rb}")

        self.store_into(instr.dst, target)

    def handle_store(self, instr: Instr) -> None:
        reg = self.load_operand(instr.a, self.SCRATCH_A)
        self.store_into(instr.dst, reg)

    def handle_load(self, instr: Instr) -> None:
        reg = self.load_operand(instr.a, self.SCRATCH_A)
        self.store_into(instr.dst, reg)

    def handle_arg(self, instr: Instr) -> None:
        reg = self.load_operand(instr.a, self.SCRATCH_A)
        self.emit("    addi $sp, $sp, -4")
        self.emit(f"    sw {reg}, 0($sp)")
        self.pending_arg_bytes += 4

    def handle_call(self, instr: Instr) -> None:
        self.emit(f"    jal {instr.a}")
        if instr.dst:
            self.store_into(instr.dst, "$v0")
        if self.pending_arg_bytes:
            self.emit(f"    addi $sp, $sp, {self.pending_arg_bytes}")
            self.pending_arg_bytes = 0

    def handle_ret(self, instr: Instr) -> None:
        if instr.dst is not None:
            reg = self.load_operand(instr.dst, "$v0")
            if reg != "$v0":
                self.emit(f"    move $v0, {reg}")
        ctx = self.ensure_context()
        self.emit(f"    j {ctx.end_label}")

    def instr_to_mips(self, instr: Instr) -> None:
        op = instr.op
        if op == 'LABEL':
            lbl = instr.dst or ''
            if lbl.startswith('func_'):
                self.start_function(lbl)
            else:
                self.emit(f"{lbl}:")
            return
        if op == 'GOTO':
            self.emit(f"    j {instr.dst}")
            return
        if op == 'IFZ':
            self.handle_ifz(instr)
            return
        if op == 'STORE':
            self.handle_store(instr)
            return
        if op == 'LOAD':
            self.handle_load(instr)
            return
        if op in {'ADD', 'SUB', 'MUL', 'DIV'}:
            self.handle_binary(instr)
            return
        if op == 'RET':
            self.handle_ret(instr)
            return
        if op == 'ARG':
            self.handle_arg(instr)
            return
        if op == 'CALL':
            self.handle_call(instr)
            return

    # --- entrada principal ---
    def emit_from_emitter(self, emitter: Emitter, out_path: Optional[str] = None) -> str:
        for instr in emitter.instrs:
            self.instr_to_mips(instr)

        # Finalizar función en curso.
        if self.current_func:
            self.finish_function()

        data_lines: List[str] = []
        if self.global_vars:
            data_lines.append('.data')
            for v in sorted(self.global_vars):
                data_lines.append(f"{v}: .word 0")
            data_lines.append('')

        out_lines = data_lines + ['.text'] + self.lines
        out = '\n'.join(out_lines)
        if out_path:
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(out)
        return out


def emit_mips(emitter: Emitter, symtab=None, out_path: Optional[str] = None) -> str:
    backend = MIPSBackend(symtab)
    return backend.emit_from_emitter(emitter, out_path)
