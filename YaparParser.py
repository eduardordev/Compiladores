from collections import defaultdict

class YaparParser:
    def __init__(self, filepath):
        self.tokens = set()
        self.ignore_tokens = set()
        self.productions = defaultdict(list)
        self.start_symbol = None
        self._parse_file(filepath)

    def _parse_file(self, filepath):
        with open(filepath, encoding='utf-8') as f:
            lines = f.readlines()

        token_section = True
        in_productions = False
        current_head = None

        for line in lines:
            line = self._strip_comments_and_whitespace(line)
            if not line:
                continue

            if line == '%%':
                token_section = False
                in_productions = True
                continue

            if token_section:
                if self._starts_with(line, '%token'):
                    tokens = self._split_words(line[6:])
                    self.tokens.update(tokens)
                elif self._starts_with(line, 'IGNORE'):
                    ignored = self._split_words(line[6:])
                    self.ignore_tokens.update(ignored)

            elif in_productions:
                if ':' in line:
                    parts = self._split_once(line, ':')
                    current_head = parts[0].strip()
                    if self.start_symbol is None:
                        self.start_symbol = current_head
                    body = parts[1].strip()
                    if body:
                        self.productions[current_head].append(self._split_words(body))
                elif self._starts_with(line, '|') and current_head:
                    alt = line[1:].strip()
                    if alt:
                        self.productions[current_head].append(self._split_words(alt))
                elif line == ';':
                    current_head = None

    def _strip_comments_and_whitespace(self, line):
        line = line.strip()
        if line.startswith('/*') or line.startswith('//'):
            return ''
        if '/*' in line:
            line = self._split_once(line, '/*')[0].strip()
        return line

    def _split_words(self, text):
        words = []
        current = ''
        for char in text:
            if char.isspace():
                if current:
                    words.append(current)
                    current = ''
            else:
                current += char
        if current:
            words.append(current)
        return words

    def _split_once(self, text, sep):
        index = text.find(sep)
        if index == -1:
            return [text]
        return [text[:index], text[index + len(sep):]]

    def _starts_with(self, text, prefix):
        return text[:len(prefix)] == prefix

    def print_summary(self):
        print("Tokens:", self.tokens)
        print("Ignorados:", self.ignore_tokens)
        print("Símbolo inicial:", self.start_symbol)
        print("Producciones:")
        for head, rules in self.productions.items():
            for alt in rules:
                print(f"  {head} -> {' '.join(alt)}")
