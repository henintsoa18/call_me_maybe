from .parse import (
    Functiondefinition,
    FunctionCallResult,
    load_function_definitions,
    load_function_calling)
from .call_me_maybe import (
    build_parameters,
    build_context,
    choose_func_name,
    model)
import json
import argparse
import os


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
        "--output",
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
    chosen = choose_func_name(prompt, funcs)
    if chosen is None:
        raise ValueError("No function found fofr this prompt")
    context_ids = build_context(model, prompt, chosen)
    parameters = build_parameters(model, context_ids, chosen)
    return FunctionCallResult(
        prompt=prompt,
        name=chosen.name,
        parameters=parameters
    )


def save_output(path: str, results: list[FunctionCallResult]) -> None:
    """Write the list of results to a JSON file.

    Args:
        path: path of the output file.
        results: the validated results, in the order of the prompts.

    Raises:
        ValueError: if the file cannot be written.
    """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    data = []
    for result in results:
        data.append(result.model_dump())
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        raise ValueError(f"Cannot write '{path}': {e}") from e


def main() -> None:
    """Load the inputs, process every prompt, save the results."""
    flags = take_flags()
    funcs = load_function_definitions(flags.functions_definition)
    tests = load_function_calling(flags.input)
    results: list[FunctionCallResult] = []
    for test in tests:
        if not test.prompt.strip():
            print("The prompt is empty")
            continue
        try:
            result = process_prompt(test.prompt, funcs)
        except ValueError as error:
            print(f"Error for the prompt {test!r} : {error}")
            continue
        else:
            results.append(result)
            print(result.model_dump_json(indent=2))
        save_output(flags.output, results)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Program interrupted.")
