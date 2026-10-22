from llm_sdk import Small_LLM_Model
from .parse import Parameterstype, Functiondefinition
from typing import Any


model = Small_LLM_Model()


def encode_strings(strings: list[str]) -> list[list[int]]:
    """Encode strings.

    Arg:
        strings: list of strings to be encoded

    Returns:
        list of tokens
    """
    encoded = []
    for string in strings:
        encoded.append(model.encode(string).tolist()[0])
    return (encoded)


def get_best_from(prompt: str, encoded_funcs: list[list[int]], functions: dict[str, str]) -> int | None:
    """Selects the function that matches the prompt by letting the model decide token by token,
    but only from among the tokens that lead to a valid function name.

    Args:
        prompt: the user prompt.
        encoded_funcs: list of encoded functions.
        functions: used only to write the text shown to the model(name, description).

    Return:
        The position of the chosen noun.
    """
    result: list[int] = []
    base_prompt = ("Get the best function name from this prompt:\n"
                    "Use fn_substitute_string_with_regex when the prompt start with replace, substitute or something like that\n"
                    "Select the appropriate function for each prompt"
                    f"Prompt: {prompt}\n"
                    f"Functions: {functions}\n"
                    "Answer:"
                    )

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
    """Takes the name of the function after obtaining the result of `get_best_from`

    Args:
        prompt: the user prompt.
        funcs: all the available funtion definitions.

    Returns:
        The chosen function name or nothing
    """
    functions = {}
    funcs_encode = encode_strings(f.name for f in funcs)
    for f in funcs:
        functions[f.name] = f.description
    index = get_best_from(prompt, funcs_encode, functions)
    if index is None:
        return None
    return funcs[index]


def extract_param(
        model: Small_LLM_Model,
        context_ids: list[int],
        param_type: Parameterstype,
        end_id: int,
        max_tokens: int = 30) -> tuple[Any, list[int]]:
    """Generates the value of a single parameter, token by token, whilst respecting its data type,
    and stops automatically once the value is complete.

    Args:
        model: LLM used
        context_ids: everything that has already been written
                    before this value, in tokens: the instructions, the prompt, and the start of the JSON
        param_type: the expected type
        end_it: the token that ends this value: , if there are any remaining parameters, }
                for the last one.
        max_tokens: for security reasons, once 30 tokens have been used, the process stops,
                    even if it is not finished

    Returns:
        A tuple (value, generated): the extracted value (for example 40.0
        or "shrek"), and its tokens, used as context for the next parameter.
    """

    digit_ids = {model.encode(d).tolist()[0][0] for d in "0123456789"}
    dot_id = model.encode(".").tolist()[0][0]
    minus_id = model.encode("-").tolist()[0][0]


    generated: list[int] = []
    is_number = param_type in (Parameterstype.NUMBER, Parameterstype.INTEGER)
    has_dot = False
    has_digit = False

    for _ in range(max_tokens):
        logits = model.get_logits_from_input_ids(context_ids + generated)
        if is_number:
            candidat = set(digit_ids)
            if not has_digit and not has_dot:
                candidat.add(minus_id)
            if has_digit and not has_dot:
                candidat.add(dot_id)
            if has_digit:
                candidat.add(end_id)

            max_value = max((logits[cand] for cand in candidat))
            next_token = logits.index(max_value)
            if next_token == end_id:
                break
            generated.append(next_token)

            if next_token == dot_id:
                has_dot = True
            if next_token in digit_ids:
                has_digit = True

        else:
            next_token = logits.index(max(logits))
            generated.append(next_token)
            if '"' in model.decode(generated):
                break
    text = model.decode(generated)
    if is_number:
        value: Any = float(text)
    else:
        position = text.find('"')
        if position != -1:
            value = text[:position]
        else:
            value = text
        generated = model.encode(value).tolist()[0]
    return (value, generated)


def build_parameters(
        model: Small_LLM_Model,
        context_ids: list[int],
        chosen_function: Functiondefinition) -> dict[str, Any]:
    comma_id = model.encode(",").tolist()[0][0]
    brace_id = model.encode("}").tolist()[0][0]
    quote_ids = model.encode('"').tolist()[0]

    brace_open_id = model.encode("{").tolist()[0]
    context = context_ids + brace_open_id

    result: dict[str, Any] = {}
    param_names = list(chosen_function.parameters.keys())

    for index, name in enumerate(param_names):
        is_last = (index == len(param_names) - 1)
        if is_last:
            end_id = brace_id
        else:
            end_id = comma_id
        param_type = chosen_function.parameters[name].type
        is_number = param_type in (Parameterstype.NUMBER, Parameterstype.INTEGER)
        if is_number:
            text = f'"{name}":'
        else:
            text = f'"{name}":"'
        context = context + model.encode(text).tolist()[0]
        value, tokens = extract_param(model, context, param_type, end_id)
        result[name] = value
        if is_number:
            context = context + tokens +[end_id]
        else:
            context = context + tokens + quote_ids + [end_id]
    return result


def build_context(
        model: Small_LLM_Model,
        prompt: str,
        chosen_function: Functiondefinition) -> list[int]:
    text = (
        "Extract the function call parameters from the prompt. Do not answer the prompt.\n"
        "Copy text values verbatim: same case, same spelling, nothing added or removed.\n"
        "Function: fn_repeat_text - Repeat a text several times\n"
        "For fn_substitute_string_with_regex, extract exactly the requested parameters, no more, no less."
        f"Function: {chosen_function.name}\n"
        f"Parameters: {chosen_function.parameters}\n"
        f"Prompt: {prompt}"
        "Answer:\n"
    )
    return model.encode(text).tolist()[0]
