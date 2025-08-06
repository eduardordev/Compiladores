import java.util.Map;
import java.util.Scanner;
import java.util.Set;

public class Main {
    public static void main(String[] args) {
        String regex = "(a|b)*abb";

        RegexToAFD regexToAFD = new RegexToAFD();
        regex = regexToAFD.aumentarRegex(regex);

        System.out.println("Regex aumentada: " + regex);
        SyntaxTree syntaxTree = new SyntaxTree(regex);

        Scanner sc = new Scanner(System.in);
        System.out.print("\nIngrese una cadena para simular el DFA: ");
        String input = sc.nextLine();
        boolean aceptada = syntaxTree.simularDFA(input);
        System.out.println("La cadena " + (aceptada ? "es aceptada." : "no es aceptada."));

        String dot = syntaxTree.generarDOT();
        System.out.println("\n=== Representación DOT del DFA ===");
        System.out.println(dot);

    }
}
