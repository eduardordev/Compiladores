"""
Comprehensive Test Suite for TAC Generation

Tests various Compiscript language constructs and their TAC generation
following Dragon Book principles and compiler testing best practices.
"""

import unittest
import sys
import os
from antlr4 import InputStream, CommonTokenStream

# Add the program directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from CompiscriptLexer import CompiscriptLexer
from CompiscriptParser import CompiscriptParser
from tac.generator import TACGenerator
from tac.instructions import TACOp, TACInstruction, TACOperand
from semantic.errors import SemanticError

class TACGenerationTest(unittest.TestCase):
    """Base class for TAC generation tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.generator = TACGenerator()
    
    def parse_and_generate_tac(self, code: str):
        """Parse Compiscript code and generate TAC"""
        input_stream = InputStream(code)
        lexer = CompiscriptLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = CompiscriptParser(tokens)
        
        tree = parser.program()
        tac_program = self.generator.generate_tac(tree)
        return tac_program
    
    def assert_has_instruction(self, tac_program, op: TACOp, comment: str = None):
        """Assert that TAC program contains an instruction with given operation"""
        found = False
        for instr in tac_program.instructions:
            if instr.op == op:
                if comment is None or (instr.comment and comment in instr.comment):
                    found = True
                    break
        
        self.assertTrue(found, f"Expected instruction with op {op} not found")
    
    def assert_has_temp_variable(self, tac_program, temp_id: int):
        """Assert that TAC program uses a specific temporary variable"""
        found = False
        for instr in tac_program.instructions:
            if (instr.result and instr.result.is_temp and instr.result.value == temp_id) or \
               (instr.arg1 and instr.arg1.is_temp and instr.arg1.value == temp_id) or \
               (instr.arg2 and instr.arg2.is_temp and instr.arg2.value == temp_id):
                found = True
                break
        
        self.assertTrue(found, f"Expected temporary variable t{temp_id} not found")

class TestBasicExpressions(TACGenerationTest):
    """Test TAC generation for basic expressions"""
    
    def test_integer_literal(self):
        """Test TAC generation for integer literals"""
        code = "let x = 42;"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have assignment instruction
        self.assert_has_instruction(tac_program, TACOp.ASSIGN, "Initialize x")
    
    def test_string_literal(self):
        """Test TAC generation for string literals"""
        code = 'let message = "Hello World";'
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have assignment instruction
        self.assert_has_instruction(tac_program, TACOp.ASSIGN, "Initialize message")
    
    def test_boolean_literal(self):
        """Test TAC generation for boolean literals"""
        code = "let flag = true;"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have assignment instruction
        self.assert_has_instruction(tac_program, TACOp.ASSIGN, "Initialize flag")
    
    def test_arithmetic_expression(self):
        """Test TAC generation for arithmetic expressions"""
        code = "let result = 5 + 3 * 2;"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have multiplication instruction
        self.assert_has_instruction(tac_program, TACOp.MUL, "Multiplicative operation")
        # Should have addition instruction
        self.assert_has_instruction(tac_program, TACOp.ADD, "Additive operation")
    
    def test_logical_expression(self):
        """Test TAC generation for logical expressions"""
        code = "let flag = true && false;"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have logical AND instruction
        self.assert_has_instruction(tac_program, TACOp.AND, "Logical AND")
    
    def test_comparison_expression(self):
        """Test TAC generation for comparison expressions"""
        code = "let result = 5 < 10;"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have comparison instruction
        self.assert_has_instruction(tac_program, TACOp.LT, "Relational operation")
    
    def test_unary_expression(self):
        """Test TAC generation for unary expressions"""
        code = "let result = -5;"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have unary minus instruction
        self.assert_has_instruction(tac_program, TACOp.SUB, "Unary minus")
    
    def test_logical_not(self):
        """Test TAC generation for logical NOT"""
        code = "let result = !true;"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have logical NOT instruction
        self.assert_has_instruction(tac_program, TACOp.NOT, "Logical NOT")

class TestControlFlow(TACGenerationTest):
    """Test TAC generation for control flow constructs"""
    
    def test_if_statement(self):
        """Test TAC generation for if statements"""
        code = """
        if (x > 0) {
            print("Positive");
        } else {
            print("Non-positive");
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have conditional jump
        self.assert_has_instruction(tac_program, TACOp.GOTO_IF_FALSE, "If condition false, goto else")
        # Should have unconditional jump
        self.assert_has_instruction(tac_program, TACOp.GOTO, "Goto end of if")
        # Should have labels
        self.assert_has_instruction(tac_program, TACOp.LABEL)
    
    def test_while_loop(self):
        """Test TAC generation for while loops"""
        code = """
        while (x > 0) {
            x = x - 1;
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have loop label
        self.assert_has_instruction(tac_program, TACOp.LABEL)
        # Should have conditional jump to exit
        self.assert_has_instruction(tac_program, TACOp.GOTO_IF_FALSE, "While condition false, exit loop")
        # Should have jump back to condition
        self.assert_has_instruction(tac_program, TACOp.GOTO, "Continue loop")
    
    def test_for_loop(self):
        """Test TAC generation for for loops"""
        code = """
        for (let i = 0; i < 10; i = i + 1) {
            print(i);
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have multiple labels
        self.assert_has_instruction(tac_program, TACOp.LABEL)
        # Should have conditional jump
        self.assert_has_instruction(tac_program, TACOp.GOTO_IF_FALSE, "For condition false, exit loop")
        # Should have jump to increment
        self.assert_has_instruction(tac_program, TACOp.GOTO, "Continue to increment")
    
    def test_break_statement(self):
        """Test TAC generation for break statements"""
        code = """
        while (true) {
            break;
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have break jump
        self.assert_has_instruction(tac_program, TACOp.GOTO, "Break statement")
    
    def test_continue_statement(self):
        """Test TAC generation for continue statements"""
        code = """
        while (true) {
            continue;
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have continue jump
        self.assert_has_instruction(tac_program, TACOp.GOTO, "Continue statement")

class TestFunctions(TACGenerationTest):
    """Test TAC generation for functions"""
    
    def test_function_declaration(self):
        """Test TAC generation for function declarations"""
        code = """
        function add(a: integer, b: integer): integer {
            return a + b;
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have function in functions list
        self.assertTrue(len(tac_program.functions) > 0)
        
        # Should have function label
        func = tac_program.functions[0]
        self.assertTrue(any(instr.op == TACOp.LABEL for instr in func.instructions))
    
    def test_function_call(self):
        """Test TAC generation for function calls"""
        code = """
        function test(): integer {
            return 42;
        }
        let result = test();
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have call instruction
        self.assert_has_instruction(tac_program, TACOp.CALL, "Function call")
    
    def test_return_statement(self):
        """Test TAC generation for return statements"""
        code = """
        function getValue(): integer {
            return 42;
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have return instruction
        func = tac_program.functions[0]
        self.assertTrue(any(instr.op == TACOp.RETURN for instr in func.instructions))
    
    def test_return_without_value(self):
        """Test TAC generation for return without value"""
        code = """
        function doSomething(): void {
            return;
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have return instruction without argument
        func = tac_program.functions[0]
        self.assertTrue(any(instr.op == TACOp.RETURN and instr.arg1 is None 
                           for instr in func.instructions))

class TestClasses(TACGenerationTest):
    """Test TAC generation for classes"""
    
    def test_class_declaration(self):
        """Test TAC generation for class declarations"""
        code = """
        class Person {
            let name: string;
            function getName(): string {
                return this.name;
            }
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have class in classes list
        self.assertTrue(len(tac_program.classes) > 0)
        
        # Should have class with fields and methods
        cls = tac_program.classes[0]
        self.assertTrue(len(cls.fields) > 0)
        self.assertTrue(len(cls.methods) > 0)
    
    def test_object_instantiation(self):
        """Test TAC generation for object instantiation"""
        code = """
        class Person {
            let name: string;
        }
        let person = new Person();
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have object creation instruction
        self.assert_has_instruction(tac_program, TACOp.OBJECT_NEW, "Object instantiation")
    
    def test_field_access(self):
        """Test TAC generation for field access"""
        code = """
        class Person {
            let name: string;
        }
        let person = new Person();
        let name = person.name;
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have field access instruction
        self.assert_has_instruction(tac_program, TACOp.FIELD_LOAD, "Field access")
    
    def test_field_assignment(self):
        """Test TAC generation for field assignment"""
        code = """
        class Person {
            let name: string;
        }
        let person = new Person();
        person.name = "John";
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have field assignment instruction
        self.assert_has_instruction(tac_program, TACOp.FIELD_STORE, "Field assignment")

class TestArrays(TACGenerationTest):
    """Test TAC generation for arrays"""
    
    def test_array_declaration(self):
        """Test TAC generation for array declarations"""
        code = "let numbers: integer[] = [1, 2, 3];"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have array creation instruction
        self.assert_has_instruction(tac_program, TACOp.ARRAY_NEW, "Array creation")
    
    def test_array_access(self):
        """Test TAC generation for array access"""
        code = """
        let numbers: integer[] = [1, 2, 3];
        let first = numbers[0];
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have array access instruction
        self.assert_has_instruction(tac_program, TACOp.ARRAY_LOAD, "Array access")
    
    def test_array_assignment(self):
        """Test TAC generation for array assignment"""
        code = """
        let numbers: integer[] = [1, 2, 3];
        numbers[0] = 10;
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have array assignment instruction
        self.assert_has_instruction(tac_program, TACOp.ARRAY_STORE, "Array assignment")
    
    def test_multidimensional_array(self):
        """Test TAC generation for multidimensional arrays"""
        code = "let matrix: integer[][] = [[1, 2], [3, 4]];"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have array creation instructions
        self.assert_has_instruction(tac_program, TACOp.ARRAY_NEW, "Array creation")

class TestTemporaryVariables(TACGenerationTest):
    """Test temporary variable management"""
    
    def test_temp_allocation(self):
        """Test temporary variable allocation"""
        code = "let result = 5 + 3 * 2;"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should use temporary variables
        self.assert_has_temp_variable(tac_program, 0)
        self.assert_has_temp_variable(tac_program, 1)
    
    def test_temp_reuse(self):
        """Test temporary variable reuse"""
        code = """
        let a = 5 + 3;
        let b = 10 - 2;
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should reuse temporary variables when possible
        stats = self.generator.temp_manager.get_stats()
        self.assertLess(stats['total_temps'], 4)  # Should reuse temps
    
    def test_expression_stack(self):
        """Test expression stack management"""
        code = "let result = (5 + 3) * (10 - 2);"
        tac_program = self.parse_and_generate_tac(code)
        
        # Should properly manage expression stack
        self.assert_has_instruction(tac_program, TACOp.ADD, "Additive operation")
        self.assert_has_instruction(tac_program, TACOp.SUB, "Additive operation")
        self.assert_has_instruction(tac_program, TACOp.MUL, "Multiplicative operation")

class TestErrorHandling(TACGenerationTest):
    """Test error handling in TAC generation"""
    
    def test_semantic_error_propagation(self):
        """Test that semantic errors are properly propagated"""
        code = "let x = y;"  # y is not declared
        
        with self.assertRaises(SemanticError):
            self.parse_and_generate_tac(code)
    
    def test_type_mismatch_error(self):
        """Test type mismatch error handling"""
        code = "let x: integer = \"hello\";"  # Type mismatch
        
        with self.assertRaises(SemanticError):
            self.parse_and_generate_tac(code)
    
    def test_undeclared_variable_error(self):
        """Test undeclared variable error handling"""
        code = "x = 5;"  # x is not declared
        
        with self.assertRaises(SemanticError):
            self.parse_and_generate_tac(code)

class TestComplexPrograms(TACGenerationTest):
    """Test TAC generation for complex programs"""
    
    def test_factorial_function(self):
        """Test TAC generation for factorial function"""
        code = """
        function factorial(n: integer): integer {
            if (n <= 1) {
                return 1;
            }
            return n * factorial(n - 1);
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have function with recursion
        self.assertTrue(len(tac_program.functions) > 0)
        func = tac_program.functions[0]
        
        # Should have conditional and recursive call
        self.assertTrue(any(instr.op == TACOp.GOTO_IF_FALSE for instr in func.instructions))
        self.assertTrue(any(instr.op == TACOp.CALL for instr in func.instructions))
    
    def test_class_with_methods(self):
        """Test TAC generation for class with methods"""
        code = """
        class Calculator {
            let result: integer;
            
            function add(a: integer, b: integer): integer {
                this.result = a + b;
                return this.result;
            }
            
            function getResult(): integer {
                return this.result;
            }
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have class with multiple methods
        self.assertTrue(len(tac_program.classes) > 0)
        cls = tac_program.classes[0]
        self.assertTrue(len(cls.methods) >= 2)
    
    def test_nested_loops(self):
        """Test TAC generation for nested loops"""
        code = """
        for (let i = 0; i < 5; i = i + 1) {
            for (let j = 0; j < 3; j = j + 1) {
                print(i * j);
            }
        }
        """
        tac_program = self.parse_and_generate_tac(code)
        
        # Should have multiple loop labels
        label_count = sum(1 for instr in tac_program.instructions if instr.op == TACOp.LABEL)
        self.assertGreaterEqual(label_count, 4)  # At least 4 labels for nested loops

if __name__ == '__main__':
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
    print(f"\nTests run: {result.testsRun}")
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
