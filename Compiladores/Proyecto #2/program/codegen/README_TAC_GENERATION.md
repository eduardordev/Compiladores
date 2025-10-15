# Generación de Código Intermedio (TAC)

## Sintaxis del TAC

- `t0 = a ADD b`
- `STORE t0 -> x`
- `LOAD x = t0`
- `IFZ cond GOTO L1`
- `LABEL L1:`
- `RETURN val`

## Ejemplo

Código fuente:

```cps
let a = 1;
let b = 2;
let c = a + b;
```
