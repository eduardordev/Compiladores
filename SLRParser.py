class SLRParser:
    def __init__(self, slr_builder):
        self.action_table = slr_builder.action_table
        self.goto_table = slr_builder.goto_table
        self.start_symbol = slr_builder.start_symbol

    def parse(self, tokens):
        stack = [0]  # stack of states
        input_tokens = tokens + [('$', '$')]
        cursor = 0

        while True:
            state = stack[-1]
            current_token, token_value = input_tokens[cursor]

            # DEPURACIÓN: imprime los tokens válidos en el estado actual y el token recibido
            if cursor == 0:
                print("Tokens válidos en estado", state, ":", list(self.action_table[state].keys()))
                print("Token recibido:", current_token)

            action = self.action_table[state].get(current_token)
            if not action:
                raise SyntaxError(f"Error de sintaxis en token {current_token} ({token_value}) en estado {state}")

            if action[0] == 's':  # shift
                stack.append(current_token)
                stack.append(action[1])
                cursor += 1

            elif action[0] == 'r':  # reduce
                head, body = action[1], action[2]
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
