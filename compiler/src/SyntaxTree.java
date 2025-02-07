import java.util.*;

public class SyntaxTree {
    Node root;
    Map<Node, Boolean> anulable = new HashMap<>();
    Map<Node, Set<Integer>> primeraPosicion = new HashMap<>();
    Map<Node, Set<Integer>> ultimaPosicion = new HashMap<>();
    Map<Integer, Set<Integer>> siguientePosicion = new HashMap<>();
    Integer posicionCounter = 1;

    private static class Node {
        String value;
        Node left, right;
        int posicion;

        Node(String value) {
            this.value = value;
            this.posicion = -1;
        }

        @Override
        public String toString() {
            return value + (posicion != -1 ? " (Posición: " + posicion + ")" : "");
        }
    }

    public SyntaxTree(String regex) {
        this.root = buildSyntaxTree(regex);
        calcularFunciones(root);
        calcularSiguientePosicion(root);
        imprimirTodasLasPosiciones();
        imprimirTablaTransicion();
    }

    private Node buildSyntaxTree(String regex) {
        Stack<Node> operands = new Stack<>();
        Stack<Character> operators = new Stack<>();

        for (int i = 0; i < regex.length(); i++) {
            char ch = regex.charAt(i);
            if (ch == '(') {
                operators.push(ch);
            } else if (ch == ')') {
                while (!operators.isEmpty() && operators.peek() != '(') {
                    procesarOperador(operands, operators.pop());
                }
                operators.pop();
            } else if (isOperator(String.valueOf(ch))) {
                while (!operators.isEmpty() && precedence(operators.peek()) >= precedence(ch)) {
                    procesarOperador(operands, operators.pop());
                }
                operators.push(ch);
            } else {

                if (!operands.isEmpty() && !operators.contains('(') && operators.peek() != '|') {
                    while (!operators.isEmpty() && precedence(operators.peek()) >= precedence('.')) {
                        procesarOperador(operands, operators.pop());
                    }
                    operators.push('.');
                }
                Node leaf = new Node(String.valueOf(ch));
                leaf.posicion = posicionCounter++;
                operands.push(leaf);
            }
        }

        while (!operators.isEmpty()) {
            procesarOperador(operands, operators.pop());
        }

        return operands.isEmpty() ? null : operands.pop();
    }

    private void procesarOperador(Stack<Node> operands, char operator) {
        Node node = new Node(String.valueOf(operator));
        if (operator == '*') {
            if (operands.isEmpty()) {
                throw new IllegalArgumentException("Operador '*' sin operando.");
            }
            node.right = operands.pop();
        } else {
            if (operands.size() < 2) {
                throw new IllegalArgumentException("Operador '" + operator + "' sin operandos suficientes.");
            }
            node.right = operands.pop();
            node.left = operands.pop();
        }
        operands.push(node);
    }

    private boolean isOperator(String token) {
        return token.equals("|") || token.equals("*") || token.equals(".");
    }

    private int precedence(char operator) {
        return switch (operator) {
            case '|' -> 1;
            case '.' -> 2;
            case '*' -> 3;
            default -> 0;
        };
    }

    private void calcularFunciones(Node node) {
        if (node == null) return;

        calcularFunciones(node.left);
        calcularFunciones(node.right);

        switch (node.value) {
            case "|":
                anulable.put(node, anulable.get(node.left) || anulable.get(node.right));
                primeraPosicion.put(node, union(primeraPosicion.get(node.left), primeraPosicion.get(node.right)));
                ultimaPosicion.put(node, union(ultimaPosicion.get(node.left), ultimaPosicion.get(node.right)));
                break;
            case ".":
                anulable.put(node, anulable.get(node.left) && anulable.get(node.right));
                primeraPosicion.put(node, anulable.get(node.left) ? union(primeraPosicion.get(node.left), primeraPosicion.get(node.right)) : primeraPosicion.get(node.left));
                ultimaPosicion.put(node, anulable.get(node.right) ? union(ultimaPosicion.get(node.left), ultimaPosicion.get(node.right)) : ultimaPosicion.get(node.right));
                break;
            case "*":
                anulable.put(node, true);
                primeraPosicion.put(node, primeraPosicion.get(node.right));
                ultimaPosicion.put(node, ultimaPosicion.get(node.right));
                break;
            default:
                anulable.put(node, false);
                primeraPosicion.put(node, new HashSet<>(Collections.singleton(node.posicion)));
                ultimaPosicion.put(node, new HashSet<>(Collections.singleton(node.posicion)));
                break;
        }
    }

