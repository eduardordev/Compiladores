import guru.nidi.graphviz.model.LinkSource;

import java.util.List;

public class Node {
    String value;
    Node left, right;
    Integer posicion;

    public Node(String value) {
        this.value = value;
        this.left = this.right = null;
        this.posicion = -1;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public Node getLeft() {
        return left;
    }

    public void setLeft(Node left) {
        this.left = left;
    }

    public Node getRight() {
        return right;
    }

    public void setRight(Node right) {
        this.right = right;
    }

    public Integer getPosicion() {
        return posicion;
    }

    public void setPosicion(Integer posicion) {
        this.posicion = posicion;
    }

    public List<? extends LinkSource> link(Node with) {
        return List.of();
    }
}
