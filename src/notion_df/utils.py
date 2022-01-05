from typing import List, Dict, Optional, Union, Any

def flatten_dict(data: Dict):
    """Remove entries in dict whose values are None"""
    if isinstance(data, dict):
        return {
            key: flatten_dict(value)
            for key, value in data.items()
            if value is not None
        }
    elif isinstance(data, list) or isinstance(data, tuple):
        return [flatten_dict(value) for value in data]
    else:
        return data

ISO8601_STRFTIME_TRANSFORMER = lambda ele: ele.strftime('%Y-%m-%dT%H:%M:%SZ')