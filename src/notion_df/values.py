### Referring to https://developers.notion.com/reference/page#property-value-object

from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from copy import deepcopy
import numbers

from pydantic import BaseModel, parse_obj_as, validator, root_validator
import pandas as pd
from pandas.api.types import is_array_like

from notion_df.base import (
    RichTextObject,
    SelectOption,
    DateObject,
    RelationObject,
    UserObject,
    RollupObject,
    FileObject,
    FormulaObject
)
from notion_df.utils import (
    flatten_dict,
    is_list_like
)


class BasePropertyValues(BaseModel):
    id: Optional[str]  # TODO: Rethink whether we can do this
    # The Optional[id] is used when creating property values
    type: Optional[str]

    # TODO: Add abstractmethods for them
    @classmethod
    def from_value(cls, value):
        pass

    @property
    def value(self):
        pass

    def query_dict(self):
        return flatten_dict(self.dict())


class TitleValues(BasePropertyValues):
    title: List[RichTextObject]

    @property
    def value(self) -> Optional[str]:
        return (
            None
            if len(self.title) == 0
            else " ".join([text.value for text in self.title])
        )

    @classmethod
    def from_value(cls, value):
        return cls(title=RichTextObject.encode_string(value))
        # TODO: Rethink whether we should split input string to multiple elements in the list


class RichTextValues(BasePropertyValues):
    rich_text: List[RichTextObject]

    @property
    def value(self) -> Optional[str]:
        return (
            None
            if len(self.rich_text) == 0
            else " ".join([text.value for text in self.rich_text])
        )

    @classmethod
    def from_value(cls, value: str):
        return cls(rich_text=RichTextObject.encode_string(value))


class NumberValues(BasePropertyValues):
    number: Optional[Union[float, int]]

    @property
    def value(self) -> str:
        return self.number

    @classmethod
    def from_value(cls, value: Union[float, int]):
        return cls(number=value)


class SelectValues(BasePropertyValues):
    select: Optional[SelectOption]

    @property
    def value(self) -> Optional[str]:
        return self.select.name if self.select else None

    @classmethod
    def from_value(cls, value: str):
        return cls(select=SelectOption.from_value(value))


class MultiSelectValues(BasePropertyValues):
    multi_select: List[SelectOption]

    @property
    def value(self) -> List[str]:
        return [select.name for select in self.multi_select]

    @classmethod
    def from_value(cls, values: Union[List[str], str]):
        if is_list_like(values):
            return cls(
                multi_select=[SelectOption.from_value(value) for value in values]
            )
        else:
            return cls(multi_select=[SelectOption.from_value(values)])


class DateValues(BasePropertyValues):
    date: Optional[DateObject]

    @property
    def value(self) -> str:
        return self.date.value if self.date else None

    @classmethod
    def from_value(cls, value: str):
        return cls(date=DateObject.from_value(value))


class FormulaValues(BasePropertyValues):
    formula: FormulaObject
    
    @property
    def value(self):
        return self.formula.value


class RelationValues(BasePropertyValues):
    relation: List[RelationObject]

    @property
    def value(self) -> List[str]:
        return [relation.id for relation in self.relation]

    @classmethod
    def from_value(cls, values: Union[List[str], str]):
        if is_list_like(values):
            return cls(relation=[RelationObject.from_value(value) for value in values])
        else:
            return cls(relation=[RelationObject.from_value(values)])


class PeopleValues(BasePropertyValues):
    people: List[UserObject]

    @property
    def value(self) -> List[str]:
        return [people.id for people in self.people]

    @classmethod
    def from_value(cls, values: Union[List[str], str]):
        if is_list_like(values):
            return cls(people=[UserObject.from_value(value) for value in values])
        else:
            return cls(people=[UserObject.from_value(values)])


class FilesValues(BasePropertyValues):
    files: List[FileObject]

    @property
    def value(self) -> List[str]:
        return [file.value for file in self.files]

class CheckboxValues(BasePropertyValues):
    checkbox: Optional[bool]

    @property
    def value(self) -> Optional[bool]:
        return self.checkbox

    @classmethod
    def from_value(cls, value: bool):
        return cls(checkbox=value)


class URLValues(BasePropertyValues):
    url: Optional[str]

    @property
    def value(self) -> Optional[str]:
        return self.url

    @classmethod
    def from_value(cls, value: Optional[str]):
        return cls(url=value)

    def query_dict(self):
        res = flatten_dict(self.dict())
        if "url" not in res:
            res["url"] = None
            # The url value is required by the notion API
        return res


class EmailValues(BasePropertyValues):
    email: Optional[str]

    @property
    def value(self) -> Optional[str]:
        return self.email

    @classmethod
    def from_value(cls, value: str):
        return cls(email=value)


class PhoneNumberValues(BasePropertyValues):
    phone_number: Optional[str]

    @property
    def value(self) -> Optional[str]:
        return self.phone_number

    @classmethod
    def from_value(cls, value: str):
        return cls(phone_number=value)


class CreatedTimeValues(BasePropertyValues):
    created_time: Optional[str]

    @property
    def value(self) -> Optional[str]:
        return self.created_time

    @classmethod
    def from_value(cls, value: str):
        return cls(created_time=value)


class CreatedByValues(BasePropertyValues):
    created_by: UserObject

    @property
    def value(self) -> List[str]:
        return self.created_by.value


