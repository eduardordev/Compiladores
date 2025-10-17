# TAC (Three Address Code) Generation Documentation

## Overview

This document describes the design and implementation of the Three Address Code (TAC) intermediate representation for the Compiscript compiler. The TAC generation follows Dragon Book principles and provides a clean intermediate representation suitable for further optimization and code generation.

## Architecture

### Core Components

1. **TAC Instructions** (`tac/instructions.py`)
   - Defines the instruction set and operands
   - Supports arithmetic, logical, control flow, and memory operations
   - Includes specialized instructions for arrays, objects, and functions

2. **Temporary Variable Manager** (`tac/temp_manager.py`)
   - Implements efficient allocation and recycling of temporary variables
   - Provides expression stack management
   - Optimizes temporary variable usage

3. **Extended Symbol Table** (`tac/extended_symbols.py`)
   - Extends the semantic symbol table with memory addresses
   - Manages activation records for function calls
   - Tracks object layouts and field offsets

4. **TAC Generator** (`tac/generator.py`)
   - Main visitor that generates TAC from the AST
   - Extends the semantic visitor to maintain type information
   - Handles all language constructs

## TAC Instruction Set

### Basic Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| ASSIGN | `result = arg1` | Simple assignment |
| ADD | `result = arg1 + arg2` | Addition |
| SUB | `result = arg1 - arg2` | Subtraction |
| MUL | `result = arg1 * arg2` | Multiplication |
| DIV | `result = arg1 / arg2` | Division |
| MOD | `result = arg1 % arg2` | Modulo |

### Logical Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| AND | `result = arg1 && arg2` | Logical AND |
| OR | `result = arg1 \|\| arg2` | Logical OR |
| NOT | `result = !arg1` | Logical NOT |

### Comparison Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| EQ | `result = arg1 == arg2` | Equality |
| NE | `result = arg1 != arg2` | Inequality |
| LT | `result = arg1 < arg2` | Less than |
| LE | `result = arg1 <= arg2` | Less than or equal |
| GT | `result = arg1 > arg2` | Greater than |
| GE | `result = arg1 >= arg2` | Greater than or equal |

### Control Flow

| Operation | Syntax | Description |
|-----------|--------|-------------|
| GOTO | `goto label` | Unconditional jump |
| GOTO_IF_TRUE | `if arg1 goto label` | Conditional jump if true |
| GOTO_IF_FALSE | `if not arg1 goto label` | Conditional jump if false |
| LABEL | `label:` | Label definition |

### Memory Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| LOAD | `result = load address` | Load from memory |
| STORE | `store address, value` | Store to memory |
| ADDR | `result = addr variable` | Get address of variable |

### Array Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| ARRAY_NEW | `result = new array[size]` | Create new array |
| ARRAY_LOAD | `result = array[index]` | Load array element |
| ARRAY_STORE | `array[index] = value` | Store array element |

### Object Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| OBJECT_NEW | `result = new class` | Create new object |
| FIELD_LOAD | `result = object.field` | Load object field |
| FIELD_STORE | `object.field = value` | Store object field |

### Function Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| CALL | `result = call function` | Call function |
| RETURN | `return value` | Return from function |
| PARAM | `param value` | Pass parameter |

## Temporary Variable Management

### Allocation Strategy

The temporary variable manager uses a stack-based allocation strategy:

1. **Expression Stack**: Temporaries are pushed onto a stack during expression evaluation
2. **Reuse Optimization**: Freed temporaries are added to a free list for reuse
3. **Live Range Tracking**: Tracks when temporaries are first defined and last used

### Example

```compiscript
let result = 5 + 3 * 2;
```

Generated TAC:
```
t0 = 3 * 2          // t0 = 6
t1 = 5 + t0          // t1 = 11
result = t1          // result = 11
```

### Optimization

- **Single-use Elimination**: Temporaries used only once are eliminated
- **Register Coalescing**: Adjacent temporaries are merged when possible
- **Dead Code Elimination**: Unused temporaries are removed

## Memory Management

### Activation Records

Functions use activation records to manage local variables and parameters:

```
+------------------+
| Return Address   |
+------------------+
| Static Link      |
+------------------+
| Dynamic Link     |
+------------------+
| Parameters       |
+------------------+
| Local Variables  |
+------------------+
| Temporary Vars   |
+------------------+
```

### Memory Layout

- **Global Variables**: Stored in global memory space
- **Parameters**: Stored at positive offsets from frame pointer
- **Local Variables**: Stored at negative offsets from frame pointer
- **Temporary Variables**: Stored in temporary space

## Expression Translation

### Arithmetic Expressions

Compiscript expressions are translated to TAC following operator precedence:

```compiscript
let result = 5 + 3 * 2;
```

TAC Generation:
1. Generate TAC for `3 * 2` → `t0 = 3 * 2`
2. Generate TAC for `5 + t0` → `t1 = 5 + t0`
3. Assign result → `result = t1`

### Logical Expressions

Logical expressions use short-circuit evaluation:

```compiscript
let result = a && b;
```

