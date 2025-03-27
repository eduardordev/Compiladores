import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ThompsonConstructor {
    private final AtomicInteger estadoId = new AtomicInteger();

    // Método que construye un AFN a partir de una expresión regular en notación postfija.
    public AFN construirDesdePostfijo(String postfijo) {
        Stack<AFN> pila = new Stack<>();
        int i = 0;
        while (i < postfijo.length()) {
            char c = postfijo.charAt(i);
            if (c == '{') {
                // Se detecta un literal envuelto en llaves.
                int j = postfijo.indexOf('}', i);
                if (j == -1) {
                    throw new RuntimeException("Error: llave de cierre '}' no encontrada.");
                }
                String literal = postfijo.substring(i + 1, j);
                // Construir un AFN para la cadena literal completa.
                AFN afnLiteral = construirAFNParaLiteral(literal);
                pila.push(afnLiteral);
                i = j + 1;
            } else {
                switch (c) {
                    case '*': {
                        AFN afn = pila.pop();
                        Estado sInicio = new Estado(estadoId.getAndIncrement());
                        Estado sFin = new Estado(estadoId.getAndIncrement());

                        sInicio.agregarTransicionEpsilon(afn.inicio);
                        sInicio.agregarTransicionEpsilon(sFin);
                        afn.fin.agregarTransicionEpsilon(afn.inicio);
                        afn.fin.agregarTransicionEpsilon(sFin);

                        pila.push(new AFN(sInicio, sFin));
                        i++;
                        break;
                    }
                    case '.': {
                        AFN afn2 = pila.pop();
                        AFN afn1 = pila.pop();

                        afn1.fin.agregarTransicionEpsilon(afn2.inicio);
                        pila.push(new AFN(afn1.inicio, afn2.fin));
                        i++;
                        break;
                    }
                    case '|': {
                        AFN afn2 = pila.pop();
                        AFN afn1 = pila.pop();

                        Estado sInicio = new Estado(estadoId.getAndIncrement());
                        Estado sFin = new Estado(estadoId.getAndIncrement());

                        sInicio.agregarTransicionEpsilon(afn1.inicio);
                        sInicio.agregarTransicionEpsilon(afn2.inicio);

                        afn1.fin.agregarTransicionEpsilon(sFin);
                        afn2.fin.agregarTransicionEpsilon(sFin);

                        pila.push(new AFN(sInicio, sFin));
                        i++;
                        break;
                    }
                    default: {
                        // Operando individual (un solo caracter)
                        Estado sInicio = new Estado(estadoId.getAndIncrement());
                        Estado sFin = new Estado(estadoId.getAndIncrement());

                        sInicio.agregarTransicion(c, sFin);
                        pila.push(new AFN(sInicio, sFin));
                        i++;
                        break;
                    }
                }
            }
        }
        return pila.pop();
    }

    // Crea un AFN para una cadena literal completa (por ejemplo, "if")
    private AFN construirAFNParaLiteral(String literal) {
        Estado sInicio = new Estado(estadoId.getAndIncrement());
        Estado current = sInicio;
        for (int i = 0; i < literal.length(); i++) {
            Estado next = new Estado(estadoId.getAndIncrement());
            current.agregarTransicion(literal.charAt(i), next);
            current = next;
        }
        return new AFN(sInicio, current);
    }

    // Convierte una expresión regular en notación infija a notación postfija usando el algoritmo de Shunting-yard.
    // Se adapta para detectar literales entre llaves y tratarlos como un solo token.
    public String convertirPostfija(String regex) {
        StringBuilder salida = new StringBuilder();
        Stack<Character> operadores = new Stack<>();
        String input = insertarConcatenaciones(regex);

        Map<Character, Integer> precedencia = Map.of(
                '*', 3,
                '.', 2,
                '|', 1
        );

        for (int i = 0; i < input.length(); i++) {
            char c = input.charAt(i);
            if (c == '{') {
                // Se copia el literal completo
                int j = input.indexOf('}', i);
                if (j == -1) {
                    throw new RuntimeException("Error: llave de cierre '}' no encontrada en conversión a postfija.");
                }
                String token = input.substring(i, j + 1);
                salida.append(token);
                i = j; // saltar el literal ya procesado
            } else if (c == '(') {
                operadores.push(c);
            } else if (c == ')') {
                while (!operadores.isEmpty() && operadores.peek() != '(') {
                    salida.append(operadores.pop());
                }
                if (!operadores.isEmpty()) {
                    operadores.pop(); // quitar '('
                }
            } else if (precedencia.containsKey(c)) {
                while (!operadores.isEmpty() && operadores.peek() != '(' &&
                        precedencia.get(c) <= precedencia.get(operadores.peek())) {
                    salida.append(operadores.pop());
                }
                operadores.push(c);
            } else {
                salida.append(c);
            }
        }

        while (!operadores.isEmpty()) {
            salida.append(operadores.pop());
        }

        return salida.toString();
    }

    private String insertarConcatenaciones(String regex) {
        // Manejo explícito de tokens literales atómicos:
        if (regex.equals("[") || regex.equals("]") ||
                regex.equals("(") || regex.equals(")") ||
                regex.equals("{") || regex.equals("}")) {
            return "{" + regex + "}";
        }

        // Otras condiciones especiales para operadores y literales alfanuméricos.
        if (regex.equals("*") ||
                regex.equals("==") || regex.equals("!=") ||
                regex.equals("<=") || regex.equals(">=") ||
                regex.equals("&&") || regex.equals("||") ||
                regex.matches("[a-zA-Z0-9]+")) {
            return "{" + regex + "}";
        }

        // Si no se cumple ningún caso especial, se procede a insertar concatenaciones normalmente.
        StringBuilder result = new StringBuilder();
        String operadores = "*|().";
        int i = 0;
        while (i < regex.length()) {
            // Detectar operadores de dos caracteres (como "==", etc.)
            if (i + 1 < regex.length()) {
                String dosChars = "" + regex.charAt(i) + regex.charAt(i + 1);
                Set<String> opMulti = Set.of("==", "!=", "<=", ">=", "&&", "||");
                if (opMulti.contains(dosChars)) {
                    result.append(dosChars);
                    i += 2;
                    if (i < regex.length()) {
                        char siguiente = regex.charAt(i);
                        if (!operadores.contains(String.valueOf(siguiente)) &&
                                siguiente != '(' && siguiente != '|' && siguiente != ')') {
                            result.append('.');
                        }
                    }
                    continue;
                }
            }
            char actual = regex.charAt(i);
            result.append(actual);
            i++;
            if (i < regex.length()) {
                char siguiente = regex.charAt(i);
                if ((actual != '(' && actual != '|' && !operadores.contains(String.valueOf(siguiente))) ||
                        (actual == '*' && (siguiente != ')' && siguiente != '|' && siguiente != '*'))) {
                    result.append('.');
                }
            }
        }
        return result.toString();
    }
}
