from utils import GetTextInsideParenthesis, IdentExists
from pprint import pprint
from cfg_classes import *
from math import inf

CONTEXT_WORDS = ['EXCEPT', 'ANY', 'IGNORE', 'IGNORECASE']
SCANNER_WORDS = ['COMPILER', 'CHARACTERS',
                 'KEYWORDS', 'TOKENS', 'END', 'PRODUCTIONS']


class CFG():
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

        self.compiler_name = None
        self.characters = list()
        self.keywords = list()
        self.tokens = list()

        self.file_lines = self.ReadFile()
        self.curr_line = None
        self.Next()

        self.ReadLines()

    def Next(self):
        try:
            self.curr_line = next(self.file_lines)
        except StopIteration:
            self.curr_line = None

    def ReadFile(self):
        try:
            self.file = open(self.filepath, 'r')
        except:
            raise Exception('File not found!')
        finally:
            lines = self.file.readlines()
            temp = list()
            for line in lines:
                if line != '\n':
                    line = line.strip('\r\t\n')
                    line = line.strip()
                    line = line.split(' ')
                    line[:] = [i for i in line if i != '' or i]
                    temp.append(line)

        return iter(temp)

    def ReadLines(self):
        while self.curr_line != None:
            # Check if we got any important word in the lines
            if any(word in SCANNER_WORDS for word in self.curr_line):

                if 'COMPILER' in self.curr_line:
                    self.compiler_name = self.curr_line[self.curr_line.index(
                        'COMPILER')+1]
                    self.Next()

                elif 'CHARACTERS' in self.curr_line:
                    self.Next()
                    self.ReadSection('CHARACTERS')

                elif 'KEYWORDS' in self.curr_line:
                    self.Next()
                    self.ReadSection('KEYWORDS')

                elif 'TOKENS' in self.curr_line:
                    self.Next()
                    self.ReadSection('TOKENS')

                elif 'PRODUCTIONS' in self.curr_line:
                    self.Next()

                elif 'END' in self.curr_line:
                    print('END')
                    self.Next()

            elif '(.' in self.curr_line:
                self.ReadComment()
                self.Next()

            else:
                self.Next()

    def ReadSection(self, section):
        joined_set = ''
        prev_set = ''
        while not any(word in SCANNER_WORDS for word in self.curr_line):
            curr_set = ' '.join(self.curr_line)
            print(curr_set)

            # Is there a comment?
            if '(.' in curr_set:
                self.ReadComment()

            # Does the set contains both = and .
            if '=' in curr_set and '.' == curr_set[-1]:
                curr_set = curr_set[:-1]
                self.GetKeyValue(curr_set, section)
                self.Next()

            # If it doesn't contains a ., it's probably part of the previous set
            elif not '.' == curr_set[-1]:
                joined_set += curr_set
                self.Next()

            # If there's a ., it's probably the end of a previously joined set
            elif '.' == curr_set[-1]:
                joined_set += curr_set
                joined_set = joined_set[:-1]
                self.GetKeyValue(joined_set, section)
                self.Next()

    def ReadComment(self):
        while not '.)' in self.curr_line:
            self.Next()

    def GetKeyValue(self, line, attr):
        if attr == 'CHARACTERS':
            self.SetDecl(line)
        elif attr == 'KEYWORDS':
            self.KeywordDecl(line)
        elif attr == 'TOKENS':
            print('pending')

    def KeywordDecl(self, line):
        ident, value = line.split('=')
        ident = ident.strip()
        value = value.strip().replace('.', '')

        # Create ident object
        keyword = Keyword(ident, value)

        # Check if ident exists, else append it to list
        if IdentExists(ident, self.keywords):
            raise Exception('Keyword declared twice!')
        self.keywords.append(keyword)

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

        # Check if it has a . or a CHR or even "
        char_vals = ['.', 'CHR', '"', '\'']
        if not any(char in char_vals for char in string):
            # Check if ident exists
            if not IdentExists(string, item_set):
                raise Exception(
                    f'In CHARACTERS, char is not defined correctly: indent "{string}" not defined')
            return string

        elif '"' in string:
            return string

        temp = list()
        string = string.split('..')

        for char in string:
            # Check if there's a dot in some value
            if '.' in char or not char:
                raise Exception(
                    'In CHARACTERS, a set is not defined correctly')

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

    def __repr__(self):
        return f'''
    Compiler: {self.compiler_name}
        Characters: {self.characters}
        Keywords: {self.keywords}
        Tokens: {self.tokens}
    '''


cfg = CFG('input/grammar.cfg')
print(cfg)
