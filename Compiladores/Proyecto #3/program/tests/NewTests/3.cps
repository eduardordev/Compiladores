function complex(n: integer): integer {
    let s: integer = 0;
    for (let i: integer = 0; i < n; i = i + 1) {
        let j: integer = 0;
        while (j < i) {
            if ((i * j) < 10) {
                s = s + i * j;
            } else {
                s = s - j;
            }
            j = j + 1;
        }
        if (s > 50) {
            return s;
        }
    }
    return s;
}

let result: integer = complex(6);