#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import InputStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser
from program.semantic.visitor import SemanticVisitor
from program.semantic.errors import SemanticError

class DebugVisitor(SemanticVisitor):
    def visit(self, tree):
        print(f"DEBUG: visit() called with {tree.__class__.__name__}")
        return super().visit(tree)
    
    def visitExpression(self, ctx):
        print("DEBUG: visitExpression called!")
        return super().visitExpression(ctx)
    
    def visitAdditiveExpr(self, ctx):
        print("DEBUG: visitAdditiveExpr called!")
        return super().visitAdditiveExpr(ctx)

def test_expression_debug():
    print("=== Testing expression debug ===")
    
    # Test case: Simple arithmetic expression
    code = "let x = 1 + 2;"
    print(f"Code: {code}")
    
    input_stream = InputStream(code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    visitor = DebugVisitor()
    try:
        visitor.visit(tree)
        print("SUCCESS: No errors")
    except SemanticError as e:
        print(f"SEMANTIC ERROR: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    test_expression_debug()
