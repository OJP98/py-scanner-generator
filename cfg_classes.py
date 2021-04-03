class Character:
    def __init__(self, ident, value):
        self.ident = ident
        self.value = value

    def __repr__(self):
        return f'{self.ident} = {self.value}'


class Keyword:
    def __init__(self, ident, value):
        self.ident = ident
        self.value = value

    def __repr__(self):
        return f'{self.ident} = {self.value}'


class Token:
    def __init__(self, ident, value, context=None):
        self.ident = ident
        self.value = value
        self.context = context

    def __repr__(self):
        if self.context != None:
            return f'{self.ident} = {self.value} {self.context}'
        return f'{self.ident} = {self.value}'


class Char:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return ''
