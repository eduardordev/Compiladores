import java.util.*;

public class AFNCombiner {
    private int estadoFinalId = 10000; // para asegurar que no haya conflictos

    public static class AFNToken {
        public final AFN afn;
        public final int tokenId;

        public AFNToken(AFN afn, int tokenId) {
            this.afn = afn;
            this.tokenId = tokenId;
        }
    }

    // Une todos los AFNs individuales en uno solo
    public AFN combinarAFNs(List<AFNToken> afnTokens) {
        Estado nuevoInicio = new Estado(estadoFinalId++);

        for (AFNToken at : afnTokens) {
            nuevoInicio.agregarTransicionEpsilon(at.afn.inicio);
            // Etiquetamos el estado final con el ID del token
            at.afn.fin.id = -1 * at.tokenId; // negativo para identificar aceptación
        }

        // No necesitamos un único estado de aceptación aquí porque cada AFN ya tiene su propio "fin"
        return new AFN(nuevoInicio, null);
    }
}
