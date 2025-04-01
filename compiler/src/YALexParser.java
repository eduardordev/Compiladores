import java.io.*;
import java.util.*;
import java.util.regex.*;

public class YALexParser {
    public static class TokenRule {
        public final String regex;
        public final String action;
        public final int priority;

        public TokenRule(String regex, String action, int priority) {
            this.regex = regex;
            this.action = action;
            this.priority = priority;
        }
    }

    private final Map<String, String> definitions = new HashMap<>();
    private final List<TokenRule> rules = new ArrayList<>();
    private final StringBuilder header = new StringBuilder();
    private final StringBuilder trailer = new StringBuilder();

    public void parse(String filePath) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(filePath));
        String line;
        boolean inHeader = false, inTrailer = false, inRules = false;
        int priority = 0;

        while ((line = reader.readLine()) != null) {
            line = line.trim();

            if (line.startsWith("{")) {
                if (!inHeader && !inRules) {
                    inHeader = true;
                    continue;
                } else if (inRules) {
                    inTrailer = true;
                    continue;
                }
            }

            if (line.startsWith("let ")) {
                // Parse definition: let ident = regexp
                Pattern pattern = Pattern.compile("let\\s+(\\w+)\\s*=\\s*(.+)");
                Matcher matcher = pattern.matcher(line);
                if (matcher.find()) {
                    definitions.put(matcher.group(1), matcher.group(2));
                }
                continue;
            }

            if (line.startsWith("rule ")) {
                inHeader = false;
                inRules = true;
                continue;
            }

            if (inTrailer) {
                trailer.append(line).append("\n");
                continue;
            }

            if (inHeader) {
                header.append(line).append("\n");
                continue;
            }

            if (inRules) {
                if (line.isEmpty()) continue;
                Pattern rulePattern = Pattern.compile("(.+)\\s*\\{(.+)}");
                Matcher matcher = rulePattern.matcher(line);
                if (matcher.find()) {
                    String rawRegex = matcher.group(1).trim();
                    String action = matcher.group(2).trim();

                    for (Map.Entry<String, String> def : definitions.entrySet()) {
                        rawRegex = rawRegex.replaceAll("\\b" + def.getKey() + "\\b", "(" + def.getValue() + ")");
                    }

                    rules.add(new TokenRule(rawRegex, action, priority++));
                }
            }
        }
        reader.close();
    }

    public String getHeader() {
        return header.toString();
    }

    public String getTrailer() {
        return trailer.toString();
    }

    public List<TokenRule> getRules() {
        return rules;
    }

    public String expandirConjuntos(String regex) {
        StringBuilder resultado = new StringBuilder();
        boolean dentroDeSet = false;
        List<Character> charsEnSet = new ArrayList<>();
    
        for (int i = 0; i < regex.length(); i++) {
            char actual = regex.charAt(i);
    
            // Ignorar comillas simples
            if (actual == '\'') {
                continue;
            }
    
            if (actual == '[') {
                dentroDeSet = true;
                charsEnSet.clear();
            } else if (actual == ']' && dentroDeSet) {
                dentroDeSet = false;
                // Expandir el conjunto: unir los caracteres con '|'
                StringBuilder expandido = new StringBuilder();
                for (int j = 0; j < charsEnSet.size(); j++) {
                    if (j > 0) expandido.append('|');
                    expandido.append(charsEnSet.get(j));
                }
                resultado.append("(").append(expandido).append(")");
            } else if (dentroDeSet) {
                // Ignorar la coma dentro de un conjunto
                if (actual == ',') {
                    continue;
                }
                // Si es un rango: por ejemplo, 0-9
                if (i + 2 < regex.length() && regex.charAt(i + 1) == '-' && regex.charAt(i + 2) != ']') {
                    char desde = actual;
                    char hasta = regex.charAt(i + 2);
                    for (char c = desde; c <= hasta; c++) {
                        charsEnSet.add(c);
                    }
                    i += 2; // saltar el rango
                } else {
                    charsEnSet.add(actual);
                }
            } else {
                resultado.append(actual);
            }
        }
    
        return resultado.toString();
    }
    


    public String expandirLiteralSiEsNecesario(String regex) {
        // Solo se elimina las comillas si la cadena tiene al menos 2 caracteres
        if (regex.length() >= 2 && regex.startsWith("\"") && regex.endsWith("\"")) {
            return regex.substring(1, regex.length() - 1);
        }
        return regex;
    }

}
