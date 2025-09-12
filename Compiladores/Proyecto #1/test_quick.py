#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.Driver import run

print("Testing func_bad.cps (should error):")
result = run('program/tests/func_bad.cps')
print(f"Result: {result}")

print("\nTesting func_ok.cps (should be valid):")
result = run('program/tests/func_ok.cps')
print(f"Result: {result}")

print("\nTesting arrays_bad.cps (should error):")
result = run('program/tests/arrays_bad.cps')
print(f"Result: {result}")

print("\nTesting arrays_ok.cps (should be valid):")
result = run('program/tests/arrays_ok.cps')
print(f"Result: {result}")
