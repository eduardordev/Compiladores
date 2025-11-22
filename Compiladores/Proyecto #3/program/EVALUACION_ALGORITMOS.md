# Evaluación de los Algoritmos en el Código Actual

## 1. Algoritmo de Selección de Registros

### ✅ **Aspectos Positivos:**

1. **Implementación simple y funcional** (líneas 51-58):
   - El mapeo cíclico funciona para programas pequeños/medianos
   - Es rápido de ejecutar (O(1))
   - No requiere análisis complejo

2. **Función `load_operand_to_reg()` bien estructurada** (líneas 92-137):
   - Maneja diferentes tipos de operandos (temporales, inmediatos, strings, globals)
   - Tiene lógica para arrays
   - Retorna el registro donde quedó el valor

### ⚠️ **Problemas y Limitaciones:**

1. **No hay análisis de liveness**:
   ```python
   # Problema: Si t0 y t10 están vivos al mismo tiempo, ambos mapean a $t0
   # t0 → $t0
   # t10 → $t0  # ¡CONFLICTO! Sobrescribe el valor de t0
   ```
   - **Consecuencia**: Puede sobrescribir valores que aún se necesitan
   - **Solución**: Necesitarías análisis de liveness para saber cuándo un temporal ya no se usa

2. **Uso fijo de registros auxiliares**:
   ```python
   # Líneas 177-178, 201-202, etc.
   ra = self.load_operand_to_reg(a, "$t9")  # Siempre usa $t9
   rb = self.load_operand_to_reg(b, "$t8")  # Siempre usa $t8
   ```
   - **Problema**: Si `a` o `b` ya están en `$t9` o `$t8`, hace `move` innecesario
   - **Mejora**: Verificar primero si el operando ya está en el registro destino

3. **No guarda/restaura registros en llamadas**:
   - Si una función usa `$t0-$t9`, puede corromper valores del llamador
   - **Convención MIPS**: Los registros `$t0-$t9` son "caller-saved", pero tu código no los guarda antes de CALL

4. **Registros hardcodeados en diferentes operaciones**:
   ```python
   # Aritmética usa $t7 y $t1 (líneas 409-410)
   # Relacionales usa $t9 y $t8 (líneas 177-178)
   # GETPROP usa $t9 (línea 270)
   # SETPROP usa $t9 y $t8 (líneas 282, 285)
   ```
   - **Problema**: No hay coordinación, puede haber conflictos

### 📊 **Calificación: 6/10**

**Funciona para casos básicos**, pero tiene limitaciones serias que pueden causar bugs en programas complejos.

---

## 2. Algoritmo para Llamadas a Procedimientos y Retornos

### ✅ **Aspectos Positivos:**

1. **Prologue bien implementado** (líneas 305-308):
   ```python
   addi $sp, $sp, -32    # Reserva espacio
   sw $ra, 28($sp)       # Guarda return address
   sw $fp, 24($sp)       # Guarda frame pointer anterior
   move $fp, $sp         # Establece nuevo frame pointer
   ```
   - ✅ Guarda correctamente `$ra` y `$fp`
   - ✅ Establece frame pointer correctamente

2. **Epilogue correcto** (líneas 149-160):
   ```python
   move $sp, $fp         # Restaura stack pointer
   lw $ra, 28($sp)       # Restaura return address
   lw $fp, 24($sp)       # Restaura frame pointer
   addi $sp, $sp, 32     # Libera frame
   jr $ra                # Retorna
   ```
   - ✅ Restaura todo correctamente
   - ✅ Maneja main vs funciones normales

3. **Paso de argumentos funcional** (líneas 422-427, 429-460):
   - ✅ Acumula argumentos correctamente
   - ✅ Los guarda en el stack antes de CALL
   - ✅ Libera el espacio después

4. **Retorno de valores** (líneas 462-471):
   - ✅ Usa `$v0` correctamente
   - ✅ Maneja valores de retorno

### ⚠️ **Problemas y Limitaciones:**

1. **Frame size fijo de 32 bytes** (línea 305):
   ```python
   addi $sp, $sp, -32  # ¿Por qué 32? ¿Qué pasa si necesitas más?
   ```
   - **Problema**: 
     - Si una función tiene muchas variables locales, 32 bytes pueden no ser suficientes
     - Si tiene pocas, desperdicia espacio
   - **Mejora**: Calcular el tamaño real del frame basado en variables locales

2. **Argumentos solo en stack, no usa registros** (líneas 438-442):
   ```python
   # Tu código pasa TODO en stack
   for idx, arg in enumerate(self.pending_args):
       reg = self.load_operand_to_reg(arg, "$t9")
       self.emit(f"    sw {reg}, {idx * 4}($sp)")
   ```
   - **Convención MIPS estándar**: Los primeros 4 argumentos van en `$a0-$a3`
   - **Ventaja de tu enfoque**: Funciona para cualquier número de argumentos
   - **Desventaja**: Más lento (acceso a memoria vs registros)

