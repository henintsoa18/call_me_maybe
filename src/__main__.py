from src import (
    Functiondefinition,
    load_function_definitions,
    encode_strings, 
    get_best_from)


if __name__ == "__main__":
    funcs = load_function_definitions("data/input/functions_definition.json")
    prompt = "Greet shrek"
    encoded_string = (encode_strings([f.name for f in funcs]))
    functions = {f.name: f.description for f in funcs}
    result = get_best_from(prompt, encoded_string, functions)
    print(result)
    if result is not None:
        print(funcs[result].name)
