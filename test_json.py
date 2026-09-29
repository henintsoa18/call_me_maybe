from llm_sdk import Small_LLM_Model
from src.parse import load_function_definitions, load_function_calling
from src.__main__ import choose_func_name

model = Small_LLM_Model()

funcs = load_function_definitions("data/input/functions_definition.json")
tests = load_function_calling("data/input/function_calling_tests.json")

for test in tests:
    chosen = choose_func_name(test.prompt, funcs)
    name = chosen.name if chosen else None
    print(f"{test.prompt!r} -> {name}")
