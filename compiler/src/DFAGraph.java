import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;
import java.util.Set;

public class DFAGraph {
    public static void generarDOT(AFDConstructor.AFD afd, String nombreArchivo) {
        StringBuilder dot = new StringBuilder();
        dot.append("digraph AFD {\n");
        dot.append("  rankdir=LR;\n");
        dot.append("  __start [shape=none,label=\"\"];\n");

        // Nodos del AFD
        for (int estado : afd.transiciones.keySet()) {
            boolean esFinal = afd.estadosFinales.contains(estado);
            dot.append("  q").append(estado)
                    .append(" [shape=").append(esFinal ? "doublecircle" : "circle")
                    .append(", label=\"q").append(estado).append("\"];\n");
        }

        // Flecha inicial
        dot.append("  __start -> q").append(afd.estadoInicial).append(";\n");

        // Transiciones
        for (Map.Entry<Integer, Map<Character, Integer>> entrada : afd.transiciones.entrySet()) {
            int origen = entrada.getKey();
            for (Map.Entry<Character, Integer> trans : entrada.getValue().entrySet()) {
                char simbolo = trans.getKey();
                int destino = trans.getValue();

                // Escape seguro del símbolo para el label
                String etiquetaEscapada = switch (simbolo) {
                    case '"' -> "\\\"";
                    case '\\' -> "\\\\";
                    case '\n' -> "\\n";
                    case '\t' -> "\\t";
                    default -> String.valueOf(simbolo);
                };

                dot.append("  q").append(origen)
                        .append(" -> q").append(destino)
                        .append(" [label=\"").append(etiquetaEscapada).append("\"];\n");
            }
        }

        dot.append("}\n");

        // Escribir el archivo .dot
        try (FileWriter writer = new FileWriter(nombreArchivo + ".dot")) {
            writer.write(dot.toString());
            System.out.println("Archivo DOT generado: " + nombreArchivo + ".dot");
        } catch (IOException e) {
            System.err.println("Error al escribir el archivo DOT: " + e.getMessage());
            return;
        }

        // Ejecutar Graphviz para generar PNG
        try {
            ProcessBuilder pb = new ProcessBuilder("dot", "-Tpng", nombreArchivo + ".dot", "-o", nombreArchivo + ".png");
            pb.redirectErrorStream(true);
            Process proceso = pb.start();
            int exitCode = proceso.waitFor();
            if (exitCode == 0) {
                System.out.println("Imagen PNG generada: " + nombreArchivo + ".png");
            } else {
                System.err.println("Error al ejecutar Graphviz. Código: " + exitCode);
            }
        } catch (IOException | InterruptedException e) {
            System.err.println("Error al generar imagen PNG: " + e.getMessage());
        }
    }
}
