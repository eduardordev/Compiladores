import java.util.*;

public class AFDConstructor {
    public static class AFD {
        public Set<Integer> estadosFinales = new HashSet<>();
        public Map<String, Integer> estadoTokenMap = new HashMap<>();
        public int estadoInicial;
        public Map<Integer, Map<Character, Integer>> transiciones = new HashMap<>();
    }

    private int estadoId = 0;

    public AFD convertirAFNtoAFD(AFN afn) {
        Map<Set<Estado>, Integer> estadoMap = new HashMap<>();
        Queue<Set<Estado>> cola = new LinkedList<>();
        AFD afd = new AFD();

        Set<Estado> inicial = eClosure(Set.of(afn.inicio));
        int idInicial = estadoId++;
        estadoMap.put(inicial, idInicial);
        cola.add(inicial);
        afd.estadoInicial = idInicial;

        while (!cola.isEmpty()) {
            Set<Estado> actual = cola.poll();
            int idActual = estadoMap.get(actual);

            Map<Character, Set<Estado>> movimientos = new HashMap<>();

            for (Estado e : actual) {
                for (Map.Entry<Character, List<Estado>> entry : e.transiciones.entrySet()) {
                    char c = entry.getKey();
                    for (Estado destino : entry.getValue()) {
                        movimientos.computeIfAbsent(c, k -> new HashSet<>()).add(destino);
                    }
                }
            }

            for (char c : movimientos.keySet()) {
                Set<Estado> cerradura = eClosure(movimientos.get(c));
                if (!estadoMap.containsKey(cerradura)) {
                    estadoMap.put(cerradura, estadoId++);
                    cola.add(cerradura);
                }

                afd.transiciones
                        .computeIfAbsent(idActual, k -> new HashMap<>())
                        .put(c, estadoMap.get(cerradura));
            }

            // Si algún estado es de aceptación, registrar
            for (Estado e : actual) {
                if (e.id < 0) {
                    afd.estadosFinales.add(idActual);
                    afd.estadoTokenMap.put("q" + idActual, -1 * e.id); // token ID positivo
                    break;
                }
            }
        }

        return afd;
    }

    private Set<Estado> eClosure(Set<Estado> estados) {
        Set<Estado> resultado = new HashSet<>(estados);
        Stack<Estado> stack = new Stack<>();
        stack.addAll(estados);

        while (!stack.isEmpty()) {
            Estado e = stack.pop();
            for (Estado next : e.epsilonTransiciones) {
                if (!resultado.contains(next)) {
                    resultado.add(next);
                    stack.push(next);
                }
            }
        }
        return resultado;
    }
}
