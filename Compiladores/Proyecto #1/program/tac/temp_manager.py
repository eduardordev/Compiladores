"""
Temporary Variable Manager for TAC Generation

Implements efficient allocation and recycling of temporary variables
following Dragon Book principles for register allocation optimization.
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from .instructions import TACOperand, TACInstruction, TACOp

@dataclass
class TempVarInfo:
    """Information about a temporary variable"""
    temp_id: int
    is_active: bool = True
    last_use_line: int = -1
    first_def_line: int = -1
    live_range: Set[int] = None
    
    def __post_init__(self):
        if self.live_range is None:
            self.live_range = set()

class TempVarManager:
    """Manages temporary variable allocation and recycling"""
    
    def __init__(self):
        self.next_temp_id: int = 0
        self.active_temps: Dict[int, TempVarInfo] = {}
        self.free_temps: List[int] = []
        self.temp_history: List[TempVarInfo] = []
        self.current_line: int = 0
    
    def new_temp(self) -> TACOperand:
        """Allocate a new temporary variable"""
        temp_id = self._allocate_temp_id()
        temp_info = TempVarInfo(temp_id, first_def_line=self.current_line)
        self.active_temps[temp_id] = temp_info
        self.temp_history.append(temp_info)
        return TACOperand(temp_id, is_temp=True)
    
    def _allocate_temp_id(self) -> int:
        """Allocate a temporary ID, reusing if possible"""
        if self.free_temps:
            return self.free_temps.pop()
        else:
            temp_id = self.next_temp_id
            self.next_temp_id += 1
            return temp_id
    
    def free_temp(self, temp: TACOperand):
        """Mark a temporary variable as free for reuse"""
        if not temp.is_temp:
            return
        
        temp_id = temp.value
        if temp_id in self.active_temps:
            temp_info = self.active_temps[temp_id]
            temp_info.is_active = False
            temp_info.last_use_line = self.current_line
            del self.active_temps[temp_id]
            self.free_temps.append(temp_id)
    
    def update_live_range(self, temp: TACOperand, line: int):
        """Update the live range of a temporary variable"""
        if not temp.is_temp:
            return
        
        temp_id = temp.value
        if temp_id in self.active_temps:
            self.active_temps[temp_id].live_range.add(line)
    
    def advance_line(self):
        """Advance to the next line number"""
        self.current_line += 1
    
    def get_active_temps(self) -> List[TACOperand]:
        """Get all currently active temporary variables"""
        return [TACOperand(temp_id, is_temp=True) 
                for temp_id in self.active_temps.keys()]
    
    def get_temp_info(self, temp: TACOperand) -> Optional[TempVarInfo]:
        """Get information about a temporary variable"""
        if not temp.is_temp:
            return None
        
        temp_id = temp.value
        return self.active_temps.get(temp_id)
    
    def optimize_temps(self) -> List[TACInstruction]:
        """Generate optimization instructions for temporary variables"""
        optimizations = []
        
        # Find temporaries that can be coalesced
        for temp_info in self.temp_history:
            if not temp_info.is_active and len(temp_info.live_range) == 1:
                # Single-use temporary, can be eliminated
                optimizations.append(
                    TACInstruction(TACOp.COPY, comment=f"Optimize temp {temp_info.temp_id}")
                )
        
        return optimizations
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about temporary variable usage"""
        total_temps = len(self.temp_history)
        active_temps = len(self.active_temps)
        reused_temps = len(self.free_temps)
        
        return {
            'total_temps': total_temps,
            'active_temps': active_temps,
            'reused_temps': reused_temps,
            'max_temps': self.next_temp_id
        }

class ExpressionTempManager:
    """Specialized manager for expression temporary variables"""
    
    def __init__(self, temp_manager: TempVarManager):
        self.temp_manager = temp_manager
        self.expression_stack: List[TACOperand] = []
    
    def push_temp(self, temp: TACOperand):
        """Push a temporary onto the expression stack"""
        self.expression_stack.append(temp)
    
    def pop_temp(self) -> Optional[TACOperand]:
        """Pop a temporary from the expression stack"""
        if self.expression_stack:
            return self.expression_stack.pop()
        return None
    
    def peek_temp(self) -> Optional[TACOperand]:
        """Peek at the top temporary without removing it"""
        if self.expression_stack:
            return self.expression_stack[-1]
        return None
    
    def clear_stack(self):
        """Clear the expression stack and free all temporaries"""
        while self.expression_stack:
            temp = self.expression_stack.pop()
            self.temp_manager.free_temp(temp)
    
    def get_stack_depth(self) -> int:
        """Get the current depth of the expression stack"""
        return len(self.expression_stack)
