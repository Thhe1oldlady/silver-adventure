"""
Utility functions.
"""

import json
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np


def generate_hash(data: Any) -> str:
    """
    Generate hash for any data structure.
    """
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(data_str.encode()).hexdigest()[:16]


def validate_json_structure(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate JSON data against a schema.
    """
    errors = []
    
    # Check required fields
    required_fields = schema.get('required', [])
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Check field types
    field_types = schema.get('types', {})
    for field, expected_type in field_types.items():
        if field in data and not isinstance(data[field], expected_type):
            errors.append(f"Field '{field}' should be of type {expected_type.__name__}")
    
    return errors


def convert_to_dataframe(data: Any) -> pd.DataFrame:
    """
    Convert various data formats to pandas DataFrame.
    """
    if isinstance(data, dict):
        if 'records' in data:
            return pd.DataFrame(data['records'])
        else:
            return pd.DataFrame([data])
    elif isinstance(data, list):
        return pd.DataFrame(data)
    else:
        return pd.DataFrame([{'value': data}])


def clean_dataframe(df: pd.DataFrame, options: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Clean DataFrame with various options.
    """
    if options is None:
        options = {}
    
    # Drop null values
    if options.get('drop_nulls', False):
        df = df.dropna()
    
    # Fill null values
    fill_value = options.get('fill_nulls')
    if fill_value is not None:
        df = df.fillna(fill_value)
    
    # Remove duplicates
    if options.get('remove_duplicates', False):
        df = df.drop_duplicates()
    
    # Convert data types
    type_conversions = options.get('type_conversions', {})
    for column, target_type in type_conversions.items():
        if column in df.columns:
            df[column] = df[column].astype(target_type)
    
    return df


def format_response(data: Any, status: str = "success", message: str = None) -> Dict[str, Any]:
    """
    Format API response.
    """
    response = {
        "status": status,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    if message:
        response["message"] = message
    
    return response


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics for numerical data.
    """
    if not data:
        return {}
    
    np_data = np.array(data)
    
    return {
        "count": len(data),
        "mean": float(np.mean(np_data)),
        "median": float(np.median(np_data)),
        "std": float(np.std(np_data)),
        "min": float(np.min(np_data)),
        "max": float(np.max(np_data)),
        "q25": float(np.percentile(np_data, 25)),
        "q75": float(np.percentile(np_data, 75))
    }


def batch_process(items: List[Any], batch_size: int = 100) -> List[List[Any]]:
    """
    Split items into batches.
    """
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON string with default fallback.
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: Any = None) -> str:
    """
    Safely dump data to JSON string.
    """
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return json.dumps(default) if default is not None else "{}"


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Basic phone number validation.
    """
    import re
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits) <= 15


def get_data_type_info(data: Any) -> Dict[str, Any]:
    """
    Get information about data type and structure.
    """
    info = {
        "type": type(data).__name__,
        "size": 0,
        "structure": {}
    }
    
    if isinstance(data, dict):
        info["size"] = len(data)
        info["structure"] = {
            "keys": list(data.keys()),
            "key_count": len(data),
            "nested_levels": _get_nested_levels(data)
        }
    elif isinstance(data, list):
        info["size"] = len(data)
        info["structure"] = {
            "length": len(data),
            "item_types": list(set(type(item).__name__ for item in data))
        }
    elif isinstance(data, str):
        info["size"] = len(data)
        info["structure"] = {
            "length": len(data),
            "encoding": "utf-8"
        }
    
    return info


def _get_nested_levels(data: Dict[str, Any], level: int = 0) -> int:
    """
    Get the maximum nesting level in a dictionary.
    """
    if not isinstance(data, dict):
        return level
    
    max_level = level
    for value in data.values():
        if isinstance(value, dict):
            max_level = max(max_level, _get_nested_levels(value, level + 1))
    
    return max_level