from enum import Enum
from dataclasses import dataclass


# __________IMPORTANT DATA CLASSES__________
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


# __________ALL THE DIFFERENT SYMBOLS__________
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
    name: str = None

    def __repr__(self):
        if self.name:
            return f'{self.type.name}: {self.name}'
        return self.type.name + (f':{self.value}' if self.value != None else '')
        # return self.type.name


# __________NODE TYPES__________
class Kleene:
    def __init__(self, a):
        self.a = a

    def __repr__(self):
        return f'{ {self.a} }'


class Bracket:
    def __init__(self, a):
        self.a = a

    def __repr__(self):
        return f'[ {self.a} ]'


class Or:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        # return f'({self.a} | {self.b})'
        return f'{self.a} | {self.b}'


class Append:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        # return f'({self.a} . {self.b})'
        return f'{self.a} . {self.b}'


class Symbol:
    def __init__(self, value, type_=None, ident_name=None):
        self.value = value
        self.type = type_
        self.ident_name = ident_name

    def __repr__(self):
        if self.ident_name:
            return f'{self.ident_name}'
        return f'{self.value}'
