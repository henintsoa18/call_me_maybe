import json


def load_vocab(path: str) -> dict[str, int]:
    try:
        with open(path, 'r', encoding="utf-8") as f:
            vocab: dict[str, int] = json.load(f)
    except OSError as e:
        raise ValueError(f"Cannot read {path}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")
    if not isinstance(vocab, dict):
        raise ValueError(f"{path} is invalid")
    return vocab


def build_digit_token_ids(vocab: dict[str, int]) -> set[int]:
    digit_ids: set[int] = set()
    for text, token_id in vocab.items():
        cleaned = text.removeprefix("Ġ")
        if cleaned.isdigit():
            digit_ids.add(token_id)
    return digit_ids
