"""
Three Address Code (TAC) Instructions for Compiscript Compiler

This module defines the intermediate representation instructions used for code generation.
Based on Dragon Book principles and adapted for Compiscript language features.
"""

from dataclasses import dataclass
from typing import List, Optional, Union, Any
from enum import Enum

class TACOp(Enum):
    """TAC Operation Types"""
    # Assignment operations
    ASSIGN = "="
    COPY = "copy"
    
    # Arithmetic operations
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    
    # Logical operations
    AND = "&&"
    OR = "||"
    NOT = "!"
    
    # Comparison operations
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    
    # Memory operations
    LOAD = "load"
    STORE = "store"
    ADDR = "addr"
    
    # Array operations
    ARRAY_LOAD = "array_load"
    ARRAY_STORE = "array_store"
    ARRAY_NEW = "array_new"
    
    # Object operations
    FIELD_LOAD = "field_load"
    FIELD_STORE = "field_store"
    OBJECT_NEW = "object_new"
    
    # Control flow
    GOTO = "goto"
    GOTO_IF_TRUE = "goto_if_true"
    GOTO_IF_FALSE = "goto_if_false"
    LABEL = "label"
    
    # Function operations
    CALL = "call"
    RETURN = "return"
    PARAM = "param"
    
    # String operations
    STRING_CONCAT = "string_concat"
    
    # Type conversion
    CAST = "cast"

@dataclass
class TACOperand:
    """Represents an operand in TAC instruction"""
    value: Union[str, int, float, bool]
    is_temp: bool = False
    is_label: bool = False
    is_address: bool = False
    
    def __str__(self) -> str:
        if self.is_label:
            return f"L{self.value}"
        elif self.is_temp:
            return f"t{self.value}"
        elif self.is_address:
            return f"&{self.value}"
        elif isinstance(self.value, str):
            return f'"{self.value}"'
        else:
            return str(self.value)

@dataclass
class TACInstruction:
    """Represents a single TAC instruction"""
    op: TACOp
    result: Optional[TACOperand] = None
    arg1: Optional[TACOperand] = None
    arg2: Optional[TACOperand] = None
    label: Optional[str] = None
    comment: Optional[str] = None
    
    def __str__(self) -> str:
        parts = []
        
        if self.label:
            parts.append(f"{self.label}:")
        
        if self.op == TACOp.LABEL:
            return f"{self.label}:"
        elif self.op == TACOp.GOTO:
            return f"goto {self.arg1}"
        elif self.op == TACOp.GOTO_IF_TRUE:
            return f"if {self.arg1} goto {self.arg2}"
        elif self.op == TACOp.GOTO_IF_FALSE:
            return f"if not {self.arg1} goto {self.arg2}"
        elif self.op == TACOp.RETURN:
            if self.arg1:
                return f"return {self.arg1}"
            else:
                return "return"
        elif self.op == TACOp.CALL:
            if self.result:
                return f"{self.result} = call {self.arg1}"
            else:
                return f"call {self.arg1}"
        elif self.op == TACOp.PARAM:
            return f"param {self.arg1}"
        elif self.op == TACOp.ASSIGN:
            return f"{self.result} = {self.arg1}"
        elif self.op == TACOp.COPY:
            return f"{self.result} = {self.arg1}"
        elif self.op == TACOp.ARRAY_NEW:
            return f"{self.result} = new array[{self.arg1}]"
        elif self.op == TACOp.ARRAY_LOAD:
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        elif self.op == TACOp.ARRAY_STORE:
            return f"{self.arg1}[{self.arg2}] = {self.arg3}"
        elif self.op == TACOp.OBJECT_NEW:
            return f"{self.result} = new {self.arg1}"
        elif self.op == TACOp.FIELD_LOAD:
            return f"{self.result} = {self.arg1}.{self.arg2}"
        elif self.op == TACOp.FIELD_STORE:
            return f"{self.arg1}.{self.arg2} = {self.arg3}"
        elif self.op == TACOp.CAST:
            return f"{self.result} = ({self.arg1}) {self.arg2}"
        else:
            # Binary operations
            if self.result and self.arg1 and self.arg2:
                return f"{self.result} = {self.arg1} {self.op.value} {self.arg2}"
            elif self.result and self.arg1:
                # Unary operations
                return f"{self.result} = {self.op.value} {self.arg1}"
        
        result = " ".join(str(p) for p in parts if p)
        if self.comment:
            result += f"  // {self.comment}"
        return result

class TACProgram:
    """Represents a complete TAC program"""
    
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.global_vars: List[str] = []
        self.functions: List['TACFunction'] = []
        self.classes: List['TACClass'] = []
        self.next_label: int = 0
        self.next_temp: int = 0
    
    def add_instruction(self, instruction: TACInstruction):
        """Add an instruction to the program"""
        self.instructions.append(instruction)
    
    def new_label(self) -> str:
        """Generate a new unique label"""
        label = f"L{self.next_label}"
        self.next_label += 1
        return label
    
    def new_temp(self) -> TACOperand:
        """Generate a new temporary variable"""
        temp = TACOperand(self.next_temp, is_temp=True)
        self.next_temp += 1
        return temp
    
    def add_global_var(self, name: str):
        """Add a global variable declaration"""
        if name not in self.global_vars:
            self.global_vars.append(name)
    
    def add_function(self, func: 'TACFunction'):
        """Add a function definition"""
        self.functions.append(func)
    
    def add_class(self, cls: 'TACClass'):
        """Add a class definition"""
        self.classes.append(cls)
    
    def __str__(self) -> str:
        """String representation of the TAC program"""
        lines = []
        
        # Global variables
        if self.global_vars:
            lines.append("// Global Variables")
            for var in self.global_vars:
                lines.append(f"global {var}")
            lines.append("")
        
        # Classes
        for cls in self.classes:
            lines.append(str(cls))
            lines.append("")
        
        # Functions
        for func in self.functions:
            lines.append(str(func))
            lines.append("")
        
        # Main program instructions
        lines.append("// Main Program")
        for instr in self.instructions:
            lines.append(str(instr))
        
        return "\n".join(lines)

@dataclass
class TACFunction:
    """Represents a TAC function"""
    name: str
    params: List[str]
    return_type: str
    instructions: List[TACInstruction]
    local_vars: List[str]
    
    def __str__(self) -> str:
        lines = []
        lines.append(f"function {self.name}({', '.join(self.params)}) -> {self.return_type}")
        
        if self.local_vars:
            lines.append("// Local Variables")
            for var in self.local_vars:
                lines.append(f"  local {var}")
        
        lines.append("// Function Body")
        for instr in self.instructions:
            lines.append(f"  {instr}")
        
        lines.append("end function")
        return "\n".join(lines)

@dataclass
class TACClass:
    """Represents a TAC class"""
    name: str
    parent: Optional[str]
    fields: List[str]
    methods: List[TACFunction]
    
    def __str__(self) -> str:
        lines = []
        lines.append(f"class {self.name}")
        
        if self.parent:
            lines.append(f"  extends {self.parent}")
        
        if self.fields:
            lines.append("  // Fields")
            for field in self.fields:
                lines.append(f"    field {field}")
        
        if self.methods:
            lines.append("  // Methods")
            for method in self.methods:
                lines.append(f"    {method}")
        
        lines.append("end class")
        return "\n".join(lines)
