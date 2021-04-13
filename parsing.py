from pprint import pprint
from cfg_classes import (
    Variable, VarType, Or,
    Append, Kleene, Symbol,
    Bracket
)


class Parser:
    def __init__(self, cfg):
        self.cfg = cfg
        self.tokens = iter(self.cfg.tokens[0].value)
        self.Next()

    def Next(self):
        try:
            self.curr_token = next(self.tokens)
        except StopIteration:
            self.curr_token = None

    def NewSymbol(self):
        token = self.curr_token

        if token.type == VarType.LPAR:
            self.Next()
            res = self.Expression()

            if self.curr_token.type != VarType.RPAR:
                raise Exception('No right parenthesis for expression!')

            self.Next()
            return res

        elif token.type == VarType.CHAR or token.type == VarType.IDENT or token.type == VarType.STRING:
            self.Next()
            if token.type == VarType.IDENT:
                return Symbol(token.value, token.type, token.name)
            return Symbol(token.value, token.type)

    def NewGroup(self):
        res = self.NewSymbol()

        while self.curr_token != None and \
                (
                    self.curr_token.type == VarType.LKLEENE or
                    self.curr_token.type == VarType.LBRACKET
                ):
            if self.curr_token.type == VarType.LKLEENE:
                self.Next()
                res = Kleene(self.Expression())

                if self.curr_token.type != VarType.RKLEENE:
                    raise Exception('No right curly bracket for a token!')
                self.Next()

            elif self.curr_token.type == VarType.LBRACKET:
                self.Next()
                res = Bracket(self.Expression())

                if self.curr_token.type != VarType.RBRACKET:
                    raise Exception('No right bracket for a token!')
                self.Next()

        return res

    def Expression(self):
        res = self.NewGroup()

        while self.curr_token != None and \
                (
                    self.curr_token.type == VarType.APPEND or
                    self.curr_token.type == VarType.OR
                ):
            if self.curr_token.type == VarType.OR:
                self.Next()
                res = Or(res, self.NewGroup())

            elif self.curr_token.type == VarType.APPEND:
                self.Next()
                res = Append(res, self.NewGroup())

        return res

    def Parse(self):
        if self.curr_token == None:
            return None

        res = self.Expression()

        return res
