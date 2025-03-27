import java.util.*;

public class AFDSimulador {
    private final AFDConstructor.AFD afd;

    public AFDSimulador(AFDConstructor.AFD afd) {
        this.afd = afd;
    }

    public static class ResultadoToken {
        public final String lexema;
        public final int tokenId;

        public ResultadoToken(String lexema, int tokenId) {
            this.lexema = lexema;
            this.tokenId = tokenId;
        }

        @Override
        public String toString() {
            return "Token[" + tokenId + "]: \"" + lexema + "\"";
        }
    }

    public List<ResultadoToken> analizar(String entrada) {
        List<ResultadoToken> tokens = new ArrayList<>();
        int i = 0;

        while (i < entrada.length()) {
            int estadoActual = afd.estadoInicial;
            int ultimoEstadoAceptacion = -1;
            int finLexema = -1;

            for (int j = i; j < entrada.length(); j++) {
                char simbolo = entrada.charAt(j);
                Map<Character, Integer> transiciones = afd.transiciones.get(estadoActual);

                if (transiciones == null || !transiciones.containsKey(simbolo)) {
                    break;
                }

                estadoActual = transiciones.get(simbolo);

                if (afd.estadosFinales.contains(estadoActual)) {
                    ultimoEstadoAceptacion = estadoActual;
                    finLexema = j + 1;
                }
            }

            if (ultimoEstadoAceptacion != -1) {
                String lexema = entrada.substring(i, finLexema);
                int tokenId = afd.estadoTokenMap.get("q" + ultimoEstadoAceptacion);
                tokens.add(new ResultadoToken(lexema, tokenId));
                i = finLexema;
            } else {
                System.err.println("❌ Error léxico en posición " + i + ": '" + entrada.charAt(i) + "'");
                i++; // opcional: podrías lanzar excepción o marcar el error
            }
        }

        return tokens;
    }
}
