from pydantic import (
        BaseModel,
        Field,
        ValidationError,
        ConfigDict
    )
from enum import Enum
from typing import Any
import json


class Parameterstype(Enum):
    """Allowed parameter types."""
    NUMBER = "number"
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    NONE = "None"


class Returntype(Enum):
    """Allowed return types"""
    NUMBER = "number"
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    NONE = "None"


class ParameterSpec(BaseModel):
    """Specification of a single function parameter.

    Attributes:
        type: the type of the parameter,
            among the allowed Parameterstype values.
    """
    type: Parameterstype


class ReturnSpec(BaseModel):
    """Specification of a function's return value.

    Attributes:
        type: the return type, among the allowed Returntype values.
    """
    type: Returntype


class Functiondefinition(BaseModel):
    """Definition of a function the LLM can choose to call.

    Attributes:
        name: function name (at least 2 characters).
        description: description of what the function does.
        parameters: the name and the type of the parameters.
        returns: the type of the return value.
    """
    name: str = Field(min_length=2)
    description: str = Field()
    parameters: dict[str, ParameterSpec]
    returns: ReturnSpec


class Functioncalling(BaseModel):
    """A natural-language prompt for which a function call must be found.

    Attributes:
        prompt: the user prompt to translate into a function call.
    """
    prompt: str = Field()


class FunctionCallResult(BaseModel):
    """Output of the function-calling step for one prompt.

    Extra fields are forbidden so the serialized
    JSON matches the expected format.

    Attributes:
        prompt: the original prompt.
        name: name of the selected function.
        parameters: arguments extracted from the prompt,
            keyed by parameter name.
    """
    model_config = ConfigDict(extra="forbid")
    prompt: str
    name: str
    parameters: dict[str, Any]


def load_function_definitions(path: str) -> list[Functiondefinition]:
    """Load and validate function definitions from a JSON file.

    Args:
        path: path to a JSON file containing an array of function definitions.

    Returns:
        The list of valid Functiondefinition objects.

    Raises:
        ValueError: If the file cannot be read, is not valid JSON,
            or does not contain a JSON array.
    """
    try:
        with open(path, 'r', encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise ValueError(f"Cannot read {path}: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in {path}: {e}")
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
    """Load and validate the prompts to process from a JSON file.

    Args:
        path: path to a JSON file containing an array of prompts.

    Returns:
        The list of valid Functioncalling objects.

    Raises:
        ValueError: If the file cannot be read, is not valid JSON,
            or does not contain a JSON array.
    """
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
