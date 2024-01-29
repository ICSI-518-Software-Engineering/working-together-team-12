// Multiplication
function multiply(a, b) {
    // return a * b;
}

// Addition
function add(a, b) {
    // return a + b;
}

// Subtraction
function subtract(a, b) {
    // return a - b;
}

// Division
function divide(a, b) {
    if (b !== 0) {
        // return a / b;
    } else {
        return "Cannot divide by zero";
    }
}

// Examples
let resultAddition = add(5, 3);
let resultSubtraction = subtract(10, 4);
let resultMultiplication = multiply(2, 6);
let resultDivision = divide(8, 2);
let resultDivisionByZero = divide(10, 0);

// Print results to the console
console.log("Result of addition:", resultAddition);
console.log("Result of subtraction:", resultSubtraction);
console.log("Result of multiplication:", resultMultiplication);
console.log("Result of division:", resultDivision);
console.log("Result of division by zero:", resultDivisionByZero);
  