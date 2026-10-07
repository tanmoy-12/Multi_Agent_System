import re
import json
from typing import Any, Type, TypeVar
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

def extract_json(text: str) -> dict | list:
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1)
    else:
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if match:
            text = match.group(1)
    
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode failed: {e}. Text snippet: {text[:100]}...")
        raise ValueError(f"Invalid JSON: {e}")

def parse_and_validate(text: str, model: Type[T]) -> T:
    data = extract_json(text)
    try:
        return model.model_validate(data)
    except ValidationError as e:
        logger.error(f"Pydantic validation failed: {e}")
        raise ValueError(f"Validation error: {e}")