from typing import List, Dict, Optional
import re
from enum import Enum
from pydantic import BaseModel, validator
import pandas as pd

from notion_df.utils import is_time_string

### All colors supported in NOTION


class NotionColorEnum(str, Enum):
    Default = "default"
    Gray = "gray"
    Brown = "brown"
    Orange = "orange"
    Yellow = "yellow"
    Green = "green"
    Blue = "blue"
    Purple = "purple"
    Pink = "pink"
    Red = "red"


class NotionExtendedColorEnum(str, Enum):
    Default = "default"
    Gray = "gray"
    Brown = "brown"
    Orange = "orange"
    Yellow = "yellow"
    Green = "green"
    Blue = "blue"
    Purple = "purple"
    Pink = "pink"
    Red = "red"
    GrayBackground = "gray_background"
    BrownBackground = "brown_background"
    OrangeBackground = "orange_background"
    YellowBackground = "yellow_background"
    GreenBackground = "green_background"
    BlueBackground = "blue_background"
    PurpleBackground = "purple_background"
    PinkBackground = "pink_background"
    RedBackground = "red_background"


class RichTextTypeEnum(str, Enum):
    Text = "text"
    Mention = "mention"
    Equation = "equation"


class Annotation(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: NotionExtendedColorEnum


class BaseRichText(BaseModel):
    plain_text: Optional[str]
    # TODO: The Optional[plain_text] is used when creating property values
    href: Optional[str] = None
    annotations: Optional[Annotation] = None
    type: Optional[RichTextTypeEnum]


class Link(BaseModel):
    type: str
    url: str


class Text(BaseModel):
    content: str
    link: Optional[Link]


class RichText(BaseRichText):
    text: Text

    @classmethod
    def from_value(cls, value: str):
        return cls(text=Text(content=value))


class Mention(BaseModel):
    pass  # TODO


class SelectOption(BaseModel):
    id: Optional[str]
    name: str
    color: Optional[NotionColorEnum]

    @classmethod
    def from_value(cls, value: str):
        return cls(name=value)

    @validator("name")
    def name_cannot_contain_comma(cls, v):
        if "," in v:
            raise ValueError(f"Invalid option name {v} that contains comma")
        return v


class SelectOptions(BaseModel):
    options: Optional[List[SelectOption]]

    @classmethod
    def from_value(cls, values: List[str]):
        return cls(options=[SelectOption.from_value(value) for value in values])


class RelationObject(BaseModel):
    id: str
    # TODO: Change this to UUID validation

    @classmethod
    def from_value(cls, value: str):
        return cls(id=value)


class UserObject(BaseModel):
    object: str = "user"
    id: str
    type: Optional[str]
    name: Optional[str]
    avatar_url: Optional[str]

    @classmethod
    def from_value(cls, value: str):
        return cls(id=value)

    @validator("object")
    def object_is_name(cls, v):
        if v != "user":
            raise ValueError(f"Invalid user object value {v}")
        return v


class NumberFormat(BaseModel):
    format: str


class RollupProperty(BaseModel):
    relation_property_name: Optional[str]
    relation_property_id: Optional[str]
    rollup_property_name: Optional[str]
    rollup_property_id: Optional[str]
    function: str
    # TODO: Change this to ENUM https://developers.notion.com/reference/create-a-database#rollup-configuration


class FormulaProperty(BaseModel):
    expression: str


class RelationProperty(BaseModel):
    database_id: str
    # TODO: Change this to UUID validation
    synced_property_name: Optional[str]
    synced_property_id: Optional[str]


class Date(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    time_zone: Optional[str] = None

    @validator("start")
    def is_start_ISO8601(cls, v):
        # TODO: Currently it cannot suport time ranges
        if v is not None:
            if not is_time_string(v):
                raise ValueError(
                    "The data start is not appropriately formatted as an ISO 8601 date string."
                )
        return v

    @validator("end")
    def is_end_ISO8601(cls, v):
        if v is not None:
            if not is_time_string(v):
                raise ValueError(
                    "The data end is not appropriately formatted as an ISO 8601 date string."
                )
        return v

    @classmethod
    def from_value(cls, value: str):
        return cls(start=value)
        # TODO: Now we assume the value has already been formated as strings
        # But we should parse them into appropriate formats.

    @property
    def value(self):
        return pd.to_datetime(self.start)
        # TODO: what should the data structure be if self.end is not None?
