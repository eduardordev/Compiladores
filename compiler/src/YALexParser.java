import java.io.*;
import java.util.*;


public class YALexParser {
    public static class TokenRule {
        public final String RegexNative;
        public final String action;
        public final int priority;

        public TokenRule(String RegexNative, String action, int priority) {
            this.RegexNative = RegexNative;
            this.action = action;
            this.priority = priority;
        }
    }


    private final Map<String, String> definitions = new LinkedHashMap<>();

    private final List<TokenRule> rules = new ArrayList<>();

    private final StringBuilder header = new StringBuilder();

    private final StringBuilder trailer = new StringBuilder();


    public void parse(String filePath) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(filePath));
        String line;
        boolean inHeader  = false;
        boolean inRules   = false;
        boolean inTrailer = false;
        int priority = 0;

        while ((line = reader.readLine()) != null) {
            String trimmed = line.trim();

            // 1) Inicio de sección HEADER
            if (trimmed.equals("{") && !inHeader && !inRules && !inTrailer) {
                inHeader = true;
                continue;
            }
            if (inHeader) {
                if (trimmed.equals("}")) {
                    inHeader = false;
                } else {
                    header.append(line).append("\n");
                }
                continue;
            }

            // 2) Definiciones "let X = Y"
            if (trimmed.startsWith("let ")) {
                // Usamos nuestro propio regex
                RegexNative defPattern = RegexNative.compile("let\\s+(\\w+)\\s*=\\s*(.+)");
                MyMatcher m = defPattern.matcher(line);
                if (m.find()) {
                    String name  = m.group(1);
                    String value = m.group(2);
                    definitions.put(name, value);
                }
                continue;
            }

            // 3) Marca inicio de reglas
            if (trimmed.equals("rule") || trimmed.startsWith("rule ")) {
                inRules = true;
                continue;
            }

            // 4) Cambio a TRAILER tras encontrar '{' después de rules
            if (inRules && trimmed.equals("{")) {
                inRules   = false;
                inTrailer = true;
                continue;
            }

            // 5) Lectura de cada regla
            if (inRules) {
                if (trimmed.isEmpty()) continue;
                // localiza EL bloque de acción, no el literal
                int open  = line.lastIndexOf('{');
                int close = line.lastIndexOf('}');
                if (open >= 0 && close > open) {
                    // raw = todo antes de la llave de acción
                    String raw    = line.substring(0, open).trim();
                    // action = contenido entre { … }
                    String action = line.substring(open + 1, close).trim();

                    // expandir las definitions sin regex
                    for (Map.Entry<String, String> def : definitions.entrySet()) {
                        raw = replaceWord(raw, def.getKey(), "(" + def.getValue() + ")");
                    }

                    rules.add(new TokenRule(raw, action, priority++));
                }
                continue;
            }


            // 6) Lectura de sección TRAILER
            if (inTrailer) {
                if (trimmed.equals("}")) {
                    inTrailer = false;
                } else {
                    trailer.append(line).append("\n");
                }
                continue;
            }

            // Fuera de secciones → ignorar
        }

        reader.close();
    }

    public List<TokenRule> getRules()    { return rules;           }
    public String       getHeader()      { return header.toString(); }
    public String       getTrailer()     { return trailer.toString(); }

    /**
     * Expande conjuntos [a-z0-9] → (a|b|...|9)
     */
    public String expandirConjuntos(String RegexNative) {
        StringBuilder resultado    = new StringBuilder();
        boolean dentroDeSet        = false;
        List<Character> charsEnSet = new ArrayList<>();

        for (int i = 0; i < RegexNative.length(); i++) {
            char actual = RegexNative.charAt(i);

            if (actual == '\'') {
                continue;
            }
            if (actual == '[') {
                dentroDeSet = true;
                charsEnSet.clear();
            } else if (actual == ']' && dentroDeSet) {
                dentroDeSet = false;
                StringBuilder expandido = new StringBuilder();
                for (int j = 0; j < charsEnSet.size(); j++) {
                    if (j > 0) expandido.append('|');
                    expandido.append(charsEnSet.get(j));
                }
                resultado.append("(").append(expandido).append(")");
            } else if (dentroDeSet) {
                if (actual == ',') {
                    continue;
                }
                // rango como a-z
                if (i + 2 < RegexNative.length()
                        && RegexNative.charAt(i+1) == '-'
                        && RegexNative.charAt(i+2) != ']'
                ) {
                    char desde = actual;
                    char hasta = RegexNative.charAt(i + 2);
                    for (char c = desde; c <= hasta; c++) {
                        charsEnSet.add(c);
                    }
                    i += 2;
                } else {
                    charsEnSet.add(actual);
                }
            } else {
                resultado.append(actual);
            }
        }
        return resultado.toString();
    }

    /**
     * Si la regex está entre comillas "abc" → devuelve abc
     */
    public String expandirLiteralSiEsNecesario(String RegexNative) {
        if (RegexNative.length() >= 2
                && RegexNative.startsWith("\"")
                && RegexNative.endsWith("\"")
        ) {
            return RegexNative.substring(1, RegexNative.length() - 1);
        }
        return RegexNative;
    }

    /**
     * Reemplaza solo ocurrencias completas de 'word' en 'text' por 'replacement',
     * sin usar replaceAll ni regex de Java.
     */
    private static String replaceWord(String text, String word, String replacement) {
        StringBuilder sb = new StringBuilder();
        int len  = text.length();
        int wlen = word.length();
        for (int i = 0; i < len; ) {
            // coincide el token completo?
            if (i + wlen <= len
                    && text.substring(i, i + wlen).equals(word)
                    && (i == 0 || !Character.isLetterOrDigit(text.charAt(i - 1)))
                    && (i + wlen == len || !Character.isLetterOrDigit(text.charAt(i + wlen)))
            ) {
                sb.append(replacement);
                i += wlen;
            } else {
                sb.append(text.charAt(i));
                i++;
            }
        }
        return sb.toString();
    }
}


