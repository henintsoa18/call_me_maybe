from llm_sdk import Small_LLM_Model

model = Small_LLM_Model()


def encode_strings(strings: list[str]) -> None:
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
        candidat = {func[i] for func in encoded_funcs if len(func) > i}
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

def choose_func_name(prompt: str, funcs: list[str]) -> str:
    functions = {}
    funcs_encode = encode_strings(funcs)
    for f in funcs:
        functions[f["name"]] = f["description"]
    return get_best_from(prompt, funcs_encode, functions)

if __name__ == "__main__":
    function_name = {
        "fn_add_numbers": "Add two numbers",
        "fn_greet": "Say hello",
        "fn_reverse_string": "Reverse a string",
        "fn_get_square_root": "Calculate the square root of a number",
        "fn_substitute_string_with_regex": "Transform a string using regex"
    }
    prompt = "What is the sum of 1 and 2? The name of the function who can do this is"
    encoded_string = (encode_strings(function_name))
    result = get_best_from(prompt, encoded_string, function_name)
    print(result)
