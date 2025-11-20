class A { let n: integer; function constructor(n: integer) { this.n = n; } function val(): integer { return this.n; } }
let a: A = new A(3);
let v: integer = a.val();
