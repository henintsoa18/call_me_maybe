from llm_sdk.llm_sdk import Small_LLM_Model

if __name__ == "__main__":
    model = Small_LLM_Model()
    prompt = "What is the sum of 3 and 2?"

    inputs_ids = model.encode(prompt).tolist()[0]

    generated = ""
    for i in range(50):
        logits = model.get_logits_from_input_ids(inputs_ids)
        next_token = logits.index(max(logits))
        inputs_ids.append(next_token)

        generated += model.decode([next_token])

    print(generated)
