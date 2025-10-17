#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import FileStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser
from program.semantic.visitor import SemanticVisitor
from program.semantic.errors import SemanticError

class DebugVisitor(SemanticVisitor):
    def visitProgram(self, ctx):
        print("DEBUG: visitProgram called")
        print(f"DEBUG: Number of statements: {len(ctx.statement())}")
        for i, stmt in enumerate(ctx.statement()):
            print(f"DEBUG: Visiting statement {i}: {stmt.__class__.__name__}")
            print(f"DEBUG: Statement has functionDeclaration: {bool(stmt.functionDeclaration())}")
            print(f"DEBUG: Statement has returnStatement: {bool(stmt.returnStatement())}")
            self.visit(stmt)
        return None
    
    def visitStatement(self, ctx):
        print("DEBUG: visitStatement called")
        print(f"DEBUG: ctx.variableDeclaration(): {ctx.variableDeclaration()}")
        print(f"DEBUG: ctx.functionDeclaration(): {ctx.functionDeclaration()}")
        print(f"DEBUG: ctx.returnStatement(): {ctx.returnStatement()}")
        return super().visitStatement(ctx)
    
    def visitFunctionDeclaration(self, ctx):
        print("DEBUG: visitFunctionDeclaration called")
        return super().visitFunctionDeclaration(ctx)
    
    def visitReturnStatement(self, ctx):
        print("DEBUG: visitReturnStatement called")
        return super().visitReturnStatement(ctx)

def test_func_bad():
    print("=== Testing func_bad.cps with detailed debug ===")
    
    filepath = "program/tests/func_bad.cps"
    input_stream = FileStream(filepath, encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    print("AST generated successfully")
    print("Tree structure:")
    print(tree.toStringTree(recog=parser))
    
    visitor = DebugVisitor()
    try:
        visitor.visit(tree)
        print("SUCCESS: No semantic errors detected")
    except SemanticError as e:
        print(f"SEMANTIC ERROR: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    test_func_bad()
