from llm_sdk import Small_LLM_Model
from src.vocab import load_vocab, build_digit_token_ids

model = Small_LLM_Model()
vocab = load_vocab(model.get_path_to_vocab_file())
digit_ids = build_digit_token_ids(vocab)

print(f"Sum of token in vocab : {len(vocab)}")
print(f"Sum of number token in vocab: {len(digit_ids)}")

for txt in ["4", "40", "Ġ4", "Ġ40", "cat", "4.5", "-4", ".", "-", '"']:
    token_id = vocab.get(txt)
    if token_id is not None:
        print(f"{txt!r} -> id {token_id} -> is_digit ? {token_id in digit_ids}")
    else:
        print(f"{txt!r} is_notdigit")
