from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Type:
    name: str
    base: Optional['Type'] = None
    def is_array(self) -> bool:
        return self.base is not None
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
    return t in (INTEGER, FLOAT)

def are_compatible(t1: Type, t2: Type) -> bool:
    if t1 == t2:
        return True
    if is_numeric(t1) and is_numeric(t2):
        return True
    if t1 == NULL or t2 == NULL:
        return True
    if t1.is_array() and t2 == NULL:
        return True
    return False

def result_numeric(t1: Type, t2: Type) -> Optional[Type]:
    if is_numeric(t1) and is_numeric(t2):
        return FLOAT if FLOAT in (t1, t2) else INTEGER
    return None
