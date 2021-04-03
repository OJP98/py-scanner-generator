def GetTextInsideParenthesis(string):
    return string[string.find('(')+1:string.find(')')]


def IdentExists(string, char_set):
    ident = next(filter(lambda x: x.ident == string, char_set))
    return True if ident != None else False
