from cfg_classes import (
    Variable,
    VarType,
    Character
)

from utils import (
    GetElementType
)


class SetParser:

    symbol_ignore = ['(', '[', '{', '|']
    closing_symbols = ['{', '(', '[']

    def __init__(self, set_, idents):
        self.set = iter(set_)
        self.idents = idents
        self.curr_char = None
        self.prev_char = None
        self.last_char = None
        self.symbol_ignore = ['(', '[', '{', '|']
        self.closing_symbols = ['{', '(', '[']
        self.Next()

    def Next(self):
        try:
            if self.curr_char == ' ' and self.prev_char == '|':
                self.last_char = self.prev_char
                self.prev_char = '.'
            else:
                self.last_char = self.prev_char
                self.prev_char = self.curr_char

            self.curr_char = next(self.set)
        except StopIteration:
            self.curr_char = None

    def Parse(self):
        while self.curr_char != None:

            # curr_char is a letter
            if self.curr_char.isalpha():
                if self.prev_char and \
                        self.prev_char not in self.symbol_ignore and \
                        self.last_char not in self.symbol_ignore:

                    yield Variable(VarType.APPEND)
                yield self.GenerateWord()

            # curr_char is a char
            elif self.curr_char == '\'' or self.curr_char == '"':
                if self.prev_char and \
                        self.prev_char not in self.symbol_ignore and \
                        self.last_char not in self.symbol_ignore:

                    yield Variable(VarType.APPEND)
                yield self.GenerateVar(self.curr_char)

            # curr_char is a closing symbols
            elif self.curr_char in self.closing_symbols:
                if self.prev_char and \
                        self.prev_char not in self.symbol_ignore and \
                        self.last_char not in self.symbol_ignore:

                    yield Variable(VarType.APPEND)

                if self.curr_char == '{':
                    yield Variable(VarType.LKLEENE)
                elif self.curr_char == '[':
                    yield Variable(VarType.LBRACKET)
                elif self.curr_char == '(':
                    yield Variable(VarType.LPAR)

                self.Next()

            # curr_char is kleene expr.
            elif self.curr_char == '}':
                self.Next()
                yield Variable(VarType.RKLEENE)

            elif self.curr_char == ']':
                self.Next()
                yield Variable(VarType.RBRACKET)

            elif self.curr_char == ')':
                self.Next()
                yield Variable(VarType.RPAR)

            elif self.curr_char == '|':
                self.Next()
                yield Variable(VarType.OR)

            elif self.curr_char == ' ':
                self.Next()
                continue

            else:
                raise Exception(f'Invalid character: {self.curr_char}')

    def GenerateWord(self):
        word = self.curr_char
        self.Next()

        while self.curr_char != None \
                and self.curr_char.isalpha() and self.curr_char != ' ':
            word += self.curr_char
            self.Next()

        res = GetElementType(word, self.idents)
        if not res:
            raise Exception(f'Invalid ident: {word}')

        return res

    def GenerateVar(self, symbol_type):
        var = self.curr_char
        self.Next()

        while self.curr_char and self.curr_char != ' ':
            var += self.curr_char
            self.Next()

            if self.curr_char == symbol_type:
                var += self.curr_char
                self.Next()
                break

        if var.count(symbol_type) != 2:
            raise Exception(f'Expected {symbol_type} for set')

        return Variable(VarType.CHAR, var) if symbol_type == '\'' \
            else Variable(VarType.STRING, var)
