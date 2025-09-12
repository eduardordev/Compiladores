#!/usr/bin/env python3
"""
Test comprehensivo para verificar el funcionamiento del IDE y análisis semántico
"""
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.Driver import run

def test_file(file_path, expected_error=True, description=""):
    """Test individual file and verify expected result"""
    print(f"\n{'='*60}")
    print(f"Testing: {file_path}")
    print(f"Description: {description}")
    print(f"Expected error: {expected_error}")
    print(f"{'='*60}")
    
    try:
        result = run(file_path)
        print(f"Return code: {result}")
        
        if expected_error and result == 0:
            print("❌ FAIL: Expected error but got success")
            return False
        elif not expected_error and result != 0:
            print("❌ FAIL: Expected success but got error")
            return False
        else:
            print("✅ PASS: Result matches expectation")
            return True
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_manual_input():
    """Test manual input like PRINT statements"""
    print(f"\n{'='*60}")
    print("Testing manual input")
    print(f"{'='*60}")
    
    test_cases = [
        ('PRINT("Hello World!");', True, "Basic PRINT statement"),
        ('let x = 1 + 2;', False, "Simple arithmetic"),
        ('let x: integer = "hello";', True, "Type mismatch"),
        ('let arr: integer[] = [1, 2, 3];', False, "Valid array"),
        ('let arr: integer[] = [1, "hello", 3];', True, "Mixed array types"),
    ]
    
    for code, expected_error, description in test_cases:
        print(f"\n--- Testing: {description} ---")
        print(f"Code: {code}")
        
        # Create temporary file
        temp_file = "temp_test.cps"
        with open(temp_file, 'w') as f:
            f.write(code)
        
        try:
            result = run(temp_file)
            print(f"Return code: {result}")
            
            if expected_error and result == 0:
                print("❌ FAIL: Expected error but got success")
            elif not expected_error and result != 0:
                print("❌ FAIL: Expected success but got error")
            else:
                print("✅ PASS: Result matches expectation")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

def main():
    print("🧪 COMPREHENSIVE TEST SUITE")
    print("Testing IDE and semantic analysis functionality")
    
    # Test files that should have errors (bad files)
    bad_files = [
        ("program/tests/func_bad.cps", True, "Function with type mismatch"),
        ("program/tests/arrays_bad.cps", True, "Array with mixed types"),
        ("program/tests/class_bad.cps", True, "Class with errors"),
        ("program/tests/sem_types_bad.cps", True, "Semantic type errors"),
        ("program/tests/flow_bad.cps", True, "Control flow errors"),
    ]
    
    # Test files that should be valid (ok files)
    ok_files = [
        ("program/tests/func_ok.cps", False, "Valid function"),
        ("program/tests/arrays_ok.cps", False, "Valid array"),
        ("program/tests/class_ok.cps", False, "Valid class"),
        ("program/tests/sem_types_ok.cps", False, "Valid semantic types"),
        ("program/tests/flow_ok.cps", False, "Valid control flow"),
    ]
    
    # Run tests
    print("\n🔍 Testing BAD files (should have errors):")
    bad_results = []
    for file_path, expected, description in bad_files:
        if os.path.exists(file_path):
            result = test_file(file_path, expected, description)
            bad_results.append(result)
        else:
            print(f"⚠️  File not found: {file_path}")
            bad_results.append(False)
    
    print("\n🔍 Testing OK files (should be valid):")
    ok_results = []
    for file_path, expected, description in ok_files:
        if os.path.exists(file_path):
            result = test_file(file_path, expected, description)
            ok_results.append(result)
        else:
            print(f"⚠️  File not found: {file_path}")
            ok_results.append(False)
    
    # Test manual input
    test_manual_input()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    bad_passed = sum(bad_results)
    bad_total = len(bad_results)
    ok_passed = sum(ok_results)
    ok_total = len(ok_results)
    
    print(f"Bad files: {bad_passed}/{bad_total} passed")
    print(f"OK files: {ok_passed}/{ok_total} passed")
    print(f"Total: {bad_passed + ok_passed}/{bad_total + ok_total} passed")
    
    if bad_passed == bad_total and ok_passed == ok_total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed - check individual results above")

if __name__ == "__main__":
    main()
