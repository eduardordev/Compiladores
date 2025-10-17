# Compiscript TAC Generation - Manual de Uso

## Descripción General

Este proyecto implementa la generación de código intermedio (TAC - Three Address Code) para el compilador de Compiscript. El sistema genera una representación intermedia del código fuente que puede ser utilizada para la generación de código assembler o para optimizaciones posteriores.

## Requisitos

- Python 3.7 o superior
- ANTLR 4.13.1 o superior
- Tkinter (para el IDE)

## Estructura del Proyecto

```
Proyecto #1/program/
├── Driver.py                    # Punto de entrada principal
├── tac/                        # Módulo de generación TAC
│   ├── instructions.py         # Definiciones de instrucciones TAC
│   ├── temp_manager.py         # Gestión de variables temporales
│   ├── extended_symbols.py     # Tabla de símbolos extendida
│   ├── generator.py            # Generador principal de TAC
│   └── README_TAC_DESIGN.md    # Documentación técnica
├── tests/                      # Suite de pruebas
│   ├── test_tac_generation.py  # Pruebas completas
│   └── test_runner.py         # Ejecutor de pruebas
├── ide/                        # IDE integrado
│   └── mini_ide.py            # Interfaz gráfica
├── semantic/                   # Análisis semántico
└── example_tac.cps            # Archivo de ejemplo
```

## Instalación

1. Clona el repositorio
2. Navega al directorio del proyecto:
   ```bash
   cd "Proyecto #1/program"
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Generación de TAC desde Línea de Comandos

#### Sintaxis básica
```bash
python Driver.py <archivo.cps> [--tac]
```

#### Ejemplos
```bash
# Generar TAC para un archivo
python Driver.py program.cps --tac

# Usar el archivo de ejemplo
python Driver.py example_tac.cps --tac

# Solo análisis semántico (sin TAC)
python Driver.py program.cps
```

#### Salida esperada
```
TAC Generated Successfully!
==================================================
// Global Variables
global global_counter
global message

// Main Program
t0 = 3 * 2          // Multiplicative operation
t1 = 5 + t0         // Additive operation
result = t1          // Initialize result
...
==================================================
Temporary Variables: 15
Active Temporaries: 3
Reused Temporaries: 5
Global Memory: 24 bytes
Local Memory: 48 bytes
String Literals: 3
```

### Uso del IDE

1. Iniciar el IDE:
   ```bash
   python ide/mini_ide.py
   ```

2. Cargar un archivo Compiscript:
   - File → Abrir → Seleccionar archivo .cps

3. Generar TAC:
   - Presionar F6 o Tools → Generar TAC
   - Se abrirá una ventana con el código TAC y estadísticas

4. Atajos de teclado:
   - F5: Compilar (análisis semántico)
   - F6: Generar TAC
   - Ctrl+O: Abrir archivo
   - Ctrl+S: Guardar archivo

### Ejecución de Pruebas

#### Ejecutar todas las pruebas
```bash
python tests/test_runner.py
```

#### Ejecutar pruebas rápidas
```bash
python tests/test_runner.py quick
```

#### Ejecutar prueba específica
```bash
python tests/test_runner.py specific TestBasicExpressions.test_integer_literal
```

#### Ejecutar pruebas por categoría
```bash
# Pruebas de expresiones básicas
python -m unittest tests.test_tac_generation.TestBasicExpressions

# Pruebas de control de flujo
python -m unittest tests.test_tac_generation.TestControlFlow

# Pruebas de funciones
python -m unittest tests.test_tac_generation.TestFunctions
```

## Ejemplos de Código

### Expresiones Aritméticas
```compiscript
let result = 5 + 3 * 2;
```
**TAC generado:**
```
t0 = 3 * 2          // Multiplicative operation
t1 = 5 + t0         // Additive operation
result = t1          // Initialize result
```

### Control de Flujo
```compiscript
if (x > 10) {
    print("Mayor");
} else {
    print("Menor");
}
```
**TAC generado:**
```
t0 = x > 10          // Relational operation
if not t0 goto L1    // If condition false, goto else
param "Mayor"         // Print statement
call print
goto L2              // Goto end of if
L1:                  // Else label
param "Menor"         // Print statement
call print
L2:                  // End label
```

### Funciones
```compiscript
function add(a: integer, b: integer): integer {
    return a + b;
}
```
**TAC generado:**
```
function add(a, b) -> integer
    t0 = a + b       // Additive operation
    return t0         // Return with value
