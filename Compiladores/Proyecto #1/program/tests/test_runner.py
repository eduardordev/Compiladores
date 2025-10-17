"""
Test Runner for TAC Generation Tests

Provides a simple way to run TAC generation tests and validate the implementation.
"""

import unittest
import sys
import os

# Add the program directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tests.test_tac_generation import *

def run_tac_tests():
    """Run all TAC generation tests"""
    print("Running TAC Generation Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBasicExpressions,
        TestControlFlow,
        TestFunctions,
        TestClasses,
        TestArrays,
        TestTemporaryVariables,
        TestErrorHandling,
        TestComplexPrograms
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")
    
    return success

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"Running test: {test_name}")
    print("=" * 50)
    
    # Find the test class and method
    test_class = None
    test_method = None
    
    if '.' in test_name:
        class_name, method_name = test_name.split('.', 1)
        for cls in [TestBasicExpressions, TestControlFlow, TestFunctions, 
                   TestClasses, TestArrays, TestTemporaryVariables, 
                   TestErrorHandling, TestComplexPrograms]:
            if cls.__name__ == class_name:
                test_class = cls
                test_method = method_name
                break
    
    if test_class and test_method:
        suite = unittest.TestSuite()
        suite.addTest(test_class(test_method))
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return len(result.failures) == 0 and len(result.errors) == 0
    else:
        print(f"Test not found: {test_name}")
        return False

def run_quick_tests():
    """Run a subset of quick tests"""
    print("Running Quick TAC Tests...")
    print("=" * 50)
    
    quick_tests = [
        TestBasicExpressions('test_integer_literal'),
        TestBasicExpressions('test_arithmetic_expression'),
        TestControlFlow('test_if_statement'),
        TestFunctions('test_function_declaration'),
        TestTemporaryVariables('test_temp_allocation')
    ]
    
    suite = unittest.TestSuite()
    for test in quick_tests:
        suite.addTest(test)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nQuick tests result: {'PASSED' if len(result.failures) == 0 and len(result.errors) == 0 else 'FAILED'}")
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'quick':
            run_quick_tests()
        elif sys.argv[1] == 'specific':
            if len(sys.argv) > 2:
                run_specific_test(sys.argv[2])
            else:
                print("Usage: python test_runner.py specific <test_name>")
        else:
            print("Usage: python test_runner.py [quick|specific <test_name>]")
    else:
        run_tac_tests()
