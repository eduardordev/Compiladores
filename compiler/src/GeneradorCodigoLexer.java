import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

public class GeneradorCodigoLexer {
    public static void generarLexer(
            String nombreArchivo,
            AFDConstructor.AFD afd,
            Map<Integer, String> acciones,
            String header,
            String trailer
    ) throws IOException {

        FileWriter writer = new FileWriter("src/" + nombreArchivo + ".java");

        // Header
        writer.write(header + "\n\n");

        // Clase del lexer
        writer.write("public class " + nombreArchivo + " {\n\n");

        // Método principal de análisis
        writer.write("    public static void getTokens(String input) {\n");
        writer.write("        int i = 0;\n");
        writer.write("        while (i < input.length()) {\n");
        writer.write("            int estado = " + afd.estadoInicial + ";\n");
        writer.write("            int ultimoAceptado = -1;\n");
        writer.write("            int finLexema = -1;\n");
        writer.write("            int j = i;\n");
        writer.write("            while (j < input.length()) {\n");
        writer.write("                char c = input.charAt(j);\n");

        // Transiciones
        writer.write("                switch (estado) {\n");
        for (var entry : afd.transiciones.entrySet()) {
            int origen = entry.getKey();
            writer.write("                    case " + origen + ":\n");
            writer.write("                        switch (c) {\n");
            for (var trans : entry.getValue().entrySet()) {
                char simbolo = trans.getKey();
                int destino = trans.getValue();
                String simboloEscapado = escapeChar(simbolo);
                writer.write("                            case '" + simboloEscapado + "': estado = " + destino + "; j++; break;\n");
            }
            writer.write("                            default: j = input.length(); break;\n");
            writer.write("                        }\n");
            writer.write("                        break;\n");
        }
        writer.write("                    default: j = input.length(); break;\n");
        writer.write("                }\n");

        // Verifica aceptación
        writer.write("                if (" + generarCondicionesFinales(afd) + ") {\n");
        writer.write("                    ultimoAceptado = estado;\n");
        writer.write("                    finLexema = j;\n");
        writer.write("                }\n");
        writer.write("            }\n");

        // Acción y avance
        writer.write("            if (ultimoAceptado != -1) {\n");
        writer.write("                String lexema = input.substring(i, finLexema);\n");
        writer.write("                switch (ultimoAceptado) {\n");
        for (var estado : afd.estadoTokenMap.entrySet()) {
            int estadoId = Integer.parseInt(estado.getKey().substring(1));
            String accion = acciones.get(estado.getValue());
            writer.write("                    case " + estadoId + ": " + accion + "; break;\n");
        }
        writer.write("                }\n");
        writer.write("                i = finLexema;\n");
        writer.write("            } else {\n");
        writer.write("                System.err.println(\"Error léxico en: \" + input.charAt(i));\n");
        writer.write("                i++;\n");
        writer.write("            }\n");
        writer.write("        }\n");
        writer.write("    }\n");

        // Cierre de clase
        writer.write("\n" + trailer + "\n");
        writer.write("}\n");

        writer.close();
        System.out.println("Lexer generado en: " + nombreArchivo + ".java");
    }

    private static String generarCondicionesFinales(AFDConstructor.AFD afd) {
        if (afd.estadosFinales.isEmpty()) return "false";
        StringBuilder sb = new StringBuilder();
        for (int f : afd.estadosFinales) {
            if (sb.length() > 0) sb.append(" || ");
            sb.append("estado == ").append(f);
        }
        return sb.toString();
    }

    private static String escapeChar(char c) {
        return switch (c) {
            case '\'' -> "\\'";
            case '"'  -> "\\\"";
            case '\\' -> "\\\\";
            case '\n' -> "\\n";
            case '\t' -> "\\t";
            case '\r' -> "\\r";
            default -> String.valueOf(c);
        };
    }
}
