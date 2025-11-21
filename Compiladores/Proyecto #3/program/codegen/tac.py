"""
TAC (Three Address Code) emitter.
Genera instrucciones de tres direcciones con reciclaje de temporales y etiquetas.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Instr:
    op: str
    dst: Optional[str] = None
    a: Optional[str] = None
    b: Optional[str] = None

    def __str__(self):
        if self.op == "LABEL":
            return f"{self.dst}:"
        if self.op == "GOTO":
            return f"GOTO {self.dst}"
        if self.op == "IFZ":
            return f"IFZ {self.a} GOTO {self.dst}"
        if self.op == "ARG":
            return f"ARG {self.a}"
        if self.op == "CALL":
            # CALL f  or dst = CALL f
            if self.dst:
                return f"{self.dst} = CALL {self.a}"
            return f"CALL {self.a}"
        if self.op == "STORE":
            return f"STORE {self.a} -> {self.dst}"
        if self.op == "LOAD":
            return f"{self.dst} = LOAD {self.a}"
        if self.op == "NEWOBJ":
            # NEWOBJ dst, ClassName
            return f"NEWOBJ {self.dst}, {self.a}"
        if self.op == "GETPROP":
            # GETPROP dst, obj, prop
            return f"GETPROP {self.dst}, {self.a}, {self.b}"
        if self.op == "SETPROP":
            # SETPROP obj, prop, value
            return f"SETPROP {self.dst}, {self.a}, {self.b}"
        if self.op == "RET":
            return f"RETURN {self.dst or ''}".strip()
        if self.b:
            return f"{self.dst} = {self.a} {self.op} {self.b}"
        if self.a:
            return f"{self.dst} = {self.op} {self.a}"
        return f"{self.dst} = {self.op}"


class Emitter:
    def __init__(self):
        self.instrs: List[Instr] = []
        self.temp_counter = 0
        self.free_temps: List[str] = []
        self.label_counter = 0

    def emit(self, op, dst=None, a=None, b=None):
        self.instrs.append(Instr(op, dst, a, b))

    def new_temp(self):
        if self.free_temps:
            return self.free_temps.pop()
        t = f"t{self.temp_counter}"
        self.temp_counter += 1
        return t

    def free_temp(self, t):
        if isinstance(t, str) and t.startswith("t"):
            self.free_temps.append(t)

    def new_label(self):
        lbl = f"L{self.label_counter}"
        self.label_counter += 1
        return lbl

    def __str__(self):
        return "\n".join(str(i) for i in self.instrs) if self.instrs else "(sin instrucciones TAC)"
