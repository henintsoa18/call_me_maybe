from src.parse import load_function_definitions, load_function_calling
from src.call_me_maybe import model, choose_func_name, build_parameters

funcs = load_function_definitions("data/input/functions_definition.json")
tests = load_function_calling("data/input/function_calling_tests.json")

for test in tests:
    # Étape 1 : le LLM choisit la fonction (déjà validé)
    chosen = choose_func_name(test.prompt, funcs)
    if chosen is None:
        print(f"{test.prompt!r} -> aucune fonction trouvée")
        continue

    # Étape 2 : contexte de départ pour les paramètres
    text = (
        "Extract the parameters of the function call.\n"
        f"Function: {chosen.name} - {chosen.description}\n"
        f"Prompt: {test.prompt}\n"
        "Parameters: "
    )
    context_ids = model.encode(text).tolist()[0]

    # Étape 3 : génération des paramètres
    params = build_parameters(model, context_ids, chosen)
    print(f"{test.prompt!r} -> {chosen.name} {params}")
