from utils import GetTextInsideParenthesis, IdentExists
from pprint import pprint
from cfg_classes import *
from math import inf

CONTEXT_WORDS = ['EXCEPT', 'ANY', 'IGNORE', 'IGNORECASE']


class CFG():
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None
        self.file_lines = list()
        self.compiler_name = None
        self.characters = list()
        self.keywords = list()
        self.tokens = list()

    def ReadFile(self):
        try:
            self.file = open(self.filepath, 'r')
        except:
            raise Exception('File not found!')
        finally:
            lines = self.file.readlines()
            for line in lines:
                if line != '\n':
                    line = line.strip('\r\t\n')
                    line = line.split(' ')
                    line[:] = [i for i in line if i != '' or i]
                    self.file_lines.append(line)

        return self.file_lines

    def ReadLines(self):
        parsing_attr = None

        for line in self.file_lines:

            if 'COMPILER' in line:
                self.compiler_name = line[line.index('COMPILER')+1]

            elif 'CHARACTERS' in line and self.compiler_name != None:
                parsing_attr = 'CHARACTERS'
                continue

            elif 'KEYWORDS' in line and self.compiler_name != None:
                if not '=' in line:
                    parsing_attr = 'KEYWORDS'
                    continue

            elif 'TOKENS' in line and self.compiler_name != None:
                parsing_attr = 'TOKENS'
                continue

            elif 'PRODUCTIONS' in line and self.compiler_name != None:
                parsing_attr = None

            elif 'END' in line:
                break

            if parsing_attr != None:
                self.GetKeyValue(' '.join(line), parsing_attr)

    def GetKeyValue(self, line, attr):
        if attr == 'CHARACTERS':
            self.SetDecl(line)
        elif attr == 'KEYWORDS':
            self.KeywordDecl(line)
        elif attr == 'TOKENS':
            print('pending')

    def KeywordDecl(self, line):
        key, value = line.split('=')
        key = key.strip()
        value = value.strip().replace('.', '')

        self.keywords.append({key: value})

    def SetDecl(self, line):

        def BasicSet(string):
            temp = list()

            while string:
                plus_index = string.find('+')
                minus_index = string.find('-')

                plus_index = plus_index if plus_index != -1 else inf
                minus_index = minus_index if minus_index != -1 else inf

                if plus_index < minus_index:
                    char = self.Char(string[:plus_index], self.characters)
                    temp.append(char)
                    temp.append('+')
                    string = string[plus_index+1:]

                elif minus_index < plus_index:
                    char = self.Char(string[:minus_index], self.characters)
                    temp.append(char)
                    temp.append('-')
                    string = string[minus_index+1:]

                else:
                    char = self.Char(string, self.characters)
                    temp.append(char)
                    break

            return temp

        def Set(value):
            value = value.replace(' ', '')
            bset = [value]

            if any(i in '+-' for i in value):
                bset = BasicSet(value)

            return bset

        key, value = line.split('=')

        key = key.strip()
        value = Set(value.strip())
        self.characters.append(Character(key, value))

    def Char(self, string, item_set):
        # Check if it has a . or a CHR
        if '.' not in string and 'CHR' not in string:
            if '"' not in string:
                # Doesn't have double quotes, check if ident exists
                if not IdentExists(string, item_set):
                    raise Exception(
                        f'In CHARACTERS, char is not defined correctly: {string} is not defined')
            return string

        temp = list()
        string = string.split('..')

        for char in string:
            # Check if there's a dot in some value
            if '.' in char or not char:
                raise Exception(
                    'In CHARACTERS, char is not defined correctly')

            # Is it a CHR-defined value?
            if 'CHR' in char:

                # Check for missing or extra parenthesis
                par_count = char.count('(') + char.count(')')
                if not par_count == 2:
                    raise Exception(
                        'In CHARACTERS, char is not defined correctly: missplaced parenthesis')

                # Finally, we check for the text inside the parenthesis
                value = GetTextInsideParenthesis(char)
                if not value.isdigit():
                    raise Exception(
                        'In CHARACTERS, char is not defined correctly: non-digit CHR value')

            temp.append(char)

            if len(string) > 1 and char != string[-1]:
                temp.append('..')

        return temp


cfg = CFG('input/grammar.cfg')
cfg.ReadFile()
cfg.ReadLines()
pprint(cfg.characters)
