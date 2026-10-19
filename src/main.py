from parse import (
    Functiondefinition,
    FunctionCallResult,
    load_function_definitions,
    load_function_calling)
from call_me_maybe import (
    encode_strings,
    get_best_from,
    build_parameters,
    build_context,
    choose_func_name)
import json
import argparse
import os
from llm_sdk import Small_LLM_Model


#    funcs = load_function_definitions("data/input/functions_definition.json")
#    prompt = "Greet shrek"
#    encoded_string = (encode_strings([f.name for f in funcs]))
#    functions = {f.name: f.description for f in funcs}
#    result = get_best_from(prompt, encoded_string, functions)
#    print(result)
#    if result is not None:
#        print(funcs[result].name)

#    donnees = {
#        "nom": "Alice",
#        "age": 30,
#        "competences": ["Python", "SQL"]
#    }
#    json_str = json.dumps(donnees, indent=4, ensure_ascii=False)
#    print(json_str)
#
#    funcs = load_function_definitions("data/input/functions_definition.json")
#    tests = load_function_calling("data/input/function_calling_tests.json")
#
#    model = Small_LLM_Model()
#    for test in tests:
#        chosen = choose_func_name(test.prompt, funcs)
#        if chosen is None:
#            print(f"{test.prompt!r} -> aucune fonction trouvée")
#            continue
#
#        text = (
#            "Extract the parameters of the function call.\n"
#            f"Function: {chosen.name} - {chosen.description}\n"
#            f"Prompt: {test.prompt}\n"
#            "Parameters: "
#        )
#        context_ids = model.encode(text).tolist()[0]
#
#        params = build_parameters(model, context_ids, chosen)
#        print(f"{test.prompt!r} -> {chosen.name} {params}")


def take_flags() -> argparse.Namespace:
    """Read the command line options, with the default paths.

    Returns:
        A Namespace with the attributes functions_definition,
        input and output.
    """
    parser = argparse.ArgumentParser(
        description="Turn the natural language prompts into function calls.")

    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
        help="The json path for file containing the function definitions"
    )
    parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json",
        help="The json path for file containing the user prompts"
    )
    parser.add_argument(
        "output",
        default="data/output/function_calling_results.json",
        help="The json path for file containing the results"
    )
    return parser.parse_args()


def process_prompt(
        prompt: str,
        funcs: list[Functiondefinition]) -> FunctionCallResult:
    """Run the whole pipeline for ONE prompt.

    Args:
        prompt: the user prompt.
        funcs: all the available function definitions.

    Returns:
        The validated result for this prompt.

    Raises:
        ValueError: if no function matches, or a value cannot be read.
    """
    # TODO 3 : choisis la fonction avec choose_func_name.
    # Si elle renvoie None, lève une ValueError avec un message clair.
    chosen = ...

    # TODO 4 : construis le contexte (build_context), puis les
    # paramètres (build_parameters).
    context_ids = ...
    parameters = ...

    # TODO 5 : renvoie un FunctionCallResult avec le prompt, le nom de
    # la fonction choisie et les paramètres.
    return ...


def save_output(path: str, results: list[FunctionCallResult]) -> None:
    """Write the list of results to a JSON file.

    Args:
        path: path of the output file.
        results: the validated results, in the order of the prompts.

    Raises:
        ValueError: if the file cannot be written.
    """
    # TODO 6a : crée le dossier parent s'il n'existe pas
    # (attention au cas où le chemin n'a pas de dossier).

    # TODO 6b : transforme chaque résultat en dict (model_dump).
    data = ...

    # TODO 6c : écris "data" dans le fichier avec json.dump (indent=2),
    # dans un "with open(...)". Si l'écriture échoue (OSError), lève
    # une ValueError avec un message clair, comme dans parse.py.
    ...


def main() -> None:
    """Load the inputs, process every prompt, save the results."""
    flags = define_flags()

    # TODO 7a : charge les fonctions et les prompts de test.
    funcs = ...
    tests = ...

    results: list[FunctionCallResult] = []
    for test in tests:
        # TODO 7b : ignore un prompt vide (message + passer au suivant).

        # TODO 7c : appelle process_prompt dans un try/except ValueError.
        # En cas d'erreur : affiche un message clair avec le prompt, et
        # passe au prompt suivant. Sinon, ajoute le résultat à "results".
        ...

    # TODO 7d : sauvegarde les résultats avec save_output.
    ...


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Program interrupted.")
