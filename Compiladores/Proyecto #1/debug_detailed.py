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

def debug_visit_tree(tree, visitor, level=0):
    """Debug function to see what's being visited"""
    indent = "  " * level
    class_name = tree.__class__.__name__
    print(f"{indent}Visiting: {class_name}")
    
    # Try to visit this node
    method_name = f"visit{class_name}"
    if hasattr(visitor, method_name):
        method = getattr(visitor, method_name)
        try:
            result = method(tree)
            print(f"{indent}  -> Result: {result}")
        except Exception as e:
            print(f"{indent}  -> ERROR: {e}")
            raise
    else:
        print(f"{indent}  -> No visit method found")
    
    # Visit children
    for i, child in enumerate(tree.getChildren()):
        print(f"{indent}  Child {i}:")
        debug_visit_tree(child, visitor, level + 1)

def test_func_bad():
    print("=== Detailed test of func_bad.cps ===")
    
    filepath = "program/tests/func_bad.cps"
    input_stream = FileStream(filepath, encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    print("AST generated successfully")
    print("Tree structure:")
    debug_visit_tree(tree, SemanticVisitor())

if __name__ == "__main__":
    test_func_bad()
