import guru.nidi.graphviz.attribute.Label;
import guru.nidi.graphviz.attribute.Rank;
import guru.nidi.graphviz.attribute.Shape;
import guru.nidi.graphviz.engine.Format;
import guru.nidi.graphviz.engine.Graphviz;
import guru.nidi.graphviz.model.Graph;
import guru.nidi.graphviz.model.Node;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import static guru.nidi.graphviz.model.Factory.graph;
import static guru.nidi.graphviz.model.Factory.node;
import static guru.nidi.graphviz.model.Link.to;

public class DFAGraph {
    private final Map<String, Map<Character, String>> dfa;
    private final String initialState;
    private final Set<String> finalStates;

    public DFAGraph() {
        this.dfa = new HashMap<>();
        this.initialState = "q0";
        this.finalStates = Set.of("q2"); // Estados finales

        // Definir transiciones del DFA
        dfa.put("q0", Map.of('a', "q1", 'b', "q0"));
        dfa.put("q1", Map.of('a', "q1", 'b', "q2"));
        dfa.put("q2", Map.of('a', "q2", 'b', "q0")); // q2 es final
    }

    public void generarGrafico(String fileName) throws IOException {
        Graph g = graph("DFA").directed().graphAttr().with(Rank.dir(Rank.RankDir.LEFT_TO_RIGHT));
        Node startNode = (Node) node("__start").with(Shape.NONE);
        Map<String, Node> nodeMap = new HashMap<>();

        // Crear nodos del DFA
        for (String state : dfa.keySet()) {
            boolean isFinal = finalStates.contains(state);
            Node n = (Node) node(state).with(isFinal ? Shape.DOUBLE_CIRCLE : Shape.CIRCLE);
            nodeMap.put(state, n);
        }

        // Agregar transiciones
        for (var entry : dfa.entrySet()) {
            String state = entry.getKey();
            for (var transition : entry.getValue().entrySet()) {
                Character symbol = transition.getKey();
                String nextState = transition.getValue();
                nodeMap.get(state).link(to((Node) nodeMap.get(nextState)).with(Label.of(symbol.toString())));
            }
        }

        // Conectar estado inicial
        g = g.with(startNode.link(nodeMap.get(initialState)));

        // Guardar el gráfico en un archivo
        Graphviz.fromGraph(g).render(Format.PNG).toFile(new File(fileName));
        System.out.println("DFA generado en: " + fileName);
    }


}
