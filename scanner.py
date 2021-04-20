import pickle

global aut

def ReadFile(file_dir):
    try:
        curr_file = open(file_dir, "r")
    except:
        print("	ERR: File not found!")
        exit()
    lines = curr_file.readlines()
    lines = [line.strip("\n\t\r") for line in lines]
    lines = [line.strip() for line in lines]
    lines = " ".join(lines)
    lines = lines.split(" ")
    return [line for line in lines if line]

def EvalWord(word):
    curr_state = "A"
    for symbol in word:
        try:
            curr_state = aut.trans_func[curr_state][symbol]
        except:
            return "None"
    if curr_state not in aut.accepting_states:
        return "None"
    gen_state = aut.accepting_dict[curr_state]
    token = next(filter(lambda x: "#-" in x.value and x._id in gen_state, aut.nodes))
    token_type = token.value.split("#-")[1]
    if token_type == "ident" and word in aut.keywords_value:
        keyword = next(filter(lambda x: x.value.value == word, aut.keywords))
        return f"KEYWORD: {keyword.ident}"
    return f"{token_type}"

aut = pickle.load(open("./output/automata.p", "rb"))

words = ReadFile("./input/test_input.txt")
for word in words:
    print(f"{word}\t=> {EvalWord(word)}")

