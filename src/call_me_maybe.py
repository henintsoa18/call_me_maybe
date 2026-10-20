from llm_sdk import Small_LLM_Model
from .parse import Parameterstype, Functiondefinition
from typing import Any


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


def extract_param(
        model: Small_LLM_Model,
        context_ids: list[int],
        param_type: Parameterstype,
        end_id: int,
        max_tokens: int = 30) -> tuple[Any, list[int]]:

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
            text = f'"{name}": '
        else:
            text = f'"{name}": "'
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
    params_text = ""
    for name, spec in chosen_function.parameters.items():
        params_text += f"{name} ({spec.type.value}), "
    params_text = params_text.rstrip(", ")

    example = '{"text": "hi", "times": 3.0}'
    text = (
        "Extract the parameters of a function call from the prompt.\n"
        "Copy text values exactly as written in the prompt: same case, "
        "same spelling, no added words.\n"
        "Numbers are written as decimals. Regex parameters must be valid "
        "regular expressions (for example [A-Z] matches capital "
        "letters).\n\n"
        "Don't reverse string if it's a request, take just the parameters"
        "Function: fn_repeat_text - Repeat a text several times\n"
        "Parameters: text (string), times (number)\n"
        "Prompt: Repeat the word 'hi' 3 times\n"
        f"Answer:\n{example}\n\n"
        f"Function: {chosen_function.name} - {chosen_function.description}\n"
        f"Parameters: {params_text}\n"
        f"Prompt: {prompt}\n"
        "Answer:\n"
    )
    return model.encode(text).tolist()[0]
