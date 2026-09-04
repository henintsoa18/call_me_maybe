from llm_sdk.llm_sdk import Small_LLM_Model

model = Small_LLM_Model()

x = model.encode("dick")[0].tolist()

y = model.get_logits_from_input_ids(x)

print(y)
k = y.index(max(y))

print(model.decode(x))
print(model.decode(k))

z = x + [k]
print(model.decode(z))

# print(model.get_path_to_vocab_file())