class LastEditedTimeValues(BasePropertyValues):
    last_edited_time: str

    @property
    def value(self) -> Optional[str]:
        return self.last_edited_time

    @classmethod
    def from_value(cls, value: str):
        return cls(last_edited_time=value)


class LastEditedByValues(BasePropertyValues):
    last_edited_by: UserObject

    @property
    def value(self) -> List[str]:
        return self.last_edited_by.value


VALUES_MAPPING = {
    list(_cls.__fields__.keys())[-1]: _cls
    for _cls in BasePropertyValues.__subclasses__()
    if len(_cls.__fields__)
    == 3  # TODO: When all classes have been implemented, we can just remove this check
}


class RollupValues(BasePropertyValues):
    rollup: RollupObject

    @validator("rollup", pre=True)
    def check_rollup_values(cls, val):
        val = deepcopy(val)
        if val.get("array") is not None:
            val["array"] = [
                parse_obj_as(VALUES_MAPPING[data["type"]], data)
                for data in val["array"]
            ]
        return val

    @property
    def value(self):
        return self.rollup.value


VALUES_MAPPING["rollup"] = RollupValues


def parse_single_values(data: Dict) -> BasePropertyValues:
    return parse_obj_as(VALUES_MAPPING[data["type"]], data)


def _guess_value_schema(val: Any) -> object:

    if isinstance(val, str):
        return RichTextValues
    elif isinstance(val, numbers.Number):
        return NumberValues
    elif isinstance(val, bool):
        return CheckboxValues
    else:
        raise ValueError(f"Unknown value type: {type(val)}")


def _is_item_empty(item):

    if item is None or item == []:
        return True

    isna = pd.isna(item)
    if is_array_like(isna):
        isna = isna.all()
        # TODO: Rethink it is all or any

    return isna


RESERVED_VALUES = ["url"]
# Even if the value is none, we still want to keep it in the dataframe


def _is_reserved_value(key, schema):
    return schema[key].type in RESERVED_VALUES


def parse_value_with_schema(
    idx: int, key: str, value: Any, schema: "DatabaseSchema"
) -> BasePropertyValues:
    # TODO: schema shouldn't be allowed to be empty in the future version
    # schema should be determined at the dataframe level.

    if schema is not None:
        value_func = VALUES_MAPPING[schema[key].type]
    else:
        if idx == 0:
            # TODO: Brutally enforce the first one to be the title, though
            # should be optimized in future versions
            value_func = TitleValues
            value = str(value)
        else:
            value_func = _guess_value_schema(value)

    return value_func.from_value(value)


@dataclass
class PageProperty:
    """This class is used to parse properties of a single Notion Page. 
    
    :: example:
    
        >>> data = \
                {"Description": {"id": "ji%3Dc", "type": "rich_text", "rich_text": []},
                "Created": {"id": "mbOA", "type": "date", "date": None},
                "Title": {"id": "title", "type": "title", "title": []}}
        >>> property = PageProperty.from_raw(data)
    """

    properties: Dict[str, BasePropertyValues]

    @classmethod
    def from_raw(cls, properties: Dict) -> "PageProperty":
        properties = {k: parse_single_values(v) for k, v in properties.items()}
        return cls(properties)

    def __getitem__(self, key):
        return self.properties[key]

    def to_series(self):
        return pd.Series(
            {key: property.value for key, property in self.properties.items()}
        )

    @classmethod
    def from_series(
        cls, series: pd.Series, schema: "DatabaseSchema" = None
    ) -> "PageProperty":
        return cls(
            {
                key: parse_value_with_schema(idx, key, val, schema)
                for idx, (key, val) in enumerate(series.items())
                if not _is_item_empty(val) or _is_reserved_value(key, schema)
            }
        )

    def query_dict(self) -> Dict:
        return {key: property.query_dict() for key, property in self.properties.items()}


@dataclass
class PageProperties:
    """This class is used to parse multiple page properties within a database
    
    :: example:
    
        >>> data = \
                [
                    {
                        "object": "page",
                        "id": "xxxx",
                        "created_time": "2032-01-03T00:00:00.000Z",
                        "properties": {
                            "Description": {"id": "ji%3Dc", "type": "rich_text", "rich_text": []},
                            "Created": {"id": "mbOA", "type": "date", "date": None},
                            "Title": {"id": "title", "type": "title", "title": []}
                        }
                    },
                    {
                        "object": "page",
                        "id": "xxxx",
                        "created_time": "2032-01-03T00:00:01.000Z",
                        "properties": {
                            "Description": {"id": "ji%3Dc", "type": "rich_text", "rich_text": []},
                            "Created": {"id": "mbOA", "type": "date", "date": None},
                            "Title": {"id": "title", "type": "title", "title": []}
                        }
                    }
                ]
        >>> property = PageProperties.from_raw(data)
    """

    page_properties: List[PageProperty]

    @classmethod
    def from_raw(cls, properties: List[Dict]) -> "PageProperties":
        page_properties = [
            PageProperty.from_raw(property["properties"]) for property in properties
        ]
        return cls(page_properties)

    def __getitem__(self, key: int):
        return self.page_properties[key]

    def to_frame(self):
        return pd.DataFrame([property.to_series() for property in self.page_properties])
