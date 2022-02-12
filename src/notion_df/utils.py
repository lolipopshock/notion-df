from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from dateutil.parser import parse
from uuid import UUID

import pandas as pd
from pandas.api.types import is_array_like, is_datetime64_any_dtype, is_list_like


def flatten_dict(data: Dict):
    """Remove entries in dict whose values are None"""
    if isinstance(data, dict):
        return {
            key: flatten_dict(value) for key, value in data.items() if value is not None
        }
    elif isinstance(data, list) or isinstance(data, tuple):
        return [flatten_dict(value) for value in data]
    else:
        return data


def is_item_empty(item: Any) -> bool:

    if item is None or item == []:
        return True

    isna = pd.isna(item)
    if is_array_like(isna):
        isna = isna.all()
        # TODO: Rethink it is all or any

    return isna


def is_time_string(s: str) -> bool:

    # Ref https://stackoverflow.com/questions/25341945/check-if-string-has-date-any-format
    try:
        parse(s)
        return True
    except ValueError:
        return False


def is_uuid(s: str) -> bool:
    # Kind of an OK solution.. But can be further improved?
    try:
        UUID(str(s))
        return True
    except ValueError:
        return False


ISO8601_REGEX = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
# See https://stackoverflow.com/questions/41129921/validate-an-iso-8601-datetime-string-in-python
ISO8601_STRFTIME_TRANSFORM = lambda ele: ele.strftime("%Y-%m-%dT%H:%M:%SZ")

strtime_transform = lambda ele: parse(ele).strftime("%Y-%m-%dT%H:%M:%SZ")
datetime_transform = lambda ele: ele.strftime("%Y-%m-%dT%H:%M:%SZ")


def transform_time(s: Any) -> str:
    if not is_item_empty(s):
        if isinstance(s, str):
            return strtime_transform(s)
        elif isinstance(s, datetime):
            return datetime_transform(s)
        elif is_datetime64_any_dtype(s):
            return datetime_transform(s)


IDENTITY_TRANSFORM = lambda ele: ele
SECURE_STR_TRANSFORM = lambda ele: str(ele) if not is_item_empty(ele) else ""
LIST_TRANSFORM = lambda ele: ele if is_list_like(ele) else [ele]
REMOVE_EMPTY_STR_TRANSFORM = (
    lambda ele: None if ele == "" or ele is None or pd.isna(ele) else SECURE_STR_TRANSFORM(ele)
)
SECURE_BOOL_TRANSFORM = lambda ele: bool(ele) if not is_item_empty(ele) else None
SECURE_TIME_TRANSFORM = transform_time