3. **No guarda registros caller-saved antes de CALL**:
   ```python
   # Línea 444: jal func_name
   # Problema: Si la función llamada usa $t0-$t9, corrompe valores del llamador
   ```
   - **Solución**: Guardar `$t0-$t9` (y otros caller-saved) antes de CALL si contienen valores importantes

4. **La función llamada no recibe argumentos desde stack**:
   ```python
   # Tu código guarda argumentos en stack (línea 442)
   # Pero la función llamada nunca los lee desde ahí
   ```
   - **Problema crítico**: Los argumentos se guardan pero nunca se usan
   - **Solución**: La función debe leer argumentos desde `0($fp)`, `4($fp)`, etc.

5. **No hay espacio para variables locales en el frame**:
   - El frame solo guarda `$ra` y `$fp` (8 bytes)
   - No hay espacio reservado para variables locales de la función
   - **Mejora**: Calcular espacio necesario y ajustar el frame

### 📊 **Calificación: 5/10**

**Estructura correcta**, pero tiene bugs importantes:
- ❌ Argumentos no se leen en la función llamada
- ❌ Frame size fijo puede causar problemas
- ❌ No guarda registros antes de CALL

---

## Comparación con Implementación Ideal

### Algoritmo de Registros Ideal:

```python
# Pseudocódigo de algoritmo mejorado
def temp_reg(self, tname: str, liveness_info: Dict) -> str:
    # 1. Verificar si el temporal ya está en un registro
    if tname in self.register_map:
        return self.register_map[tname]
    
    # 2. Buscar registro libre
    for reg in available_regs:
        if reg not in self.used_regs or not liveness_info[reg]:
            self.register_map[tname] = reg
            self.used_regs.add(reg)
            return reg
    
    # 3. Si no hay libre, hacer spill (guardar en memoria)
    victim = self.choose_victim_reg()  # LRU o similar
    self.spill_reg(victim)
    return victim
```

### Algoritmo de Llamadas Ideal:

```python
# CALL mejorado
def call_function(self, func_name, args):
    # 1. Guardar registros caller-saved que están en uso
    self.save_caller_saved_regs()
    
    # 2. Pasar primeros 4 args en $a0-$a3, resto en stack
    for i, arg in enumerate(args[:4]):
        self.load_operand_to_reg(arg, f"$a{i}")
    for arg in args[4:]:
        # Guardar en stack
        ...
    
    # 3. Llamar
    self.emit(f"jal {func_name}")
    
    # 4. Restaurar registros
    self.restore_caller_saved_regs()
    
    # 5. Leer resultado de $v0
    ...
```

```python
# Prologue mejorado
def prologue(self, local_vars_size):
    frame_size = 8 + local_vars_size  # $ra + $fp + variables locales
    self.emit(f"addi $sp, $sp, -{frame_size}")
    self.emit(f"sw $ra, {frame_size-4}($sp)")
    self.emit(f"sw $fp, {frame_size-8}($sp)")
    self.emit("move $fp, $sp")
    
    # Leer argumentos desde stack del llamador
    # (están en posiciones conocidas relativas a $fp del llamador)
```

---

## Recomendaciones Prioritarias

### Para Selección de Registros (Prioridad Media):

1. **Corto plazo**: Agregar verificación para evitar `move` innecesarios
2. **Mediano plazo**: Implementar análisis de liveness básico
3. **Largo plazo**: Implementar graph coloring o linear scan

### Para Llamadas a Procedimientos (Prioridad Alta):

1. **CRÍTICO**: Hacer que las funciones lean argumentos desde stack
2. **Importante**: Calcular frame size dinámicamente
3. **Importante**: Guardar registros caller-saved antes de CALL
4. **Opcional**: Usar `$a0-$a3` para primeros 4 argumentos

---

## Resumen Ejecutivo

| Aspecto | Estado Actual | Funcionalidad | Mejora Necesaria |
|---------|---------------|---------------|------------------|
| **Selección de Registros** | Básico | ✅ Funciona para casos simples | ⚠️ Puede tener bugs con muchos temporales |
| **Prologue/Epilogue** | Bueno | ✅ Estructura correcta | ⚠️ Frame size fijo |
| **Paso de Argumentos** | Parcial | ⚠️ Guarda pero no lee | ❌ **BUG CRÍTICO** |
| **Retorno de Valores** | Bueno | ✅ Funciona correctamente | ✅ OK |
| **Manejo de Stack** | Bueno | ✅ Estructura correcta | ⚠️ No guarda registros |

**Conclusión**: Tu código tiene una **base sólida** pero necesita correcciones importantes, especialmente en el manejo de argumentos de funciones.

