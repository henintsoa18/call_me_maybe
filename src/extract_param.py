from llm_sdk import Small_LLM_Model
from src import Parameterstype
from typing import Any


#def generate_number(
#        model: Small_LLM_Model,
#        context: list[int],
#        digit_ids: set[int],
#        dot_id: int,
#        minus_id: int,
#        end_id: int) -> tuple[float, list[int]]:
#    generated: list[int] = []
#    has_dot = False
#    has_digit = False
#
#    while True:
#        candidat = set(digit_ids)
#        if not has_digit and not has_dot:
#            candidat.add(minus_id)
#        if has_digit and not has_dot:
#            candidat.add(dot_id)
#        if not has_digit and has_dot:
#            candidat.add(end_id)

def extract_param(
        model: Small_LLM_Model,
        context_ids: list[int],
        param_type: Parameterstype,
        digit_ids: set[int],
        dot_id: int,
        minus_id: int,
        quote_id: int,
        end_id: int,
        max_tokens: int = 30) -> tuple[Any, list[int]]:

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
            if next_token == quote_id:
                break
            generated.append(next_token)
    text = model.decode(generated)
    value: Any = float(text) if is_number else text
    return (value, generated)