TAC Generation:
```
t0 = a
if not t0 goto L1
t1 = b
goto L2
L1: t1 = false
L2: result = t1
```

## Control Flow Translation

### If Statements

```compiscript
if (condition) {
    then_block;
} else {
    else_block;
}
```

TAC Generation:
```
t0 = condition
if not t0 goto L1
// then_block TAC
goto L2
L1: // else_block TAC
L2: // end of if
```

### While Loops

```compiscript
while (condition) {
    body;
}
```

TAC Generation:
```
L1: t0 = condition
    if not t0 goto L2
    // body TAC
    goto L1
L2: // end of while
```

### For Loops

```compiscript
for (init; condition; increment) {
    body;
}
```

TAC Generation:
```
// init TAC
goto L2
L1: // increment TAC
L2: t0 = condition
    if not t0 goto L3
    // body TAC
    goto L1
L3: // end of for
```

## Function Translation

### Function Declaration

```compiscript
function add(a: integer, b: integer): integer {
    return a + b;
}
```

TAC Generation:
```
func_add:
    t0 = a + b
    return t0
end function
```

### Function Call

```compiscript
let result = add(5, 3);
```

TAC Generation:
```
param 5
param 3
t0 = call add
result = t0
```

## Class Translation

### Class Declaration

```compiscript
class Person {
    let name: string;
    function getName(): string {
        return this.name;
    }
}
```

TAC Generation:
```
class Person:
    field name: string
    
    method getName:
        t0 = this.name
        return t0
    end method
end class
```

### Object Instantiation

```compiscript
let person = new Person();
```

TAC Generation:
```
t0 = new Person
person = t0
```

## Array Translation

### Array Declaration

```compiscript
let numbers: integer[] = [1, 2, 3];
```

TAC Generation:
```
t0 = new array[3]
t0[0] = 1
t0[1] = 2
t0[2] = 3
numbers = t0
```

### Array Access

```compiscript
let first = numbers[0];
```

TAC Generation:
```
t0 = numbers[0]
first = t0
```

## Error Handling

### Semantic Error Propagation

The TAC generator extends the semantic visitor, so all semantic errors are properly propagated:

- **Type Mismatches**: Detected during semantic analysis
- **Undeclared Variables**: Caught before TAC generation
- **Invalid Operations**: Prevented by type checking

### Runtime Error Handling

```compiscript
try {
    dangerous_operation();
} catch (error) {
    handle_error(error);
}
```

TAC Generation:
```
L1: // dangerous_operation TAC
    goto L3
L2: // handle_error TAC
L3: // end of try-catch
```

## Testing

### Test Suite Structure

The test suite (`tests/test_tac_generation.py`) includes:

1. **Basic Expressions**: Arithmetic, logical, comparison operations
2. **Control Flow**: If, while, for, break, continue statements
3. **Functions**: Declaration, calls, returns, parameters
4. **Classes**: Declaration, instantiation, field access
5. **Arrays**: Declaration, access, assignment
6. **Temporary Variables**: Allocation, reuse, optimization
7. **Error Handling**: Semantic error propagation
8. **Complex Programs**: Real-world examples

### Running Tests

```bash
# Run all tests
python tests/test_runner.py

# Run quick tests
python tests/test_runner.py quick

# Run specific test
python tests/test_runner.py specific TestBasicExpressions.test_integer_literal
```

## Usage

### Command Line

```bash
# Generate TAC for a Compiscript file
python Driver.py program.cps --tac
```

### Programmatic Usage

```python
from tac.generator import TACGenerator
from antlr4 import InputStream, CommonTokenStream
from CompiscriptLexer import CompiscriptLexer
from CompiscriptParser import CompiscriptParser

# Parse Compiscript code
input_stream = InputStream(code)
lexer = CompiscriptLexer(input_stream)
tokens = CommonTokenStream(lexer)
parser = CompiscriptParser(tokens)
tree = parser.program()

# Generate TAC
generator = TACGenerator()
tac_program = generator.generate_tac(tree)

# Print TAC
print(tac_program)
```

## Future Enhancements

### Optimization Passes

1. **Constant Folding**: Evaluate constant expressions at compile time
2. **Dead Code Elimination**: Remove unreachable code
3. **Common Subexpression Elimination**: Reuse computed expressions
4. **Loop Optimization**: Unroll loops, optimize loop conditions

### Advanced Features

1. **Exception Handling**: Complete try-catch translation
2. **Switch Statements**: Efficient jump table generation
3. **Foreach Loops**: Iterator-based loop translation
4. **Closures**: Capture environment translation

### Code Generation

1. **Assembly Generation**: Convert TAC to target assembly
2. **Register Allocation**: Map temporaries to physical registers
3. **Instruction Selection**: Choose optimal machine instructions
4. **Peephole Optimization**: Local instruction improvements

## Conclusion

The TAC generation system provides a solid foundation for the Compiscript compiler. It follows established compiler construction principles and provides a clean intermediate representation that can be easily optimized and translated to target code.

The modular design allows for easy extension and modification, while the comprehensive test suite ensures correctness and reliability. The system is ready for integration with code generation phases and optimization passes.
