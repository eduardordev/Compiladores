// Example Compiscript program for TAC generation demonstration
// This program demonstrates various language constructs and their TAC translation

// Global variables
let global_counter: integer = 0;
let message: string = "Hello, Compiscript!";

// Function declaration
function factorial(n: integer): integer {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// Class declaration
class Calculator {
    let result: integer;
    
    function constructor() {
        this.result = 0;
    }
    
    function add(a: integer, b: integer): integer {
        this.result = a + b;
        return this.result;
    }
    
    function getResult(): integer {
        return this.result;
    }
}

// Main program
function main(): void {
    // Variable declarations
    let x: integer = 5;
    let y: integer = 10;
    let sum: integer;
    
    // Arithmetic expressions
    sum = x + y * 2;
    let product: integer = x * y;
    
    // Control flow
    if (sum > 15) {
        print("Sum is greater than 15");
    } else {
        print("Sum is not greater than 15");
    }
    
    // Loop
    for (let i: integer = 0; i < 5; i = i + 1) {
        print(i);
    }
    
    // Function call
    let fact: integer = factorial(5);
    print("Factorial of 5 is: " + fact);
    
    // Object instantiation and method calls
    let calc: Calculator = new Calculator();
    let result: integer = calc.add(10, 20);
    print("Calculator result: " + result);
    
    // Array operations
    let numbers: integer[] = [1, 2, 3, 4, 5];
    let first: integer = numbers[0];
    numbers[1] = 10;
    
    // While loop
    let counter: integer = 0;
    while (counter < 3) {
        print("Counter: " + counter);
        counter = counter + 1;
    }
    
    // Logical expressions
    let flag1: boolean = true;
    let flag2: boolean = false;
    let result_flag: boolean = flag1 && flag2;
    
    // Comparison expressions
    let is_equal: boolean = x == y;
    let is_greater: boolean = x > y;
    
    // Unary expressions
    let negative_x: integer = -x;
    let not_flag: boolean = !flag1;
    
    // String concatenation
    let greeting: string = "Hello" + " " + "World";
    
    // Return statement
    return;
}
