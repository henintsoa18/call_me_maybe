from pydantic import (
        BaseModel,
        Field,
        ValidationError
    )
from enum import Enum
from typing import Any
import json
import os


class Parameterstype(Enum):
    NUMBER = "number"
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    NONE = "None"


class Returntype(Enum):
    NUMBER = "number"
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    NONE = "None"


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
    try:
        with open(path, 'r', encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise ValueError(f"Cannot read {path}: {e}")
    except json.JSONDecodeError as e:
        raise(f"Invalid JSON in {path}: {e}")
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    functions: list[Functiondefinition] = []
    for entry in data:
        try:
            functions.append(Functiondefinition(**entry))
        except ValidationError as e:
            print(f"{entry}: {e}")
    return functions


def load_function_calling(path: str) -> list[Functioncalling]:
    try:
        with open(path, 'r', encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise ValueError(f"Cannot read {path}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    functions: list[Functioncalling] = []
    for entry in data:
        try:
            functions.append(Functioncalling(**entry))
        except ValidationError as e:
            print(f"{entry}\n{e}")
    return functions


if __name__ == "__main__":
    print(load_function_definitions("data/input/functions_definition.json"))
    print()
    print(load_function_calling("data/input/function_calling_tests.json"))
