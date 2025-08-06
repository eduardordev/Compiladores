class SLRParser:
    def __init__(self, slr_builder):
        self.action_table = slr_builder.action_table
        self.goto_table = slr_builder.goto_table
        self.start_symbol = slr_builder.start_symbol

        print("\nTabla de acciones del estado 0:", self.action_table.get(0, {}))

    def parse(self, tokens):
        stack = [0]  # stack of states
        input_tokens = tokens + [('$', '$')]
        cursor = 0

        while True:
            state = stack[-1]
            # PROTECCIÓN: verifica que el token sea una tupla de dos elementos
            if cursor >= len(input_tokens):
                raise SyntaxError("No hay más tokens para analizar.")
            token_item = input_tokens[cursor]
            if not isinstance(token_item, tuple) or len(token_item) != 2:
                print("❌ Token inválido o mal formado:", token_item)
                raise SyntaxError(f"Token inválido: {token_item}")
            current_token, token_value = token_item

            # DEPURACIÓN: imprime los tokens válidos en el estado actual y el token recibido
            print(f"\nEstado actual: {state}")
            print("Tokens válidos en este estado:", list(self.action_table[state].keys()))
            print(f"Token recibido: {current_token} (valor: {token_value})")

            action = self.action_table[state].get(current_token)
            print(f"Acción tomada: {action}")

            if not action:
                raise SyntaxError(f"Error de sintaxis en token {current_token} ({token_value}) en estado {state}")

            if action[0] == 's':  # shift
                stack.append(current_token)
                stack.append(action[1])
                cursor += 1

            elif action[0] == 'r':  # reduce
                head, body = action[1], action[2]
                print(f"Reduciendo por la regla: {head} -> {' '.join(body)}")
                if body != ['']:  # not epsilon
                    for _ in range(len(body) * 2):
                        stack.pop()
                top_state = stack[-1]
                stack.append(head)
                goto_state = self.goto_table[top_state].get(head)
                if goto_state is None:
                    raise SyntaxError(f"No GOTO para {head} desde estado {top_state}")
                stack.append(goto_state)

            elif action[0] == 'acc':
                print("Cadena aceptada.")
                return True

            else:
                raise SyntaxError(f"Acción desconocida: {action}")
