import os


class CodeGen(object):
    cr = '\r'
    lf = '\n'
    tab = '    '

    def __init__(self, output_dir):
        self.output_dir = output_dir
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
        self.NewMethod('EvalWord', 'word')
        self.WriteLine('curr_state = "A"', 1)
        self.WriteLine('for symbol in word:', 1)

        self.WriteLine('try:', 2)
        self.WriteLine('curr_state = aut.trans_func[curr_state][symbol]', 3)
        self.WriteLine('except:', 2)
        self.WriteLine('return "None"', 3)

        self.WriteLine('if curr_state not in aut.accepting_states:', 1)
        self.WriteLine('return "None"', 2)

        self.WriteLine('gen_state = aut.accepting_dict[curr_state]', 1)
        self.WriteLine(
            'token = next(filter(lambda x: "#-" in x.value and x._id in gen_state, aut.nodes))', 1)

        self.WriteLine('token_type = token.value.split("#-")[1]', 1)
        self.WriteLine('return f"{token_type}"', 1, 2)

    def WriteReadFileFunction(self):
        self.NewMethod('ReadFile', 'file_dir')
        self.WriteLine('try:', 1)
        self.WriteLine('curr_file = open(file_dir, "r")', 2)
        self.WriteLine('except:', 1)
        self.WriteLine('print("\tERR: File not found!")', 2)
        self.WriteLine('exit()', 2)

        self.WriteLine('lines = curr_file.readlines()', 1)
        self.WriteLine(
            'lines = [line.strip("\\n\\t\\r") for line in lines]', 1)
        self.WriteLine('lines = [line.strip() for line in lines]', 1)
        self.WriteLine('lines = " ".join(lines)', 1)
        self.WriteLine('lines = lines.split(" ")', 1)
        self.WriteLine('return [line for line in lines if line]', 1, 2)

    def GenerateScannerFile(self):
        code_gen = CodeGen('output.py')

        code_gen.CreateFile()
        code_gen.WriteLine('import pickle', newlines=2)
        code_gen.WriteLine('global aut', newlines=2)

        code_gen.WriteReadFileFunction()

        code_gen.WriteEvalFunction()

        code_gen.ReadAutomataWithPickle()

        code_gen.WriteLine('words = ReadFile("./input/test.txt")')
        code_gen.WriteLine('for word in words:')
        code_gen.WriteLine('print(f"{word}\\t=> {EvalWord(word)}")', 1, 2)


CodeGen('./output.py').GenerateScannerFile()
