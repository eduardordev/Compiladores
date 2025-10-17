from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .typesys import Type

@dataclass
class Symbol:
    name: str
    type: Type

@dataclass
class VarSymbol(Symbol):
    is_const: bool = False

@dataclass
class FuncSymbol(Symbol):
    params: List['VarSymbol'] = field(default_factory=list)
    captures: List[str] = field(default_factory=list)

@dataclass
class ClassSymbol(Symbol):
    attributes: Dict[str, 'VarSymbol'] = field(default_factory=dict)
    methods: Dict[str, 'FuncSymbol'] = field(default_factory=dict)

class Scope:
    def __init__(self, name: str, parent: Optional['Scope']=None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def define(self, sym: Symbol):
        if sym.name in self.symbols:
            raise KeyError(f"Redeclaración en el mismo ámbito: {sym.name}")
        self.symbols[sym.name] = sym

    def resolve(self, name: str) -> Optional[Symbol]:
        s = self.symbols.get(name)
        if s:
            return s
        return self.parent.resolve(name) if self.parent else None

class SymbolTable:
    def __init__(self):
        self.scopes: List[Scope] = [Scope('global')]

    @property
    def current(self) -> Scope:
        return self.scopes[-1]

    def push(self, name: str):
        self.scopes.append(Scope(name, self.current))

    def pop(self):
        self.scopes.pop()

    def define(self, sym: Symbol):
        self.current.define(sym)

    def resolve(self, name: str) -> Optional[Symbol]:
        return self.current.resolve(name)
