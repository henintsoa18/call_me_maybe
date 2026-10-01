from llm_sdk import Small_LLM_Model
from typing import Any
from enum import Enum, auto
#from pydantic import Basemodel
from src import Functiondefinition, load_function_definitions


model = Small_LLM_Model()


def encode_strings(strings: list[str]) -> list[list[int]]:
    """Encode strings"""
    encoded = []
    for string in strings:
        encoded.append(model.encode(string).tolist()[0])
    return (encoded)


def get_best_from(prompt: str, encoded_funcs: list[list[int]], functions: dict[str, str]) -> int | None:
    result: list[int] = []
    base_prompt = f"""Get the best function name from this prompt:

Prompt: {prompt}

Functions: {functions}

Answer: """
    encoded_string = model.encode(base_prompt).tolist()[0]
    i = 0
    while True:
        candidat = {func[i] for func in encoded_funcs if len(func) > i and func[:i] == result}
        if not candidat:
            return None

        logits = model.get_logits_from_input_ids(encoded_string + result)
        max_value = max((logits[cand] for cand in candidat))
        max_ids = logits.index(max_value)
        result.append(max_ids)

        if result in encoded_funcs:
            break
        i += 1
    return encoded_funcs.index(result)


def choose_func_name(prompt: str, funcs: list[Functiondefinition]) -> Functiondefinition | None:
    functions = {}
    funcs_encode = encode_strings(f.name for f in funcs)
    for f in funcs:
        functions[f.name] = f.description
    index = get_best_from(prompt, funcs_encode, functions)
    if index is None:
        return None
    return funcs[index]


def find_function_by_name(name: str, functions: list[Functiondefinition]) -> Functiondefinition | None:
    for fun in functions:
        if fun.name == name:
            return fun
    return None


#class ParamState(Enum):
#    START = auto()
#    KEY = auto()
#    # COLON = auto()
#    VALUE = auto()
#    COMMA = auto()
#    END = auto()
#
#
#def get_best_sequence(encoded_prompt: list[int], candidates_encoded: list[list[int]]) -> list[int] | None:
#    res = []
#    i = 0
#    while True:
#        candidat = {cand[i] for cand in candidates_encoded if len(cand) > i and cand[:i] == result}
#        if not candidat:
#            return None
#        logits = model.get_logits_from_input_ids(encoded_prompt + res)
#        print(logits)
#        max_value = max((logits[cand] for cand in candidat))
#        max_ids = logits.index(max_value)
#        res.append(max_ids)
#        if res in candidates_encoded:
#            break
#        if not candidat:
#            return
#        i += 1
#    return res
#
#
#class ParamExtract:
#    def __init__(self, param_spec: dict, encoded_prompt: list[int]):
#        self.state = ParamState.START
#        self.param_spec = param_spec
#        self.fields_remaining = set(param_spec.keys())
#        self.current_key = ""
#        self.extracted: dict = {}
#        self.ctx = encoded_prompt
#
#    def valid_numbers(vocab: dict[str, int], has_digit: bool) -> set[int]:
#        ...



if __name__ == "__main__":
    funcs = load_function_definitions("data/input/functions_definition.json")
    prompt = "Greet shrek"
    encoded_string = (encode_strings([f.name for f in funcs]))
    functions = {f.name: f.description for f in funcs}
    result = get_best_from(prompt, encoded_string, functions)
    print(result)
    if result is not None:
        print(funcs[result].name)
