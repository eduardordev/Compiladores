#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import InputStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser

def debug_expression_structure():
    # Test case: Simple arithmetic expression
    code = "let x = 1 + 2;"
    print(f"Code: {code}")
    
    input_stream = InputStream(code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    # Navigate to the expression
    stmt = tree.statement(0)
    var_decl = stmt.variableDeclaration()
    initializer = var_decl.initializer()
    expression = initializer.expression()
    
    print(f"\nExpression type: {expression.__class__.__name__}")
    print(f"Expression text: {expression.getText()}")
    
    # Check what children it has
    children = list(expression.getChildren())
    print(f"\nChildren count: {len(children)}")
    for i, child in enumerate(children):
        print(f"  Child {i}: {child.__class__.__name__} - {child.getText()}")
    
    # Check if it has assignmentExpr
    if hasattr(expression, 'assignmentExpr'):
        assignment_exprs = expression.assignmentExpr()
        print(f"\nassignmentExpr count: {len(assignment_exprs)}")
        for i, ae in enumerate(assignment_exprs):
            print(f"  assignmentExpr {i}: {ae.__class__.__name__} - {ae.getText()}")
            
            # Check what children assignmentExpr has
            ae_children = list(ae.getChildren())
            print(f"    Children count: {len(ae_children)}")
            for j, child in enumerate(ae_children):
                print(f"      Child {j}: {child.__class__.__name__} - {child.getText()}")

if __name__ == "__main__":
    debug_expression_structure()
