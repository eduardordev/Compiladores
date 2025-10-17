"""
Extended Symbol Table for TAC Generation

Adds memory addresses, activation records, and runtime information
to support intermediate code generation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from .symbols import Symbol, VarSymbol, FuncSymbol, ClassSymbol, Scope, SymbolTable
from .typesys import Type

@dataclass
class MemoryAddress:
    """Represents a memory address for a symbol"""
    offset: int
    scope_level: int
    is_global: bool = False
    is_parameter: bool = False
    is_local: bool = False
    
    def __str__(self) -> str:
        if self.is_global:
            return f"global_{self.offset}"
        elif self.is_parameter:
            return f"param_{self.offset}"
        else:
            return f"local_{self.offset}"

@dataclass
class ActivationRecord:
    """Represents an activation record for function calls"""
    function_name: str
    return_address: str
    static_link: Optional[str] = None
    dynamic_link: Optional[str] = None
    parameters: List[MemoryAddress] = field(default_factory=list)
    local_vars: List[MemoryAddress] = field(default_factory=list)
    temp_vars: List[MemoryAddress] = field(default_factory=list)
    
    def get_total_size(self) -> int:
        """Calculate total size of activation record"""
        return (len(self.parameters) + len(self.local_vars) + len(self.temp_vars)) * 4  # Assuming 4 bytes per variable

@dataclass
class ExtendedVarSymbol(VarSymbol):
    """Extended variable symbol with memory information"""
    address: Optional[MemoryAddress] = None
    size: int = 4  # Default size in bytes
    alignment: int = 4  # Default alignment
    
    def __post_init__(self):
        if self.address is None:
            self.address = MemoryAddress(0, 0)

@dataclass
class ExtendedFuncSymbol(FuncSymbol):
    """Extended function symbol with activation record information"""
    activation_record: Optional[ActivationRecord] = None
    stack_frame_size: int = 0
    parameter_size: int = 0
    local_size: int = 0
    
    def __post_init__(self):
        if self.activation_record is None:
            self.activation_record = ActivationRecord(self.name, "return_addr")

@dataclass
class ExtendedClassSymbol(ClassSymbol):
    """Extended class symbol with object layout information"""
    object_size: int = 0
    field_offsets: Dict[str, int] = field(default_factory=dict)
    method_table: Dict[str, str] = field(default_factory=dict)  # method_name -> address
    vtable_address: Optional[str] = None

class ExtendedScope(Scope):
    """Extended scope with memory management"""
    
    def __init__(self, name: str, parent: Optional['ExtendedScope'] = None):
        super().__init__(name, parent)
        self.next_offset: int = 0
        self.max_offset: int = 0
        self.is_function_scope: bool = False
        self.is_class_scope: bool = False
    
    def allocate_variable(self, symbol: ExtendedVarSymbol) -> MemoryAddress:
        """Allocate memory for a variable in this scope"""
        if symbol.address is None:
            address = MemoryAddress(
                offset=self.next_offset,
                scope_level=self._get_scope_level(),
                is_global=self.name == 'global',
                is_parameter=self.name.startswith('param_'),
                is_local=not self.name.startswith('param_') and self.name != 'global'
            )
            symbol.address = address
            self.next_offset += symbol.size
            self.max_offset = max(self.max_offset, self.next_offset)
        
        return symbol.address
    
    def _get_scope_level(self) -> int:
        """Get the nesting level of this scope"""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level

class ExtendedSymbolTable(SymbolTable):
    """Extended symbol table with memory management and activation records"""
    
    def __init__(self):
        super().__init__()
        self.scopes = [ExtendedScope('global')]
        self.activation_records: List[ActivationRecord] = []
        self.current_function: Optional[ExtendedFuncSymbol] = None
        self.global_offset: int = 0
        self.string_literals: Dict[str, str] = {}  # literal -> address
        self.next_string_id: int = 0
    
    @property
    def current(self) -> ExtendedScope:
        return self.scopes[-1]
    
    def push(self, name: str):
        """Push a new scope"""
        self.scopes.append(ExtendedScope(name, self.current))
    
    def define_variable(self, name: str, var_type: Type, is_const: bool = False) -> ExtendedVarSymbol:
        """Define a variable with memory allocation"""
        symbol = ExtendedVarSymbol(name, var_type, is_const)
        self.current.allocate_variable(symbol)
        self.define(symbol)
        return symbol
    
    def define_function(self, name: str, return_type: Type, params: List[VarSymbol]) -> ExtendedFuncSymbol:
        """Define a function with activation record"""
        func_symbol = ExtendedFuncSymbol(name, return_type, params)
        
        # Create activation record
        activation_record = ActivationRecord(name, f"return_{name}")
        
        # Allocate space for parameters
        param_offset = 0
        for param in params:
            param_addr = MemoryAddress(param_offset, 0, is_parameter=True)
            activation_record.parameters.append(param_addr)
            param_offset += 4  # Assuming 4 bytes per parameter
        
        func_symbol.activation_record = activation_record
        func_symbol.parameter_size = param_offset
        
        self.define(func_symbol)
        return func_symbol
    
    def define_class(self, name: str, parent: Optional[str] = None) -> ExtendedClassSymbol:
        """Define a class with object layout"""
        class_symbol = ExtendedClassSymbol(name, Type(name))
        
        # Calculate object size and field offsets
        field_offset = 0
        for field_name, field_symbol in class_symbol.attributes.items():
            class_symbol.field_offsets[field_name] = field_offset
            field_offset += field_symbol.size
        
        class_symbol.object_size = field_offset
        
        self.define(class_symbol)
        return class_symbol
    
    def resolve_with_address(self, name: str) -> Optional[ExtendedVarSymbol]:
        """Resolve a symbol and return its extended version with address"""
        symbol = self.resolve(name)
        if isinstance(symbol, ExtendedVarSymbol):
            return symbol
        elif isinstance(symbol, VarSymbol):
            # Convert to extended version
            extended_symbol = ExtendedVarSymbol(symbol.name, symbol.type, symbol.is_const)
            extended_symbol.address = self.current.allocate_variable(extended_symbol)
            return extended_symbol
        return None
    
    def get_current_function(self) -> Optional[ExtendedFuncSymbol]:
        """Get the current function symbol"""
        return self.current_function
    
    def set_current_function(self, func_symbol: ExtendedFuncSymbol):
        """Set the current function"""
        self.current_function = func_symbol
    
    def add_string_literal(self, literal: str) -> str:
        """Add a string literal and return its address"""
        if literal not in self.string_literals:
            address = f"str_{self.next_string_id}"
            self.string_literals[literal] = address
            self.next_string_id += 1
        return self.string_literals[literal]
    
    def get_global_variables(self) -> List[ExtendedVarSymbol]:
        """Get all global variables"""
        global_scope = self.scopes[0]
        return [sym for sym in global_scope.symbols.values() 
                if isinstance(sym, ExtendedVarSymbol)]
    
    def get_function_symbols(self) -> List[ExtendedFuncSymbol]:
        """Get all function symbols"""
        functions = []
        for scope in self.scopes:
            for symbol in scope.symbols.values():
                if isinstance(symbol, ExtendedFuncSymbol):
                    functions.append(symbol)
        return functions
    
    def get_class_symbols(self) -> List[ExtendedClassSymbol]:
        """Get all class symbols"""
        classes = []
        for scope in self.scopes:
            for symbol in scope.symbols.values():
                if isinstance(symbol, ExtendedClassSymbol):
                    classes.append(symbol)
        return classes
    
    def calculate_stack_frame_size(self, func_symbol: ExtendedFuncSymbol) -> int:
        """Calculate the total stack frame size for a function"""
        if not func_symbol.activation_record:
            return 0
        
        ar = func_symbol.activation_record
        return ar.get_total_size()
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get memory usage statistics"""
        total_global_size = 0
        total_local_size = 0
        total_param_size = 0
        
        for scope in self.scopes:
            if scope.name == 'global':
                total_global_size += scope.max_offset
            else:
                total_local_size += scope.max_offset
        
        for func_symbol in self.get_function_symbols():
            if func_symbol.activation_record:
                total_param_size += func_symbol.parameter_size
        
        return {
            'global_size': total_global_size,
            'local_size': total_local_size,
            'param_size': total_param_size,
            'string_literals': len(self.string_literals)
        }
