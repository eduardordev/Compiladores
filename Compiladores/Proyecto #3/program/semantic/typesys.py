from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Type:
    name: str
    base: Optional['Type'] = None
    def is_array(self) -> bool:
        return self.base is not None
    def is_numeric(self) -> bool:
        return self in (INTEGER, FLOAT)
    def is_boolean(self) -> bool:
        return self is BOOLEAN
    def is_compatible(self, other: Optional['Type']) -> bool:
        if other is None:
            return False
        if self == other:
            return True
        # numeric coercion (int <-> float)
        if self.is_numeric() and other.is_numeric():
            return True
        # null compatibility
        if self == NULL or other == NULL:
            return True
        # arrays: allow null or same base compatibility
        if self.is_array() and other.is_array():
            return self.base.is_compatible(other.base)
        if self.is_array() and other == NULL:
            return True
        return False
    def __str__(self) -> str:
        return f"{self.base}[]" if self.base else self.name

INTEGER = Type('integer')
FLOAT   = Type('float')
STRING  = Type('string')
BOOLEAN = Type('boolean')
NULL    = Type('null')
VOID    = Type('void')

PRIMS = {t.name: t for t in (INTEGER, FLOAT, STRING, BOOLEAN, NULL, VOID)}

def array_of(t: Type) -> Type:
    return Type(name=f'{t.name}[]', base=t)

def is_numeric(t: Type) -> bool:
    return t.is_numeric()

def are_compatible(t1: Type, t2: Type) -> bool:
    return t1.is_compatible(t2)

def result_numeric(t1: Type, t2: Type) -> Optional[Type]:
    if is_numeric(t1) and is_numeric(t2):
        return FLOAT if FLOAT in (t1, t2) else INTEGER
    return None

def coerce_result(t1: Type, t2: Type) -> Optional[Type]:
    """Return the resulting type after coercion for binary arithmetic operations.
    Follows numeric promotion: if either is FLOAT -> FLOAT, else INTEGER. Returns None if not numeric.
    """
    return result_numeric(t1, t2)
