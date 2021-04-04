from cfg_classes import VarType, Variable


def GetTextInsideParenthesis(string):
    return string[string.find('(')+1:string.find(')')]


def IdentExists(string, char_set):
    try:
        next(filter(lambda x: x.ident == string, char_set))
        return True
    except StopIteration:
        return False


def GetElementType(string, char_set):

    if '"' in string:
        return Variable(VarType.STRING, string)

    if '\'' in string:
        return Variable(VarType.CHAR, string)

    if string.isdigit():
        return Variable(VarType.NUMBER, string)

    if IdentExists(string, char_set):
        return Variable(VarType.IDENT, string)

    if 'CHR' in string:
        return Variable(VarType.CHAR, string)