end function
```

### Clases
```compiscript
class Person {
    let name: string;
    function getName(): string {
        return this.name;
    }
}
```
**TAC generado:**
```
class Person
    field name: string
    
    method getName:
        t0 = this.name
        return t0
    end method
end class
```

## Características del Sistema

### Gestión de Variables Temporales
- Asignación automática y reciclaje de variables temporales
- Optimización de reutilización
- Seguimiento de rangos de vida
- Estadísticas de uso

### Gestión de Memoria
- Registros de activación para funciones
- Seguimiento de layout de objetos
- Asignación de direcciones de memoria
- Gestión de literales de cadena

### Traducción de Control de Flujo
- Generación adecuada de etiquetas
- Optimización de saltos
- Preservación de estructura de bucles
- Manejo de break/continue

### Manejo de Errores
- Propagación de errores semánticos
- Integración con verificación de tipos
- Manejo elegante de fallos
- Reporte comprehensivo de errores

## Formato de Instrucciones TAC

### Operaciones Básicas
- `result = arg1 + arg2` - Suma
- `result = arg1 - arg2` - Resta
- `result = arg1 * arg2` - Multiplicación
- `result = arg1 / arg2` - División

### Operaciones Lógicas
- `result = arg1 && arg2` - AND lógico
- `result = arg1 || arg2` - OR lógico
- `result = !arg1` - NOT lógico

### Operaciones de Comparación
- `result = arg1 == arg2` - Igualdad
- `result = arg1 != arg2` - Desigualdad
- `result = arg1 < arg2` - Menor que
- `result = arg1 > arg2` - Mayor que

### Control de Flujo
- `goto label` - Salto incondicional
- `if arg1 goto label` - Salto condicional
- `if not arg1 goto label` - Salto condicional negado
- `label:` - Definición de etiqueta

### Operaciones de Memoria
- `result = load address` - Cargar de memoria
- `store address, value` - Almacenar en memoria
- `result = addr variable` - Obtener dirección

### Operaciones de Arreglos
- `result = new array[size]` - Crear arreglo
- `result = array[index]` - Acceder a elemento
- `array[index] = value` - Asignar elemento

### Operaciones de Objetos
- `result = new class` - Crear objeto
- `result = object.field` - Acceder a campo
- `object.field = value` - Asignar campo

### Operaciones de Funciones
- `result = call function` - Llamar función
- `return value` - Retornar valor
- `param value` - Pasar parámetro

## Solución de Problemas

### Errores Comunes

1. **Error de sintaxis**
   ```
   [Syntax] line X:Y mensaje de error
   ```
   - Verificar la sintaxis del código Compiscript
   - Revisar paréntesis, llaves y punto y coma

2. **Error semántico**
   ```
   [Semantic] line X:Y mensaje de error
   ```
   - Verificar tipos de datos
   - Revisar declaraciones de variables
   - Comprobar compatibilidad de tipos

3. **Variable no declarada**
   ```
   Identificador no declarado: variable_name
   ```
   - Declarar la variable antes de usarla
   - Verificar el ámbito de la variable

4. **Tipo incompatible**
   ```
   Asignación incompatible: tipo1 := tipo2
   ```
   - Verificar tipos en asignaciones
   - Usar conversiones de tipo si es necesario

### Verificación del Sistema

1. **Ejecutar pruebas básicas:**
   ```bash
   python tests/test_runner.py quick
   ```

2. **Verificar archivos de ejemplo:**
   ```bash
   python Driver.py example_tac.cps --tac
   ```

3. **Probar IDE:**
   ```bash
   python ide/mini_ide.py
   ```

## Desarrollo y Extensión

### Agregar Nuevas Instrucciones

1. Definir la operación en `tac/instructions.py`
2. Implementar la generación en `tac/generator.py`
3. Agregar pruebas en `tests/test_tac_generation.py`

### Agregar Nuevas Pruebas

1. Crear método de prueba en la clase apropiada
2. Usar `assert_has_instruction()` para verificar TAC
3. Ejecutar con `python tests/test_runner.py`

### Modificar el IDE

1. Editar `ide/mini_ide.py`
2. Agregar nuevas funcionalidades
3. Actualizar menús y atajos de teclado

## Contribución

1. Fork del repositorio
2. Crear rama para nueva funcionalidad
3. Implementar cambios
4. Agregar pruebas
5. Crear pull request

## Licencia

Este proyecto es parte de un curso universitario de construcción de compiladores.

## Contacto

Para preguntas o problemas, contactar a los desarrolladores del proyecto.
