public class Main {
    public static void main(String[] args) {
        String regex = "(a|b*)*ba";
        RegexToAFD regexToAFD = new RegexToAFD();
        regex = regexToAFD.aumentarRegex(regex);

        System.out.println("Regex aumentada: " + regex);

        SyntaxTree syntaxTree = new SyntaxTree(regex);

    }
}
