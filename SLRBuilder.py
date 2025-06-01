from collections import defaultdict
from YaparParser import YaparParser

print("[SLRBuilder] Archivo SLRBuilder.py cargado")

class LR0Item:
    def __init__(self, head, body, dot_pos=0):
        self.head = head
        self.body = body
        self.dot_pos = dot_pos

    def __eq__(self, other):
        return (self.head == other.head and
                self.body == other.body and
                self.dot_pos == other.dot_pos)

    def __hash__(self):
        return hash((self.head, tuple(self.body), self.dot_pos))

    def __str__(self):
        before_dot = ' '.join(self.body[:self.dot_pos])
        after_dot = ' '.join(self.body[self.dot_pos:])
        return f"{self.head} -> {before_dot} • {after_dot}"

class SLRBuilder:
    def __init__(self, yapar_parser):
        print("[SLRBuilder] __init__ ejecutado")
        self.grammar = yapar_parser.productions
        self.start_symbol = yapar_parser.start_symbol
        print("[SLRBuilder] start_symbol:", self.start_symbol)  # DEPURACIÓN
        self.terminals = yapar_parser.tokens
        self.non_terminals = set(self.grammar.keys())
        self.augmented_start = self.start_symbol + "'"
        self.states = []
        self.transitions = {}
        self.action_table = defaultdict(dict)
        self.goto_table = defaultdict(dict)
        self.follow_sets = defaultdict(set)
        self.first_sets = defaultdict(set)
        self._augment_grammar()
        self._compute_first_sets()
        self._compute_follow_sets()
        self._build_automaton()
        self._build_parsing_table()

    def _augment_grammar(self):
        self.grammar[self.augmented_start] = [[self.start_symbol]]
        self.start_symbol = self.augmented_start
        self.non_terminals.add(self.augmented_start)
        print("[SLRBuilder] Gramática aumentada:")
        for head, prods in self.grammar.items():
            for prod in prods:
                print(f"  {head} -> {' '.join(prod)}")

    def closure(self, items):
        closure_set = set(items)
        added = True
        while added:
            added = False
            new_items = set()
            for item in closure_set:
                if item.dot_pos < len(item.body):
                    symbol = item.body[item.dot_pos]
                    if symbol in self.grammar:
                        for prod in self.grammar[symbol]:
                            new_item = LR0Item(symbol, prod, 0)
                            if new_item not in closure_set and new_item not in new_items:
                                new_items.add(new_item)
            if new_items:
                closure_set.update(new_items)
                added = True
        return closure_set

    def goto(self, items, symbol):
        moved_items = set()
        for item in items:
            if item.dot_pos < len(item.body) and item.body[item.dot_pos] == symbol:
                moved_items.add(LR0Item(item.head, item.body, item.dot_pos + 1))
        return self.closure(moved_items)

    def _build_automaton(self):
        initial_item = LR0Item(self.start_symbol, self.grammar[self.start_symbol][0], 0)
        initial_state = self.closure({initial_item})
        self.states = [initial_state]
        state_map = {self._state_key(initial_state): 0}
        pending = [initial_state]

        while pending:
            current = pending.pop(0)
            current_index = state_map[self._state_key(current)]
            symbols = self._get_next_symbols(current)
            for symbol in symbols:
                new_state = self.goto(current, symbol)
                key = self._state_key(new_state)
                if key not in state_map:
                    state_map[key] = len(self.states)
                    self.states.append(new_state)
                    pending.append(new_state)
                self.transitions[(current_index, symbol)] = state_map[key]
        print("[SLRBuilder] Estado 0:")
        for item in self.states[0]:
            print(f"  {item}")

    def _state_key(self, state):
        return frozenset(state)

    def _get_next_symbols(self, state):
        symbols = set()
        for item in state:
            if item.dot_pos < len(item.body):
                symbols.add(item.body[item.dot_pos])
        return symbols

    def _compute_first_sets(self):
        
        for terminal in self.terminals:
            self.first_sets[terminal] = {terminal}
        
        for nt in self.non_terminals:
            self.first_sets[nt] = set()

        max_iterations = len(self.non_terminals) ** 2

        for _ in range(max_iterations):
            updated = False
            for head, prods in self.grammar.items():
                for prod in prods:
                    prev_size = len(self.first_sets[head])
                    if not prod:
                        
                        self.first_sets[head].add('')
                    else:
                        for symbol in prod:
                            self.first_sets[head].update(self.first_sets[symbol] - {''})
                            if '' not in self.first_sets[symbol]:
                                break
                        else:
                            
                            self.first_sets[head].add('')
                    if len(self.first_sets[head]) > prev_size:
                        updated = True
            if not updated:
                break

    def _compute_follow_sets(self):
  
        for nt in self.non_terminals:
            self.follow_sets[nt] = set()
        self.follow_sets[self.start_symbol] = {'$'}

        max_iterations = len(self.non_terminals) ** 2

        for _ in range(max_iterations):
            updated = False
            for head, prods in self.grammar.items():
                for prod in prods:
                    follow_temp = self.follow_sets[head].copy()
                    for symbol in reversed(prod):
                        if symbol in self.non_terminals:
                            prev_size = len(self.follow_sets[symbol])
                            self.follow_sets[symbol].update(follow_temp)

                            if '' in self.first_sets[symbol]:
                                follow_temp.update(self.first_sets[symbol] - {''})
                            else:
                                follow_temp = self.first_sets[symbol]

                            if len(self.follow_sets[symbol]) > prev_size:
                                updated = True
                        else:
                            follow_temp = self.first_sets.get(symbol, {symbol})
            if not updated:
                break

    def _build_parsing_table(self):
        print("[SLRBuilder] Ejecutando _build_parsing_table")
        for idx, state in enumerate(self.states):
            for item in state:
                if item.dot_pos < len(item.body):
                    symbol = item.body[item.dot_pos]
                    # DEPURACIÓN: Mostrar símbolo y terminales
                    print(f"[SLRBuilder] Estado {idx}, item: {item}, símbolo en el punto: '{symbol}', terminales: {self.terminals}")
                    if symbol in self.terminals:
                        target = self.transitions.get((idx, symbol))
                        if target is not None:
                            print(f"[SLRBuilder]  -> shift agregado: ACTION[{idx}][{symbol}] = ('s', {target})")
                            self.action_table[idx][symbol] = ('s', target)
                else:
                    if item.head == self.start_symbol:
                        self.action_table[idx]['$'] = ('acc',)
                    else:
                        for terminal in self.follow_sets[item.head]:
                            self.action_table[idx][terminal] = ('r', item.head, item.body)
            for nt in self.non_terminals:
                target = self.transitions.get((idx, nt))
                if target is not None:
                    self.goto_table[idx][nt] = target

    def print_states(self):
        for i, state in enumerate(self.states):
            print(f"Estado {i}:")
            for item in sorted(state, key=lambda x: (x.head, x.dot_pos)):
                print(f"  {item}")
            print()

    def print_transitions(self):
        print("Transiciones:")
        for (state_index, symbol), target_index in self.transitions.items():
            print(f"  δ({state_index}, '{symbol}') = {target_index}")

    def print_tables(self):
        print("\nFIRST SETS:")
        for nt, first in self.first_sets.items():
            print(f"  FIRST({nt}) = {first}")

        print("\nFOLLOW SETS:")
        for nt, follow in self.follow_sets.items():
            print(f"  FOLLOW({nt}) = {follow}")

        print("\nACTION TABLE:")
        for state, actions in self.action_table.items():
            for symbol, act in actions.items():
                print(f"  ACTION[{state}][{symbol}] = {act}")

        print("\nGOTO TABLE:")
        for state, gotos in self.goto_table.items():
            for nt, target in gotos.items():
                print(f"  GOTO[{state}][{nt}] = {target}")

# Ejemplo de uso
if __name__ == '__main__':
    parser = YaparParser('media.yapar')
    slr = SLRBuilder(parser)
    slr.print_states()
    slr.print_transitions()
    slr.print_tables()
