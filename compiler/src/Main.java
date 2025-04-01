import java.util.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;

public class Main {
    public static void main(String[] args) {
        try {
            if (args.length != 2) {
                System.out.println("Uso: java Main archivo.yal NombreLexer");
                return;
            }

            String archivoYal = args[0];
            String nombreLexer = args[1];

            // Paso 1: Parsear el archivo YALex
            YALexParser parser = new YALexParser();
            parser.parse(archivoYal);
            List<YALexParser.TokenRule> reglas = parser.getRules();

            // Paso 2: Construir un AFN por regla
            ThompsonConstructor thompson = new ThompsonConstructor();
            List<AFNCombiner.AFNToken> afns = new ArrayList<>();
            Map<Integer, String> acciones = new HashMap<>();

            for (int i = 0; i < reglas.size(); i++) {
                YALexParser.TokenRule regla = reglas.get(i);

                try {
                    // Expansión de conjuntos (como [a-z])
                    String expandida = parser.expandirConjuntos(regla.regex);
                    System.out.println("Regla #" + (i + 1));
                    System.out.println("Original: " + regla.regex);
                    System.out.println("Expandida: " + expandida);

                    String regexLiteralExpandida = parser.expandirLiteralSiEsNecesario(expandida);
                    String regexPostfija = thompson.convertirPostfija(regexLiteralExpandida);
                    System.out.println("Postfija: " + regexPostfija);

                    AFN afn = thompson.construirDesdePostfijo(regexPostfija);
                    afns.add(new AFNCombiner.AFNToken(afn, regla.priority));
                    acciones.put(regla.priority, regla.action);

                } catch (Exception ex) {
                    System.err.println("Error en regla #" + (i + 1) + ": " + regla.regex);
                    ex.printStackTrace();
                    return; // Detenemos todo para depurar
                }
            }

            // Paso 3: Combinar AFNs
            AFNCombiner combinador = new AFNCombiner();
            AFN afnCombinado = combinador.combinarAFNs(afns);

            // Paso 4: Convertir a AFD
            AFDConstructor afdConstructor = new AFDConstructor();
            AFDConstructor.AFD afd = afdConstructor.convertirAFNtoAFD(afnCombinado);

            // Paso 5: Generar el Lexer Java
            GeneradorCodigoLexer.generarLexer(
                    nombreLexer,
                    afd,
                    acciones,
                    parser.getHeader(),
                    parser.getTrailer()
            );

            // Paso 6: Generar gráfica del AFD
            DFAGraph.generarDOT(afd, nombreLexer + "_AFD");

            // Paso 7: Probar el lexer con un archivo de entrada real
            System.out.println("\n🔍 Analizando archivo: prueba-complejidad-alta.txt");

            try {
                String input = new String(Files.readAllBytes(Paths.get("prueba-complejidad-alta.txt")));
                System.out.println("\n Entrada:\n" + input);
                System.out.println("\n Tokens reconocidos:");
                //LexerGenerado.getTokens(input);
            } catch (IOException e) {
                System.err.println("No se pudo leer el archivo de prueba: " + e.getMessage());
            }

        } catch (Exception e) {
            System.err.println("Error general: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
