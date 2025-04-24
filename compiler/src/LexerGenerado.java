

public class LexerGenerado {

    public static void getTokens(String input) {
        int i = 0;
        while (i < input.length()) {
            int estado = 0;
            int ultimoAceptado = -1;
            int finLexema = -1;
            int j = i;
            while (j < input.length()) {
                char c = input.charAt(j);
                switch (estado) {
                    case 0:
                        switch (c) {
                            case '\\': estado = 1; j++; break;
                            case ']': estado = 2; j++; break;
                            case ' ': estado = 3; j++; break;
                            case '!': estado = 4; j++; break;
                            case 'b': estado = 5; j++; break;
                            case '\"': estado = 6; j++; break;
                            case 'c': estado = 7; j++; break;
                            case 'd': estado = 8; j++; break;
                            case '%': estado = 9; j++; break;
                            case 'e': estado = 10; j++; break;
                            case '&': estado = 11; j++; break;
                            case 'f': estado = 12; j++; break;
                            case '(': estado = 13; j++; break;
                            case ')': estado = 14; j++; break;
                            case 'i': estado = 15; j++; break;
                            case '*': estado = 16; j++; break;
                            case '+': estado = 17; j++; break;
                            case ',': estado = 18; j++; break;
                            case 'm': estado = 19; j++; break;
                            case '-': estado = 20; j++; break;
                            case 'n': estado = 21; j++; break;
                            case '/': estado = 22; j++; break;
                            case 'r': estado = 23; j++; break;
                            case 't': estado = 24; j++; break;
                            case 'v': estado = 25; j++; break;
                            case 'w': estado = 26; j++; break;
                            case '{': estado = 27; j++; break;
                            case ';': estado = 28; j++; break;
                            case '|': estado = 29; j++; break;
                            case '<': estado = 30; j++; break;
                            case '=': estado = 31; j++; break;
                            case '}': estado = 32; j++; break;
                            case '>': estado = 33; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 1:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 2:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 3:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 4:
                        switch (c) {
                            case '=': estado = 34; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 5:
                        switch (c) {
                            case 'o': estado = 35; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 6:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 7:
                        switch (c) {
                            case 'h': estado = 36; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 8:
                        switch (c) {
                            case 'i': estado = 37; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 9:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 10:
                        switch (c) {
                            case 'l': estado = 38; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 11:
                        switch (c) {
                            case '&': estado = 39; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 12:
                        switch (c) {
                            case 'a': estado = 40; j++; break;
                            case 'l': estado = 41; j++; break;
                            case 'o': estado = 42; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 13:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 14:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 15:
                        switch (c) {
                            case 'd': estado = 43; j++; break;
                            case 'f': estado = 44; j++; break;
                            case 'n': estado = 45; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 16:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 17:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 18:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 19:
                        switch (c) {
                            case 'a': estado = 46; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 20:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 21:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 22:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 23:
                        switch (c) {
                            case 'e': estado = 47; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 24:
                        switch (c) {
                            case 'r': estado = 48; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 25:
                        switch (c) {
                            case 'o': estado = 49; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 26:
                        switch (c) {
                            case 'h': estado = 50; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 27:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 28:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 29:
                        switch (c) {
                            case '|': estado = 51; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 30:
                        switch (c) {
                            case '=': estado = 52; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 31:
                        switch (c) {
                            case '=': estado = 53; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 32:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 33:
                        switch (c) {
                            case '=': estado = 54; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 34:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 35:
                        switch (c) {
                            case 'o': estado = 55; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 36:
                        switch (c) {
                            case 'a': estado = 56; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 37:
                        switch (c) {
                            case 'g': estado = 57; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 38:
                        switch (c) {
                            case 's': estado = 58; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 39:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 40:
                        switch (c) {
                            case 'l': estado = 59; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 41:
                        switch (c) {
                            case 'o': estado = 60; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 42:
                        switch (c) {
                            case 'r': estado = 61; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 43:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 44:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 45:
                        switch (c) {
                            case 't': estado = 62; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 46:
                        switch (c) {
                            case 'i': estado = 63; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 47:
                        switch (c) {
                            case 't': estado = 64; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 48:
                        switch (c) {
                            case 'u': estado = 65; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 49:
                        switch (c) {
                            case 'i': estado = 66; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 50:
                        switch (c) {
                            case 'i': estado = 67; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 51:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 52:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 53:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 54:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 55:
                        switch (c) {
                            case 'l': estado = 68; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 56:
                        switch (c) {
                            case 'r': estado = 69; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 57:
                        switch (c) {
                            case 'i': estado = 70; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 58:
                        switch (c) {
                            case 'e': estado = 71; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 59:
                        switch (c) {
                            case 's': estado = 72; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 60:
                        switch (c) {
                            case 'a': estado = 73; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 61:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 62:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 63:
                        switch (c) {
                            case 'n': estado = 74; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 64:
                        switch (c) {
                            case 'u': estado = 75; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 65:
                        switch (c) {
                            case 'e': estado = 76; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 66:
                        switch (c) {
                            case 'd': estado = 77; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 67:
                        switch (c) {
                            case 'l': estado = 78; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 68:
                        switch (c) {
                            case 'e': estado = 79; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 69:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 70:
                        switch (c) {
                            case 't': estado = 80; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 71:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 72:
                        switch (c) {
                            case 'e': estado = 81; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 73:
                        switch (c) {
                            case 't': estado = 82; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 74:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 75:
                        switch (c) {
                            case 'r': estado = 83; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 76:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 77:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 78:
                        switch (c) {
                            case 'e': estado = 84; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 79:
                        switch (c) {
                            case 'a': estado = 85; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 80:
                        switch (c) {
                            case 's': estado = 86; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 81:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 82:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 83:
                        switch (c) {
                            case 'n': estado = 87; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 84:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 85:
                        switch (c) {
                            case 'n': estado = 88; j++; break;
                            default: j = input.length(); break;
                        }
                        break;
                    case 86:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 87:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    case 88:
                        switch (c) {
                            default: j = input.length(); break;
                        }
                        break;
                    default: j = input.length(); break;
                }
                if (estado == 1 || estado == 2 || estado == 3 || estado == 4 || estado == 69 || estado == 6 || estado == 71 || estado == 9 || estado == 74 || estado == 76 || estado == 13 || estado == 77 || estado == 14 || estado == 16 || estado == 17 || estado == 81 || estado == 18 || estado == 82 || estado == 20 || estado == 84 || estado == 21 || estado == 22 || estado == 86 || estado == 23 || estado == 87 || estado == 24 || estado == 88 || estado == 27 || estado == 28 || estado == 30 || estado == 31 || estado == 32 || estado == 33 || estado == 34 || estado == 39 || estado == 43 || estado == 51 || estado == 52 || estado == 53 || estado == 54 || estado == 61 || estado == 62) {
                    ultimoAceptado = estado;
                    finLexema = j;
                }
            }
            if (ultimoAceptado != -1) {
                String lexema = input.substring(i, finLexema);
                switch (ultimoAceptado) {
                    case 71: System.out.println("ELSE");; break;
                    case 51: System.out.println("OR");; break;
                    case 31: System.out.println("ASSIGN");; break;
                    case 53: System.out.println("EQ");; break;
                    case 30: System.out.println("LT");; break;
                    case 52: System.out.println("LE");; break;
                    case 74: System.out.println("MAIN");; break;
                    case 33: System.out.println("GT");; break;
                    case 77: System.out.println("VOID_TYPE");; break;
                    case 32: System.out.println("RBRACE");; break;
                    case 54: System.out.println("GE");; break;
                    case 76: System.out.println("TRUE");; break;
                    case 13: System.out.println("LPAREN");; break;
                    case 34: System.out.println("NEQ");; break;
                    case 14: System.out.println("RPAREN");; break;
                    case 17: System.out.println("PLUS");; break;
                    case 39: System.out.println("AND");; break;
                    case 16: System.out.println("MULTIPLY");; break;
                    case 18: System.out.println("COMMA");; break;
                    case 1: ; break;
                    case 2: System.out.println("RBRACKET");; break;
                    case 3: ; break;
                    case 4: System.out.println("NOT");; break;
                    case 6: System.out.println("LBRACKET");; break;
                    case 9: System.out.println("MODULO");; break;
                    case 82: System.out.println("FLOAT_TYPE");; break;
                    case 81: System.out.println("FALSE");; break;
                    case 62: System.out.println("INT_TYPE");; break;
                    case 84: System.out.println("WHILE");; break;
                    case 61: System.out.println("FOR");; break;
                    case 20: System.out.println("MINUS");; break;
                    case 86: System.out.println("NUM: " + lexema);; break;
                    case 22: System.out.println("DIVIDE");; break;
                    case 88: System.out.println("BOOLEAN_TYPE");; break;
                    case 21: System.out.println("EOL");; break;
                    case 43: System.out.println("ID: " + lexema);; break;
                    case 87: System.out.println("RETURN");; break;
                    case 24: ; break;
                    case 23: ; break;
                    case 69: System.out.println("CHAR_TYPE");; break;
                    case 28: System.out.println("SEMICOLON");; break;
                    case 27: System.out.println("LBRACE");; break;
                }
                i = finLexema;
            } else {
                System.err.println("Error léxico en: " + input.charAt(i));
                i++;
            }
        }
    }


}
