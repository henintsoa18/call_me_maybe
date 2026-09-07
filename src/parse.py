from pydantic import (
        BaseModel,
        Field,
        ValidationError,
        model_validator
    )
from enum import Enum
import json
import os


class Parameterstype(Enum):
    Number = "number"
    String = "string"
    Non = "None"


class Returntype(Enum):
    Number = "number"
    String = "string"
    Non = "None"


class ParameterSpec(BaseModel):
    type: Parameterstype


class ReturnSpec(BaseModel):
    type: Returntype


class Functiondefinition(BaseModel):
    name: str = Field(min_length=2)
    description: str = Field()
    parameters: dict[str, ParameterSpec]
    returns: ReturnSpec


class Functioncalling(BaseModel):
    prompt: str = Field()


def load_function_definitions(path: str) -> list[Functiondefinition]:
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"{path} is not found")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"{path}: {e}")
        return []
    functions: list[Functiondefinition] = []
    for entry in data:
        try:
            functions.append(Functiondefinition(**entry))
        except ValidationError as e:
            print(f"{entry}\n{e}")
    print(f"Total of funtions: {len(functions)}")
    for fn in functions:
        print(f"{fn.name} -> {fn.parameters}")
    return functions


def load_function_calling(path: str) -> list[Functioncalling]:
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"{path} is not found")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"{path}: {e}")
        return []
    functions: list[Functioncalling] = []
    for entry in data:
        try:
            functions.append(Functioncalling(**entry))
        except ValidationError as e:
            print(f"{entry}\n{e}")
    print(f"Total of funtions: {len(functions)}")
    for fn in functions:
        print(f"{fn.prompt}")
    return functions


load_function_definitions("data/input/functions_definition.json")
load_function_calling("data/input/function_calling_tests.json")
