function suma(a: integer, b: integer): integer {
    return a + b;
}

let total: integer = 0;
let i: integer = 1;
while (i <= 5) {
    total = suma(total, i);
    i = i + 1;
}
