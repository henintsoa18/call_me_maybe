from llm_sdk import Small_LLM_Model
from typing import Any
from enum import Enum, auto
#from pydantic import Basemodel
from .parse import (
        load_function_calling,
        load_function_definitions,
        Functiondefinition
        )


model = Small_LLM_Model()


def encode_strings(strings: list[str]) -> None:
    """Encode strings"""
    encoded = []
    for string in strings:
        encoded.append(model.encode(string).tolist()[0])
    return (encoded)


def get_best_from(prompt: str, encoded_funcs: list[list[int]], functions: dict[str, str]) -> str:
    result = []
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
        if not candidat:
            return
        i += 1
    return result


def choose_func_name(prompt: str, funcs: list[str]) -> str:
    functions = {}
    funcs_encode = encode_strings(funcs)
    for f in funcs:
        functions[f["name"]] = f["description"]
    return get_best_from(prompt, funcs_encode, functions)


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


0
if __name__ == "__main__":
    function_name = {
        "fn_add_numbers": "Add two numbers",
        "fn_greet": "Say hello",
        "fn_reverse_string": "Reverse a string",
        "fn_get_square_root": "Calculate the square root of a number",
        "fn_substitute_string_with_regex": "Transform a string using regex"
    }

    prompt = "Greet shrek"
    encoded_string = (encode_strings(function_name))
    result = get_best_from(prompt, encoded_string, function_name)
    print(result)
    print(model.decode(result))
    #print(find_function_by_name("fn_greet", load_function_definitions("data/input/functions_definition.json")))
