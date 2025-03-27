import java.util.*;

public class Estado {
    public int id;
    public Map<Character, List<Estado>> transiciones = new HashMap<>();
    public List<Estado> epsilonTransiciones = new ArrayList<>();

    public Estado(int id) {
        this.id = id;
    }

    public void agregarTransicion(char simbolo, Estado destino) {
        transiciones.computeIfAbsent(simbolo, k -> new ArrayList<>()).add(destino);
    }

    public void agregarTransicionEpsilon(Estado destino) {
        epsilonTransiciones.add(destino);
    }
}