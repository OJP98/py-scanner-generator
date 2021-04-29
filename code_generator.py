import os


class CodeGen(object):
    cr = '\r'
    lf = '\n'
    tab = '    '

    def __init__(self, output_dir, tokens, ddfa):
        self.output_dir = output_dir
        self.tokens = tokens
        self.ddfa = ddfa
        self.file = None

    def CreateFile(self):
        try:
            self.file = open(self.output_dir, 'w+')
        except Exception as e:
            raise Exception(e)

    def Ident(self, n=1):
        self.file.write(CodeGen.tab * n)

    def WriteLine(self, line, tabs=0, newlines=1):
        line = CodeGen.tab*tabs + str(line) + CodeGen.lf*newlines
        self.file.write(line)

    def NewMethod(self, method_name, param=''):
        self.file.write(f'def {method_name}({param}):\n')

    def WriteCode(self, code):
        code = str(code)
        self.file.write(code)

    def ReadAutomataWithPickle(self):
        self.WriteLine(
            'aut = pickle.load(open("./output/automata.p", "rb"))', newlines=2)

    def WriteEvalFunction(self):
        self.NewMethod('EvalFile', 'chars')

        self.WriteLine('curr_state = "A"', 1)
        self.WriteLine('token_val = ""', 1)
        self.WriteLine('for i, symbol in enumerate(chars):', 1, 2)
        self.WriteLine('''
        if symbol in aut.ignore_set and i < len(chars)-1:
            continue
''')

        self.WriteLine('if symbol in aut.trans_func[curr_state]:', 2)
        self.WriteLine('token_val += symbol', 3)
        self.WriteLine('curr_state = aut.trans_func[curr_state][symbol]', 3)
        self.WriteLine('continue', 3, 2)

        self.file.write('''
        if curr_state in aut.accepting_states:
            gen_state = aut.accepting_dict[curr_state]
            token = next(filter(lambda x: "#-" in x.value and x._id in gen_state, aut.nodes))
            token_type = token.value.split("#-")[1]
''')

        for token in self.tokens:
            if token.context:
                self.WriteLine(
                    f'if token_type == "{token.ident}" and token_val in aut.keywords_value:', 3)
                self.WriteLine(
                    f'keyword = next(filter(lambda x: x.value.value == token_val, aut.keywords))', 4)
                self.WriteLine(
                    'token_type = f"KEYWORD: {keyword.value.value}"', 4)

        self.WriteLine('else:', 2)
        self.WriteLine('token_type = "None"', 3, 2)

        self.file.write('''
        if token_val:
            print(f"{repr(token_val)}\\t=>\\t{token_type}")
        token_val = symbol

        if not symbol in aut.trans_func["A"]:
            print(f"{repr(token_val)}\\t=>\\tNone")
            token_val = ""
            curr_state = "A"
            continue

        curr_state = aut.trans_func["A"][symbol]
''')

    def WriteGetFileFunction(self):
        self.WriteLine('file_name = "./input/test_input.txt"')
        self.WriteLine('if len(sys.argv) > 1: file_name = sys.argv[1]')

    def WriteReadFileFunction(self):
        self.NewMethod('ReadFile', 'file_dir')
        self.WriteLine('try:', 1)
        self.WriteLine(
            'curr_file = open(file_dir, "r", encoding="latin-1")', 2)
        self.WriteLine('except:', 1)
        self.WriteLine('print("ERR: File not found!")', 2)
        self.WriteLine('exit()', 2)

        self.WriteLine('lines = curr_file.read()', 1)
        self.WriteLine('chars = list()', 1)
        self.WriteLine('for line in lines:', 1)
        self.WriteLine('for char in line:', 2)
        self.WriteLine('chars.append(char)', 3)

        self.WriteLine('return chars', 1, 2)

    def WriteAutomataClass(self):
        self.WriteLine(f'''
class Automata:
    def __init__(self):
        self.trans_func = dict()
        self.accepting_states = set()
        self.accepting_dict = dict()
        self.nodes = list()
        self.keywords = dict()

    def AddTransition(self, state, value):
        self.trans_func[state] = value

    def AddAcceptingState(self, new_state, value):
        self.accepting_states.update(new_state)
        self.accepting_dict[new_state] = value

    def AddNode(self, _id, value):
        self.nodes.append(Node(_id, value))

    def AddKeyword(self, keyword, value):
        self.keywords[keyword] = value


class Node:
    def __init__(self, _id, value):
        self._id = _id
        self.value = value

aut = Automata()''')

        for state, value in self.ddfa.trans_func.items():
            self.WriteLine(f'aut.AddTransition("{state}", {value})')

        self.WriteLine('\n# Add the accepting states')
        for state, value in self.ddfa.accepting_dict.items():
            self.WriteLine(f'aut.AddAcceptingState("{state}", {value})')

        self.WriteLine('\n# Add the nodes of the accepting states')
        for node in self.ddfa.nodes:
            if '#-' in node.value:
                self.WriteLine(f'aut.AddNode({node._id}, "{node.value}")')

        self.WriteLine('\n# Finally, add the keywords')
        for keyword in self.ddfa.keywords:
            self.WriteLine(
                f'aut.AddKeyword("{keyword.ident}", "{keyword.value.value}")')
        self.WriteLine('\n')

    def GenerateScannerFile(self):
        self.CreateFile()
        self.WriteLine('import pickle')
        self.WriteLine('import sys', newlines=2)
        self.WriteLine('global aut', newlines=2)

        # self.WriteAutomataClass()

        self.WriteReadFileFunction()

        self.WriteEvalFunction()

        self.ReadAutomataWithPickle()

        self.WriteGetFileFunction()

        self.WriteLine('chars = ReadFile(file_name)')
        self.WriteLine('EvalFile(chars)')
