#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.Driver import run

def test_simple():
    print("Testing func_ok.cps:")
    result = run('program/tests/func_ok.cps')
    print(f"Return code: {result}")
    
    print("\nTesting arrays_ok.cps:")
    result = run('program/tests/arrays_ok.cps')
    print(f"Return code: {result}")
    
    print("\nTesting arrays_bad.cps:")
    result = run('program/tests/arrays_bad.cps')
    print(f"Return code: {result}")

if __name__ == "__main__":
    test_simple()
