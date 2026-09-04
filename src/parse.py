try:
    from pydantic import (
        BaseModel,
        Field,
        ValidationError,
        model_validator
    )
except ImportError as e:
    print(e)
from enum import Enum
import json


class Parameters(Enum):
    Number = "number"
    String = "string"
    Non = "None"


class Return(Enum):
    Number = "number"
    String = "string"
    Non = "None"


class Function_definition(BaseModel):
    name: str = Field(min_lenght=2, max_length=...)
    description: str = Field(max_lenght=...)
    parameters: dict[str, Parameters]
    returns: Return


def load_function_definition(path: str) -> list[Function_definition]:
    if not path:
        raise FileNotFoundError(f"{path} is not found")
    with open('data/input/function_calling_tests.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    functions: list[Function_definition] = []
    for entry in data:
        try:
            functions.append(Function_definition(**entry))
        except ValidationError as e:
            print(f"{entry}\n{e}")

    print(f"{len(functions)}.")
    for fn in functions:
        print(fn.name, "->", fn.parameters)

load_function_definition()
