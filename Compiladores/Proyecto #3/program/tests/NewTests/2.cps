function is_even(n: integer): integer {
    if (n == 0) { return 1; }
    else { return is_odd(n - 1); }
}
function is_odd(n: integer): integer {
    if (n == 0) { return 0; }
    else { return is_even(n - 1); }
}

let arr: integer[] = [0,0,0,0,0];
let i: integer = 0;
for (i = 0; i < 5; i = i + 1) {
    let v = is_even(i);
    arr[i] = v;
}
let sum: integer = 0;
i = 0;
while (i < 5) {
    sum = sum + arr[i];
    i = i + 1;
}