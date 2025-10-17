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
    
    def visitAssignmentExpr(self, ctx):
        print("DEBUG: visitAssignmentExpr called!")
        return super().visitAssignmentExpr(ctx)
    
    def visitConditionalExpr(self, ctx):
        print("DEBUG: visitConditionalExpr called!")
        return super().visitConditionalExpr(ctx)
    
    def visitLogicalOrExpr(self, ctx):
        print("DEBUG: visitLogicalOrExpr called!")
        return super().visitLogicalOrExpr(ctx)
    
    def visitLogicalAndExpr(self, ctx):
        print("DEBUG: visitLogicalAndExpr called!")
        return super().visitLogicalAndExpr(ctx)
    
    def visitEqualityExpr(self, ctx):
        print("DEBUG: visitEqualityExpr called!")
        return super().visitEqualityExpr(ctx)
    
    def visitRelationalExpr(self, ctx):
        print("DEBUG: visitRelationalExpr called!")
        return super().visitRelationalExpr(ctx)
    
    def visitAdditiveExpr(self, ctx):
        print("DEBUG: visitAdditiveExpr called!")
        return super().visitAdditiveExpr(ctx)
    
    def visitMultiplicativeExpr(self, ctx):
        print("DEBUG: visitMultiplicativeExpr called!")
        return super().visitMultiplicativeExpr(ctx)
    
    def visitUnaryExpr(self, ctx):
        print("DEBUG: visitUnaryExpr called!")
        return super().visitUnaryExpr(ctx)
    
    def visitPrimaryExpr(self, ctx):
        print("DEBUG: visitPrimaryExpr called!")
        return super().visitPrimaryExpr(ctx)
    
    def visitArrayLiteral(self, ctx):
        print("DEBUG: visitArrayLiteral called!")
        return super().visitArrayLiteral(ctx)

def test_array_debug_final():
    print("=== Testing array debug final ===")
    
    code = "let xs = [1, true];"
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
    test_array_debug_final()
