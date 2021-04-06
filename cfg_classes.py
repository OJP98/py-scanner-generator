from enum import Enum
from dataclasses import dataclass


class Element:
    def __init__(self, ident, value):
        self.ident = ident
        self.value = value

    def __repr__(self):
        return f'{self.ident} = {self.value}'


class Character(Element):
    def __init__(self, ident, value):
        super().__init__(ident, value)


class Keyword(Element):
    def __init__(self, ident, value):
        super().__init__(ident, value)


class Token(Element):
    def __init__(self, ident, value, context=None):
        super().__init__(ident, value)
        self.context = context

    def __repr__(self):
        if self.context != None:
            return f'{self.ident} = {self.value} {self.context}'
        return f'{self.ident} = {self.value}'


class Char:
    def __init__(self, ident, value):
        super().__init__(ident, value)


class VarType(Enum):
    IDENT = 0
    STRING = 1
    CHAR = 2
    NUMBER = 3
    UNION = 4
    DIFFERENCE = 5
    RANGE = 6
    APPEND = 7
    LKLEENE = 8
    RKLEENE = 9
    LPAR = 10
    RPAR = 11
    LBRACKET = 12
    RBRACKET = 13
    OR = 14


@dataclass
class Variable:
    type: VarType
    value: any = None

    def __repr__(self):
        # return self.type.name
        return self.type.name + (f':{self.value}' if self.value != None else '')
