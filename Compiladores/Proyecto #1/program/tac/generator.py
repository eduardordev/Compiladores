"""
TAC Generation Visitor for Compiscript

Extends the semantic visitor to generate Three Address Code (TAC)
intermediate representation following Dragon Book principles.
"""

from typing import Any, Dict, List, Optional
from antlr4 import ParserRuleContext

from ..semantic.visitor import SemanticVisitor
from ..semantic.typesys import *
from ..semantic.errors import SemanticError, at

from .instructions import *
from .temp_manager import TempVarManager, ExpressionTempManager
from .extended_symbols import ExtendedSymbolTable, ExtendedVarSymbol, ExtendedFuncSymbol, ExtendedClassSymbol

class TACGenerator(SemanticVisitor):
    """TAC Generation Visitor extending Semantic Visitor"""
    
    def __init__(self):
        super().__init__()
        # Replace symbol table with extended version
        self.symtab = ExtendedSymbolTable()
        self.tac_program = TACProgram()
        self.temp_manager = TempVarManager()
        self.expr_temp_manager = ExpressionTempManager(self.temp_manager)
        
        # Control flow labels
        self.loop_labels: List[Dict[str, str]] = []
        self.if_labels: List[Dict[str, str]] = []
        
        # Function context
        self.current_function: Optional[ExtendedFuncSymbol] = None
        self.return_label: Optional[str] = None
        
        # Class context
        self.current_class: Optional[ExtendedClassSymbol] = None
        
        # Expression context
        self.expression_result: Optional[TACOperand] = None
    
    def generate_tac(self, tree) -> TACProgram:
        """Generate TAC for the entire program"""
        self.visit(tree)
        return self.tac_program
    
    def new_label(self) -> str:
        """Generate a new label"""
        return self.tac_program.new_label()
    
    def new_temp(self) -> TACOperand:
        """Generate a new temporary variable"""
        return self.temp_manager.new_temp()
    
    def add_instruction(self, instruction: TACInstruction):
        """Add an instruction to the TAC program"""
        self.tac_program.add_instruction(instruction)
        self.temp_manager.advance_line()
    
    def get_operand(self, ctx) -> TACOperand:
        """Get TAC operand from context"""
        if hasattr(ctx, 'Identifier') and ctx.Identifier():
            name = ctx.Identifier().getText()
            symbol = self.symtab.resolve_with_address(name)
            if symbol and symbol.address:
                return TACOperand(symbol.address.offset, is_address=True)
        
        # Handle literals
        text = ctx.getText()
        if text in ('true', 'false'):
            return TACOperand(text == 'true')
        elif text == 'null':
            return TACOperand(0)  # null pointer
        elif text.startswith('"') and text.endswith('"'):
            # String literal
            string_addr = self.symtab.add_string_literal(text)
            return TACOperand(string_addr, is_address=True)
        elif text.isdigit():
            return TACOperand(int(text))
        elif text.replace('.', '').isdigit():
            return TACOperand(float(text))
        
        return TACOperand(text)
    
    # Override semantic visitor methods to add TAC generation
    
    def visitProgram(self, ctx):
        """Generate TAC for program"""
        # Generate TAC for global declarations first
        for stmt in ctx.statement():
            if stmt.variableDeclaration() or stmt.constantDeclaration():
                self.visit(stmt)
        
        # Generate TAC for functions and classes
        for stmt in ctx.statement():
            if stmt.functionDeclaration() or stmt.classDeclaration():
                self.visit(stmt)
        
        # Generate TAC for main program statements
        for stmt in ctx.statement():
            if not (stmt.variableDeclaration() or stmt.constantDeclaration() or 
                   stmt.functionDeclaration() or stmt.classDeclaration()):
                self.visit(stmt)
        
        return None
    
    def visitVariableDeclaration(self, ctx):
        """Generate TAC for variable declaration"""
        # First do semantic analysis
        super().visitVariableDeclaration(ctx)
        
        # Generate TAC
        name = ctx.Identifier().getText()
        symbol = self.symtab.resolve_with_address(name)
        
        if ctx.initializer():
            # Generate assignment TAC
            self.visit(ctx.initializer())
            if self.expression_result:
                result_temp = TACOperand(symbol.address.offset, is_address=True)
                self.add_instruction(TACInstruction(
                    TACOp.ASSIGN,
                    result=result_temp,
                    arg1=self.expression_result,
                    comment=f"Initialize {name}"
                ))
        
        return None
    
    def visitConstantDeclaration(self, ctx):
        """Generate TAC for constant declaration"""
        # First do semantic analysis
        super().visitConstantDeclaration(ctx)
        
        # Generate TAC
        name = ctx.Identifier().getText()
        symbol = self.symtab.resolve_with_address(name)
        
        # Generate assignment TAC
        self.visit(ctx.initializer())
        if self.expression_result:
            result_temp = TACOperand(symbol.address.offset, is_address=True)
            self.add_instruction(TACInstruction(
                TACOp.ASSIGN,
                result=result_temp,
                arg1=self.expression_result,
                comment=f"Initialize constant {name}"
            ))
        
        return None
    
    def visitAssignment(self, ctx):
        """Generate TAC for assignment"""
        # First do semantic analysis
        super().visitAssignment(ctx)
        
        # Generate TAC for right-hand side
        self.visit(ctx.expression())
        rhs_result = self.expression_result
        
        if rhs_result:
            # Generate TAC for left-hand side
            lhs_result = self.visit(ctx.leftHandSide())
            if lhs_result:
                self.add_instruction(TACInstruction(
                    TACOp.ASSIGN,
                    result=lhs_result,
                    arg1=rhs_result,
                    comment="Assignment"
                ))
        
        return None
    
    def visitExpressionStatement(self, ctx):
        """Generate TAC for expression statement"""
        # First do semantic analysis
        super().visitExpressionStatement(ctx)
        
        # Generate TAC for expression
        self.visit(ctx.expression())
        # Expression result is discarded for statement
        
        return None
    
    def visitPrintStatement(self, ctx):
        """Generate TAC for print statement"""
        # First do semantic analysis
        super().visitPrintStatement(ctx)
        
        # Generate TAC for print
        self.visit(ctx.expression())
        if self.expression_result:
            self.add_instruction(TACInstruction(
                TACOp.CALL,
                arg1=TACOperand("print"),
                arg2=self.expression_result,
                comment="Print statement"
            ))
        
        return None
    
    def visitIfStatement(self, ctx):
        """Generate TAC for if statement"""
        # First do semantic analysis
        super().visitIfStatement(ctx)
        
        # Generate TAC for condition
        self.visit(ctx.expression())
        condition_result = self.expression_result
        
        # Generate labels
        else_label = self.new_label()
        end_label = self.new_label()
        
        if condition_result:
            # Generate conditional jump
            self.add_instruction(TACInstruction(
                TACOp.GOTO_IF_FALSE,
                arg1=condition_result,
                arg2=TACOperand(else_label, is_label=True),
                comment="If condition false, goto else"
            ))
        
        # Generate TAC for then block
        self.visit(ctx.block(0))
        
        # Jump to end
        self.add_instruction(TACInstruction(
            TACOp.GOTO,
            arg1=TACOperand(end_label, is_label=True),
            comment="Goto end of if"
        ))
        
        # Else label
        self.add_instruction(TACInstruction(
            TACOp.LABEL,
            label=else_label
        ))
        
        # Generate TAC for else block if present
        if len(ctx.block()) > 1:
            self.visit(ctx.block(1))
        
        # End label
        self.add_instruction(TACInstruction(
            TACOp.LABEL,
            label=end_label
        ))
        
        return None
    
    def visitWhileStatement(self, ctx):
        """Generate TAC for while statement"""
        # First do semantic analysis
        super().visitWhileStatement(ctx)
        
        # Generate labels
        loop_label = self.new_label()
        end_label = self.new_label()
        
        # Store labels for break/continue
        self.loop_labels.append({
            'continue': loop_label,
            'break': end_label
        })
        
        # Loop label
        self.add_instruction(TACInstruction(
            TACOp.LABEL,
            label=loop_label
        ))
        
        # Generate TAC for condition
        self.visit(ctx.expression())
        condition_result = self.expression_result
        
        if condition_result:
            # Generate conditional jump
            self.add_instruction(TACInstruction(
                TACOp.GOTO_IF_FALSE,
                arg1=condition_result,
                arg2=TACOperand(end_label, is_label=True),
                comment="While condition false, exit loop"
            ))
        
        # Generate TAC for body
        self.visit(ctx.block())
        
        # Jump back to condition
        self.add_instruction(TACInstruction(
            TACOp.GOTO,
            arg1=TACOperand(loop_label, is_label=True),
            comment="Continue loop"
        ))
        
        # End label
        self.add_instruction(TACInstruction(
            TACOp.LABEL,
            label=end_label
        ))
        
        # Remove loop labels
        self.loop_labels.pop()
        
        return None
    
    def visitForStatement(self, ctx):
        """Generate TAC for for statement"""
        # First do semantic analysis
        super().visitForStatement(ctx)
        
        # Generate labels
        init_label = self.new_label()
        condition_label = self.new_label()
        increment_label = self.new_label()
        end_label = self.new_label()
        
        # Store labels for break/continue
        self.loop_labels.append({
            'continue': increment_label,
            'break': end_label
        })
        
        # Generate TAC for initialization
        if ctx.variableDeclaration():
            self.visit(ctx.variableDeclaration())
        elif ctx.assignment():
            self.visit(ctx.assignment())
        
        # Jump to condition
        self.add_instruction(TACInstruction(
            TACOp.GOTO,
            arg1=TACOperand(condition_label, is_label=True),
            comment="Goto condition"
        ))
        
        # Increment label
        self.add_instruction(TACInstruction(
            TACOp.LABEL,
            label=increment_label
        ))
        
        # Generate TAC for increment
        if len(ctx.assignment()) > 1:
            self.visit(ctx.assignment(1))
        
        # Condition label
        self.add_instruction(TACInstruction(
            TACOp.LABEL,
            label=condition_label
        ))
        
        # Generate TAC for condition
        if ctx.expression():
            self.visit(ctx.expression())
            condition_result = self.expression_result
            
            if condition_result:
                # Generate conditional jump
                self.add_instruction(TACInstruction(
                    TACOp.GOTO_IF_FALSE,
                    arg1=condition_result,
                    arg2=TACOperand(end_label, is_label=True),
                    comment="For condition false, exit loop"
                ))
        
        # Generate TAC for body
        self.visit(ctx.block())
        
        # Jump to increment
        self.add_instruction(TACInstruction(
            TACOp.GOTO,
            arg1=TACOperand(increment_label, is_label=True),
            comment="Continue to increment"
        ))
        
        # End label
        self.add_instruction(TACInstruction(
            TACOp.LABEL,
            label=end_label
        ))
        
        # Remove loop labels
        self.loop_labels.pop()
        
        return None
    
    def visitBreakStatement(self, ctx):
        """Generate TAC for break statement"""
        # First do semantic analysis
        super().visitBreakStatement(ctx)
        
        if self.loop_labels:
            break_label = self.loop_labels[-1]['break']
            self.add_instruction(TACInstruction(
                TACOp.GOTO,
                arg1=TACOperand(break_label, is_label=True),
                comment="Break statement"
            ))
        
        return None
    
    def visitContinueStatement(self, ctx):
        """Generate TAC for continue statement"""
        # First do semantic analysis
        super().visitContinueStatement(ctx)
        
        if self.loop_labels:
            continue_label = self.loop_labels[-1]['continue']
            self.add_instruction(TACInstruction(
                TACOp.GOTO,
                arg1=TACOperand(continue_label, is_label=True),
                comment="Continue statement"
            ))
        
        return None
    
    def visitReturnStatement(self, ctx):
        """Generate TAC for return statement"""
        # First do semantic analysis
        super().visitReturnStatement(ctx)
        
        if ctx.expression():
            # Generate TAC for return expression
            self.visit(ctx.expression())
            if self.expression_result:
                self.add_instruction(TACInstruction(
                    TACOp.RETURN,
                    arg1=self.expression_result,
                    comment="Return with value"
                ))
        else:
            self.add_instruction(TACInstruction(
                TACOp.RETURN,
                comment="Return without value"
            ))
        
        return None
    
    def visitFunctionDeclaration(self, ctx):
        """Generate TAC for function declaration"""
        # First do semantic analysis
        super().visitFunctionDeclaration(ctx)
        
        # Get function symbol
        fname = ctx.Identifier().getText()
        func_symbol = self.symtab.resolve(fname)
        
        if isinstance(func_symbol, ExtendedFuncSymbol):
            self.current_function = func_symbol
            self.return_label = self.new_label()
            
            # Generate function TAC
            func_tac = self._generate_function_tac(ctx, func_symbol)
            self.tac_program.add_function(func_tac)
        
        return None
    
    def _generate_function_tac(self, ctx, func_symbol: ExtendedFuncSymbol) -> TACFunction:
        """Generate TAC for a function"""
        instructions = []
        
        # Function entry
        instructions.append(TACInstruction(
            TACOp.LABEL,
            label=f"func_{func_symbol.name}",
            comment=f"Function {func_symbol.name} entry"
        ))
        
        # Generate TAC for function body
        self.visit(ctx.block())
        
        # Function exit
        instructions.append(TACInstruction(
            TACOp.LABEL,
            label=self.return_label,
            comment=f"Function {func_symbol.name} exit"
        ))
        
        return TACFunction(
            name=func_symbol.name,
            params=[param.name for param in func_symbol.params],
            return_type=str(func_symbol.type),
            instructions=instructions,
            local_vars=[]
        )
    
    def visitClassDeclaration(self, ctx):
        """Generate TAC for class declaration"""
        # First do semantic analysis
        super().visitClassDeclaration(ctx)
        
        # Get class symbol
        cname = ctx.Identifier(0).getText()
        class_symbol = self.symtab.resolve(cname)
        
        if isinstance(class_symbol, ExtendedClassSymbol):
            self.current_class = class_symbol
            
            # Generate class TAC
            class_tac = self._generate_class_tac(ctx, class_symbol)
            self.tac_program.add_class(class_tac)
        
        return None
    
    def _generate_class_tac(self, ctx, class_symbol: ExtendedClassSymbol) -> TACClass:
        """Generate TAC for a class"""
        methods = []
        
        # Generate TAC for class methods
        for member in ctx.classMember():
            if member.functionDeclaration():
                # Generate method TAC
                method_tac = self._generate_method_tac(member.functionDeclaration())
                if method_tac:
                    methods.append(method_tac)
        
        return TACClass(
            name=class_symbol.name,
            parent=ctx.Identifier(1).getText() if len(ctx.Identifier()) > 1 else None,
            fields=list(class_symbol.field_offsets.keys()),
            methods=methods
        )
    
    def _generate_method_tac(self, ctx) -> Optional[TACFunction]:
        """Generate TAC for a class method"""
        # Similar to function generation but with 'this' parameter
        return None  # Placeholder
    
    # Expression TAC generation methods
    
    def visitExpression(self, ctx):
        """Generate TAC for expression"""
        # First do semantic analysis
        result = super().visitExpression(ctx)
        
        # Store expression result
        self.expression_result = self.expr_temp_manager.peek_temp()
        
        return result
    
    def visitAssignmentExpr(self, ctx):
        """Generate TAC for assignment expression"""
        # First do semantic analysis
        result = super().visitAssignmentExpr(ctx)
        
        if ctx.leftHandSide() and ctx.assignmentExpr():
            # Assignment case
            lhs_result = self.visit(ctx.leftHandSide())
            rhs_result = self.visit(ctx.assignmentExpr())
            
            if lhs_result and rhs_result:
                self.add_instruction(TACInstruction(
                    TACOp.ASSIGN,
                    result=lhs_result,
                    arg1=rhs_result,
                    comment="Assignment expression"
                ))
                self.expression_result = rhs_result
        else:
            # Non-assignment case
            result = self.visit(ctx.conditionalExpr(0))
            self.expression_result = self.expr_temp_manager.peek_temp()
        
        return result
    
    def visitAdditiveExpr(self, ctx):
        """Generate TAC for additive expression"""
        # First do semantic analysis
        result = super().visitAdditiveExpr(ctx)
        
        # Generate TAC for first operand
        self.visit(ctx.multiplicativeExpr(0))
        left_result = self.expression_result
        
        # Generate TAC for remaining operands
        for i in range(1, len(ctx.multiplicativeExpr())):
            self.visit(ctx.multiplicativeExpr(i))
            right_result = self.expression_result
            
            if left_result and right_result:
                # Determine operation
                op_text = ctx.getText()
                if '+' in op_text:
                    op = TACOp.ADD
                else:
                    op = TACOp.SUB
                
                # Generate TAC instruction
                result_temp = self.new_temp()
                self.add_instruction(TACInstruction(
                    op,
                    result=result_temp,
                    arg1=left_result,
                    arg2=right_result,
                    comment=f"Additive operation"
                ))
                
                left_result = result_temp
                self.expr_temp_manager.push_temp(result_temp)
        
        self.expression_result = left_result
        return result
    
    def visitMultiplicativeExpr(self, ctx):
        """Generate TAC for multiplicative expression"""
        # First do semantic analysis
        result = super().visitMultiplicativeExpr(ctx)
        
        # Generate TAC for first operand
        self.visit(ctx.unaryExpr(0))
        left_result = self.expression_result
        
        # Generate TAC for remaining operands
        for i in range(1, len(ctx.unaryExpr())):
            self.visit(ctx.unaryExpr(i))
            right_result = self.expression_result
            
            if left_result and right_result:
                # Determine operation
                op_text = ctx.getText()
                if '*' in op_text:
                    op = TACOp.MUL
                elif '/' in op_text:
                    op = TACOp.DIV
                else:
                    op = TACOp.MOD
                
                # Generate TAC instruction
                result_temp = self.new_temp()
                self.add_instruction(TACInstruction(
                    op,
                    result=result_temp,
                    arg1=left_result,
                    arg2=right_result,
                    comment=f"Multiplicative operation"
                ))
                
                left_result = result_temp
                self.expr_temp_manager.push_temp(result_temp)
        
        self.expression_result = left_result
        return result
    
    def visitUnaryExpr(self, ctx):
        """Generate TAC for unary expression"""
        # First do semantic analysis
        result = super().visitUnaryExpr(ctx)
        
        # Generate TAC for operand
        self.visit(ctx.primaryExpr())
        operand_result = self.expression_result
        
        if operand_result:
            # Check for unary operators
            op_text = ctx.getText()
            if op_text.startswith('!'):
                result_temp = self.new_temp()
                self.add_instruction(TACInstruction(
                    TACOp.NOT,
                    result=result_temp,
                    arg1=operand_result,
                    comment="Logical NOT"
                ))
                self.expression_result = result_temp
                self.expr_temp_manager.push_temp(result_temp)
            elif op_text.startswith('-'):
                result_temp = self.new_temp()
                self.add_instruction(TACInstruction(
                    TACOp.SUB,
                    result=result_temp,
                    arg1=TACOperand(0),
                    arg2=operand_result,
                    comment="Unary minus"
                ))
                self.expression_result = result_temp
                self.expr_temp_manager.push_temp(result_temp)
            else:
                self.expression_result = operand_result
        
        return result
    
    def visitPrimaryExpr(self, ctx):
        """Generate TAC for primary expression"""
        # First do semantic analysis
        result = super().visitPrimaryExpr(ctx)
        
        if ctx.literalExpr():
            self.visit(ctx.literalExpr())
        elif ctx.leftHandSide():
            self.visit(ctx.leftHandSide())
        elif ctx.expression():
            self.visit(ctx.expression())
        
        return result
    
    def visitLiteralExpr(self, ctx):
        """Generate TAC for literal expression"""
        # First do semantic analysis
        result = super().visitLiteralExpr(ctx)
        
        # Generate TAC operand for literal
        self.expression_result = self.get_operand(ctx)
        
        return result
    
    def visitLeftHandSide(self, ctx):
        """Generate TAC for left-hand side expression"""
        # First do semantic analysis
        result = super().visitLeftHandSide(ctx)
        
        if ctx.Identifier():
            # Simple identifier
            self.expression_result = self.get_operand(ctx)
        else:
            # Complex left-hand side (array access, property access, etc.)
            # This would need more complex TAC generation
            self.expression_result = self.get_operand(ctx)
        
        return result
