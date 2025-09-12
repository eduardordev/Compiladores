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
    
    def visitArrayLiteral(self, ctx):
        print("DEBUG: visitArrayLiteral called!")
        return super().visitArrayLiteral(ctx)
    
    def visitLiteralExpr(self, ctx):
        print(f"DEBUG: visitLiteralExpr called with: {ctx.getText()}")
        return super().visitLiteralExpr(ctx)

def test_array_detailed():
    print("=== Testing array detailed ===")
    
    code = "let xs = [1, true];"
    print(f"Code: {code}")
    
    input_stream = InputStream(code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    print("AST generated")
    print("Tree structure:")
    print(tree.toStringTree(recog=parser))
    
    visitor = DebugVisitor()
    try:
        visitor.visit(tree)
        print("SUCCESS: No errors")
    except SemanticError as e:
        print(f"SEMANTIC ERROR: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    test_array_detailed()
