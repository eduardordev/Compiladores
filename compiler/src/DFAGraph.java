// DFAGraph.java
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

public class DFAGraph {

    public static void generarDOT(AFDConstructor.AFD afd, String nombreArchivo) {
        StringBuilder dot = new StringBuilder();
        dot.append("digraph AFD {\n");
        dot.append("  rankdir=LR;\n");
        dot.append("  __start [shape=none,label=\"\"];\n");

        // --- Recolectar TODOS los nodos: inicial, finales, orígenes y destinos ---
        Set<Integer> nodos = new LinkedHashSet<>();
        nodos.add(afd.estadoInicial);
        nodos.addAll(afd.estadosFinales);
        nodos.addAll(afd.transiciones.keySet());
        for (Map<Character, Integer> m : afd.transiciones.values()) {
            nodos.addAll(m.values());
        }

        // Dibujar cada nodo con su forma (doublecircle si es final)
        for (int estado : nodos) {
            boolean esFinal = afd.estadosFinales.contains(estado);
            String shape = esFinal ? "doublecircle" : "circle";
            dot.append(String.format("  q%d [shape=%s,label=\"q%d\"];\n", estado, shape, estado));
        }

        // Flecha al estado inicial
        dot.append(String.format("  __start -> q%d;\n", afd.estadoInicial));

        // Dibujar transiciones existentes
        for (Map.Entry<Integer, Map<Character, Integer>> entrada : afd.transiciones.entrySet()) {
            int origen = entrada.getKey();
            for (Map.Entry<Character, Integer> trans : entrada.getValue().entrySet()) {
                char simbolo = trans.getKey();
                int destino = trans.getValue();

                // Escapar caracteres especiales
                String label;
                switch (simbolo) {
                    case '"'  -> label = "\\\"";
                    case '\\' -> label = "\\\\";
                    case '\n' -> label = "\\n";
                    case '\t' -> label = "\\t";
                    default   -> label = String.valueOf(simbolo);
                }

                dot.append(String.format("  q%d -> q%d [label=\"%s\"];\n", origen, destino, label));
            }
        }

        dot.append("}\n");

        // Escribir el .dot y generar PNG usando Graphviz
        try (FileWriter writer = new FileWriter(nombreArchivo + ".dot")) {
            writer.write(dot.toString());
        } catch (IOException e) {
            System.err.println("Error al escribir " + nombreArchivo + ".dot: " + e.getMessage());
            return;
        }

        try {
            ProcessBuilder pb = new ProcessBuilder("dot", "-Tpng", nombreArchivo + ".dot", "-o", nombreArchivo + ".png");
            pb.redirectErrorStream(true);
            Process p = pb.start();
            if (p.waitFor() != 0) {
                System.err.println("Graphviz devolvió código de error al generar PNG.");
            }
        } catch (IOException | InterruptedException e) {
            System.err.println("Error al ejecutar Graphviz: " + e.getMessage());
        }
    }
}
