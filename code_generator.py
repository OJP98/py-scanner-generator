import os


class CodeGen(object):
    cr = '\r'
    lf = '\n'
    tab = '    '

    def __init__(self, output_dir, tokens):
        self.output_dir = output_dir
        self.tokens = tokens
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
        self.WriteLine('for symbol in chars:', 1, 2)

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
                self.WriteLine('token_type = f"KEYWORD: {keyword.ident}"', 4)

        self.WriteLine('else:', 2)
        self.WriteLine('token_type = "None"', 3, 2)

        self.file.write('''
        print(f"{repr(token_val)}\\t=>\\t{token_type}")
        token_val = symbol

        if not symbol in aut.trans_func["A"]:
            print(f"{repr(token_val)}\\t=>\\tNone")
            token_val = ""
            continue

        curr_state = aut.trans_func["A"][symbol]
''')

    def WriteGetFileFunction(self):
        self.WriteLine('file_name = "./input/test_input.txt"')
        self.WriteLine('if len(sys.argv) > 1: file_name = sys.argv[1]')

    def WriteReadFileFunction(self):
        self.NewMethod('ReadFile', 'file_dir')
        self.WriteLine('try:', 1)
        self.WriteLine('curr_file = open(file_dir, "r")', 2)
        self.WriteLine('except:', 1)
        self.WriteLine('print("ERR: File not found!")', 2)
        self.WriteLine('exit()', 2)

        self.WriteLine('lines = curr_file.read()', 1)
        self.WriteLine('chars = list()', 1)
        self.WriteLine('for line in lines:', 1)
        self.WriteLine('for char in line:', 2)
        self.WriteLine('chars.append(char)', 3)

        self.WriteLine('return chars', 1, 2)

    def GenerateScannerFile(self):
        self.CreateFile()
        self.WriteLine('import pickle')
        self.WriteLine('import sys', newlines=2)
        self.WriteLine('global aut', newlines=2)

        self.WriteReadFileFunction()

        self.WriteEvalFunction()

        self.ReadAutomataWithPickle()

        self.WriteGetFileFunction()

        self.WriteLine('chars = ReadFile(file_name)')
        self.WriteLine('EvalFile(chars)')
