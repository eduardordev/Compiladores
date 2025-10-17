#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.Driver import run

def test_files():
    test_cases = [
        ("func_bad.cps", "Should have semantic errors"),
        ("arrays_bad.cps", "Should have semantic errors"), 
        ("class_bad.cps", "Should have semantic errors"),
        ("func_ok.cps", "Should be valid"),
        ("arrays_ok.cps", "Should be valid"),
        ("class_ok.cps", "Should be valid")
    ]
    
    for filename, expected in test_cases:
        filepath = f"program/tests/{filename}"
        print(f"\n=== Testing {filename} ===")
        print(f"Expected: {expected}")
        
        try:
            result = run(filepath)
            print(f"Return code: {result}")
            if "bad" in filename and result == 0:
                print("❌ PROBLEM: Bad file returned success!")
            elif "ok" in filename and result != 0:
                print("❌ PROBLEM: Good file returned error!")
            else:
                print("✅ OK")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_files()
