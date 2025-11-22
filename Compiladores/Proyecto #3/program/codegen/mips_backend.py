from typing import List, Dict, Optional
from codegen.tac import Instr, Emitter

class MIPSBackend:
    def __init__(self) -> None:
        # líneas de código de la sección .text
        self.text_lines: List[str] = []
        # nombres de variables globales detectadas
        self.global_vars = set()
        # literales de string: texto -> label
        self.string_literals: Dict[str, str] = {}
        self.next_string_id: int = 0

        # campos de objetos: nombre_campo -> offset en bytes
        self.field_offsets: Dict[str, int] = {}
        self.next_field_offset: int = 0  # en bytes

        # si se detecta uso de heap (NEWOBJ o ALLOC)
        self.uses_heap: bool = False

        # estado de funciones
        self.current_func: Optional[str] = None
        self.has_main: bool = False

        # argumentos pendientes antes de un CALL
        self.pending_args: List[str] = []

        # arreglos/variables inicializados en .data
        self.static_arrays = {}

    def emit(self, line: str) -> None:
        """Agrega una línea al código .text."""
        self.text_lines.append(line)

    def is_temp(self, name: Optional[str]) -> bool:
        return isinstance(name, str) and name.startswith("t") and name[1:].isdigit()

    def is_immediate(self, x: Optional[str]) -> bool:
        if not isinstance(x, str):
            return False
        if x.isdigit():
            return True
        if x.startswith("-") and x[1:].isdigit():
            return True
        return False

    def is_string_literal(self, x: Optional[str]) -> bool:
        # Heurística: en tu TAC los strings suelen venir entre comillas
        return isinstance(x, str) and len(x) >= 2 and x[0] == '"' and x[-1] == '"'

    def temp_reg(self, tname: str) -> str:
        """Mapea t0, t1, ... a $t0..$t9 (cíclico)."""
        try:
            n = int(tname[1:])
        except ValueError:
            n = 0
        n = n % 10
        return f"$t{n}"

    def ensure_global(self, name: str) -> None:
        """Registra un nombre como variable global si no es temp, ni literal, ni None."""
        if not isinstance(name, str):
            return
        if self.is_temp(name):
            return
        if self.is_immediate(name):
            return
        if self.is_string_literal(name):
            return
        if name in ("None", "", None):
            return
        # parámetros como "arg0" los tratamos como globales por simplicidad
        self.global_vars.add(name)

    def string_label_for(self, literal: str) -> str:
        """Devuelve etiqueta de .data para un literal de string."""
        if literal in self.string_literals:
            return self.string_literals[literal]
        label = f"__str{self.next_string_id}"
        self.next_string_id += 1
        self.string_literals[literal] = label
        return label

    def field_offset(self, field_name: str) -> int:
        """Devuelve offset en bytes para un campo de objeto (global, no por clase)."""
        if field_name not in self.field_offsets:
            self.field_offsets[field_name] = self.next_field_offset
            self.next_field_offset += 4
        return self.field_offsets[field_name]


    def load_operand_to_reg(self, operand: str, target_reg: str, is_array: bool = False) -> str:
        """
        Garantiza que 'operand' quede en 'target_reg'. Devuelve el registro
        donde quedó el valor (normalmente target_reg).
        """
        if self.is_temp(operand):
            reg = self.temp_reg(operand)
            if reg != target_reg:
                self.emit(f"    move {target_reg}, {reg}")
            return target_reg
        elif self.is_immediate(operand):
            self.emit(f"    li {target_reg}, {operand}")
            return target_reg
        elif self.is_string_literal(operand):
            lbl = self.string_label_for(operand)
            self.emit(f"    la {target_reg}, {lbl}")
            return target_reg
        else:
            # variable global
            self.ensure_global(operand)
            if is_array:
                self.emit(f"    la {target_reg}, {operand}")
            else:
                self.emit(f"    lw {target_reg}, {operand}")
            return target_reg

    def is_temp_addr(self, name: Optional[str]) -> bool:
        # Heurística: si es un temporal (tN) lo tratamos como dirección calculada
        return self.is_temp(name)

    def is_static_array(self, name: str) -> bool:
        """Verifica si un nombre es un array estático"""
        # Necesitamos pasar static_arrays como atributo de la clase
        return hasattr(self, 'static_arrays') and name in self.static_arrays


    def emit_epilogue(self):
        """Emite el epílogo estándar para main o funciones."""
        self.emit("    move $sp, $fp")
        self.emit("    lw $ra, 28($sp)")
        self.emit("    lw $fp, 24($sp)")
        self.emit("    addi $sp, $sp, 32")
        self.emit("    jr $ra")

    # ---------------------------------------------------------
    # ACA PASA LA MAGIA DEL TAC
    # ---------------------------------------------------------
    def instr_to_mips(self, instr: Instr) -> None:
        op = instr.op
        dst = getattr(instr, "dst", None)
        a = getattr(instr, "a", None)
        b = getattr(instr, "b", None)

        # ---------- Relacionales ----------
        if op in ("EQ", "NE", "LT", "LE", "GT", "GE"):
            if dst is None or not self.is_temp(dst):
                return

            rd = self.temp_reg(dst)
            ra = self.load_operand_to_reg(a, "$t9")
            rb = self.load_operand_to_reg(b, "$t8")

            if op == "EQ":
                self.emit(f"    seq {rd}, {ra}, {rb}")
            elif op == "NE":
                self.emit(f"    sne {rd}, {ra}, {rb}")
            elif op == "LT":
                self.emit(f"    slt {rd}, {ra}, {rb}")
            elif op == "LE":
                self.emit(f"    sle {rd}, {ra}, {rb}")
            elif op == "GT":
                self.emit(f"    sgt {rd}, {ra}, {rb}")
            elif op == "GE":
                self.emit(f"    sge {rd}, {ra}, {rb}")

            return

        # ---------- Lógicos ----------
        if op in ("AND", "OR"):
            if dst is None or not self.is_temp(dst):
                return

            rd = self.temp_reg(dst)
            ra = self.load_operand_to_reg(a, "$t9")
            rb = self.load_operand_to_reg(b, "$t8")

            if op == "AND":
                self.emit(f"    and {rd}, {ra}, {rb}")
            elif op == "OR":
                self.emit(f"    or {rd}, {ra}, {rb}")

            return

        # ---------- NOT ----------
        if op == "NOT":
            if dst is None or not self.is_temp(dst):
                return

            rd = self.temp_reg(dst)
            ra = self.load_operand_to_reg(a, "$t9")
            self.emit(f"    seq {rd}, {ra}, $zero")
            return

        # Soporte para CALL con asignación: tX = CALL foo
        if op == "CALL" and dst is not None and dst not in ("None", ""):
            # Llama como siempre, pero mueve el resultado a dst
            # Simula como si fuera CALL a; dst = $v0
            # Llama a la función normalmente
            self.instr_to_mips(Instr("CALL", a=a))
            if self.is_temp(dst):
                rd = self.temp_reg(dst)
                self.emit(f"    move {rd}, $v0")
            else:
                self.ensure_global(dst)
                self.emit(f"    sw $v0, {dst}")
            return

        # Soporte para PRINT con asignación a None: None = PRINT t1
        if op == "PRINT" and dst == "None":
            # Ejecuta como PRINT normal
            instr2 = Instr("PRINT", a=a)
            self.instr_to_mips(instr2)
            return

        # Soporte para tX = LOAD var o tX = LOAD t_addr (acceso a memoria)
        if op == "LOAD" and dst is not None and self.is_temp(dst):
            rd = self.temp_reg(dst)
            if a is None:
                return
            if self.is_immediate(a) or self.is_string_literal(a):
                self.load_operand_to_reg(a, rd)
            elif self.is_temp_addr(a):
                reg_addr = self.temp_reg(a)
                self.emit(f"    lw {rd}, 0({reg_addr})")
            else:
                is_arr = self.is_static_array(a)
                self.ensure_global(a)
                if is_arr:
                    self.emit(f"    la {rd}, {a}")  # Load address para arrays
                else:
                    self.emit(f"    lw {rd}, {a}")  # Load word para variables normales
            return

        # Soporte para tX = GETPROP tY, campo
        if op == "GETPROP" and dst is not None and self.is_temp(dst):
            # Espera: GETPROP dst, obj, campo
            # Si a y b no están, pero hay un campo extra, intenta extraerlo
            if a is not None and b is not None:
                rd = self.temp_reg(dst)
                obj = a
                field = b
                offset = self.field_offset(field)
                self.load_operand_to_reg(obj, "$t9")
                if offset != 0:
                    self.emit(f"    addi $t9, $t9, {offset}")
                self.emit(f"    lw {rd}, 0($t9)")
                return

        # Soporte para SETPROP tY, campo, tX
        if op == "SETPROP" and a is not None and b is not None and dst is not None:
            obj = a
            field = b
            val = dst
            offset = self.field_offset(field)
            self.load_operand_to_reg(obj, "$t9")
            if offset != 0:
                self.emit(f"    addi $t9, $t9, {offset}")
            reg_val = self.load_operand_to_reg(val, "$t8")
            if reg_val != "$t8":
                self.emit(f"    move $t8, {reg_val}")
            self.emit("    sw $t8, 0($t9)")
            return

        # ---------- LABEL ----------
        if op == "LABEL":
            lbl = dst
            if not lbl:
                return

            if lbl.startswith("func_") or lbl.startswith("method_"):
                self.current_func = lbl
                if lbl == "func_main":
                    self.has_main = True
                    self.emit("main:")
                else:
                    self.emit(f"{lbl}:")
                # prologue estándar para TODA función
                self.emit("    addi $sp, $sp, -32")
                self.emit("    sw $ra, 28($sp)")
                self.emit("    sw $fp, 24($sp)")
                self.emit("    move $fp, $sp")
                # Si es un constructor (newClase), reservar heap aquí
                if lbl.startswith("func_new") or lbl.startswith("method_new"):
                    self.emit("    lw $t9, heap_ptr")
                    self.emit("    move $v0, $t9")
                    self.emit("    addi $t9, $t9, 32")
                    self.emit("    sw $t9, heap_ptr")
            else:
                self.emit(f"{lbl}:")
            return
        # ---------- GOTO ----------
        if op == "GOTO":
            if dst:
                self.emit(f"    j {dst}")
            return

        # ---------- IFZ ----------
        if op == "IFZ":
            # if a == 0: goto dst
            if a is None or dst is None:
                return
            reg = self.load_operand_to_reg(a, "$t9")
            # Salta si la condición es falsa (a == 0)
            self.emit(f"    beq {reg}, $zero, {dst}")
            # El flujo sigue al bloque if si la condición es verdadera
            return
        # ---------- STORE ----------
        if op == "STORE":
            if dst is None:
                return
            
        # IGNORAR STORE a arrays estáticos
        if hasattr(self, 'static_arrays') and dst in self.static_arrays:
            return  # No emitir nada para arrays estáticos
    
            # dst = a   (asignación a temporal)
            if self.is_temp(dst):
                rd = self.temp_reg(dst)
                if a is None:
                    return
                self.load_operand_to_reg(a, rd)
                return

            # Si dst es un temporal (dirección calculada), acceso a memoria (arreglo)
            if self.is_temp_addr(dst):
                reg_addr = self.temp_reg(dst)
                reg_val = self.load_operand_to_reg(a, "$t9")
                self.emit(f"    sw {reg_val}, 0({reg_addr})")
                return

            # global = a
            self.ensure_global(dst)
            # Si la variable global ya está inicializada en .data y a == 0, NO sobrescribas
            if hasattr(self, 'static_arrays') and dst in self.static_arrays:
                return
            if a is None:
                return
            # Si la variable global es un arreglo inicializado, no sobrescribas
            if hasattr(self, 'static_arrays') and dst in self.static_arrays:
                return
            reg = self.load_operand_to_reg(a, "$t9")
            self.emit(f"    sw {reg}, {dst}")
            return

        # ---------- LOAD ----------
        if op == "LOAD":
            # LOAD dst, a   => dst = contenido de variable global a
            if dst is None or not self.is_temp(dst):
                return
            rd = self.temp_reg(dst)
            if a is None:
                return
            if self.is_immediate(a) or self.is_string_literal(a):
                # caso degenerado: lo tratamos como literal
                self.load_operand_to_reg(a, rd)
            else:
                self.ensure_global(a)
                self.emit(f"    lw {rd}, {a}")
            return

        # ---------- Aritmética ----------
        if op in ("ADD", "SUB", "MUL", "DIV"):
            if dst is None or not self.is_temp(dst):
                return
            rd = self.temp_reg(dst)

            if a is None or b is None:
                return

            # Verificar si es array para el primer operando
            is_arr_a = not self.is_temp(a) and not self.is_immediate(a) and self.is_static_array(a)
            is_arr_b = not self.is_temp(b) and not self.is_immediate(b) and self.is_static_array(b)

            # cargar operandos a registros
            ra = self.load_operand_to_reg(a, "$t9", is_array=is_arr_a)
            rb = self.load_operand_to_reg(b, "$t8", is_array=is_arr_b)

            if op == "ADD":
                self.emit(f"    add {rd}, {ra}, {rb}")
            elif op == "SUB":
                self.emit(f"    sub {rd}, {ra}, {rb}")
            elif op == "MUL":
                self.emit(f"    mul {rd}, {ra}, {rb}")
            elif op == "DIV":
                self.emit(f"    div {ra}, {rb}")
                self.emit(f"    mflo {rd}")
            return

        # ---------- ARG ----------
        if op == "ARG":
            # vamos acumulando los argumentos hasta ver CALL
            if a is not None:
                self.pending_args.append(a)
            return

        # ---------- CALL ----------
        if op == "CALL":
            func_name = a
            if func_name is None:
                return

            num_args = len(self.pending_args)
            if num_args > 0:
                # reservar espacio para args
                self.emit(f"    addi $sp, $sp, -{4 * num_args}")
                # guardar cada arg en stack
                for idx, arg in enumerate(self.pending_args):
                    reg = self.load_operand_to_reg(arg, "$t9")
                    self.emit(f"    sw {reg}, {idx * 4}($sp)")
            # llamada
            self.emit(f"    jal {func_name}")
            # liberar args
            if num_args > 0:
                self.emit(f"    addi $sp, $sp, {4 * num_args}")
            # resultado en dst si corresponde
            if dst is not None and dst not in ("None", ""):
                # si es temporal
                if self.is_temp(dst):
                    rd = self.temp_reg(dst)
                    self.emit(f"    move {rd}, $v0")
                else:
                    # variable global
                    self.ensure_global(dst)
                    self.emit(f"    sw $v0, {dst}")
            # limpiar lista de args
            self.pending_args = []
            return

        # ---------- RET (RETURN) ----------
        if op == "RET":
            val = dst if dst is not None else a
            if val is not None:
                reg = self.load_operand_to_reg(val, "$v0")
                if reg != "$v0":
                    self.emit(f"    move $v0, {reg}")
            # epílogo profesional
            self.emit_epilogue()
            return

        # ---------- NEWOBJ ----------
        if op == "NEWOBJ":
            # NEWOBJ dst, Clase
            self.uses_heap = True
            return

        # ---------- ALLOC ----------
        if op == "ALLOC":
            # ALLOC dst, a   ; a = número de enteros
            if dst is None or not self.is_temp(dst):
                return
            if a is None:
                return
            self.uses_heap = True
            rd = self.temp_reg(dst)
            # bytes = a * 4
            if self.is_immediate(a):
                bytes_num = int(a) * 4
                self.emit("    lw $t9, heap_ptr")
                self.emit(f"    move {rd}, $t9")
                self.emit(f"    addi $t9, $t9, {bytes_num}")
                self.emit("    sw $t9, heap_ptr")
            else:
                # a en registro
                ra = self.load_operand_to_reg(a, "$t8")
                self.emit("    lw $t9, heap_ptr")
                self.emit(f"    move {rd}, $t9")
                # bytes = a * 4
                self.emit("    sll $t8, $t8, 2")
                self.emit("    add $t9, $t9, $t8")
                self.emit("    sw $t9, heap_ptr")
            return

        # ---------- GETPROP ----------
        if op == "GETPROP":
            # GETPROP dst, obj, campo
            if dst is None or not self.is_temp(dst):
                return
            if a is None or b is None:
                return
            rd = self.temp_reg(dst)
            obj = a
            field = b
            offset = self.field_offset(field)  # bytes
            # cargar puntero obj en $t9
            self.load_operand_to_reg(obj, "$t9")
            if offset != 0:
                self.emit(f"    addi $t9, $t9, {offset}")
            self.emit(f"    lw {rd}, 0($t9)")
            return

        # ---------- SETPROP ----------
        if op == "SETPROP":
            # SETPROP obj, campo, val  (a=obj, b=campo, dst=val)
            if a is None or b is None or dst is None:
                return
            obj = a
            field = b
            val = dst
            offset = self.field_offset(field)
            # obj -> $t9
            self.load_operand_to_reg(obj, "$t9")
            if offset != 0:
                self.emit(f"    addi $t9, $t9, {offset}")
            # val -> $t8
            reg_val = self.load_operand_to_reg(val, "$t8")
            if reg_val != "$t8":
                self.emit(f"    move $t8, {reg_val}")
            self.emit("    sw $t8, 0($t9)")
            return

        # ---------- PRINT ----------
        if op == "PRINT":
            if a is None:
                return
            # Detectar si es string o entero
            if self.is_string_literal(a):
                reg = self.load_operand_to_reg(a, "$a0")
                if reg != "$a0":
                    self.emit(f"    move $a0, {reg}")
                self.emit("    li $v0, 4")
                self.emit("    syscall")
            else:
                reg = self.load_operand_to_reg(a, "$a0")
                if reg != "$a0":
                    self.emit(f"    move $a0, {reg}")
                self.emit("    li $v0, 1")
                self.emit("    syscall")
            return

        # Si llega aquí, es un opcode no soportado explícitamente.
        # Lo ignoramos silenciosamente para no romper el backend.
        return

    def emit_from_emitter(self, emitter: Emitter, out_path: Optional[str] = None, static_arrays: Optional[dict] = None) -> str:
        """Convierte todas las instrucciones TAC en código MIPS."""
        
        self.static_arrays = static_arrays or {}
        
        # recorrer instrucciones TAC
        for instr in emitter.instrs:
            self.instr_to_mips(instr)

        # construir salida final
        out_lines: List[str] = []

        # Sección .data
        out_lines.append(".data")
        
        # ✅ Primero emitir los arrays estáticos
        if static_arrays:
            for name, elems in static_arrays.items():
                elems_str = ", ".join(str(e) for e in elems)
                out_lines.append(f"{name}: .word {elems_str}")
        
        # Luego emitir las variables globales normales
        for name in sorted(self.global_vars):
            # ✅ Saltar si ya está en static_arrays
            if static_arrays and name in static_arrays:
                continue
            out_lines.append(f"{name}: .word 0")

        # literales de string
        for literal, lbl in self.string_literals.items():
            val = literal[1:-1]
            out_lines.append(f'{lbl}: .asciiz "{val}"')

        # heap si es necesario
        if self.uses_heap:
            out_lines.append("heap: .space 4096")
            out_lines.append("heap_ptr: .word heap")

        out_lines.append("")

        # Sección .text
        out_lines.append(".text")
        if self.has_main:
            out_lines.append(".globl main")

        for line in self.text_lines:
            # No emitir la etiqueta 'end_main:'
            if line.strip() == 'end_main:':
                continue
            out_lines.append(line)

        out = "\n".join(out_lines)

        if out_path is not None:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(out)

        return out


def emit_mips(emitter: Emitter, symtab=None, out_path: Optional[str] = None, static_arrays: Optional[dict] = None) -> str:
    backend = MIPSBackend()
    return backend.emit_from_emitter(emitter, out_path, static_arrays=static_arrays)