    private void calcularSiguientePosicion(Node node) {
        if (node == null) return;

        if (node.value.equals(".")) {
            for (int pos : ultimaPosicion.get(node.left)) {
                siguientePosicion.computeIfAbsent(pos, k -> new HashSet<>()).addAll(primeraPosicion.get(node.right));
            }
        } else if (node.value.equals("*")) {
            for (int pos : ultimaPosicion.get(node.right)) {
                siguientePosicion.computeIfAbsent(pos, k -> new HashSet<>()).addAll(primeraPosicion.get(node.right));
            }
        }

        calcularSiguientePosicion(node.left);
        calcularSiguientePosicion(node.right);
    }

    private Set<Integer> union(Set<Integer> a, Set<Integer> b) {
        Set<Integer> result = new HashSet<>(a);
        result.addAll(b);
        return result;
    }

    private void imprimirTodasLasPosiciones() {
        System.out.println("=== Funciones Calculadas ===");
        imprimirRecursivo(root);
        System.out.println("\n=== Siguientes Posiciones ===");
        siguientePosicion.forEach((k, v) -> System.out.println("Posición " + k + " → " + v));
    }

    public Map<Set<Integer>, Map<Character, Set<Integer>>> construirTablaTransicion() {

        Set<Integer> estadoInicial = primeraPosicion.get(root);

        Set<Character> alfabeto = new HashSet<>();
        for (int pos : siguientePosicion.keySet()) {
            Node nodo = encontrarNodoPorPosicion(root, pos);
            if (nodo != null && !nodo.value.equals("#") && !isOperator(nodo.value)) {
                alfabeto.add(nodo.value.charAt(0));
            }
        }

        Map<Set<Integer>, Map<Character, Set<Integer>>> tablaTransicion = new LinkedHashMap<>();
        Queue<Set<Integer>> cola = new LinkedList<>();
        cola.add(estadoInicial);
        tablaTransicion.put(estadoInicial, new HashMap<>());

        while (!cola.isEmpty()) {
            Set<Integer> estadoActual = cola.poll();

            for (char simbolo : alfabeto) {
                Set<Integer> siguienteEstado = new HashSet<>();
                for (int pos : estadoActual) {
                    Node nodo = encontrarNodoPorPosicion(root, pos);
                    if (nodo != null && nodo.value.equals(String.valueOf(simbolo))) {
                        siguienteEstado.addAll(siguientePosicion.get(pos));
                    }
                }
                if (!siguienteEstado.isEmpty()) {
                    if (!tablaTransicion.containsKey(siguienteEstado)) {
                        tablaTransicion.put(siguienteEstado, new HashMap<>());
                        cola.add(siguienteEstado);
                    }
                    tablaTransicion.get(estadoActual).put(simbolo, siguienteEstado);
                }
            }
        }

        return tablaTransicion;
    }

    private Node encontrarNodoPorPosicion(Node node, int posicion) {
        if (node == null) return null;
        if (node.posicion == posicion) return node;
        Node izquierda = encontrarNodoPorPosicion(node.left, posicion);
        if (izquierda != null) return izquierda;
        return encontrarNodoPorPosicion(node.right, posicion);
    }

    public void imprimirTablaTransicion() {
        Map<Set<Integer>, Map<Character, Set<Integer>>> tabla = construirTablaTransicion();
        int posicionAceptacion = posicionCounter - 1;

        System.out.println("\n=== Tabla de Transiciones del AFD ===");
        System.out.printf("%-20s", "Estado");
        Set<Character> alfabeto = new HashSet<>();
        for (Map.Entry<Set<Integer>, Map<Character, Set<Integer>>> entry : tabla.entrySet()) {
            alfabeto.addAll(entry.getValue().keySet());
        }
        for (char c : alfabeto) {
            System.out.printf("%-20s", "Con '" + c + "'");
        }
        System.out.println();

        for (Set<Integer> estado : tabla.keySet()) {
            System.out.printf("%-20s", estado);
            for (char c : alfabeto) {
                Set<Integer> destino = tabla.get(estado).get(c);
                System.out.printf("%-20s", destino != null ? destino : "∅");
            }
            System.out.println();
        }

        // Estados de aceptación
        System.out.println("\nEstados de Aceptación:");
        for (Set<Integer> estado : tabla.keySet()) {
            if (estado.contains(posicionAceptacion)) {
                System.out.println(estado);
            }
        }
    }

    private void imprimirRecursivo(Node node) {
        if (node == null) return;
        imprimirRecursivo(node.left);
        imprimirRecursivo(node.right);
        System.out.println("Nodo: " + node);
        System.out.println("  Anulable: " + anulable.get(node));
        System.out.println("  Primera Posición: " + primeraPosicion.get(node));
        System.out.println("  Última Posición: " + ultimaPosicion.get(node));
    }
}
