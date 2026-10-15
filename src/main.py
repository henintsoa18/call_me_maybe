from parse import (
    Functiondefinition,
    load_function_definitions,
    load_function_calling)
from call_me_maybe import (
    encode_strings,
    get_best_from,
    build_parameters,
    choose_func_name)
import json
from llm_sdk import Small_LLM_Model

if __name__ == "__main__":
#    funcs = load_function_definitions("data/input/functions_definition.json")
#    prompt = "Greet shrek"
#    encoded_string = (encode_strings([f.name for f in funcs]))
#    functions = {f.name: f.description for f in funcs}
#    result = get_best_from(prompt, encoded_string, functions)
#    print(result)
#    if result is not None:
#        print(funcs[result].name)

    donnees = {
        "nom": "Alice",
        "age": 30,
        "competences": ["Python", "SQL"]
    }
    json_str = json.dumps(donnees, indent=4, ensure_ascii=False)
    print(json_str)

    funcs = load_function_definitions("data/input/functions_definition.json")
    tests = load_function_calling("data/input/function_calling_tests.json")

    model = Small_LLM_Model()
    for test in tests:
        chosen = choose_func_name(test.prompt, funcs)
        if chosen is None:
            print(f"{test.prompt!r} -> aucune fonction trouvée")
            continue

        text = (
            "Extract the parameters of the function call.\n"
            f"Function: {chosen.name} - {chosen.description}\n"
            f"Prompt: {test.prompt}\n"
            "Parameters: "
        )
        context_ids = model.encode(text).tolist()[0]

        params = build_parameters(model, context_ids, chosen)
        print(f"{test.prompt!r} -> {chosen.name} {params}")
