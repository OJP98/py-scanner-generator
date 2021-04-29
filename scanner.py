import pickle
import sys

global aut

def ReadFile(file_dir):
    try:
        curr_file = open(file_dir, "r", encoding="latin-1")
    except:
        print("ERR: File not found!")
        exit()
    lines = curr_file.read()
    chars = list()
    for line in lines:
        for char in line:
            chars.append(char)
    return chars

def EvalFile(chars):
    curr_state = "A"
    token_val = ""
    for i, symbol in enumerate(chars):


        if symbol in aut.ignore_set and i < len(chars)-1:
            continue

        if symbol in aut.trans_func[curr_state]:
            token_val += symbol
            curr_state = aut.trans_func[curr_state][symbol]
            continue


        if curr_state in aut.accepting_states:
            gen_state = aut.accepting_dict[curr_state]
            token = next(filter(lambda x: "#-" in x.value and x._id in gen_state, aut.nodes))
            token_type = token.value.split("#-")[1]
            if token_type == "ident" and token_val in aut.keywords_value:
                keyword = next(filter(lambda x: x.value.value == token_val, aut.keywords))
                token_type = f"KEYWORD: {keyword.value.value}"
            if token_type == "hexnumber" and token_val in aut.keywords_value:
                keyword = next(filter(lambda x: x.value.value == token_val, aut.keywords))
                token_type = f"KEYWORD: {keyword.value.value}"
        else:
            token_type = "None"


        if token_val:
            print(f"{repr(token_val)}\t=>\t{token_type}")
        token_val = symbol

        if not symbol in aut.trans_func["A"]:
            print(f"{repr(token_val)}\t=>\tNone")
            token_val = ""
            curr_state = "A"
            continue

        curr_state = aut.trans_func["A"][symbol]
aut = pickle.load(open("./output/automata.p", "rb"))

file_name = "./input/test_input.txt"
if len(sys.argv) > 1: file_name = sys.argv[1]
chars = ReadFile(file_name)
EvalFile(chars)