// ---------------------------------------------------
// Implementación propia de regex: RegexNative + MyMatcher
// ---------------------------------------------------

/**
 * Guarda el patrón y cuenta paréntesis para grupos.
 */
class RegexNative {
    private final String regex;
    private final int groupCount;

    private RegexNative(String regex, int groupCount) {
        this.regex      = regex;
        this.groupCount = groupCount;
    }

    public static RegexNative compile(String regex) {
        int groups = countGroups(regex);
        return new RegexNative(regex, groups);
    }

    public MyMatcher matcher(String input) {
        return new MyMatcher(this, input);
    }

    public String getRegex() {
        return regex;
    }

    public int groupCount() {
        return groupCount;
    }

    private static int countGroups(String regex) {
        int count = 0;
        boolean escape = false;
        for (char c : regex.toCharArray()) {
            if (!escape && c == '\\') {
                escape = true;
            } else {
                if (!escape && c == '(') {
                    count++;
                }
                escape = false;
            }
        }
        return count;
    }
}

/**
 * Matcher recursivo que soporta:
 *  - Literales
 *  - Agrupaciones ( )
 *  - Cuantificadores * y +
 *  - Metacaracteres \s (whitespace), \w (word), . (cualquiera)
 */
class MyMatcher {
    private final RegexNative pattern;
    private final String text;
    private final int[] groupStarts;
    private final int[] groupEnds;
    private boolean matched = false;
    private int currentIndex = 0;

    public MyMatcher(RegexNative pattern, String text) {
        this.pattern     = pattern;
        this.text        = text;
        this.groupStarts = new int[pattern.groupCount() + 1];
        this.groupEnds   = new int[pattern.groupCount() + 1];
    }

    /** Busca la siguiente coincidencia en text a partir de currentIndex */
    public boolean find() {
        for (int i = currentIndex; i <= text.length(); i++) {
            if (match(0, i, 0)) {
                currentIndex = i + 1;
                matched = true;
                return true;
            }
        }
        return false;
    }

    /** Comprueba si todo el texto coincide exactamente */
    public boolean matches() {
        matched = match(0, 0, 0);
        return matched;
    }

    /** Devuelve el contenido del grupo capturado */
    public String group(int group) {
        if (!matched) throw new IllegalStateException("No se encontró coincidencia.");
        if (group < 0 || group >= groupStarts.length) throw new IndexOutOfBoundsException();
        return text.substring(groupStarts[group], groupEnds[group]);
    }

    /**
     * Algoritmo recursivo:
     *  p = posición en el patrón
     *  t = posición en el texto
     *  g = índice del grupo actual
     */
    private boolean match(int p, int t, int g) {
        String regex = pattern.getRegex();
        int rlen = regex.length();

        // Si llegamos al final del patrón, coincidir sólo si también fin de texto
        if (p == rlen) {
            return t == text.length();
        }

        char rc = regex.charAt(p);

        // Agrupación
        if (rc == '(') {
            int closing = findClosingParen(regex, p);
            if (closing == -1) return false;
            int groupNum = g + 1;
            groupStarts[groupNum] = t;
            for (int i = t; i <= text.length(); i++) {
                if (match(p + 1, i, groupNum)) {
                    groupEnds[groupNum] = i;
                    if (match(closing + 1, i, g)) return true;
                }
            }
            return false;
        }

        // Cierre de grupo
        if (rc == ')') {
            return match(p + 1, t, g);
        }

        // Cuantificadores '*' o '+'
        if (p + 1 < rlen && (regex.charAt(p + 1) == '*' || regex.charAt(p + 1) == '+')) {
            char quant = regex.charAt(p + 1);
            int i = t;
            // '+' requiere al menos una coincidencia
            if (quant == '+' && (i >= text.length() || !matchSingle(regex, p, text.charAt(i)))) {
                return false;
            }
            // comer tantos como pueda
            while (i < text.length() && matchSingle(regex, p, text.charAt(i))) {
                i++;
            }
            // retroceder intentando la recursión
            for (int j = i; j >= t + (quant == '+' ? 1 : 0); j--) {
                if (match(p + 2, j, g)) return true;
            }
            return false;
        }

        // Un carácter literal / metacaracter 
        if (t >= text.length()) return false;
        if (!matchSingle(regex, p, text.charAt(t))) return false;
        return match(p + 1, t + 1, g);
    }

    /** Comprueba un solo carácter según el patrón en p */
    private boolean matchSingle(String regex, int p, char c) {
        char rc = regex.charAt(p);
        if (rc == '\\') {
            if (p + 1 >= regex.length()) return false;
            char next = regex.charAt(p + 1);
            switch (next) {
                case 's': return Character.isWhitespace(c);
                case 'w': return Character.isLetterOrDigit(c) || c == '_';
                default:  return c == next;
            }
        } else if (rc == '.') {
            return true;  // cualquier cosa
        } else {
            return c == rc;
        }
    }

    /** Encuentra el paréntesis de cierre correspondiente */
    private int findClosingParen(String regex, int openIndex) {
        int depth = 0;
        boolean escape = false;
        for (int i = openIndex; i < regex.length(); i++) {
            char c = regex.charAt(i);
            if (!escape && c == '\\') {
                escape = true;
                continue;
            }
            if (!escape) {
                if (c == '(') depth++;
                else if (c == ')') {
                    depth--;
                    if (depth == 0) return i;
                }
            } else {
                escape = false;
            }
        }
        return -1;
    }
}
